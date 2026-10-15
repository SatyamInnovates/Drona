# Drona

Local learning and coding activity tracker for Windows. Each person runs their own copy; data stays on that computer.

## Install

1. Download and extract the Drona project.
2. Open PowerShell in the `Drona` folder and run:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Install-Drona.ps1
   ```

   Setup creates a private Python environment, installs the server packages, offers to configure a Git repository, and installs the VS Code extension when the `code` command is available. It requires Python 3.10 or newer. Git, VS Code, and a GitHub login are only needed for their optional features.

3. Start the app by double-clicking `Start Drona.bat`. Keep the server window open. The dashboard opens at <http://127.0.0.1:8000/Frontend/>.

## VS Code tracking

The installer uses `drona-activity-tracker/drona-activity-tracker-0.0.1.vsix`. If it cannot install it automatically, install that file from VS Code's **Extensions** panel using **Install from VSIX...**.

Tracking sends the workspace name, language, and time to the local Drona server. It does not send file contents or full paths. By default, it stops counting five minutes after the last edit.

## Optional GitHub push

During setup, choose `y` and enter the path to a Git repository with an `origin` remote, checked out on its `main` branch. Set up GitHub authentication for that repository first. The dashboard push action commits changes and pushes to `origin/main`; review your changes before using it.

## Important


- Drona currently supports Windows. The server listens only on this computer (`127.0.0.1`).
- Keep `.env` and the local `Database` JSON files private. They contain API keys or per-user settings and activity.
- Optional AI recaps require `GROQ_API_KEY` in a private `.env` file.
=======
The dashboard's **Push To Github** action commits changes in that repository and auto pushes them to `origin/main`. Review changes before pushing.

##API key
in the .env give your groq api key => GROQ_API_KEY="your_api_key"
## Local files

- Dashboard: `Frontend/`
- Server: `Backend(main files)/server2.py`
- Extension source: `drona-activity-tracker/src/extension.ts`
- Local records and settings: `Database/`
- Optional AI recap key: set `GROQ_API_KEY` in a private `.env` file.

Do not share `.env` or personal database files. The server listens on this computer only (`127.0.0.1`).

