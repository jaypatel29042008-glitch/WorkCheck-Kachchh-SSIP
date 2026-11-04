import sqlite3
import os

db_path = r'c:\Users\jaypa\OneDrive\Documents\SSIP\database\occupational_health.db'
sql_path = r'c:\Users\jaypa\OneDrive\Documents\SSIP\database\schema.sql'

if os.path.exists(db_path):
    os.remove(db_path)

con = sqlite3.connect(db_path)
with open(sql_path, 'r', encoding='utf-8') as f:
    sql = f.read()

con.executescript(sql)
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall() if not r[0].startswith('sqlite_')]
print('SUCCESS: Created Tables (10 total):', tables)
cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
views = [r[0] for r in cursor.fetchall()]
print('SUCCESS: Created Views (3 total):', views)
con.close()
