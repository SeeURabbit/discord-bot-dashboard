    import discord
    from discord.ext import commands, tasks
    from datetime import datetime, timedelta
    import sqlite3
    import os
    from dotenv import load_dotenv

    load_dotenv()
    GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

    class Reminders(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.check_reminders.start()

        def cog_unload(self):
            self.check_reminders.cancel()

        @tasks.loop(minutes=1)
        async def check_reminders(self):
            now = datetime.utcnow()
            try:
                conn = sqlite3.connect('data/events.db')
                c = conn.cursor()

                c.execute("""
                    SELECT id, title, event_time, role 
                    FROM events 
                    WHERE event_time BETWEEN ? AND ?
                """, (now.isoformat(), (now + timedelta(hours=1)).isoformat()))

                upcoming_events = c.fetchall()
                conn.close()

                for event_id, title, event_time, role in upcoming_events:
                    try:
                        event_dt = datetime.fromisoformat(event_time)
                        minutes_until = int((event_dt - now).total_seconds() / 60)

                        if minutes_until in [60, 30, 10]:
                            guild = self.bot.get_guild(GUILD_ID)
                            if not guild:
                                continue

                            # Look for a channel named "events"
                            channel = discord.utils.get(guild.text_channels, name="events")
                            if not channel:
                                print("⚠️ 'events' channel not found in guild.")
                                continue

                            mention = f"<@&{role}>" if role and role.isdigit() else role or "@everyone"
                            await channel.send(
                                f"⏰ {mention} Reminder: **{title}** starts in {minutes_until} minutes!"
                            )
                    except Exception as e:
                        print(f"❌ Error processing event: {e}")

            except sqlite3.Error as db_err:
                print(f"❌ Database error: {db_err}")
            except Exception as gen_err:
                print(f"❌ General error: {gen_err}")

        @check_reminders.before_loop
        async def before_check_reminders(self):
            await self.bot.wait_until_ready()

    async def setup(bot):
        await bot.add_cog(Reminders(bot))
