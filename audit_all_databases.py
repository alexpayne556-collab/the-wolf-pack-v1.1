import sqlite3
import os

def quick_audit(db_path):
    """Quick audit showing tables and row counts"""
    
    if not os.path.exists(db_path):
        print(f"❌ Not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print(f"📁 {db_path}: EMPTY (0 tables)")
            conn.close()
            return
        
        print(f"\n{'='*80}")
        print(f"📊 DATABASE: {db_path}")
        print(f"{'='*80}")
        print(f"Tables: {len(tables)}")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table:30s} {count:>6d} rows")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error reading {db_path}: {e}")

if __name__ == "__main__":
    databases = [
        "wolfpack.db",
        "data/wolfpack.db",
        "data/wolf_brain/autonomous_memory.db",
        "data/wolf_brain/memory.db",
        "wolfpack/data/wolfpack.db",
        "wolfpack/data/wolfpack_v2.db",
        "wolfpack/fenrir/fenrir_trades.db",
    ]
    
    print("="*80)
    print("WOLF PACK DATABASE AUDIT")
    print("="*80)
    
    for db in databases:
        quick_audit(db)
    
    print(f"\n{'='*80}")
    print("AUDIT COMPLETE")
    print("="*80)
