import json
import os
import re
import urllib.error
import urllib.request
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_DIR / "Database"
SESSIONS_FILE = DATABASE_DIR / "focus_sessions.json"
DAY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


def load_local_env():
    """Load simple KEY=value entries from the project .env without dependencies."""
    env_file = PROJECT_DIR / ".env"
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip("\"'")
        if name and name not in os.environ:
            os.environ[name] = value


load_local_env()


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)

    def _read_sessions(self):
        try:
            data = json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/focus-sessions":
            return super().do_GET()
        day = parse_qs(parsed.query).get("day", [""])[0]
        if not DAY_PATTERN.fullmatch(day):
            return self._write_json(400, {"error": "A day in YYYY-MM-DD format is required."})
        try:
            date.fromisoformat(day)
        except ValueError:
            return self._write_json(400, {"error": "Invalid day."})
        sessions = self._read_sessions().get(day, [])
        return self._write_json(200, {"sesseeegions": sessions if isinstance(sessions, list) else []})

    def do_PUT(self):
        if urlparse(self.path).path != "/api/focus-sessions":
            return self._write_json(404, {"error": "Not found."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            day = payload["day"]
            sessions = payload["sessions"]
            if not isinstance(day, str) or not DAY_PATTERN.fullmatch(day):
                raise ValueError
            date.fromisoformat(day)
            if not isinstance(sessions, list) or len(sessions) > 10000:
                raise ValueError
            if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value > 86400000 for value in sessions):
                raise ValueError
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return self._write_json(400, {"error": "Expected a valid day and a list of session durations in milliseconds."})

        data = self._read_sessions()
        data[day] = sessions
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        SESSIONS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return self._write_json(200, {"saved": True})

    def do_POST(self):
        if urlparse(self.path).path != "/api/recap":
            return self._write_json(404, {"error": "Not found."})

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 32_000:
                raise ValueError
            payload = json.loads(self.rfile.read(length))
            topics = payload["topics"]
            focus_time = payload["focusTime"]
            if not isinstance(topics, list) or len(topics) > 100:
                raise ValueError
            if any(not isinstance(topic, (str, dict)) for topic in topics):
                raise ValueError
            if not isinstance(focus_time, str) or len(focus_time) > 40:
                raise ValueError
            day = payload.get("day", date.today().isoformat())
            if not isinstance(day, str) or not DAY_PATTERN.fullmatch(day):
                raise ValueError
            date.fromisoformat(day)
        except (ValueError, TypeError, KeyError, json.JSONDecodeError):
            return self._write_json(400, {
                "error": "Expected topics (a list), focusTime (a string), and an optional day in YYYY-MM-DD format."
            })

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return self._write_json(503, {"error": "GROQ_API_KEY is not set in the server environment or project .env file."})

        prompt = (
            "Write a natural, concise daily learning recap in 2–3 short sentences. Use only the supplied data. "
            "Do not add headings, bullet points, markdown, repeated praise, or generic motivational slogans. "
            "Mention the topics and focus time plainly. If there are no topics, say that none were recorded; "
            "do not imply the user studied a topic. Suggest one small, practical next action suited to the "
            "activity shown. For very little focus time, invite the user to start or continue a short session; "
            "do not suggest taking a break or planning tomorrow unless the data supports it.\n\n"
            f"Date: {day}\nTopics: {json.dumps(topics, ensure_ascii=False)}\nFocus time: {focus_time}"
        )
        request_body = json.dumps({
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_completion_tokens": 500,
        }).encode("utf-8")
        request = urllib.request.Request(
            GROQ_API_URL,
            data=request_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Drona-Learning-Dashboard/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
            recap = result["choices"][0]["message"]["content"].strip()
            if not recap:
                raise ValueError("The AI returned an empty recap.")
        except urllib.error.HTTPError as error:
            # Log the provider's diagnostic locally; never return it to the browser.
            try:
                provider_error = error.read().decode("utf-8", errors="replace")[:2000]
            except OSError:
                provider_error = "(could not read provider error response)"
            self.log_error("Groq API returned HTTP %s: %s", error.code, provider_error)
            return self._write_json(502, {"error": "The AI provider rejected the recap request. Check the API key and model access."})
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError) as error:
            self.log_error("Could not generate recap: %s", error)
            return self._write_json(502, {"error": "Could not generate a recap right now. Please try again."})
        return self._write_json(200, {"recap": recap})


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    print(f"Drona dashboard server: http://localhost:{port}/Frontend/")
    ThreadingHTTPServer((host, port), DashboardHandler).serve_forever()
