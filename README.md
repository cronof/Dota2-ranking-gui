# Dota2-ranking-gui

Desktop GUI app that shows Dota 2 player profile and rank information using the OpenDota API.

## Features

- Search a player by Dota 2 account ID.
- Displays rank tier, leaderboard rank, and estimated MMR.
- Shows win/loss totals and calculated win rate.
- Simple Tkinter-based GUI (no browser required).

## Requirements

- Python 3.10+
- `pip` to install dependencies

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

## Where to get an Account ID

- You can use any public Dota 2 account ID (for example from OpenDota).
- Enter numeric account ID only.
