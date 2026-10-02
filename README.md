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
