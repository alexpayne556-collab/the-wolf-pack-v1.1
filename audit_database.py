import sqlite3
import os

def audit_database(db_path):
    """Complete database audit for wolfpack.db"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("=" * 80)
    print(f"DATABASE AUDIT: {db_path}")
    print("=" * 80)
    print(f"\nTotal tables: {len(tables)}")
    print("\nTABLES:")
    for table in tables:
        print(f"  - {table}")
    
    print("\n" + "=" * 80)
    print("TABLE SCHEMAS AND ROW COUNTS")
    print("=" * 80 + "\n")
    
    for table in tables:
        # Get schema
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        schema = cursor.fetchone()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        print(f"\n{'='*80}")
        print(f"TABLE: {table}")
        print(f"ROWS: {count}")
        print(f"{'='*80}")
        if schema and schema[0]:
            print(schema[0])
        else:
            print("(No schema - likely a system table)")
        
        # If small table, show sample data
        if count > 0 and count <= 5:
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                print(f"\nSAMPLE DATA ({len(rows)} rows):")
                for row in rows:
                    print(f"  {row}")
        elif count > 0:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print(f"\nSAMPLE DATA (first 3 of {count} rows):")
                for row in rows:
                    print(f"  {row}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    audit_database("wolfpack.db")
    
    # Check if autonomous_memory.db exists
    if os.path.exists("autonomous_memory.db"):
        print("\n\n")
        audit_database("autonomous_memory.db")
