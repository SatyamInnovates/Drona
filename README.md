# Drona

Drona is a local learning and coding activity dashboard for Windows. It runs on your computer and stores your Drona records in your Windows user profile.

## Download and run

1. Download `Drona-v0.1.0-Windows.zip` from the GitHub release.
2. Extract the entire ZIP to a folder you can keep, such as `C:\Users\<you>\Apps\Drona`. Keep `Drona.exe` and the `_internal` folder together.
3. Make sure [Git for Windows](https://git-scm.com/install/windows) is installed and available on `PATH`. Drona uses Git for repository activity and local commits; Git is not included in the Drona ZIP.
4. Double-click `Drona.exe`. On first run, choose a Git repository to track and set its activity category. You can also enable or skip the optional GitHub push feature.
5. Open <http://127.0.0.1:8000/> in your browser. Keep the Drona console window open while using the dashboard. Close that window to stop Drona.

If Windows SmartScreen shows a warning, Windows has not recognized the unsigned app yet. Only run it if you downloaded it from the Drona release you trust.

## Repository activity and GitHub push

The dashboard button **Commit and update activity** creates a local Git commit and refreshes activity and streak data. If GitHub push is enabled in first-run setup, the button becomes **Commit and push to GitHub** and asks before pushing to `origin/main`.

GitHub push requires the selected repository to have an `origin` remote, be on the `main` branch, and have GitHub authentication configured in Git. Drona stages detected changes in the selected repository when you confirm the action, so review the changes before using the button. If you skip push setup, Drona makes local commits only.

## VS Code activity tracking

Coding-time tracking requires the Drona VS Code extension. If the extension is provided as a separate `.vsix` download, install it from VS Code's **Extensions** panel using **Install from VSIX...**. Then open the repository you selected in Drona in VS Code.

The extension sends the workspace name, language, and time to the local Drona server. It does not send file contents or full paths. By default, it stops counting five minutes after the last edit. The dashboard can still be used without the extension, but coding-time tracking will not be collected.

## AI recaps

AI recaps need a Groq API key. Create a private file named `.env` next to `Drona.exe` with this line:

```text
GROQ_API_KEY=your-key
```

Do not share or commit this file.

## Data and privacy

- Drona listens on `127.0.0.1` and is intended for use on this computer.
- Each Windows user gets their own records and settings under `%LOCALAPPDATA%\Drona\Database`.
- The release ZIP should contain the app files, not your personal `Database` JSON files or `.env` file.
- Back up your local database folder if you want to preserve your Drona history when moving to another computer.

## Troubleshooting

- If the dashboard does not load, confirm the Drona console is still open and visit <http://127.0.0.1:8000/>.
- If Drona reports that the port is already in use, close the other app or Drona process using port `8000`, then start Drona again.
- If repository setup appears again, select the repository again and make sure Drona can write its settings under `%LOCALAPPDATA%\Drona\Database`.
- If Git operations fail, confirm Git for Windows is installed, `git` works in PowerShell, and the selected folder is a Git repository.
