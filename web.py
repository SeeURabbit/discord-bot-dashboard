from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import sqlite3
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

DATABASE = 'events.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    if request.method == 'GET':
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events")
            events = cursor.fetchall()

            if not events:
                return jsonify({"error": "Keine Events gefunden"}), 404

            events_list = [dict(event) for event in events]
            return jsonify(events_list), 200

        except sqlite3.DatabaseError as db_error:
            logging.error(f"Database error: {db_error}")
            return jsonify({"error": "Datenbankfehler"}), 500
        except Exception as e:
            logging.error(f"Fehler beim Abrufen der Events: {e}")
            return jsonify({"error": "Interner Fehler"}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            title = data.get('title')
            description = data.get('description')
            date = data.get('date')

            if not title or not description or not date:
                return jsonify({"error": "Alle Felder sind erforderlich"}), 400

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO events (title, description, date) VALUES (?, ?, ?)", 
                         (title, description, date))
            conn.commit()

            return jsonify({"message": "Event erstellt"}), 201

        except sqlite3.DatabaseError as db_error:
            logging.error(f"Database error: {db_error}")
            return jsonify({"error": "Datenbankfehler"}), 500
        except Exception as e:
            logging.error(f"Fehler beim Erstellen: {e}")
            return jsonify({"error": "Interner Fehler"}), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()

        if event is None:
            return jsonify({"error": "Event nicht gefunden"}), 404

        return jsonify(dict(event)), 200

    except sqlite3.DatabaseError as db_error:
        logging.error(f"Database error: {db_error}")
        return jsonify({"error": "Datenbankfehler"}), 500
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Events: {e}")
        return jsonify({"error": "Interner Fehler"}), 500

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/calendar')
def calendar():
    return render_template("calendar.html")

@app.route('/create-event')
def create_event_page():
    return render_template("create_event.html")

@app.route('/diplomacy')
def diplomacy():
    return render_template("diplomacy.html")

@app.route('/downloads')
def downloads():
    return render_template("downloads.html")

@app.route('/edit-event')
def edit_event():
    return render_template("edit_event.html")

@app.route('/events')
def events():
    return render_template("events.html")

@app.route('/leaderboards')
def leaderboards():
    return render_template("leaderboards.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/lore')
def lore():
    return render_template("lore.html")

@app.route('/participants')
def participants():
    return render_template("participants.html")

@app.route('/public')
def public_leaderboard():
    return render_template("public_leaderboard.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)