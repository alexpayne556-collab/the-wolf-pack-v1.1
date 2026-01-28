"""
STEP 0: Complete audit of existing data/wolfpack.db
Before ANY schema changes - document everything that exists.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = 'data/wolfpack.db'
BACKUP_PATH = 'data/wolfpack_backup_jan28.db'

def full_audit():
    """Complete audit of existing database"""
    
    print("=" * 80)
    print("WOLFPACK.DB FULL AUDIT")
    print(f"Date: {datetime.now()}")
    print("=" * 80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📊 TOTAL TABLES: {len(tables)}")
    print("-" * 40)
    
    audit_results = {}
    
    for table in tables:
        print(f"\n{'='*60}")
        print(f"TABLE: {table}")
        print(f"{'='*60}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"ROWS: {count}")
        
        # Get schema
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        schema = cursor.fetchone()
        print(f"\nSCHEMA:")
        if schema and schema[0]:
            print(schema[0])
        
        # Get all data if table has rows
        if count > 0:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            print(f"\nCOLUMNS: {columns}")
            print(f"\nALL DATA ({count} rows):")
            print("-" * 40)
            
            for i, row in enumerate(rows):
                print(f"\nRow {i+1}:")
                for j, col in enumerate(columns):
                    value = row[j]
                    # Truncate long values for readability
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    print(f"  {col}: {value}")
            
            audit_results[table] = {
                'count': count,
                'columns': columns,
                'data': rows
            }
        else:
            audit_results[table] = {
                'count': 0,
                'columns': [],
                'data': []
            }
    
    conn.close()
    
    # Summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    
    print("\nTables with data:")
    for table, info in audit_results.items():
        if info['count'] > 0:
            print(f"  ✓ {table}: {info['count']} rows")
    
    print("\nEmpty tables:")
    for table, info in audit_results.items():
        if info['count'] == 0:
            print(f"  ○ {table}: 0 rows")
    
    return audit_results

if __name__ == "__main__":
    audit_results = full_audit()
    
    print("\n" + "=" * 80)
    print("BACKUP STATUS")
    print("=" * 80)
    import os
    if os.path.exists(BACKUP_PATH):
        backup_size = os.path.getsize(BACKUP_PATH)
        original_size = os.path.getsize(DB_PATH)
        print(f"✓ Backup exists: {BACKUP_PATH}")
        print(f"  Original size: {original_size:,} bytes")
        print(f"  Backup size: {backup_size:,} bytes")
        if backup_size == original_size:
            print(f"  ✓ Sizes match - backup verified")
        else:
            print(f"  ⚠️ Sizes differ - check backup")
    else:
        print(f"✗ BACKUP NOT FOUND: {BACKUP_PATH}")
        print("  DO NOT PROCEED WITHOUT BACKUP")
