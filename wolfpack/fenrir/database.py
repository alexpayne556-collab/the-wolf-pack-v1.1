# 🐺 FENRIR V2 - DATABASE
# SQLite database for logging trades, alerts, and patterns

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from config import DB_PATH


def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)


def init_database():
    """Initialize all database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Alerts table - what Fenrir flagged
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ticker TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            price REAL,
            change_pct REAL,
            volume_ratio REAL,
            catalyst TEXT,
            fenrir_opinion TEXT,
            user_action TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Trades table - what you actually did
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
    
    # Patterns table - what we've learned
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_name TEXT NOT NULL UNIQUE,
            description TEXT,
            total_trades INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            win_rate REAL,
            avg_win_pct REAL,
            avg_loss_pct REAL,
            expected_value REAL,
            last_updated TEXT
        )
    ''')
    
    # Catalysts table - track what catalysts work
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS catalysts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ticker TEXT NOT NULL,
            catalyst_type TEXT NOT NULL,
            headline TEXT,
            source TEXT,
            move_pct REAL,
            day2_pct REAL,
            day5_pct REAL,
            worked INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Stock state table - adaptive tracking
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
    
    # Intraday ticks - for tracking within-day movement
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
    
    # Daily summary - end of day snapshot
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
    print("Database initialized.")


# =============================================================================
# ALERTS
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
# TRADES
# =============================================================================

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
# PATTERNS
# =============================================================================

def update_pattern(pattern_name: str, won: bool, gain_pct: float):
    """Update pattern statistics after a trade"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current stats
    cursor.execute('SELECT * FROM patterns WHERE pattern_name = ?', (pattern_name,))
    row = cursor.fetchone()
    
    if row:
        # Update existing
        cursor.execute('''
            UPDATE patterns SET
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
            INSERT INTO patterns (pattern_name, total_trades, wins, losses, last_updated)
            VALUES (?, 1, ?, ?, ?)
        ''', (
            pattern_name,
            1 if won else 0,
            0 if won else 1,
            datetime.now().isoformat()
        ))
    
    # Recalculate win rate
    cursor.execute('''
        UPDATE patterns SET 
            win_rate = CAST(wins AS REAL) / total_trades
        WHERE pattern_name = ?
    ''', (pattern_name,))
    
    conn.commit()
    conn.close()


def get_all_patterns() -> List[Dict]:
    """Get all patterns and their stats"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patterns ORDER BY win_rate DESC')
    
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]


# =============================================================================
# CATALYSTS
# =============================================================================

def log_catalyst(ticker: str, catalyst_type: str, headline: str,
                 move_pct: float, source: str = None) -> int:
    """Log a catalyst and its immediate move"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO catalysts (timestamp, ticker, catalyst_type, headline, source, move_pct)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        ticker,
        catalyst_type,
        headline,
        source,
        move_pct
    ))
    
    catalyst_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return catalyst_id


def get_catalyst_stats(catalyst_type: str = None) -> Dict:
    """Get statistics on catalyst performance"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if catalyst_type:
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(move_pct) as avg_move,
                AVG(day2_pct) as avg_day2,
                SUM(CASE WHEN day2_pct > 0 THEN 1 ELSE 0 END) as day2_green
            FROM catalysts WHERE catalyst_type = ?
        ''', (catalyst_type,))
    else:
        cursor.execute('''
            SELECT 
                catalyst_type,
                COUNT(*) as total,
                AVG(move_pct) as avg_move,
                AVG(day2_pct) as avg_day2
            FROM catalysts GROUP BY catalyst_type
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows


# =============================================================================
# INIT & TEST
# =============================================================================
if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    
    # Test logging a trade
    print("\nLogging test trade...")
    trade_id = log_trade(
        ticker="IBRX",
        action="BUY",
        shares=20,
        price=4.00,
        account="robinhood",
        thesis="Cancer drug revenue beat",
        fenrir_said="This looks like a buy, boss"
    )
    print(f"Trade logged with ID: {trade_id}")
    
    # Test logging an alert
    print("\nLogging test alert...")
    alert_id = log_alert(
        ticker="IBRX",
        alert_type="BIG_MOVER",
        price=4.00,
        change_pct=30.0,
        catalyst="Q4 revenue beat",
        fenrir_opinion="Running on real news"
    )
    print(f"Alert logged with ID: {alert_id}")
    
    print("\nDatabase ready! 🐺")
