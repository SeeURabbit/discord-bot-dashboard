import sqlite3
import discord
from discord.ext import tasks
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

class WeeklyNewsletter:
    def __init__(self, bot):
        self.bot = bot
        self.send_weekly_newsletter.start()

    @tasks.loop(hours=24)
    async def send_weekly_newsletter(self):
        now = datetime.utcnow()
        if now.weekday() != 6 or now.hour != 12:  # Sunday at 12:00 UTC
            return

        conn = sqlite3.connect('data/events.db')
        c = conn.cursor()
        next_week = now + timedelta(days=7)
        c.execute(
            "SELECT title, event_time FROM events WHERE event_time BETWEEN ? AND ? ORDER BY event_time",
            (now.isoformat(), next_week.isoformat())
        )
        events = c.fetchall()
        conn.close()

        if not events:
            return

        lines = ["**Your events for this week at FUR 🐇🔥**\n"]
        for title, event_time in events:
            try:
                dt = datetime.fromisoformat(event_time)
                lines.append(f"📅 {dt.strftime('%A %H:%M')} UTC – **{title}**")
            except Exception as e:
                print(f"❌ Failed to format event time: {e}")

        message = "\n".join(lines)
        guild = self.bot.get_guild(GUILD_ID)
        if guild is None:
            print("❌ Guild not found.")
            return

        for member in guild.members:
            if member.bot:
                continue
            try:
                await member.send(message)
            except Exception as e:
                print(f"❌ Could not DM {member.display_name}: {e}")

    @send_weekly_newsletter.before_loop
    async def before_newsletter(self):
        await self.bot.wait_until_ready()

# Bot Extension Loader
async def setup(bot):
    try:
        await bot.add_cog(WeeklyNewsletter(bot))
    except Exception as e:
        print(f"Failed to load WeeklyNewsletter: {e}")
        raise