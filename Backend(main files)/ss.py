import json
from datetime import datetime

with open(r'C:\Drona\Backend(main files)\data.json') as f:
    commits = json.load(f)
    print(commits)
    print(len(commits))
def get_streak(commits, category):
    
    dates = {
        datetime.strptime(c["date"], "%Y-%m-%d").date()
        for c in commits
        if c["category"] == category
    }
    
    current = datetime.today().date()
    streak = 0
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    return streak

from datetime import timedelta
dsa_streak = get_streak(commits, "dsa")
ml_streak = get_streak(commits, "ml")
print("DSA streak:", dsa_streak)
print("ML streak:", ml_streak)