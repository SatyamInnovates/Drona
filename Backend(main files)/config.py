import json
import os
from pathlib import Path


backend_dir = Path(__file__).resolve().parent
project_dir = backend_dir.parent
settings_file = project_dir / "Database" / "repo_settings.json"


def _configured_repo():
    configured = os.environ.get("DRONA_REPO_PATH")
    if not configured and settings_file.exists():
        try:
            configured = json.loads(settings_file.read_text(encoding="utf-8")).get("repo_path")
        except (OSError, json.JSONDecodeError):
            pass
    # Keep compatibility with the original local setup when it still exists.
    if not configured:
        legacy = Path(r"C:\Users\s3624\OneDrive\Desktop\aiml\phase3a\revising ml date 31 august 2026")
        configured = str(legacy if legacy.is_dir() else project_dir)
    path = Path(configured).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"Tracked repository does not exist: {path}. Set DRONA_REPO_PATH or repo_path in Database/repo_settings.json.")
    return path


repo = _configured_repo()
