import os
import json
import shutil
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent


def get_database_dir():
    if not getattr(sys, "frozen", False):
        return BACKEND_DIR.parent / "Database"

    exe_dir = Path(sys.executable).resolve().parent
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    database_dir = local_app_data / "Drona" / "Database"
    is_new_store = not database_dir.exists() or not any(database_dir.iterdir())
    database_dir.mkdir(parents=True, exist_ok=True)

    if is_new_store:
        sources = [
            exe_dir.parent.parent / "Database",
            exe_dir / "Database",
        ]
        source_files = {}
        for source in sources:
            if source.is_dir() and source.resolve() != database_dir.resolve():
                for item in source.iterdir():
                    if item.is_file():
                        source_files.setdefault(item.name, []).append(item)

        for filename, items in source_files.items():
            destination = database_dir / filename
            items.sort(key=lambda item: item.stat().st_mtime)
            if filename in {"focus_sessions.json", "coding_activity.json", "repo_settings.json"}:
                try:
                    merged = {}
                    for item in items:
                        content = json.loads(item.read_text(encoding="utf-8"))
                        if not isinstance(content, dict):
                            continue
                        for key, value in content.items():
                            if filename == "coding_activity.json" and isinstance(value, list):
                                existing = merged.get(key, [])
                                seen_ids = {
                                    event.get("event_id") for event in existing
                                    if isinstance(event, dict) and event.get("event_id")
                                }
                                merged[key] = existing + [
                                    event for event in value
                                    if not isinstance(event, dict)
                                    or not event.get("event_id")
                                    or event.get("event_id") not in seen_ids
                                ]
                            else:
                                merged[key] = value
                    destination.write_text(json.dumps(merged, indent=2), encoding="utf-8")
                    continue
                except (OSError, json.JSONDecodeError):
                    pass

            try:
                shutil.copy2(items[-1], destination)
            except OSError:
                pass

    return database_dir
