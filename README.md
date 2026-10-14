# Drona

A Local tool that will auto push your codes to github without even you worrying and track all your progress.

## Start Drona

Requirements: Python 3.10 or newer. For coding-time tracking, install VS Code 1.140 or newer.

1. In PowerShell, open the Drona project folder and install the server packages once:

   ```powershell
   python -m pip install fastapi uvicorn requests
   ```

2. Double-click [`Start Drona.bat`](Start%20Drona.bat). Keep its server window open while using the dashboard.
3. Open <http://127.0.0.1:8000/Frontend/> if the browser does not open automatically.

## Install the VS Code extension

In VS Code, open **Extensions** (`Ctrl+Shift+X`), choose **Install from VSIX...** from the `...` menu, and select:

`drona-activity-tracker/drona-activity-tracker-0.0.1.vsix`

The extension tracks edits in the opened workspace and sends the workspace name, language, and time to the local Drona server. It does not send file contents or full paths. It stops counting five minutes after the last edit by default. Start the server before using the extension.

## Optional GitHub push

Install Git and set up GitHub authentication. Point Drona at your repository once from PowerShell:

```powershell
python "Backend(main files)/main.py" --repo "C:\path\to\your\repository"
```

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
