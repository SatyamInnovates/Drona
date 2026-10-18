# Drona

Drona is a local learning and coding activity dashboard for Windows.

## Quick start

1. Download and extract `Drona-v0.1.0-Windows.zip` from the GitHub release.
2. Install [Git for Windows](https://git-scm.com/install/windows). Drona needs Git to track repository activity.
3. Run `Drona.exe`, choose a Git repository to track, then open <http://127.0.0.1:8000/> in your browser. Keep the Drona window open while using it.

## Commits and GitHub

To create commits, configure your Git author name and email in PowerShell:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use your GitHub `noreply` email if you prefer not to show your personal email in commits. Pushing also requires GitHub authentication and an `origin` remote.

## Optional features

- **VS Code time tracking:** Install the Drona Activity Tracker extension and open your tracked repository in VS Code.
- **AI recaps:** Add `GROQ_API_KEY=your-key` to a `.env` file next to `Drona.exe`. Keep the key private.

## Troubleshooting

- If Git is not found, install Git for Windows and restart Drona.
- If the dashboard does not load, make sure Drona is still running and visit <http://127.0.0.1:8000/>.
