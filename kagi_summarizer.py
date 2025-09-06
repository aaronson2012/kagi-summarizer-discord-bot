"""
Discord bot that summarizes the content at a given URL using Kagi.

Invoke with `/summarize`.
"""

import os
import sys
import io

import discord
import aiohttp

from dotenv import load_dotenv

load_dotenv()

KAGI_TOKEN = os.environ.get("KAGI_TOKEN")

intents = discord.Intents.default()
intents.guilds = True  # slash commands live in guilds; no message content needed
bot = discord.Bot(intents=intents)


@bot.slash_command(name="summarize", description="Summarizes the given URL's content")
async def summarize(
    ctx: discord.ApplicationContext,
    url: discord.Option(str, "The URL to summarize (http/https)"),
):
    """
    The main bot entrypoint
    """
    # Basic validation to avoid obvious errors
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        await ctx.respond("Please provide a valid http(s) URL.", ephemeral=True)
        return

    await ctx.defer()

    try:
        summary = await get_summary(url)
    except Exception as e:
        await ctx.send_followup(f"Failed to summarize: {e}")
        return

    # Respect Discord 2000 character limit; send as file if too long
    if len(summary) > 1900:
        data = io.BytesIO(summary.encode("utf-8"))
        file = discord.File(data, filename="summary.txt")
        await ctx.send_followup(content="Summary was long; attached as file.", file=file)
    else:
        await ctx.send_followup(summary)


async def get_summary(url):
    """
    Get the summary from Kagi
    """

    if not KAGI_TOKEN:
        raise RuntimeError("KAGI_TOKEN is not set in environment.")

    base_url = "https://kagi.com/api/v0/summarize"
    params = {"url": url, "summary_type": "summary", "engine": "agnes"}
    headers = {"Authorization": f"Bot {KAGI_TOKEN}"}

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(base_url, headers=headers, params=params) as resp:
                status = resp.status
                # Try to parse JSON safely; fall back to text
                try:
                    payload = await resp.json(content_type=None)
                except aiohttp.ContentTypeError:
                    text = await resp.text()
                    raise RuntimeError(
                        f"Unexpected response (status {status}): {text[:200]}"
                    )

                if status != 200:
                    # Extract error message if present
                    err = (
                        payload.get("error", [{}])[0].get("msg")
                        if isinstance(payload.get("error"), list)
                        else payload.get("error")
                    ) or "Unknown error"
                    raise RuntimeError(f"Kagi error {status}: {err}")

                output = (
                    (payload.get("data") or {}).get("output")
                    or (
                        payload.get("error", [{}])[0].get("msg")
                        if isinstance(payload.get("error"), list)
                        else payload.get("error")
                    )
                )

                if not output:
                    raise RuntimeError("Kagi returned an empty response.")

                formatted_response = (
                    f"[Click here for full article]({url})\n{output}"
                )
                return formatted_response
        except aiohttp.ServerTimeoutError:
            return "Kagi response took too long..."


# Sync slash command to Discord.
@bot.event
async def on_ready():
    """
    on_ready() syncs and updates the slash commands on the Discord server.
    """
    try:
        await bot.sync_commands()
        print("Slash commands synced.")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")


token = os.environ.get("DISCORD_TOKEN")
if not token:
    print("DISCORD_TOKEN is not set in environment.")
    sys.exit(1)

bot.run(token)
