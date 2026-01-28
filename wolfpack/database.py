#!/usr/bin/env python3
"""
🐺 UNIFIED WOLF PACK DATABASE
Consolidation of wolfpack_db.py + wolfpack_db_v2.py + fenrir/database.py

Single source of truth for:
- Daily historical records (price, volume, technicals)
- Real-time moves and investigations
- Catalysts (news, SEC filings, events)
- User decisions and trade journal
- Patterns and learning
- Alerts and monitoring
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from config import DB_PATH

# Ensure data directory exists
DATA_DIR = Path('./data')
DATA_DIR.mkdir(exist_ok=True)

def get_connection():
    """Get database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_database():
    """Initialize unified database with all tables"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # =========================================================================
    # HISTORICAL DAILY RECORDS (from wolfpack_db.py)
    # =========================================================================
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
    
    # Create indexes for daily_records
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_date ON daily_records(ticker, date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON daily_records(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sector ON daily_records(sector)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_forward_10d ON daily_records(forward_10d)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_volume_ratio ON daily_records(volume_ratio)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_big_moves ON daily_records(is_big_move)')
    
    # =========================================================================
    # REAL-TIME MOVES (from wolfpack_db_v2.py)
    # =========================================================================
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
    
    # =========================================================================
    # CATALYST ARCHIVE (from wolfpack_db_v2.py + fenrir)
    # =========================================================================
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
    
    # =========================================================================
    # USER DECISIONS & TRADE JOURNAL (from wolfpack_db_v2.py + fenrir)
    # =========================================================================
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
    
    # Enhanced trades table (from fenrir)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        ticker TEXT NOT NULL,
        action TEXT NOT NULL,
        shares REAL NOT NULL,
        price REAL NOT NULL,
        account TEXT,
        thesis TEXT,
        fenrir_said TEXT,
        day2_pct REAL,
        day5_pct REAL,
        outcome TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # =========================================================================
    # INVESTIGATIONS (from wolfpack_db.py)
    # =========================================================================
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
    
    # =========================================================================
    # PATTERNS & LEARNING (unified from all three)
    # =========================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS learned_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        sector TEXT,
        pattern_type TEXT,
        pattern_name TEXT NOT NULL,
        pattern_conditions TEXT,
        description TEXT,
        
        -- Pattern stats
        occurrences INTEGER DEFAULT 1,
        total_trades INTEGER DEFAULT 0,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        win_rate REAL,
        avg_return REAL,
        avg_win_pct REAL,
        avg_loss_pct REAL,
        avg_duration_days REAL,
        expected_value REAL,
        
        -- Context
        typical_volume_ratio REAL,
        typical_catalyst TEXT,
        
        -- Learning metadata
        your_sample_size INTEGER DEFAULT 0,
        your_win_rate REAL,
        your_avg_return REAL,
        confidence_level REAL,
        confidence_score REAL,
        last_validated TEXT,
        last_seen DATE,
        last_updated TEXT,
        notes TEXT,
        
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(pattern_name)
    )
    ''')
    
    # =========================================================================
    # ALERTS (unified from wolfpack_db.py + fenrir)
    # =========================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        priority TEXT,
        alert_type TEXT NOT NULL,
        ticker TEXT,
        price REAL,
        change_pct REAL,
        volume_ratio REAL,
        message TEXT,
        catalyst TEXT,
        fenrir_opinion TEXT,
        user_action TEXT,
        data TEXT,
        action_taken TEXT,
        dismissed BOOLEAN DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # =========================================================================
    # DAY 2 TRACKER (from wolfpack_db_v2.py)
    # =========================================================================
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
    
    # =========================================================================
    # STOCK STATE (from fenrir)
    # =========================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_state (
        ticker TEXT PRIMARY KEY,
        status TEXT,
        days_running INTEGER DEFAULT 0,
        run_start_price REAL,
        run_start_date TEXT,
        high_of_day REAL,
        low_of_day REAL,
        current_price REAL,
        prev_close REAL,
        volume_today INTEGER,
        volume_avg INTEGER,
        volume_ratio REAL,
        volume_trend TEXT,
        last_catalyst TEXT,
        catalyst_date TEXT,
        we_own INTEGER DEFAULT 0,
        our_shares REAL,
        our_avg_cost REAL,
        our_pnl_dollars REAL,
        our_pnl_percent REAL,
        check_frequency INTEGER,
        last_check TEXT,
        next_check TEXT,
        updated_at TEXT
    )
    ''')
    
    # =========================================================================
    # INTRADAY TRACKING (from fenrir)
    # =========================================================================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS intraday_ticks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        timestamp TEXT,
        price REAL,
        volume INTEGER,
        high_so_far REAL,
        low_so_far REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        ticker TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        change_pct REAL,
        catalyst TEXT,
        notes TEXT,
        UNIQUE(date, ticker)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Unified database initialized: {DB_PATH}")


# =============================================================================
# DAILY RECORDS FUNCTIONS
# =============================================================================

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


# =============================================================================
# REAL-TIME MOVES FUNCTIONS
# =============================================================================

def log_realtime_move(move_info):
    """Log a detected move in real-time"""
    
    conn = get_connection()
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


def get_recent_moves(hours=24):
    """Get moves from last N hours"""
    
    conn = get_connection()
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


# =============================================================================
# CATALYST FUNCTIONS
# =============================================================================

def store_catalyst(catalyst_info):
    """Store catalyst information permanently"""
    
    conn = get_connection()
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


def log_catalyst(ticker: str, catalyst_type: str, headline: str,
                 move_pct: float, source: str = None) -> int:
    """Log a catalyst and its immediate move"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO catalyst_archive (
            ticker, move_timestamp, catalyst_type, news_headline, 
            news_source, move_pct
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        ticker,
        datetime.now().isoformat(),
        catalyst_type,
        headline,
        source,
        move_pct
    ))
    
    catalyst_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return catalyst_id


