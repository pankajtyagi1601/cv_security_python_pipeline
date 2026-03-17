import sqlite3

conn = sqlite3.connect("guardvision.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM events")

print(cursor.fetchall())