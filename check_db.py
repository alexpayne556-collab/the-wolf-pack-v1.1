import sqlite3

# Check main learning engine
conn = sqlite3.connect('data/wolfpack.db')
c = conn.cursor()

print("=== WOLFPACK.DB TABLES ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
for table in tables:
    print(f"\n{table}:")
    c.execute(f"SELECT COUNT(*) FROM {table}")
    count = c.fetchone()[0]
    print(f"  {count} rows")
    
    # Show structure
    c.execute(f"PRAGMA table_info({table})")
    cols = c.fetchall()
    print(f"  Columns: {', '.join([col[1] for col in cols])}")
    
    # Show recent examples
    if count > 0:
        c.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 2")
        rows = c.fetchall()
        print(f"  Recent entries: {len(rows)}")

conn.close()

# Check autonomous brain database
import os
if os.path.exists('data/wolf_brain/autonomous_memory.db'):
    print("\n\n=== AUTONOMOUS_MEMORY.DB TABLES ===")
    conn2 = sqlite3.connect('data/wolf_brain/autonomous_memory.db')
    c2 = conn2.cursor()
    c2.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables2 = [t[0] for t in c2.fetchall()]
    for table in tables2:
        print(f"\n{table}:")
        c2.execute(f"SELECT COUNT(*) FROM {table}")
        count = c2.fetchone()[0]
        print(f"  {count} rows")
    conn2.close()
else:
    print("\n\nNo autonomous_memory.db found yet")
