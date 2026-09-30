import json
from datetime import date, datetime, timedelta
from pathlib import Path
from settings import load_category, FOLDER_CATEGORY

backend_dir = Path(__file__).resolve().parent
with (backend_dir / "data.json").open(encoding="utf-8") as f:
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

dsa_streak = get_streak(commits, "dsa")
ml_streak = get_streak(commits, "Machine learning")
streaks = {'dsa_streak':dsa_streak,'ml_streak':ml_streak}
selected_category = load_category()
if selected_category != FOLDER_CATEGORY:
    streaks['selected_category'] = selected_category
    streaks['selected_category_streak'] = get_streak(commits, selected_category)

today_topics = []
today = date.today().isoformat()
for commit in commits:
    if commit["date"] == today:
        today_topics.append({
            "date": commit["date"],
            "topic": commit["topic"],
            "category": commit["category"],
        })

with (backend_dir / "streaks.json").open("w", encoding="utf-8") as f:
    json.dump(streaks, f)

with (backend_dir / "today_topics.json").open("w", encoding="utf-8") as f:
    json.dump(today_topics, f, ensure_ascii=False)
    
