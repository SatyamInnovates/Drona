import subprocess
from topic import topic_finding,category_finding
import json

repo = r"C:\\Drona"

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=repo)


status = run(["git", "status", "--porcelain", "--untracked-files=all"])
if status.stdout == "":
    print("No changes to commit.")
    exit()


lines = status.stdout.splitlines()
print(lines)
topics = [topic_finding(line[3:]) for line in lines]
categories = [category_finding(line[3:]) for line in lines]
print("Topics found:", topics)
message = "save " + " ".join(topics)
print(message)

for cmd in (["git", "add", "."],
            ["git", "commit", "-m", message],
            ["git", "push"]):
    result = run(cmd)
    if result.returncode != 0:
        print(result.stderr)
        exit()

data_output = run(['git','log','--format=%ad|%s','--date=short']).stdout

commits = []
for data_point in data_output.splitlines():
    date, data_topic = data_point.split('|')
    for category in categories:
        category.split("/")
        commits.append({"date":date,"topic":data_topic,"category":category})

 

with open(r'C:\Drona\Backend(main files)\data.json','w') as file:
    json.dump(commits,file)


print("Pushed to github successfully")

