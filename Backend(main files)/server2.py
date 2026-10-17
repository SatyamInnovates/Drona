from fastapi import FastAPI,HTTPException,Request
from fastapi.staticfiles import StaticFiles
from app_paths import get_database_dir
from pathlib import Path
import re
import os
import json
from datetime import date
from typing import Union
from pydantic import BaseModel,StrictInt,StrictFloat
import requests
from urllib.parse import urlparse
import threading
import sys
from fastapi.staticfiles import StaticFiles
import webbrowser
import subprocess
import tkinter as tk
from tkinter import filedialog,messagebox,simpledialog

if getattr(sys, "frozen", False):
    PROJECT_DIR = Path(sys.executable).resolve().parent

    FRONTEND_DIR = Path(sys._MEIPASS) / "Frontend"
else:
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    FRONTEND_DIR = PROJECT_DIR / "Frontend"

DATABASE_DIR = get_database_dir()
SETTINGS_FILE = DATABASE_DIR / "repo_settings.json"
SESSIONS_FILE = DATABASE_DIR / "focus_sessions.json"

CODING_ACTIVITY_FILE = DATABASE_DIR / "coding_activity.json"

DAY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"

ACTIVITY_UPDATE_LOCK = threading.Lock()
CODING_ACTIVITY_LOCK = threading.Lock()
from main import update_activity



def load_local_env():
    env_file = PROJECT_DIR / ".env"
    try:
        lines = env_file.read_text(encoding='utf-8').splitlines()
    except OSError:
        return 
        
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name,value = line.split("=",1)
        name = name.strip()
        value = value.strip().strip("\"'")
        if name and name not in os.environ:
            os.environ[name] = value
          
          
          
          
        
load_local_env()
app = FastAPI()
# app.mount(
#     "/Frontend",
#     StaticFiles(directory=PROJECT_DIR / "Frontend", html=True),
#     name="frontend",
# )

def read_sessions():
    try:
        data = json.loads(SESSIONS_FILE.read_text(encoding='utf-8'))
        return data if isinstance(data,dict) else {}
    except (OSError,json.JSONDecodeError):
        return {}


