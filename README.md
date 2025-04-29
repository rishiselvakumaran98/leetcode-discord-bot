# LeetCode Weekly Discord Bot

## Overview
This Discord bot automatically fetches and posts the top 30 most frequently asked LeetCode questions from Microsoft, Google, Amazon, and Meta (Facebook) every week. It uses a Cloudflare‑scraping session to bypass protections, runs a scheduled job via APScheduler, and delivers nicely formatted embeds to a specified Discord channel.

## Features
- **Weekly Schedule**: Posts every Wednesday at 11:29 AM (server local time).
- **Multi-Company Support**: Retrieves top questions for Microsoft, Google, Amazon, and Meta.
- **Cloudflare Handling**: Uses `cloudscraper` to handle Cloudflare challenges and CSRF tokens.
- **Discord Embeds**: Sends each company’s questions in a clean embed.

## Prerequisites
- Python 3.8 or higher
- `pip` package manager
- A Discord application with a bot token and permissions to send messages
- A LeetCode Premium account with a valid `LEETCODE_SESSION` cookie

## Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/leetcode-discord-bot.git
   cd leetcode-discord-bot
   ```
2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # on Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. **Environment variables**: create a `.env` file in the project root with:
   ```dotenv
   DISCORD_TOKEN=your_discord_bot_token
   LEETCODE_SESSION=your_leetcode_session_cookie
   CHANNEL_ID=your_discord_channel_id
   ```
2. **Channel ID**: In Discord, enable Developer Mode → right-click your target channel → Copy ID.

## Running Locally
With your virtualenv activated and `.env` configured:
```bash
python bot.py
```

The bot will log in and schedule the weekly job. You should see a console message:
```
✅ Logged in as <BotName> (ID: 1234567890)
```

## Hosting Options

### 1. Virtual Private Server (VPS)
- Push your code to the server
- Set up the same `.env` and virtualenv
- Use `systemd`, `pm2`, or `screen` to keep `bot.py` running

### 2. Heroku
1. `heroku login` & `heroku create`
2. `git push heroku main`
3. `heroku config:set DISCORD_TOKEN=... LEETCODE_SESSION=... CHANNEL_ID=...`
4. `heroku ps:scale worker=1`

### 3. Docker (Optional)
1. Build image: `docker build -t leetcode-bot .`
2. Run container:
   ```bash
   docker run -d \
     --env-file .env \
     leetcode-bot
   ```

## Customization
- **Schedule**: modify the cron in `scheduler.add_job(...)` inside `bot.py`.
- **Companies**: adjust the `COMPANIES` dict and GraphQL `favoriteSlug` logic.
- **Embed Format**: change `post_weekly()` to include additional fields or styling.

---
*Happy coding and good luck cracking those coding interviews!*

