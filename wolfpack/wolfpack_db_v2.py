#!/usr/bin/env python3
"""
Wolf Pack V2 - Database Schema
Focus on REAL value: real-time moves, catalysts, YOUR decisions, outcomes
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

# Database path
DATA_DIR = Path('./data')
DATA_DIR.mkdir(exist_ok=True)
DB_PATH_V2 = str(DATA_DIR / 'wolfpack_v2.db')

def init_v2_database():
    """Initialize V2 database with value-focused schema"""
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    # =============================================================================
    # REAL-TIME MOVES - Can't recreate this later
    # =============================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realtime_moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        sector TEXT,
        detection_time TEXT NOT NULL,
        price REAL,
        prev_close REAL,
        move_pct REAL,
        volume INTEGER,
        alert_sent INTEGER DEFAULT 1,
        investigation_started TEXT
    )
    ''')
    
    # =============================================================================
    # CATALYST ARCHIVE - News and filings get buried
    # =============================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS catalyst_archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        move_id INTEGER,
        move_timestamp TEXT,
        move_pct REAL,
        
        catalyst_type TEXT,
        catalyst_confidence REAL,
        
        news_headline TEXT,
        news_summary TEXT,
        news_url TEXT,
        news_source TEXT,
        news_timestamp TEXT,
        
        sec_filing_type TEXT,
        sec_filing_date TEXT,
        sec_filing_url TEXT,
        
        time_diff_minutes REAL,
        
        archived_at TEXT DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (move_id) REFERENCES realtime_moves(id)
    )
    ''')
    
    # =============================================================================
    # YOUR DECISIONS - Only you know what you did
    # =============================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        ticker TEXT NOT NULL,
        move_id INTEGER,
        
        action TEXT NOT NULL,
        price REAL,
        quantity INTEGER,
        reasoning TEXT,
        
        catalyst_link INTEGER,
        
        outcome_1d REAL,
        outcome_3d REAL,
        outcome_5d REAL,
        outcome_10d REAL,
        
        FOREIGN KEY (move_id) REFERENCES realtime_moves(id),
        FOREIGN KEY (catalyst_link) REFERENCES catalyst_archive(id)
    )
    ''')
    
    # =============================================================================
    # DAY 2 TRACKER - Did your thesis play out?
    # =============================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS day2_tracker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        day1_date TEXT NOT NULL,
        day1_move_pct REAL,
        
        user_acted INTEGER DEFAULT 0,
        user_action TEXT,
        decision_id INTEGER,
        
        day2_result REAL,
        day3_result REAL,
        day5_result REAL,
        
        pattern_validated INTEGER,
        validation_notes TEXT,
        
        FOREIGN KEY (decision_id) REFERENCES user_decisions(id)
    )
    ''')
    
    # =============================================================================
    # YOUR PATTERNS - Learn from YOUR actual trades
    # =============================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learned_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_name TEXT NOT NULL UNIQUE,
        pattern_conditions TEXT,
        
        your_win_rate REAL,
        your_avg_return REAL,
        your_sample_size INTEGER DEFAULT 0,
        
        confidence_level REAL,
        last_validated TEXT,
        
        notes TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ V2 Database initialized: {DB_PATH_V2}\n")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def log_realtime_move(move_info):
    """Log a detected move in real-time"""
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO realtime_moves (
            ticker, sector, detection_time, price, prev_close,
            move_pct, volume, investigation_started
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            move_info['ticker'],
            move_info['sector'],
            move_info['timestamp'].isoformat(),
            move_info['price'],
            move_info['prev_close'],
            move_info['move_pct'],
            move_info['volume'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        move_id = cursor.lastrowid
        return move_id
        
    except Exception as e:
        print(f"  ❌ Error logging move: {e}")
        return None
    
    finally:
        conn.close()

def store_catalyst(catalyst_info):
    """Store catalyst information permanently"""
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    try:
        # Get the most recent news and filing
        news = catalyst_info['news_items'][0] if catalyst_info['news_items'] else {}
        filing = catalyst_info['filings'][0] if catalyst_info['filings'] else {}
        
        cursor.execute('''
        INSERT INTO catalyst_archive (
            ticker, move_timestamp, move_pct,
            catalyst_type, catalyst_confidence,
            news_headline, news_summary, news_url, news_source, news_timestamp,
            sec_filing_type, sec_filing_date, sec_filing_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            catalyst_info['ticker'],
            catalyst_info['move_timestamp'].isoformat(),
            catalyst_info['move_pct'],
            catalyst_info['catalyst_type'],
            catalyst_info['confidence'],
            news.get('headline', ''),
            news.get('summary', ''),
            news.get('url', ''),
            news.get('source', ''),
            news.get('timestamp').isoformat() if news.get('timestamp') else None,
            filing.get('form_type', ''),
            filing.get('filing_date', ''),
            filing.get('url', '')
        ))
        
        conn.commit()
        
    except Exception as e:
        print(f"  ❌ Error storing catalyst: {e}")
    
    finally:
        conn.close()

def log_user_decision(decision):
    """Log what the user decided to do"""
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO user_decisions (
            timestamp, ticker, action, price, quantity, reasoning
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            decision['ticker'],
            decision['action'],
            decision.get('price'),
            decision.get('quantity'),
            decision.get('reasoning', '')
        ))
        
        conn.commit()
        decision_id = cursor.lastrowid
        return decision_id
        
    except Exception as e:
        print(f"  ❌ Error logging decision: {e}")
        return None
    
    finally:
        conn.close()

def get_recent_moves(hours=24):
    """Get moves from last N hours"""
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT ticker, detection_time, move_pct, price
    FROM realtime_moves
    WHERE detection_time >= datetime('now', '-' || ? || ' hours')
    ORDER BY ABS(move_pct) DESC
    ''', (hours,))
    
    moves = cursor.fetchall()
    conn.close()
    
    return moves

if __name__ == '__main__':
    print("\n🗄️  Initializing Wolf Pack V2 Database\n")
    init_v2_database()
    print("✅ Ready for real-time monitoring\n")
