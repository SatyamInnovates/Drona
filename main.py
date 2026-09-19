import subprocess
import datetime
repo = "C:\\Drona"


# 1. anything changed?
status_git = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True,)
if status_git.stdout == '':
    print("No changes to commit.")
    exit()

# 2. stage
add_git = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
if add_git.returncode != 0:
    print(add_git.stderr)
    exit()

# 3
message = f"Auto save {datetime.date.today()}"
commit_git = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True)
if commit_git.returncode != 0:
    print(commit_git.stderr)
    exit()

# 4. push
push_git = subprocess.run(['git', 'push'], capture_output=True, text=True)
if push_git.returncode != 0:
    print(push_git.stderr)
    exit()

print("Saved and pushed.")