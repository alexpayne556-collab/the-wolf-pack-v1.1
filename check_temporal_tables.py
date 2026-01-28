import sqlite3

conn = sqlite3.connect('wolfpack.db')
c = conn.cursor()

# Check for temporal memory tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ticker_memory', 'decision_log', 'pattern_library')")
temporal_tables = [t[0] for t in c.fetchall()]

print("TEMPORAL MEMORY TABLES IN WOLFPACK.DB:")
print(temporal_tables)

if temporal_tables:
    print("\nCOUNTS:")
    for table in temporal_tables:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        print(f"  {table}: {count} records")

conn.close()
