# Kagi Summarizer Discord Bot

Discord bot (py-cord) that exposes a `/summarize` slash command for Kagi's summarizer API.

## How to use

You'll need to provide your own Kagi and Discord tokens in an `.env` file. You'll also need some credits on your Kagi account. [See more here.](https://help.kagi.com/kagi/api/summarizer.html)

After you've added the bot to your server you can invoke it with `/summarize` and provide a url.

## Setup

- Create an application and bot in the Discord Developer Portal and invite it to your server.
- Ensure the bot has the `applications.commands` scope. No privileged intents are required for slash-only usage.
- Add a `.env` file with:

  ```
  DISCORD_TOKEN=your_discord_bot_token
  KAGI_TOKEN=your_kagi_token
  ```

- Install dependencies:

  ```
  pip install -r requirements.txt
  ```

- Run:

  ```
  python kagi_summarizer.py
  ```

## Notes

- The bot defers responses and posts the summary once ready.
- If a summary exceeds Discord's 2000-character limit, the bot uploads it as a text file.
