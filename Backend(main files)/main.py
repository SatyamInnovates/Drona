import subprocess
from topic import topic_finding,category_finding
import json
import re
import sys
from pathlib import Path

repo = r"C:\\Drona"
backend_dir = Path(__file__).resolve().parent

def update_streaks():
    result = run([sys.executable, str(backend_dir / "ss.py")])
    if result.returncode != 0:
        print(result.stderr)
        exit(result.returncode)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=repo)


status = run(["git", "status", "--porcelain", "--untracked-files=all"])
if status.stdout == "":
    print("No changes to commit.")
    update_streaks()
    exit()


lines = status.stdout.splitlines()
print(lines)
content_lines = [line for line in lines if line[3:].replace('\\','/').split('/')[0].strip('"')]
if not content_lines:
    print("No learning changes to commit.")
    update_streaks()
    exit()

topics = [topic_finding(line[3:]) for line in content_lines]
categories = [category_finding(line[3:]) for line in content_lines]
print("Topics found:", topics)
messages = []
for topic,category in zip(topics,categories):
    messages.append("save:" + f"[{category}]"+ f" {topic}")
message = ' '.join(messages)
print(messages)

for cmd in (["git", "add", "."],
            ["git", "commit", "-m", message],
            ["git", "push"]):
    result = run(cmd)
    if result.returncode != 0:
        print(result.stderr)
        print("test01 completed")
        exit()

data_output = run(['git','log','--format=%ad|%s','--date=short']).stdout

commits = []
for data_point in data_output.splitlines():
    date, data_topic = data_point.split('|')
    matches = re.findall(r'\[([^\]]+)\]', data_topic)
    if not matches:
        continue
    clean_topic = re.sub(r'\[[^\]]+\]', '', data_topic).strip()
    for category in matches:
        commits.append({"date": date, "topic": clean_topic, "category": category})

 

with open(r'C:\Drona\Backend(main files)\data.json','w') as file:
    json.dump(commits,file)

update_streaks()
print("Pushed to github successfully")

