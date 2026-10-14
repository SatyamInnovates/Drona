from fastapi import FastAPI,HTTPException,Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import re
import os
import json
from datetime import date
from typing import Union
from pydantic import BaseModel,StrictInt,StrictFloat
import requests
from urllib.parse import urlparse
from fastapi.staticfiles import StaticFiles
import threading
import subprocess
import sys
# The main and defalut server other one is for backup
PROJECT_DIR = Path(__file__).resolve().parent.parent   
DATABASE_DIR = PROJECT_DIR / "Database"
SESSIONS_FILE = DATABASE_DIR / "focus_sessions.json"
CODING_ACTIVITY_FILE = DATABASE_DIR / "coding_activity.json"
DAY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"
PUSH_LOCK = threading.Lock()
CODING_ACTIVITY_LOCK = threading.Lock()
MAIN_SCRIPT = Path(__file__).resolve().with_name("main.py")


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


def validate_activity_day(day: str):
    if not DAY_PATTERN.fullmatch(day):
        raise HTTPException(status_code=400, detail="A day in YYYY-MM-DD format is required.")
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid day.")


@app.get("/api/focus-sessions")
def get_sessions(day: str = ""):
    if not DAY_PATTERN.fullmatch(day):
        raise HTTPException(status_code=400, detail="A day in YYYY-MM-DD format is required.")
    try:
        date.fromisoformat(day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid day.")
    sessions = read_sessions().get(day, [])
    return {"sessions": sessions if isinstance(sessions, list) else []}


class SessionIn(BaseModel):
    day:str
    sessions : list[Union[StrictInt,StrictFloat]]
    
    
@app.put("/api/focus-sessions")
def save_sessions(body:SessionIn):
    if not DAY_PATTERN.fullmatch(body.day):
        raise HTTPException(status_code=400,detail="A day in YYYY-MM-DD format is required.")
    try:
        date.fromisoformat(body.day)
    except ValueError:
        raise HTTPException(status_code=400,detail="Invalid day")
    if len(body.sessions) > 10000 or any(v<0 or v > 86400000 for v in body.sessions):
        raise HTTPException(status_code=400, detail="Sessions must be at most 10000 durations between 0 and 86400000 ms.")
    
    data = read_sessions()
    data[body.day] = body.sessions
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
    except requests.HTTPError as error:          # must come first
        print(f"Groq API returned HTTP {error.response.status_code}: {error.response.text[:2000]}")
        raise HTTPException(status_code=502, detail="The AI provider rejected the recap request. Check the API key and model access.")
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        print(f"Could not generate recap: {error}")
        raise HTTPException(status_code=502, detail="Could not generate a recap right now. Please try again.")
    return {"recap": recap_text}


class Github_data(BaseModel):
    category:str
    
@app.post("/api/github-push")
def github_push(body:Github_data,request:Request):
    origin = urlparse(request.headers.get("Origin", ""))
    request_host = request.headers.get("Host", "")
    if origin.netloc != request_host or origin.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise HTTPException(status_code=403, detail="GitHub push requests must come from this local dashboard.")
    category = body.category.strip()
    if not category or len(category) > 100:
        raise HTTPException(status_code=400, detail="Choose a category before pushing.")
    if not PUSH_LOCK.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="A GitHub push is already running.")
    try:
        try:
            result = subprocess.run(
                [sys.executable, str(MAIN_SCRIPT), "--category", category],
                cwd=str(PROJECT_DIR),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
                check=False,
            )
        except subprocess.TimeoutExpired:
                raise HTTPException(status_code=504, detail="The GitHub push timed out after five minutes.")
        except OSError as error:
            print(f"Could not start GitHub push script: {error}")
            raise HTTPException(status_code=500, detail="Could not start the push script.")
        output = (result.stdout or "").strip()

        if result.returncode != 0:
            details = (result.stderr or output or "The script exited without an error message.").strip()
            print(f"GitHub push script failed ({result.returncode}): {details[:2000]}")
            raise HTTPException(status_code=500, detail=details[-1200:])
        return {"success": True, "message": output or "Tracker finished successfully."}
    finally:
        PUSH_LOCK.release()
        
app.mount("/", StaticFiles(directory=str(PROJECT_DIR), html=True), name="static")
