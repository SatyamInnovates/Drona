# Drona

Drona is a local learning and coding activity tracker for Windows. It includes a browser dashboard, a small VS Code extension, a manual focus timer, and an optional GitHub push feature. Your dashboard data stays in the `Database` folder on your computer; the VS Code extension sends activity only to the Drona server running on your own computer.

This guide describes the current setup. It is not a one-command installer: install the prerequisites and Python packages once, then use `Start Drona.bat` to open Drona later.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer, available as `python` in PowerShell
- Visual Studio Code, version 1.140 or newer, for automatic coding-time tracking
- Git, with your GitHub account already authenticated, for the optional commit-and-push feature

## Get Drona

Download or clone the Drona project to a folder on your computer. Keep the project in that folder; the launcher and database paths are relative to it.

If the project maintainer gives you a Git repository URL, clone it using that URL and open PowerShell in the folder Git created. If you downloaded a ZIP instead, extract it and open PowerShell in the extracted Drona folder.

## Install the Python packages

Open PowerShell in the Drona project folder and run:

```powershell
python -m pip install fastapi uvicorn requests
```

If Windows says that `python` is not recognized, install Python and enable **Add Python to PATH**, then reopen PowerShell and try again.

## Start the dashboard

Double-click `Start Drona.bat` in the Drona project folder. A server terminal and the dashboard in your browser should open. Keep the server terminal open while using Drona; closing it stops the dashboard and automatic activity sync.

You can also start the server manually from PowerShell in the Drona project folder:

```powershell
python -m uvicorn server2:app --app-dir "Backend(main files)" --host 127.0.0.1 --port 8000
```

Then open <http://127.0.0.1:8000/Frontend/> in your browser. If port 8000 is already in use, close the other server using it before starting Drona.

## Install automatic VS Code tracking

The prebuilt extension package is `drona-activity-tracker/drona-activity-tracker-0.0.1.vsix`.

1. In VS Code, open **Extensions** with `Ctrl+Shift+X`.
2. Open the Extensions panel's **More Actions (...)** menu and choose **Install from VSIX...**.
3. Select the `.vsix` file in the Drona project folder, then reload VS Code if prompted.
4. Start Drona with `Start Drona.bat`.
5. Open a project folder in VS Code and edit a code file. The extension's status bar shows whether it is waiting, tracking, paused, or unable to reach the server.

The extension activates automatically in VS Code. It tracks edit time for files in an opened workspace, using the workspace name and language; it does not send file contents or full file paths. After the last edit, it allows a five-minute idle grace period, then stops adding time. Click its status bar item to pause or resume. The idle timeout and server URL can be changed in VS Code Settings under **Drona Activity Tracker**.

Coding activity is saved locally in `Database/coding_activity.json`. The dashboard server must be running for the extension to sync activity. If the status says **Server offline**, start the server and the extension will retry.

## Use the manual focus timer and learning dashboard

Open the dashboard at <http://127.0.0.1:8000/Frontend/>. The manual focus timer is separate from automatic coding time. Dashboard records such as focus sessions and coding activity are stored in the local `Database` folder.

The optional AI recap requires a Groq API key. Add `GROQ_API_KEY=your-key` to a `.env` file in the Drona project folder. Keep that key private; `.env` is excluded from Git.

## Set up the optional GitHub push feature

The Git feature operates on a Git repository on your computer. Before using it:

1. Install Git and sign in to GitHub using your usual Git credential manager.
2. Make sure the repository has an `origin` remote and a `main` branch that you can push to.
3. In PowerShell, from the Drona project folder, save the repository path:

   ```powershell
   python "Backend(main files)/main.py" --repo "C:\path\to\your\repository"
   ```

   Replace the example path with the full path to your Git repository. Drona saves this choice in `Database/repo_settings.json` on your computer.

The dashboard's **Push To Github** action stages changes in that selected repository, creates a categorized commit, and pushes it to `origin/main`. Review your repository changes before using it; this action commits and pushes changes. You can choose a category in the terminal, use a category from folders, or set one directly:

```powershell
python "Backend(main files)/main.py" --category "Machine learning"
```

## Troubleshooting

- **The batch file flashes or the server window shows an import error:** install the Python packages above, then run `Start Drona.bat` again.
- **The browser cannot connect:** keep the server terminal open and check that <http://127.0.0.1:8000/Frontend/> opens.
- **The extension says Server offline:** start Drona and reload the VS Code window.
- **Git push fails:** check that Git is installed, the selected path is a Git repository, `origin` is configured, and GitHub authentication works from that repository in a terminal.

## Privacy and local data

Drona's server listens on `127.0.0.1`, so it is intended for use on the same computer. Activity and dashboard records are stored in the local `Database` folder. Do not share `.env` or personal database files when sharing the project. Each person should configure their own repository path and GitHub authentication.
