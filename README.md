# Drona

Drona tracks a Git repository, creates a categorized commit from its changes, and pushes it to GitHub. It also generates data for the Drona dashboard.

## Set up the repository

Set `DRONA_REPO_PATH` to the local path of the Git repository you want to track, or provide the path when running Drona:

```sh
python "Backend(main files)/main.py" --repo "C:\path\to\your\repository"
```

Drona saves the selected repository path in `Database/repo_settings.json`. If no path is configured, it asks for one when run in a terminal. Non-interactive runs need a configured path.

Your repository must have an `origin` remote, and Git must be able to push to its `main` branch.

## Run the tracker

From the web click Push To Github.
OR
From the project folder, run: 

```sh
python "Backend(main files)/main.py"
```
    

Drona stages changed files, creates a commit using file names as topics, and pushes to `origin/main`. It assigns categories from folders by default. 

When the file be auto runned it would ask for category directly into terminal.
OR
To use a specific category, run:

```sh
python "Backend(main files)/main.py" --category "Machine learning"
```

The category is saved for future runs. The tracker also updates dashboard data in the `Database` folder.

## Open the dashboard

Start the dashboard server from the project folder:

```sh
python -m uvicorn server2:app --app-dir "Backend(main files)" --host 127.0.0.1 --port 8000
```
Sorry for the server starting code begin this long. Working on that.....

Open [http://localhost:8000/Frontend/](http://localhost:8000/Frontend/) in your browser. The server stores timer sessions in `Database/focus_sessions.json`.
