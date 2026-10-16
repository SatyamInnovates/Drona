# Drona

Local learning and coding activity tracker for Windows. Each person runs their own copy; data stays on that computer.

## Install

1. Download and extract the Drona project.
2. Open PowerShell in the `Drona` folder and run:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Drona.ps1
   ```

   Setup creates a private Python environment, installs the server packages, and ensures Git is available for local activity commits. It asks for a repository to track and whether to enable the optional GitHub push feature (recommended only if you want Drona to push to that repository). Python 3.10 or newer is required.
3. Start the app by double-clicking `Start Drona.bat`. Keep the server window open. The dashboard opens at <http://127.0.0.1:8000/Frontend/>.

## Local commits and optional GitHub push

The dashboard's activity button commits changed files locally and refreshes topics and streaks. If you enable GitHub push during setup, the button instead asks you to confirm before pushing commits to `origin/main`. Push setup requires the selected repository to have an `origin` remote and be on its `main` branch. Set up GitHub authentication for that repository before enabling push. Drona stages all detected changed files when you click the button, so review your repository changes first. If you skip GitHub push, Drona makes local commits only.

## VS Code tracking

The installer uses `drona-activity-tracker/drona-activity-tracker-0.0.2.vsix`. If it cannot install it automatically, install that file from VS Code's **Extensions** panel using **Install from VSIX...**.

Tracking sends the workspace name, language, and time to the local Drona server. It does not send file contents or full paths. By default, it stops counting five minutes after the last edit.

## Important

- Drona currently supports Windows. The server listens only on this computer (`127.0.0.1`).
- Keep `.env` and the local `Database` JSON files private. They contain API keys or per-user settings and activity.
- Optional AI recaps require `GROQ_API_KEY` in a private `.env` file.

## Local files

- Dashboard: `Frontend/`
- Server: `Backend(main files)/server2.py`
- Activity and commit script: `Backend(main files)/main.py`
- VS Code extension source: `drona-activity-tracker/src/extension.ts`
- Local records and settings: `Database/`
