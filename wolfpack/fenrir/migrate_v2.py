# 🐺 FENRIR V2 - DATABASE MIGRATION
# Add new tables for quantum leap features

import sqlite3
import database

def migrate_v2():
    """Add V2 tables for quantum leap features"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    print("🐺 Migrating database to V2...")
    
    # Trade journal table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            action TEXT NOT NULL,
            shares REAL,
            price REAL,
            setup_type TEXT,
            thesis TEXT,
            quality_score INTEGER,
            pnl REAL,
            pnl_pct REAL,
            outcome TEXT,
            reason TEXT,
            emotions TEXT,
            timestamp TEXT NOT NULL,
            is_paper INTEGER DEFAULT 0
        )
    ''')
    
    # Catalysts table (for run tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catalysts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            catalyst_type TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            verified INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Historical runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            run_start_date TEXT NOT NULL,
            run_end_date TEXT,
            start_price REAL NOT NULL,
            end_price REAL,
            max_gain_pct REAL,
            days_duration INTEGER,
            catalyst_type TEXT,
            outcome TEXT,
            notes TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # User decisions table (for behavior tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            decision TEXT NOT NULL,
            setup_score INTEGER,
            sector TEXT,
            time_of_day TEXT,
            emotional_state TEXT,
            outcome TEXT,
            notes TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Momentum shifts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS momentum_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            shift_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            price_at_shift REAL,
            outcome TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Pattern outcomes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pattern_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT NOT NULL,
            ticker TEXT,
            sector TEXT,
            setup_score INTEGER,
            outcome TEXT NOT NULL,
            gain_pct REAL,
            hold_days INTEGER,
            notes TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database migrated successfully")
    print("\nNew tables created:")
    print("  • trade_journal - Auto-logging every trade")
    print("  • catalysts - Track what moves stocks")
    print("  • historical_runs - Learn from past runs")
    print("  • user_decisions - Your trading behavior")
    print("  • momentum_shifts - Character changes")
    print("  • pattern_outcomes - What works/doesn't")


if __name__ == '__main__':
    migrate_v2()
