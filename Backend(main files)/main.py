import subprocess
from topic import topic_finding,category_finding
import json
import re
import sys
from pathlib import Path
from datetime import date, timedelta
from config import repo
from settings import choose_category, FOLDER_CATEGORY

backend_dir = Path(__file__).resolve().parent
database_dir = backend_dir.parent / "Database"

def update_streaks():
    result = run([sys.executable, str(backend_dir / "ss.py")])
    if result.returncode != 0:
        print(result.stderr)
        exit(result.returncode)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo))


selected_category = choose_category()
status = run(["git", "status", "--porcelain", "-z", "--untracked-files=all"])
if status.returncode != 0:
    print(status.stderr)
    exit(status.returncode)

status_entries = status.stdout.split("\0")
changed_paths = []
index = 0
while index < len(status_entries):
    entry = status_entries[index]
    index += 1
    if not entry:
        continue
    change_code, path = entry[:2], entry[3:]
    changed_paths.append(path)
    # With -z, Git emits the second path of a rename or copy as a separate record.
    if "R" in change_code or "C" in change_code:
        if index < len(status_entries) and status_entries[index]:
            changed_paths.append(status_entries[index])
            index += 1

if not changed_paths:
    print("No changes to commit.")
else:
    print(changed_paths)
    content_lines = changed_paths
    if content_lines:
        topics = [topic_finding(line[3:]) for line in content_lines]
        categories = [
            category_finding(line[3:], repo) if selected_category == FOLDER_CATEGORY else selected_category
            for line in content_lines
        ]
        print("Topics found:", topics)
        messages = [f"save:[{category}] {topic}" for topic, category in zip(topics, categories)]
        message = ' '.join(messages)
        print(messages)

        for cmd in (["git", "add", "-A", "--", *changed_paths],
                    ["git", "commit", "-m", message],
                    ["git", "push", "origin", "main"]):
            result = run(cmd)
            if result.returncode != 0:
                print(result.stderr)
                exit(result.returncode)

data_output = run(['git','log','--format=%ad|%s','--date=short']).stdout

# Files included in commits made yesterday (the same commits sent to origin).
yesterday = date.today() - timedelta(days=1)
today = yesterday + timedelta(days=1)
file_output = run([
    'git', 'log', 'origin/main', '--since', yesterday.isoformat(), '--until', today.isoformat(),
    '--format=', '--name-only', '--diff-filter=ACMR'
]).stdout
yesterday_files = sorted({line.strip().replace('\\', '/') for line in file_output.splitlines() if line.strip()})

commits = []
for data_point in data_output.splitlines():
    date, data_topic = data_point.split('|')
    matches = re.findall(r'\[([^\]]+)\]', data_topic)
    if not matches:
        continue
    clean_topic = re.sub(r'\[[^\]]+\]', '', data_topic)
    clean_topic = re.sub(r'^\s*save\s*:?\s*', '', clean_topic).strip()
    for category in matches:
        commits.append({"date": date, "topic": clean_topic, "category": category})

 

with (database_dir / 'data.json').open('w', encoding='utf-8') as file:
    json.dump(commits,file)

with (database_dir / 'yesterday_files.json').open('w', encoding='utf-8') as file:
    json.dump(yesterday_files, file, ensure_ascii=False)

update_streaks()
if changed_paths:
    print("Pushed to github successfully")