def read_coding_activity():
    try:
        data = json.loads(CODING_ACTIVITY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def read_database_json(filename, fallback):
    try:
        return json.loads((DATABASE_DIR / filename).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback


@app.get("/api/topics")
def get_topics():
    data = read_database_json("data.json", [])
    return data if isinstance(data, list) else []


@app.get("/api/streaks")
def get_streaks():
    data = read_database_json("streaks.json", {})
    return data if isinstance(data, dict) else {}


@app.get("/api/yesterday-files")
def get_yesterday_files():
    data = read_database_json("yesterday_files.json", [])
    return data if isinstance(data, list) else []


@app.get("/api/repo-settings")
def get_repo_settings():
    data = read_database_json("repo_settings.json", {})
    enabled = isinstance(data, dict) and data.get("github_push_enabled") is True
    return {"github_push_enabled": enabled}

def validate_activity_day(day: str):
    if not DAY_PATTERN.fullmatch(day):
        raise HTTPException(status_code=400, detail="A day in YYYY-MM-DD format is required.")
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid day.")


def read_sessions():
    try:
        data = json.loads(SESSIONS_FILE.read_text(encoding='utf-8'))
        if not isinstance(data,dict):
            return {}
    except (OSError,json.JSONDecodeError):
        return {}
    return {
        day: [normalize_session(s) for s in day_sessions]
        for day, day_sessions in data.items()
        if DAY_PATTERN.fullmatch(day) and isinstance(day_sessions, list)
    }

def normalize_session(session):
    if isinstance(session, (int, float)) and not isinstance(session, bool):
        return {"ms": session, "project": "Unassigned"}
    if isinstance(session, dict):
        ms = session.get("ms")
        project = session.get("project", "Unassigned")
        if isinstance(ms, (int, float)) and not isinstance(ms, bool):
            return {"ms": ms, "project": str(project).strip()[:60] or "Unassigned"}
    return {"ms": 0, "project": "Unassigned"}

@app.get("/api/focus-sessions")
def get_sessions(day: str = ""):
    validate_activity_day(day)
    return {"sessions": read_sessions().get(day, [])}

class SessionIn(BaseModel):
    ms: Union[StrictInt, StrictFloat]
    project: str

class SessionsIn(BaseModel):
    day: str
    sessions: list[SessionIn]
    
    
@app.put("/api/focus-sessions")
def save_sessions(body: SessionsIn):
    validate_activity_day(body.day)
    if len(body.sessions) > 10000 or any(s.ms < 0 or s.ms > 86400000 for s in body.sessions):
        raise HTTPException(status_code=400, detail="Sessions must be at most 10000 durations between 0 and 86400000 ms.")
    normalized = [
        {"ms": s.ms, "project": (s.project.strip()[:60] or "Unassigned")}
        for s in body.sessions
    ]
    data = read_sessions()
    data[body.day] = normalized
    DATABASE_DIR.mkdir(parents=True,exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps(data,indent=2),encoding="utf-8")
    return {"saved": True}    


class CodingActivityIn(BaseModel):
    event_id: str
    day: str
    project: str
    language: str
    duration_ms: StrictInt


@app.get("/api/coding-activity")
def get_coding_activity(day: str = ""):
    validate_activity_day(day)
    events = read_coding_activity().get(day, [])
    if not isinstance(events, list):
        events = []
    totals = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        key = (event.get("project", "Unknown"), event.get("language", "unknown"))
        totals[key] = totals.get(key, 0) + event.get("duration_ms", 0)
    return {
        "total_ms": sum(totals.values()),
        "projects": [
            {"project": project, "language": language, "duration_ms": duration_ms}
            for (project, language), duration_ms in totals.items()
        ],
    }


@app.post("/api/coding-activity")
def save_coding_activity(body: CodingActivityIn):
    validate_activity_day(body.day)
    if (not body.event_id or len(body.event_id) > 80 or
            not body.project.strip() or len(body.project) > 120 or
            not body.language.strip() or len(body.language) > 50 or
            body.duration_ms <= 0 or body.duration_ms > 86_400_000):
        raise HTTPException(status_code=400, detail="Invalid coding activity event.")

    with CODING_ACTIVITY_LOCK:
        data = read_coding_activity()
        events = data.get(body.day, [])
        if not isinstance(events, list):
            events = []
        if any(isinstance(event, dict) and event.get("event_id") == body.event_id for event in events):
            return {"saved": True, "duplicate": True}
        events.append({
            "event_id": body.event_id,
            "project": body.project.strip(),
            "language": body.language.strip(),
            "duration_ms": body.duration_ms,
        })
        data[body.day] = events
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        CODING_ACTIVITY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"saved": True}

class RecapIn(BaseModel):
    topics : list[Union[str,dict]]
    focusTime : str
    day:str | None = None
    

@app.post("/api/recap")
def recap(body:RecapIn):
    if len(body.topics) > 100 or len(body.focusTime) > 40:
        raise HTTPException(status_code=400, detail="Too many topics or focusTime too long.")
    day = body.day or date.today().isoformat()
    if not DAY_PATTERN.fullmatch(day):
        raise HTTPException(status_code=400,detail="Invalid DAY")
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400,detail="invalid day")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503,detail="GROQ_API_KEY is not set in the server environment or project .env file.")
    prompt = (
        "Write a natural, concise daily learning recap in 2–3 short sentences. Use only the supplied data. "
        "Do not add headings, bullet points, markdown, repeated praise, or generic motivational slogans. "
        "Mention the topics and focus time plainly. If there are no topics, say that none were recorded; "
        "do not imply the user studied a topic. Suggest one small, practical next action suited to the "
        "activity shown. For very little focus time, invite the user to start or continue a short session; "
        "do not suggest taking a break or planning tomorrow unless the data supports it.\n\n"
        f"Date: {day}\nTopics: {json.dumps(body.topics, ensure_ascii=False)}\nFocus time: {body.focusTime}"
    )
    
    try:
        response = requests.post(
            GROQ_API_URL,
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_completion_tokens": 500,
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "Drona-Learning-Dashboard/1.0",
            },
            timeout=30,
        )
        response.raise_for_status()
        recap_text = response.json()["choices"][0]["message"]["content"].strip()
        if not recap_text:
            raise ValueError("The AI returned an empty recap.")
    except requests.HTTPError as error:          
        print(f"Groq API returned HTTP {error.response.status_code}: {error.response.text[:2000]}")
        raise HTTPException(status_code=502, detail="The AI provider rejected the recap request. Check the API key and model access.")
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        print(f"Could not generate recap: {error}")
        raise HTTPException(status_code=502, detail="Could not generate a recap right now. Please try again.")
    return {"recap": recap_text}

