import json
import os
import sys
from pathlib import Path


backend_dir = Path(__file__).resolve().parent
project_dir = backend_dir.parent
settings_file = project_dir / "Database" / "repo_settings.json"

def _read_settings():
    try:
        settings = json.loads(settings_file.read_text(encoding='utf-8'))
    except (OSError , json.JSONDecodeError):
        return {}
    return settings if isinstance(settings,dict) else {}

def _valid_repo_path(value):
    path = Path(value).expanduser().resolve()
    if not path.is_dir() or not (path/".git").exists():
        return None
    return path
    
    
def configured_repo():
    env_path = os.environ.get("DRONA_REPO_PATH")
    if env_path:
        path = _valid_repo_path(env_path)
        if path is None:
            raise ValueError(f"DRONA_REPO_PATH is not a Git repository: {env_path}")
        return path

    settings = _read_settings()
    saved_path = settings.get("repo_path")
    if isinstance(saved_path, str) and saved_path.strip():
        path = _valid_repo_path(saved_path)
        if path is not None:
            return path
        print(f"Saved repository path is missing or invalid: {saved_path}")

    if not sys.stdin.isatty():
        raise RuntimeError(
            "No valid repository path is saved and no interactive terminal is available. "
            "Run this command from a terminal to choose a repository, or set DRONA_REPO_PATH."
        )

    while True:
        entered_path = input("Enter the full path to the Git repository to track: ").strip()
        if not entered_path:
            print("Path cannot be empty.")
            continue
        path = _valid_repo_path(entered_path)
        if path is None:
            print("That path is not an existing Git repository. Try again.")
            continue

        settings["repo_path"] = str(path)
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        return path


repo = configured_repo()
