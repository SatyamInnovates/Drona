import json
import sys
from pathlib import Path


backend_dir = Path(__file__).resolve().parent
database_dir = backend_dir.parent / "Database"
settings_file = database_dir / "repo_settings.json"
FOLDER_CATEGORY = "Use folder category"
CUSTOM_CATEGORY = "Choose my own category"


def load_category():
    if not settings_file.exists():
        return FOLDER_CATEGORY
    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        return settings.get("category", FOLDER_CATEGORY)
    except (OSError, json.JSONDecodeError):
        return FOLDER_CATEGORY


def choose_category(category_override=None):
    current = load_category()
    choices = ["Machine learning", "DSA", FOLDER_CATEGORY, CUSTOM_CATEGORY]
    if category_override is not None:
        selected = category_override.strip()
        if not selected:
            raise ValueError("Category cannot be empty.")
        if selected == CUSTOM_CATEGORY:
            raise ValueError("Enter a category name instead of choosing the custom category label.")
        try:
            settings = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
        except (OSError, json.JSONDecodeError):
            settings = {}
        settings["category"] = selected
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        return selected

    if not sys.stdin.isatty():
        return current

    print("Choose the category for this repository:")
    for number, choice in enumerate(choices, start=1):
        if choice == current:
            marker = " (current)"
        elif choice == CUSTOM_CATEGORY and current not in choices:
            marker = f" (current: {current})"
        else:
            marker = ""
        print(f"{number}. {choice}{marker}")

    while True:
        answer = input(f"Enter 1-{len(choices)} (Enter to keep current): ").strip()
        if not answer:
            selected = current
            break
        if answer in {str(number) for number in range(1, len(choices) + 1)}:
            selected = choices[int(answer) - 1]
            if selected == CUSTOM_CATEGORY:
                selected = input("Enter your category name: ").strip()
                if not selected:
                    print("Category cannot be empty.")
                    continue
            break
        print("Choose one of the listed numbers.")

    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8")) if settings_file.exists() else {}
    except (OSError, json.JSONDecodeError):
        settings = {}
    settings["category"] = selected
    settings_file.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return selected
