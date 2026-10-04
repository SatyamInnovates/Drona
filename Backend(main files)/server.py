import json
import re
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_DIR / "Database"
SESSIONS_FILE = DATABASE_DIR / "focus_sessions.json"
DAY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
        return self._write_json(200, {"sessions": sessions if isinstance(sessions, list) else []})

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


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    print(f"Drona dashboard server: http://localhost:{port}/Frontend/")
    ThreadingHTTPServer((host, port), DashboardHandler).serve_forever()
