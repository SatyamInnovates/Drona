import json
import os
from pathlib import Path


backend_dir = Path(__file__).resolve().parent
project_dir = backend_dir.parent
settings_file = project_dir / "Database" / "repo_settings.json"
default_repo = Path(r"C:\Users\s3624\OneDrive\Desktop\aiml\phase3a\revising ml date 31 august 2026")


def configured_repo():
    env_path = os.environ.get("DRONA_REPO_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        repo_path = settings.get("repo_path")
    except (OSError, json.JSONDecodeError):
        repo_path = None
    if isinstance(repo_path, str) and repo_path.strip():
        return Path(repo_path).expanduser().resolve()

    if default_repo.exists():
        return default_repo
    return project_dir


repo = configured_repo()
