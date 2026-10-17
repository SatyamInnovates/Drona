import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from config import configured_repo
from app_paths import get_database_dir
from settings import FOLDER_CATEGORY, choose_category
from topic import category_finding, topic_finding


DATABASE_DIR = get_database_dir()


def _run_git(command, repo):
    if command[0] == "git":
        command = ["git", "-c", f"safe.directory={repo}", *command[1:]]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo),
            timeout=300,
            check=False,
        )
    except FileNotFoundError as error:
        raise RuntimeError("Git was not found. Install Git and ensure it is available on PATH.") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("The Git activity update timed out after five minutes.") from error


def _check(result):
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "Git command failed.").strip()
        raise RuntimeError(message)
    return result


def update_activity(category=None, push=False):
    """Commit tracked repository changes and refresh Drona's activity data."""
    try:
        repo = configured_repo()
        selected_category = choose_category(category)
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(str(error)) from error

    if push:
        settings_path = DATABASE_DIR / "repo_settings.json"
        try:
            install_settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            install_settings = {}
        if not isinstance(install_settings, dict) or install_settings.get("github_push_enabled") is not True:
            raise RuntimeError("GitHub push is not enabled in Drona's installation settings.")
        remote = _run_git(["git", "remote", "get-url", "origin"], repo)
        branch = _run_git(["git", "branch", "--show-current"], repo)
        if remote.returncode != 0 or branch.returncode != 0 or branch.stdout.strip() != "main":
            raise RuntimeError("GitHub push requires an origin remote and the selected repository's main branch.")

    status = _check(_run_git(
        ["git", "status", "--porcelain", "-z", "--untracked-files=all"], repo
    ))
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
        if "R" in change_code or "C" in change_code:
            if index < len(status_entries) and status_entries[index]:
                changed_paths.append(status_entries[index])
                index += 1

    messages = []
    if not changed_paths:
        messages.append("No changes to commit.")
        if push:
            _check(_run_git(["git", "push", "origin", "main"], repo))
            messages.append("Pushed local commits to GitHub.")
    else:
        topics = [topic_finding(path) for path in changed_paths]
        categories = [
            category_finding(path, repo) if selected_category == FOLDER_CATEGORY else selected_category
            for path in changed_paths
        ]
        commit_message = "; ".join(
            f"{topic} [{item_category}]"
            for topic, item_category in zip(topics, categories)
        )
        _check(_run_git(["git", "add", "-A", "--", *changed_paths], repo))
        _check(_run_git(["git", "commit", "-m", commit_message], repo))
        if push:
            _check(_run_git(["git", "push", "origin", "main"], repo))
        messages.append("Committed and pushed to GitHub." if push else "Committed locally.")

    data_output = _check(_run_git(
        ["git", "log", "--format=%ad|%s", "--date=short"], repo
    )).stdout

    yesterday = date.today() - timedelta(days=1)
    today = yesterday + timedelta(days=1)
    file_output = _check(_run_git([
        "git", "log", "HEAD", "--since", yesterday.isoformat(), "--until", today.isoformat(),
        "--format=", "--name-only", "--diff-filter=ACMR",
    ], repo)).stdout
    yesterday_files = sorted({
        line.strip().replace("\\", "/")
        for line in file_output.splitlines()
        if line.strip()
    })

    commits = []
    for data_point in data_output.splitlines():
        commit_date, data_topic = data_point.split("|", 1)
        if re.search(r"(?:^|\s)save:", data_topic, flags=re.IGNORECASE):
            records = [
                (item_category.strip(), topic.strip())
                for item_category, topic in re.findall(
                    r"(?:^|\s)save:\s*\[([^\]]+)\]\s*(.+?)(?=\s+save:|$)",
                    data_topic,
                    flags=re.IGNORECASE,
                )
            ]
        else:
            records = []
            for record in data_topic.split(";"):
                match = re.fullmatch(r"\s*(.*?)\s+\[([^\]]+)\]\s*", record)
                if match:
                    topic, item_category = match.groups()
                    records.append((item_category.strip(), topic.strip()))

        for item_category, topic in records:
            if topic and item_category:
                commits.append({"date": commit_date, "topic": topic, "category": item_category})

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    (DATABASE_DIR / "data.json").write_text(json.dumps(commits), encoding="utf-8")
    (DATABASE_DIR / "yesterday_files.json").write_text(
        json.dumps(yesterday_files, ensure_ascii=False), encoding="utf-8"
    )

    from ss import refresh_activity
    refresh_activity()
    return "\n".join(messages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="Change and save the repository path")
    parser.add_argument("--category", help="Use and save this category")
    parser.add_argument("--push", action="store_true", help="Push the new commit to origin/main")
    args = parser.parse_args()
    try:
        if args.repo:
            configured_repo(args.repo)
        print(update_activity(args.category, push=args.push))
    except (RuntimeError, ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
