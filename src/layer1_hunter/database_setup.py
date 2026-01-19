#!/usr/bin/env python3
"""
Database setup for Wolf Pack News Tracker
Creates SQLite database with events and tickers tables
"""

import sqlite3
from datetime import datetime

def create_database(db_path='wolf_pack_events.db'):
    """Create database and tables if they don't exist"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Events table - core data
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        event_date DATETIME NOT NULL,
        event_type TEXT NOT NULL,
        headline TEXT,
        filing_url TEXT,
        market_cap_at_event REAL,
        price_at_event REAL,
        volume_at_event INTEGER,
        avg_volume_20d INTEGER,
        volume_ratio REAL,
        return_1d REAL,
        return_3d REAL,
        return_5d REAL,
        return_10d REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, event_date, event_type)
    )
    ''')
    
    # Tickers table - company fundamentals
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickers (
        ticker TEXT PRIMARY KEY,
        sector TEXT,
        industry TEXT,
        market_cap REAL,
        float_shares REAL,
        short_interest REAL,
        avg_volume REAL,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker ON events(ticker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_date ON events(event_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_returns ON events(return_5d)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database created: {db_path}")
    print(f"✅ Tables: events, tickers")
    print(f"✅ Indexes created")

if __name__ == '__main__':
    create_database()
