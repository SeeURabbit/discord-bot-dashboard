from flask import Blueprint, render_template
import sqlite3

leaderboard_bp = Blueprint("leaderboard", __name__)


def get_db_connection():
    try:
        conn = sqlite3.connect('data/events.db', timeout=20)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise


@leaderboard_bp.route("/leaderboards")
def leaderboards():
	with get_db_connection() as conn:
		data = {
	    "raids":
	    conn.execute(
	        "SELECT user_id, score FROM scores WHERE category = 'raids' ORDER BY score DESC LIMIT 10"
	    ).fetchall(),
	    "quests":
	    conn.execute(
	        "SELECT user_id, score FROM scores WHERE category = 'quests' ORDER BY score DESC LIMIT 10"
	    ).fetchall(),
	    "donations":
	    conn.execute(
	        "SELECT user_id, score FROM scores WHERE category = 'donations' ORDER BY score DESC LIMIT 10"
	    ).fetchall()
	}
	conn.close()
	return render_template("leaderboards.html", **data)


# Slash-Command Integration (Discord Bot)
import discord
from discord.ext import commands
from discord import app_commands
import os

GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))


class Leaderboard(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="leaderboard", description="Zeigt Rangliste")
	@app_commands.describe(category="Kategorie: raids, quests, donations")
	async def leaderboard(self, interaction: discord.Interaction, category: str):
		conn = sqlite3.connect('data/events.db')
		c = conn.cursor()
		c.execute(
		    "SELECT user_id, score FROM scores WHERE category = ? ORDER BY score DESC LIMIT 5",
		    (category, ))
		top = c.fetchall()
		conn.close()

		emoji_map = {"raids": "⚔️", "quests": "📜", "donations": "❤️"}
		embed = discord.Embed(
		    title=f"{emoji_map.get(category, '')} {category.title()} Leaderboard",
		    color=0xFFD700)
		for i, (user_id, score) in enumerate(top, 1):
			user = await self.bot.fetch_user(user_id)
			embed.add_field(name=f"{i}. {user.display_name}",
			                value=f"🔥 {score} Punkte",
			                inline=False)
		await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot), guild=discord.Object(id=GUILD_ID))
