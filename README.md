# Drona

Drona is a local dashboard for tracking coding activity, and focus time on Windows.

## Quick start

1. Download and extract `Drona-v0.1.0-Windows.zip` from the GitHub release.
2. Install [Git for Windows](https://git-scm.com/install/windows) if it is not already installed. Drona uses Git to track repository activity.
3. Run `Drona.exe` and choose a folder to track. **The folder must be a Git repository.**
4. Open <http://127.0.0.1:8000/> in your browser. Keep the Drona window open while using the dashboard.

## Commits and GitHub

If you are trying Drona, choose **No** when asked to enable GitHub pushing during installation. Drona will still make local commits; connecting a GitHub account is only needed if you want to push commits to GitHub.

Git needs an author name and email to create commits. If you are new to Git, configure them in PowerShell (you can run these commands from any folder):

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

These values identify the author of your commits. Use your GitHub `noreply` email if you prefer not to show your personal email in commits. Pushing to GitHub also requires GitHub authentication, an `origin` remote, and the `main` branch.

## Optional features

- **VS Code time tracking:** Install the Drona Activity Tracker extension and open your tracked repository in VS Code.
- **AI recaps:** Add `GROQ_API_KEY=your-key` to a `.env` file next to `Drona.exe`. Do not put spaces around `=`. Keep the key private and do not commit the `.env` file.

## Troubleshooting

- **Git is not found:** Install Git for Windows, then restart Drona.
- **The dashboard does not load:** Make sure Drona is still running, then visit <http://127.0.0.1:8000/>.
- **Drona says the selected folder is not a Git repository:** Choose a folder that already contains a Git repository.

## Common errors

### AI recap: Groq API key is missing

This appears when you request a recap with activity recorded for today, but Drona cannot find a Groq API key. Create a `.env` file next to `Drona.exe` and add your key on one line, with no spaces around `=`:

If you have added the api_key and it is still saying that api_key is not inserted please restart the the app!
```text
GROQ_API_KEY=your_api_key
```

![Drona showing the missing Groq API key error](https://github.com/user-attachments/assets/0a8bec9b-3b6e-4ac0-a546-8a267ab275b6)

### Git commit: author identity is not configured

Git needs a name and email to create a commit. If this appears while updating activity or pushing to GitHub, configure your Git author identity:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Replace the example values with your name and email. This configures the commit author; GitHub authentication is a separate requirement for pushing commits.

![Git reporting that the author identity is not configured](https://github.com/user-attachments/assets/f3f64d6a-6878-4c71-8622-d023baeb0939)

For other errors, see the [Drona tutorial](https://x.com/Code_Arjun/status/2111779850155667564).
