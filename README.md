# Discord Status Bot

A lightweight bot that keeps your Discord account set to **Do Not Disturb** 24/7, deployed on Railway.

---

## Features

- Keeps your status as **DND** (Do Not Disturb)
- Auto-reconnects if the connection drops
- Token stored securely as an environment variable — never hardcoded
- Runs as a background worker on Railway (no sleeping)

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | The bot script |
| `requirements.txt` | Python dependencies |
| `Procfile` | Tells Railway how to run the bot |

---

## Deployment (Railway)

### 1. Push to GitHub

Make sure all three files are in the root of a GitHub repository.

### 2. Create a Railway project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository

### 3. Add your token

1. Open your service on Railway
2. Go to the **Variables** tab
3. Add a new variable:
   ```
   DISCORD_TOKEN = your_token_here
   ```
4. Railway will automatically restart the service

Your bot is now live.

---

## Configuration

You can tweak these variables at the top of `main.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `STATUS` | `dnd` | Your status — `dnd`, `online`, or `idle` |
| `CUSTOM_STATUS` | `""` | Custom status text. Leave empty for none |
| `USE_EMOJI` | `False` | Add an emoji to your custom status |

---

## Getting Your Token

> ⚠️ **Never share your token with anyone.** It gives full access to your Discord account.

1. Open Discord in your browser
2. Press `F12` to open DevTools
3. Go to the **Network** tab
4. Send any message or perform any action
5. Look for a request to `discord.com/api`
6. Check the **Headers** — find `Authorization` and copy the value

---

## Notes

- This uses a **user token**, not a bot token. Automating user accounts is against Discord's Terms of Service. Use at your own risk.
- If your token changes (e.g. you reset your password), update the `DISCORD_TOKEN` variable on Railway.
