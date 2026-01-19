# 🐺 FENRIR V2 - STATE TRACKER
# Track stock states and adapt check frequency

from datetime import datetime, timedelta
from typing import Dict, Optional
import database
import config

def get_check_frequency(status: str, we_own: bool, change_pct: float) -> int:
    """
    Returns minutes between checks based on stock state
    
    Priority: POSITIONS > MOVERS > WATCHLIST
    """
    
    if we_own:
        if change_pct <= -5:
            return 2    # BLEEDING - check every 2 min (URGENT)
        elif change_pct >= 5:
            return 5    # Running position - every 5 min
        else:
            return 15   # Normal position - every 15 min
    else:
        if abs(change_pct) >= 10:
            return 15   # Big mover - watch closely
        elif abs(change_pct) >= 5:
            return 30   # Mover - check often
        else:
            return 60   # Watchlist - hourly


def update_stock_state(ticker: str, data: Dict):
    """Update stock state in database"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Check if we own it
    we_own = ticker in config.HOLDINGS
    our_shares = config.HOLDINGS[ticker]['shares'] if we_own else 0
    our_avg_cost = config.HOLDINGS[ticker]['avg_cost'] if we_own else 0
    
    # Calculate P/L if we own it
    our_pnl_dollars = 0
    our_pnl_percent = 0
    if we_own:
        our_pnl_dollars = (data['price'] - our_avg_cost) * our_shares
        our_pnl_percent = ((data['price'] / our_avg_cost) - 1) * 100
    
    # Determine status
    change_pct = data['change_pct']
    status = determine_status(ticker, change_pct, we_own)
    
    # Calculate check frequency
    check_freq = get_check_frequency(status, we_own, change_pct)
    next_check = datetime.now() + timedelta(minutes=check_freq)
    
    # Update or insert
    cursor.execute('''
        INSERT OR REPLACE INTO stock_state (
            ticker, status, current_price, prev_close, high_of_day, low_of_day,
            volume_today, volume_avg, volume_ratio,
            we_own, our_shares, our_avg_cost, our_pnl_dollars, our_pnl_percent,
            check_frequency, last_check, next_check, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticker, status, data['price'], data.get('prev_close'), 
        data.get('high'), data.get('low'),
        data.get('volume'), data.get('avg_volume'), data.get('volume_ratio'),
        1 if we_own else 0, our_shares, our_avg_cost, our_pnl_dollars, our_pnl_percent,
        check_freq, datetime.now().isoformat(), next_check.isoformat(), datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()


def determine_status(ticker: str, change_pct: float, we_own: bool) -> str:
    """Determine stock status based on movement"""
    
    if we_own:
        if change_pct <= -5:
            return 'BLEEDING_POSITION'
        elif change_pct >= 5:
            return 'RUNNING_POSITION'
        else:
            return 'position'
    else:
        if abs(change_pct) >= 10:
            return 'big_mover'
        elif abs(change_pct) >= 5:
            return 'mover'
        else:
            return 'watching'


def get_stock_state(ticker: str) -> Optional[Dict]:
    """
    Get current state for a ticker from database
    Returns None if not tracked
    """
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ticker, status, current_price, prev_close, high_of_day, low_of_day,
               volume_today, volume_avg, volume_ratio,
               we_own, our_shares, our_avg_cost, our_pnl_dollars, our_pnl_percent,
               check_frequency, last_check, next_check, updated_at
        FROM stock_state
        WHERE ticker = ?
    ''', (ticker,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'ticker': row[0],
        'status': row[1],
        'current_price': row[2],
        'prev_close': row[3],
        'high_of_day': row[4],
        'low_of_day': row[5],
        'volume_today': row[6],
        'volume_avg': row[7],
        'volume_ratio': row[8],
        'we_own': bool(row[9]),
        'our_shares': row[10],
        'our_avg_cost': row[11],
        'our_pnl_dollars': row[12],
        'our_pnl_percent': row[13],
        'check_frequency': row[14],
        'last_check': row[15],
        'next_check': row[16],
        'updated_at': row[17]
    }
    
    if we_own:
        if change_pct <= -5:
            return 'BLEEDING_POSITION'
        elif change_pct >= 5:
            return 'RUNNING_POSITION'
        else:
            return 'watching'  # Normal position state
    else:
        if abs(change_pct) >= 10:
            return 'running'
        elif abs(change_pct) >= 5:
            return 'mover'
        else:
            return 'watching'


def get_stocks_due_for_check() -> list:
    """Get stocks that need checking now"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        SELECT ticker, status, we_own, check_frequency, last_check
        FROM stock_state
        WHERE next_check <= ?
        ORDER BY we_own DESC, check_frequency ASC
    ''', (now,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{'ticker': r[0], 'status': r[1], 'we_own': bool(r[2]), 
             'check_frequency': r[3], 'last_check': r[4]} for r in rows]


def detect_changes(ticker: str, new_data: Dict) -> Dict:
    """Compare new data to previous state and detect significant changes"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM stock_state WHERE ticker = ?', (ticker,))
    row = cursor.fetchone()
    conn.close()
    
    changes = {'significant': False, 'alerts': []}
    
    if not row:
        return changes
    
    old_price = row[7]  # current_price column
    old_status = row[1]  # status column
    
    new_price = new_data['price']
    new_status = determine_status(ticker, new_data['change_pct'], ticker in config.HOLDINGS)
    
    # Price change
    if old_price:
        price_change = ((new_price - old_price) / old_price) * 100
        if abs(price_change) > 2:
            changes['significant'] = True
            changes['alerts'].append(f"Price moved {price_change:+.1f}% since last check")
    
    # Status change
    if old_status != new_status:
        changes['significant'] = True
        changes['alerts'].append(f"Status changed: {old_status} → {new_status}")
    
    # New high/low of day
    old_hod = row[5]
    old_lod = row[6]
    if old_hod and new_data.get('high') and new_data['high'] > old_hod:
        changes['significant'] = True
        changes['alerts'].append(f"New HOD: ${new_data['high']:.2f}")
    if old_lod and new_data.get('low') and new_data['low'] < old_lod:
        changes['significant'] = True
        changes['alerts'].append(f"New LOD: ${new_data['low']:.2f}")
    
    return changes


def log_intraday_tick(ticker: str, data: Dict):
    """Log an intraday price tick"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO intraday_ticks (ticker, timestamp, price, volume, high_so_far, low_so_far)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        ticker, datetime.now().isoformat(), data['price'], data.get('volume'),
        data.get('high'), data.get('low')
    ))
    
    conn.commit()
    conn.close()
