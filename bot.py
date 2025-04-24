import discord
from discord.ext import commands, tasks
import sqlite3
import pytz
import asyncio
import logging
from datetime import datetime, timedelta
import os

# === CONFIG ===
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))
DB_PATH = 'data/events.db'
os.makedirs('data', exist_ok=True)

# === DATABASE INIT ===
def init_db():
    try:
        with sqlite3.connect(DB_PATH, timeout=20) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA busy_timeout=5000')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        description TEXT,
                        event_time TEXT,
                        role TEXT,
                        recurrence TEXT DEFAULT 'none'
                    )''')
            c.execute('''CREATE TABLE IF NOT EXISTS participants (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id INTEGER,
                        user_id TEXT,
                        checked_in INTEGER DEFAULT 0
                    )''')
            c.execute('''CREATE TABLE IF NOT EXISTS user_settings (
                        user_id TEXT PRIMARY KEY,
                        allow_dm INTEGER DEFAULT 1,
                        language TEXT DEFAULT 'en',
                        timezone TEXT DEFAULT 'UTC'
                    )''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise

init_db()

# === BOT SETUP ===
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# === TIMEZONES ===
timezones = {
    "UTC": "UTC",
    "Berlin": "Europe/Berlin",
    "New York": "America/New_York",
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "Moscow": "Europe/Moscow",
    "Beijing": "Asia/Shanghai",
    "Istanbul": "Europe/Istanbul",
    "Rome": "Europe/Rome",
    "Hanoi": "Asia/Ho_Chi_Minh",
    "Warsaw": "Europe/Warsaw"
}

# === LANGUAGES ===
translations = {
    'en': {
        'bot_online': "✅ Bot is online!",
        'reminder': "📬 Reminder: `{title}` starts in {timeframe}!"
    },
    'de': {
        'bot_online': "✅ Bot ist online!",
        'reminder': "📬 Erinnerung: `{title}` startet in {timeframe}!"
    },
    'vi': {
        'bot_online': "✅ Bot đang hoạt động!",
        'reminder': "📬 Nhắc nhở: `{title}` sẽ bắt đầu sau {timeframe}!"
    },
    'tr': {
        'bot_online': "✅ Bot çevrimiçi!",
        'reminder': "📬 Hatırlatma: `{title}` etkinliği {timeframe} içinde başlıyor!"
    },
    'it': {
        'bot_online': "✅ Bot è online!",
        'reminder': "📬 Promemoria: `{title}` inizia tra {timeframe}!"
    },
    'cs': {
        'bot_online': "✅ Bot je online!",
        'reminder': "📬 Připomínka: `{title}` začíná za {timeframe}!"
    }
}

# === SLASH COMMANDS ===
@tree.command(name="ping", description="Check if bot is online")
@commands.cooldown(1, 60, commands.BucketType.user)
async def ping(interaction: discord.Interaction):
    try:
        user_id = str(interaction.user.id)
        language = get_user_language(user_id)
        msg = translations.get(language, translations['en'])['bot_online']
        await interaction.response.send_message(msg, ephemeral=True)
    except Exception as e:
        print(f"Error in ping command: {e}")
        await interaction.response.send_message("An error occurred", ephemeral=True)

# === REMINDER SYSTEM ===
@tasks.loop(minutes=1)
async def check_reminders():
    await bot.wait_until_ready()
    now = datetime.utcnow().replace(tzinfo=pytz.utc)

    try:
        async with asyncio.timeout(30):  # 30 second timeout
            await check_and_send_reminders(now)
    except asyncio.TimeoutError:
        logging.error("Reminder processing timed out")
    except Exception as e:
        logging.error(f"Error in check_reminders: {e}")

async def check_and_send_reminders(now):
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute("SELECT id, title, event_time FROM events")
        events = c.fetchall()

        for event_id, title, ts in events:
            try:
                event_time = datetime.fromisoformat(ts.replace('T', ' '))
                event_time = pytz.utc.localize(event_time)
                delta = event_time - now

                if timedelta(minutes=59) < delta <= timedelta(minutes=61):
                    await send_dm_reminders(event_id, title, "1 hour")
                elif timedelta(minutes=9) < delta <= timedelta(minutes=11):
                    await send_dm_reminders(event_id, title, "10 minutes")
            except Exception as e:
                print(f"❌ Invalid time format: {e}")
    except Exception as e:
        print(f"❌ Database error in check_reminders: {e}")
    finally:
        conn.close()

async def send_dm_reminders(event_id, title, timeframe):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM participants WHERE event_id = ?", (event_id,))
        users = c.fetchall()

        for (user_id,) in users:
            c.execute("SELECT allow_dm, language FROM user_settings WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            if row and row[0] == 0:
                continue

            language = row[1] if row else 'en'
            msg_template = translations.get(language, translations['en'])['reminder']
            message = msg_template.format(title=title, timeframe=timeframe)

            try:
                user = await bot.fetch_user(int(user_id))
                await user.send(message)
            except Exception as e:
                print(f"❌ Failed to DM {user_id}: {e}")

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    if not check_reminders.is_running():
        check_reminders.start()
    print(f"✅ Bot is online as {bot.user}")

def get_user_language(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT language FROM user_settings WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            return row[0] if row else 'en'
    except:
        return 'en'

def run_bot():
    if not TOKEN:
        raise ValueError("Discord token not configured")
    try:
        bot.run(TOKEN)
    except Exception as e:
        logging.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    run_bot()