class Github_data(BaseModel):
    category:str
    push: bool = False
    
@app.post("/api/github-push")
def github_push(body:Github_data,request:Request):
    origin = urlparse(request.headers.get("Origin", ""))
    request_host = request.headers.get("Host", "")
    if origin.netloc != request_host or origin.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise HTTPException(status_code=403, detail="GitHub push requests must come from this local dashboard.")
    category = body.category.strip()
    if not category or len(category) > 100:
        raise HTTPException(status_code=400, detail="Choose a category before updating activity.")
    if body.push:
        try:
            settings = json.loads((DATABASE_DIR / "repo_settings.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            settings = {}
        if not isinstance(settings, dict) or settings.get("github_push_enabled") is not True:
            raise HTTPException(status_code=403, detail="GitHub push is not enabled in Drona's installation settings.")
    if not ACTIVITY_UPDATE_LOCK.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="An activity update is already running.")
    try:
        try:
            output = update_activity(category, push=body.push)
        except RuntimeError as error:
            print(f"Activity update failed: {error}")
            raise HTTPException(status_code=500, detail=str(error)[-1200:]) from error
        except (OSError, ValueError) as error:
            print(f"Activity update failed,check your terminal: {error}")
            raise HTTPException(status_code=500, detail="Could not complete the activity update.") from error
        return {"success": True, "message": output or "Tracker finished successfully."}
    finally:
        ACTIVITY_UPDATE_LOCK.release()

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")







def load_settings():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

def run_git(folder, *args):
    return subprocess.run(
        ["git", "-C", str(folder), *args],
        capture_output=True, text=True, timeout=10, check=False,
    )

def get_repo_root(folder):
    try:
        result = run_git(folder, "rev-parse", "--show-toplevel")
    except FileNotFoundError:
        return None, "Git was not found. Install Git try again."
    except subprocess.TimeoutExpired:
        return None, "Git took too longg."
    if result.returncode != 0:
        return None, "Nope bro not a git repo."
    return Path(result.stdout.strip()).resolve(), None        
        
def can_push(repo_root):
    try:
        has_origin = run_git(repo_root, "remote", "get-url", "origin").returncode == 0
        branch = run_git(repo_root, "branch", "--show-current").stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return has_origin and branch == "main"
        
        
def ask_user(root,old_settings):
    while True:
        folder = filedialog.askdirectory(parent=root,title='choose the git repo')     
        if not folder:
            return None
        repo_root,error = get_repo_root(folder)
        if error:
            messagebox.showerror('Drona setup',error,parent=root)
            continue
        
        category = simpledialog.askstring(
        "Drona setup",
        "default category:",
        initialvalue=old_settings.get('category','use folder category'),
        parent=root                                  
        )
        if category is None:
            return None
        push = messagebox.askyesno(
            "Optional GitHub push",
            "Enable pushing commits to GitHub?\n\nChoose No for local commits only.",
            default=messagebox.NO,
            parent=root,
        )
        
        if push and not can_push(repo_root):
            messagebox.showerror(
                "Drona setup",
                "GitHub push needs an origin remote and the repository's main branch. "
                "Setup will continue with push disabled.",
                parent=root,
            )
            push = False
        return {
            "repo_path": str(repo_root),
            "category": category.strip() or "Use folder category",
            "github_push_enabled": push,
        } 


def setup_repository_if_needed():
    settings = load_settings()
    saved_path = settings.get("repo_path","")
    if saved_path and get_repo_root(saved_path)[0]:
        return True   
    
         
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)   
    try:
        new_settings = ask_user(root,settings)
        if new_settings is None:
            return False
    
        settings.update(new_settings)
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        messagebox.showinfo("Drona setup", "Repository saved. You can now use Drona.", parent=root)
        return True
    finally:
        root.destroy()
        
if __name__ == "__main__":
    import uvicorn
    if not setup_repository_if_needed():
        raise SystemExit("Drona setup was cancelled.")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
    webbrowser.open("http://127.0.0.1:8000/Frontend/")
