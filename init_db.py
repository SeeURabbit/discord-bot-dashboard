import sqlite3

def init_db():
		conn = sqlite3.connect('events.db')
		c = conn.cursor()

		# Tabelle für Events erstellen
		c.execute('''
		CREATE TABLE IF NOT EXISTS events (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT NOT NULL,
				description TEXT NOT NULL,
				event_time TEXT NOT NULL,
				role TEXT NOT NULL,
				posted INTEGER DEFAULT 0
		)''')

		conn.commit()
		conn.close()

if __name__ == '__main__':
		init_db()
		print("Datenbank und Tabelle erstellt.")
