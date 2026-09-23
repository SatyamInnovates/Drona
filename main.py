import subprocess
from topic import topic_finding

repo = "C:\\Drona"

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=repo)


status = run(["git", "status", "--porcelain", "--untracked-files=all"])
if status.stdout == "":
    print("No changes to commit.")
    exit()


lines = status.stdout.splitlines()
topics = [topic_finding(line[3:]) for line in lines]   
message = "save " + ", ".join(topics)
print(message)

for cmd in (["git", "add", "."],
            ["git", "commit", "-m", message],
            ["git", "push"]):
    result = run(cmd)
    if result.returncode != 0:
        print(result.stderr)
        exit()

data_output = run(['git','log','--format=%ad|%s','--date=short']).stdout


print(data_output)
print("Pushed to github successfully")

