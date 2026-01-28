import sqlite3
import json

conn = sqlite3.connect('data/wolfpack.db')
c = conn.cursor()

print("=== ALL TRADES IN LEARNING ENGINE ===\n")
c.execute("SELECT * FROM trades ORDER BY id DESC")
cols = [col[0] for col in c.description]
trades = c.fetchall()

for trade in trades:
    data = dict(zip(cols, trade))
    print(f"#{data['id']} - {data['ticker']} {data['action']} @ ${data['price']:.2f}")
    print(f"  Timestamp: {data['timestamp']}")
    print(f"  Shares: {data['shares']}")
    print(f"  Thesis: {data['thesis']}")
    if data['fenrir_said']:
        print(f"  Fenrir: {data['fenrir_said'][:100]}...")
    if data['day2_pct']:
        print(f"  Day 2: {data['day2_pct']}%")
    if data['day5_pct']:
        print(f"  Day 5: {data['day5_pct']}%")
    if data['outcome']:
        print(f"  Outcome: {data['outcome']}")
    if data['notes']:
        notes_str = str(data['notes'])
        if len(notes_str) > 200:
            print(f"  Notes: {notes_str[:200]}...")
        else:
            print(f"  Notes: {notes_str}")
    print()

conn.close()
