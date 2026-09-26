import json
from datetime import date, datetime, timedelta
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
with (backend_dir / "data.json").open(encoding="utf-8") as f:
    commits = json.load(f)
    
    
def get_streak(commits, category):
    
    dates = {
        datetime.strptime(c["date"], "%Y-%m-%d").date()
        for c in commits
        if c["category"] == category
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

with (backend_dir / "streaks.json").open("w", encoding="utf-8") as f:
    json.dump(streaks, f)
    
