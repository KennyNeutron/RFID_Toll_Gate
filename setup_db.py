import sqlite3

# Connect or create the database
conn = sqlite3.connect('rfid_gate.db')
c = conn.cursor()

# Create USERS table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        rfid TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        course TEXT,
        year_level TEXT,
        vehicle_type TEXT,
        plate_number TEXT
    )
''')


# Create LOGS table with timestamp support
c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rfid TEXT,
        name TEXT,
        course TEXT,
        year_level TEXT,
        vehicle_type TEXT,
        plate_number TEXT,
        timestamp TEXT,
        entry_type TEXT CHECK(entry_type IN ('enter', 'exit'))
    )
''')


conn.commit()
conn.close()
print("Database and tables created successfully.")
