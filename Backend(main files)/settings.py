import json
from pathlib import Path


backend_dir = Path(__file__).resolve().parent
settings_file = backend_dir / "repo_settings.json"
FOLDER_CATEGORY = "Use folder category"


def load_category():
    if not settings_file.exists():
        return FOLDER_CATEGORY
    try:
        settings = json.loads(settings_file.read_text(encoding="utf-8"))
        return settings.get("category", FOLDER_CATEGORY)
    except (OSError, json.JSONDecodeError):
        return FOLDER_CATEGORY


def choose_category():
    current = load_category()
    choices = ["Machine learning", "DSA", FOLDER_CATEGORY]
    print("Choose the category for this repository:")
    for number, choice in enumerate(choices, start=1):
        marker = " (current)" if choice == current else ""
        print(f"{number}. {choice}{marker}")

    while True:
        answer = input(f"Enter 1-{len(choices)} (Enter to keep current): ").strip()
        if not answer:
            selected = current
            break
        if answer in {str(number) for number in range(1, len(choices) + 1)}:
            selected = choices[int(answer) - 1]
            break
        print("Choose one of the listed numbers.")

    settings_file.write_text(
        json.dumps({"category": selected}, indent=2), encoding="utf-8"
    )
    return selected
