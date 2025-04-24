from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Datenbankverbindung herstellen
def get_db_connection():
    try:
        conn = sqlite3.connect('data/events.db', timeout=20)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

# Alle Events abrufen
@app.route('/api/events', methods=['GET'])
def get_events():
		conn = get_db_connection()
		events = conn.execute('SELECT * FROM events WHERE posted = 0').fetchall()  # Events, die noch nicht gepostet wurden
		conn.close()

		events_list = []
		for event in events:
				events_list.append({
						'id': event['id'],
						'title': event['title'],
						'description': event['description'],
						'event_time': event['event_time'],
						'role': event['role']
				})

		return jsonify(events_list)

# Event als gepostet markieren (wird vom Bot aufgerufen, nachdem es gepostet wurde)
@app.route('/api/events/update', methods=['POST'])
def update_event_status():
		data = request.json
		event_id = data['id']
		conn = get_db_connection()
		conn.execute('UPDATE events SET posted = 1 WHERE id = ?', (event_id,))
		conn.commit()
		conn.close()
		return jsonify({"message": "Event status updated"}), 200

if __name__ == "__main__":
		app.run(debug=True)
