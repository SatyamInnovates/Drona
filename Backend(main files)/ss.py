import json
from datetime import date, datetime, timedelta

with open(r'C:\Drona\Backend(main files)\data.json') as f:
    commits = json.load(f)
    
    
def get_streak(commits, category):
    
    dates = {
        datetime.strptime(c["date"], "%Y-%m-%d").date()
        for c in commits
        if c["category"] == category
    }
    
    current = date.today()
    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    return streak

dsa_streak = get_streak(commits, "dsa")
ml_streak = get_streak(commits, "Machine learning")
streaks = {'dsa_streak':dsa_streak,'ml_streak':ml_streak}

with open(r'C:\Drona\Backend(main files)\streaks.json','w') as f:
    json.dump(streaks,f)
    
