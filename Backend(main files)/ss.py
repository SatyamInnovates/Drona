import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from app_paths import get_database_dir
from settings import FOLDER_CATEGORY, load_category


DATABASE_DIR = get_database_dir()


def _get_streak(commits, category):
    dates = {
        datetime.strptime(commit["date"], "%Y-%m-%d").date()
        for commit in commits
        if commit["category"].strip().casefold() == category.strip().casefold()
    }
    current = date.today() if date.today() in dates else date.today() - timedelta(days=1)
    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    return streak


def refresh_activity():
    with (DATABASE_DIR / "data.json").open(encoding="utf-8") as file:
        commits = json.load(file)
    for commit in commits:
        commit["topic"] = commit["topic"].removeprefix("save:").strip()

    selected_category = load_category()
    categories = {"dsa": "DSA", "machine learning": "Machine learning"}
    for commit in commits:
        category = str(commit.get("category") or "").strip()
        if category:
            categories.setdefault(category.casefold(), category)
    if selected_category and selected_category != FOLDER_CATEGORY:
        selected_category = selected_category.strip()
        categories.setdefault(selected_category.casefold(), selected_category)
    streaks = {
        category: _get_streak(commits, category)
        for category in categories.values()
    }

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    today_topics = []
    yesterday_topics = []
    for commit in commits:
        if commit["date"] in (today, yesterday):
            topic_entry = {
                "date": commit["date"],
                "topic": commit["topic"],
                "category": commit["category"],
            }
            if commit["date"] == today:
                today_topics.append(topic_entry)
            else:
                yesterday_topics.append(topic_entry)

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    (DATABASE_DIR / "streaks.json").write_text(json.dumps(streaks), encoding="utf-8")
    (DATABASE_DIR / "today_topics.json").write_text(
        json.dumps(today_topics, ensure_ascii=False), encoding="utf-8"
    )
    (DATABASE_DIR / "yesterday_topics.json").write_text(
        json.dumps(yesterday_topics, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    refresh_activity()
