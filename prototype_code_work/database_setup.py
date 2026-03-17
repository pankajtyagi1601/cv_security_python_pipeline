import sqlite3

connect = sqlite3.connect("guardvision.db")
cursor = connect.cursor()

table_query = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    person_name TEXT,
    image_path TEXT,
    camera_id TEXT,
    event_type TEXT
)
"""
cursor.execute(table_query)

connect.commit()
connect.close()

print("Database initialized sucessfully.")