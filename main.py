import subprocess

status_git = subprocess.run(['git', 'status','--porcelain'], capture_output=True, text=True)

add_git = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)

commit_git = subprocess.run(['git', 'commit', '-m', 'Automated commit2'], capture_output=True, text=True)

push_git = subprocess.run(['git', 'push'], capture_output=True, text=True)

print(status_git.stdout)
print(status_git.stdout == "")