import json
from datetime import date, datetime, timedelta
from pathlib import Path
from settings import load_category, FOLDER_CATEGORY

backend_dir = Path(__file__).resolve().parent
database_dir = backend_dir.parent / "Database"
with (database_dir / "data.json").open(encoding="utf-8") as f:
    commits = json.load(f)

for commit in commits:
    commit["topic"] = commit["topic"].removeprefix("save:").strip()
    
      
def get_streak(commits, category):
    dates = {
        datetime.strptime(c["date"], "%Y-%m-%d").date()
        for c in commits
        if c["category"].strip().casefold() == category.strip().casefold()
    }
    
    today = date.today()
    current = today if today in dates else today - timedelta(days=1)
    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    return streak

selected_category = load_category()

# Keep built-in categories visible and include every category in the activity
# history, plus the selected category even if it has no activity yet.
categories = {"dsa": "DSA", "machine learning": "Machine learning"}
for commit in commits:
    category = str(commit.get("category") or "").strip()
    if category:
        categories.setdefault(category.casefold(), category)
if selected_category and selected_category != FOLDER_CATEGORY:
    selected_category = selected_category.strip()
    categories.setdefault(selected_category.casefold(), selected_category)

streaks = {
    category: get_streak(commits, category)
    for category in categories.values()
}

today_topics = []
yesterday_topics = []
today = date.today().isoformat()
yesterday = (date.today() - timedelta(days=1)).isoformat()
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

with (database_dir / "streaks.json").open("w", encoding="utf-8") as f:
    json.dump(streaks, f)

with (database_dir / "today_topics.json").open("w", encoding="utf-8") as f:
    json.dump(today_topics, f, ensure_ascii=False)

with (database_dir / "yesterday_topics.json").open("w", encoding="utf-8") as f:
    json.dump(yesterday_topics, f, ensure_ascii=False)
    
