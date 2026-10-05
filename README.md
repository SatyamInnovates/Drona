# Drona
An Ai agent which directly has access to your computer folder and whatever you code or learn it keep record of it in a website.

## Configure the tracked repository

Set `DRONA_REPO_PATH` to the Git repository Drona should track before running
`Backend(main files)/main.py`. You can also add a `repo_path` entry to
`Database/repo_settings.json`; the environment variable takes precedence. If
neither is set, Drona uses the original local repository when present, then
falls back to this project folder. Non-interactive runs keep the saved category.

Run the tracker once to generate the dashboard data files. Serve the project
folder over HTTP when opening the dashboard so the browser can fetch those
files; opening `Frontend/index.html` directly may block those requests.

## Run the dashboard with persistent timer storage

Start the included dashboard server from the project root:

```sh
python "Backend(main files)/server.py"
```

Then open `http://localhost:8000/Frontend/`. The server saves timer sessions
in `Database/focus_sessions.json`, so they survive browser restarts and server
restarts as long as that database file remains on persistent storage. A basic
static file server does not provide this API; the timer falls back to browser
storage when one is used.

Use **Push to GitHub** in the dashboard to run `Backend(main files)/main.py`
manually. Choose a category in the dashboard; it is saved, then used to label
the commit before the script pushes to `origin/main`. Configure the tracked
repository and GitHub credentials before using it.
