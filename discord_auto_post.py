import sqlite3
import json
import requests
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os

# Load webhook URL from env
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Path to your events database
DB_PATH = "data/events.db"
POSTED_EVENTS_LOG = "data/posted_events.json"

# Load already-posted event IDs
def load_posted():
		if not os.path.exists(POSTED_EVENTS_LOG):
				return []
		with open(POSTED_EVENTS_LOG, 'r') as f:
				return json.load(f)

# Save posted event IDs
def save_posted(posted_ids):
		with open(POSTED_EVENTS_LOG, 'w') as f:
				json.dump(posted_ids, f)

# Build the Discord message
def build_discord_embed(event):
		return {
				"embeds": [
						{
								"title": f"📅 {event['title']}",
								"description": f"**Description:** {event['description']}\n"
															 f"**Time:** {event['event_time']}\n"
															 f"**Role:** {event['role'] or '—'}\n"
															 f"**Recurrence:** {event['recurrence'] or '—'}",
								"color": 0xff9900,
								"footer": {"text": "FUR Command Center"}
						}
				]
		}

# Main auto-post logic
def check_and_post_events():
		posted_ids = load_posted()
		now = datetime.utcnow()
		upcoming_window = now + timedelta(hours=1)  # 1-hour lookahead

		conn = sqlite3.connect(DB_PATH)
		conn.row_factory = sqlite3.Row
		events = conn.execute("SELECT * FROM events WHERE datetime(event_time) BETWEEN ? AND ?",
													(now.isoformat(), upcoming_window.isoformat())).fetchall()
		conn.close()

		for event in events:
				if event["id"] in posted_ids:
						continue

				# Post to Discord
				data = build_discord_embed(event)
				response = requests.post(DISCORD_WEBHOOK_URL, json=data)
				if response.status_code == 204:
						print(f"✅ Posted event ID {event['id']} to Discord")
						posted_ids.append(event["id"])
				else:
						print(f"❌ Failed to post event {event['id']}: {response.text}")

		save_posted(posted_ids)

# Schedule every 60 minutes
def start_scheduler():
		scheduler = BackgroundScheduler()
		scheduler.add_job(check_and_post_events, 'interval', minutes=60)
		scheduler.start()
		print("🔄 Auto-poster is running every 60 minutes...")
		try:
				while True:
						time.sleep(60)
		except (KeyboardInterrupt, SystemExit):
				scheduler.shutdown()

if __name__ == "__main__":
		start_scheduler()