# =============================================================================
# USER DECISIONS & TRADES FUNCTIONS
# =============================================================================

def log_user_decision(decision):
    """Log what the user decided to do"""
    
    conn = get_connection()
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


def log_trade(ticker: str, action: str, shares: float, price: float,
              account: str = None, thesis: str = None, 
              fenrir_said: str = None, notes: str = None) -> int:
    """Log a trade you made"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trades (timestamp, ticker, action, shares, price, 
                           account, thesis, fenrir_said, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        ticker,
        action.upper(),
        shares,
        price,
        account,
        thesis,
        fenrir_said,
        notes
    ))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return trade_id


def update_trade_outcome(trade_id: int, day2_pct: float = None, 
                         day5_pct: float = None, outcome: str = None):
    """Update trade with outcome data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if day2_pct is not None:
        updates.append("day2_pct = ?")
        values.append(day2_pct)
    if day5_pct is not None:
        updates.append("day5_pct = ?")
        values.append(day5_pct)
    if outcome is not None:
        updates.append("outcome = ?")
        values.append(outcome)
    
    if updates:
        values.append(trade_id)
        cursor.execute(f'''
            UPDATE trades SET {', '.join(updates)} WHERE id = ?
        ''', values)
        
        conn.commit()
    
    conn.close()


def get_all_trades() -> List[Dict]:
    """Get all trades"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]


def get_trades_by_ticker(ticker: str) -> List[Dict]:
    """Get trades for a specific ticker"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM trades WHERE ticker = ? ORDER BY timestamp DESC
    ''', (ticker,))
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]


# =============================================================================
# ALERTS FUNCTIONS
# =============================================================================

def log_alert(ticker: str, alert_type: str, price: float, change_pct: float,
              volume_ratio: float = None, catalyst: str = None, 
              fenrir_opinion: str = None) -> int:
    """Log an alert from Fenrir"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alerts (timestamp, ticker, alert_type, price, change_pct, 
                           volume_ratio, catalyst, fenrir_opinion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        ticker,
        alert_type,
        price,
        change_pct,
        volume_ratio,
        catalyst,
        fenrir_opinion
    ))
    
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return alert_id


def update_alert_action(alert_id: int, user_action: str):
    """Update what the user did with an alert"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE alerts SET user_action = ? WHERE id = ?
    ''', (user_action, alert_id))
    
    conn.commit()
    conn.close()


def get_recent_alerts(count: int = 20) -> List[Dict]:
    """Get recent alerts"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?
    ''', (count,))
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]


# =============================================================================
# PATTERNS FUNCTIONS
# =============================================================================

def update_pattern(pattern_name: str, won: bool, gain_pct: float):
    """Update pattern statistics after a trade"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current stats
    cursor.execute('SELECT * FROM learned_patterns WHERE pattern_name = ?', (pattern_name,))
    row = cursor.fetchone()
    
    if row:
        # Update existing
        cursor.execute('''
            UPDATE learned_patterns SET
                total_trades = total_trades + 1,
                wins = wins + ?,
                losses = losses + ?,
                last_updated = ?
            WHERE pattern_name = ?
        ''', (
            1 if won else 0,
            0 if won else 1,
            datetime.now().isoformat(),
            pattern_name
        ))
    else:
        # Insert new
        cursor.execute('''
            INSERT INTO learned_patterns (pattern_name, total_trades, wins, losses, last_updated)
            VALUES (?, 1, ?, ?, ?)
        ''', (
            pattern_name,
            1 if won else 0,
            0 if won else 1,
            datetime.now().isoformat()
        ))
    
    # Recalculate win rate
    cursor.execute('''
        UPDATE learned_patterns SET 
            win_rate = CAST(wins AS REAL) / total_trades
        WHERE pattern_name = ?
    ''', (pattern_name,))
    
    conn.commit()
    conn.close()


def get_all_patterns() -> List[Dict]:
    """Get all patterns and their stats"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM learned_patterns ORDER BY win_rate DESC')
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]


# =============================================================================
# INITIALIZATION
# =============================================================================

if __name__ == '__main__':
    print("\n🐺 Initializing Unified Wolf Pack Database\n")
    init_database()
    print("\n✅ Database ready - all systems consolidated!\n")
