# Drona Activity Tracker

Tracks active coding time in VS Code and sends summaries to your local Drona dashboard.

## Requirements

- The Drona local server must be running.
- Start it with `Start Drona.bat` from the Drona project folder.

## Usage

The tracker starts automatically when VS Code opens. It records activity after you save files and pauses after inactivity. Use **Drona Activity Tracker: Toggle Tracking** from the Command Palette to pause or resume tracking.

Activity is sent to the local server at `http://127.0.0.1:8000`.