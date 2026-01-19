#!/usr/bin/env python3
"""
Wolf Pack Database Helpers
SQLite operations for daily records
"""

import sqlite3
import os
from datetime import datetime
from config import DB_PATH

def init_database():
    """Create database and tables if they don't exist"""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main daily records table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date DATE NOT NULL,
        sector TEXT,
        
        -- Price data
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        prev_close REAL,
        
        -- Calculated metrics
        daily_return_pct REAL,
        intraday_range_pct REAL,
        close_vs_high_pct REAL,
        
        -- Volume
        volume INTEGER,
        avg_volume_20d INTEGER,
        volume_ratio REAL,
        dollar_volume REAL,
        
        -- Context
        dist_52w_high_pct REAL,
        dist_52w_low_pct REAL,
        return_5d REAL,
        return_20d REAL,
        return_60d REAL,
        
        -- Streaks
        consecutive_green INTEGER,
        consecutive_red INTEGER,
        
        -- Technical indicators
        sma_20 REAL,
        sma_50 REAL,
        sma_200 REAL,
        rsi_14 REAL,
        above_sma_20 BOOLEAN,
        above_sma_50 BOOLEAN,
        above_sma_200 BOOLEAN,
        
        -- Move classification
        is_big_move BOOLEAN,
        move_direction TEXT,
        move_size TEXT,
        gap_pct REAL,
        
        -- Forward returns (nullable, filled later)
        forward_1d REAL,
        forward_3d REAL,
        forward_5d REAL,
        forward_10d REAL,
        forward_20d REAL,
        
        -- Metadata
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(ticker, date)
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_date ON daily_records(ticker, date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON daily_records(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector ON daily_records(sector)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_forward_10d ON daily_records(forward_10d)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_volume_ratio ON daily_records(volume_ratio)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_big_moves ON daily_records(is_big_move)')
    
    # Move investigations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investigations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date DATE NOT NULL,
        move_pct REAL NOT NULL,
        investigation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Findings
        catalyst_type TEXT,
        catalyst_confidence REAL,
        news_found TEXT,
        sec_filings TEXT,
        analyst_actions TEXT,
        sector_correlation BOOLEAN,
        volume_confirmed BOOLEAN,
        
        -- Outcome tracking
        day_2_result REAL,
        day_5_result REAL,
        pattern_repeated BOOLEAN,
        
        -- Notes
        notes TEXT,
        
        UNIQUE(ticker, date)
    )
    ''')
    
    # Learning patterns table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learned_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        sector TEXT,
        pattern_type TEXT NOT NULL,
        pattern_name TEXT NOT NULL,
        
        -- Pattern stats
        occurrences INTEGER DEFAULT 1,
        win_rate REAL,
        avg_return REAL,
        avg_duration_days REAL,
        
        -- Context
        typical_volume_ratio REAL,
        typical_catalyst TEXT,
        
        last_seen DATE,
        confidence_score REAL,
        
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(ticker, pattern_type, pattern_name)
    )
    ''')
    
    # Alerts log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        priority TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        ticker TEXT,
        message TEXT NOT NULL,
        data TEXT,
        action_taken TEXT,
        dismissed BOOLEAN DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {DB_PATH}")

def insert_daily_record(conn, record):
    """Insert or replace a daily record"""
    
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO daily_records (
            ticker, date, sector,
            open, high, low, close, prev_close,
            daily_return_pct, intraday_range_pct, close_vs_high_pct,
            volume, avg_volume_20d, volume_ratio,
            dist_52w_high_pct, dist_52w_low_pct,
            return_5d, return_20d, return_60d,
            consecutive_green, consecutive_red
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['ticker'], record['date'], record['sector'],
            record['open'], record['high'], record['low'], record['close'], record['prev_close'],
            record['daily_return_pct'], record['intraday_range_pct'], record['close_vs_high_pct'],
            record['volume'], record['avg_volume_20d'], record['volume_ratio'],
            record['dist_52w_high_pct'], record['dist_52w_low_pct'],
            record['return_5d'], record['return_20d'], record['return_60d'],
            record['consecutive_green'], record['consecutive_red']
        ))
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error inserting {record['ticker']}: {e}")
        return False

def update_forward_returns(conn, ticker, date, forward_1d=None, forward_3d=None, forward_5d=None, forward_10d=None, forward_20d=None):
    """Update forward returns for a specific record"""
    
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if forward_1d is not None:
        updates.append("forward_1d = ?")
        values.append(forward_1d)
    if forward_3d is not None:
        updates.append("forward_3d = ?")
        values.append(forward_3d)
    if forward_5d is not None:
        updates.append("forward_5d = ?")
        values.append(forward_5d)
    if forward_10d is not None:
        updates.append("forward_10d = ?")
        values.append(forward_10d)
    if forward_20d is not None:
        updates.append("forward_20d = ?")
        values.append(forward_20d)
    
    if not updates:
        return False
    
    values.extend([ticker, date])
    
    cursor.execute(f'''
    UPDATE daily_records
    SET {', '.join(updates)}
    WHERE ticker = ? AND date = ?
    ''', values)
    
    return cursor.rowcount > 0

def get_records_needing_forward_returns(conn, days_ago, forward_field):
    """Get records that need forward return calculations"""
    
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT ticker, date, close
    FROM daily_records
    WHERE {forward_field} IS NULL
    AND date <= date('now', '-{days_ago} days')
    ORDER BY date DESC
    ''')
    
    return cursor.fetchall()

def get_winners(conn, threshold, timeframe):
    """Get all records where forward return exceeded threshold"""
    
    forward_field = f'forward_{timeframe}d'
    
    cursor = conn.cursor()
    
    cursor.execute(f'''
    SELECT *
    FROM daily_records
    WHERE {forward_field} >= ?
    ORDER BY {forward_field} DESC
    ''', (threshold,))
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    return [dict(zip(columns, row)) for row in rows]

def get_latest_records(conn, limit=100):
    """Get most recent records"""
    
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT *
    FROM daily_records
    ORDER BY date DESC
    LIMIT ?
    ''', (limit,))
    
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    return [dict(zip(columns, row)) for row in rows]

def get_sector_performance(conn, date):
    """Get sector average performance for a specific date"""
    
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT sector, 
           AVG(daily_return_pct) as avg_return,
           AVG(volume_ratio) as avg_volume_ratio,
           COUNT(*) as count
    FROM daily_records
    WHERE date = ?
    GROUP BY sector
    ORDER BY avg_return DESC
    ''', (date,))
    
    return cursor.fetchall()

if __name__ == '__main__':
    init_database()
