# 🐺 FENRIR V2 - FAILED TRADES LOGGER
# Track opportunities you DIDN'T take and why

from datetime import datetime
from typing import Optional
import database

def log_missed_opportunity(ticker: str, price: float, reason: str, 
                          move_after: Optional[float] = None):
    """
    Log a trade you considered but didn't take
    
    Args:
        ticker: Stock symbol
        price: Price when you considered it
        reason: Why you didn't take it
        move_after: How much it moved after (if tracking outcome)
    """
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Add to trades table with special "MISSED" action
    cursor.execute('''
        INSERT INTO trades (
            timestamp, ticker, action, shares, price, 
            thesis, outcome, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        ticker,
        'MISSED',
        0,  # No shares bought
        price,
        reason,
        f"Moved {move_after:+.1f}%" if move_after else None,
        "Failed to execute"
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Logged missed opportunity: {ticker} @ ${price:.2f}")
    print(f"   Reason: {reason}")


def log_hesitation(ticker: str, price: float, what_stopped_you: str):
    """Track when you hesitated on a setup"""
    
    log_missed_opportunity(
        ticker=ticker,
        price=price,
        reason=f"HESITATED: {what_stopped_you}",
    )


def log_fomo_avoid(ticker: str, price: float, already_moved_pct: float):
    """Track when you avoided chasing"""
    
    log_missed_opportunity(
        ticker=ticker,
        price=price,
        reason=f"AVOIDED FOMO: Already up {already_moved_pct:.1f}%",
    )


def log_no_day_trades(ticker: str, price: float):
    """Track when PDT limit stopped you"""
    
    log_missed_opportunity(
        ticker=ticker,
        price=price,
        reason="PDT RESTRICTED: No day trades left",
    )


def get_missed_trades(days: int = 30) -> list:
    """Get all missed opportunities from last N days"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ticker, price, thesis, outcome, timestamp
        FROM trades
        WHERE action = 'MISSED'
        AND DATE(timestamp) >= DATE('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
    ''', (days,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [{'ticker': r[0], 'price': r[1], 'reason': r[2], 
             'outcome': r[3], 'timestamp': r[4]} for r in rows]


def analyze_missed_trades() -> str:
    """Analyze what you're missing and why"""
    
    missed = get_missed_trades(days=30)
    
    if not missed:
        return "\n✅ No missed trades logged\n"
    
    # Group by reason
    reasons = {}
    for trade in missed:
        reason = trade['reason'].split(':')[0]  # Get prefix like "HESITATED"
        reasons[reason] = reasons.get(reason, 0) + 1
    
    output = "\n" + "=" * 60 + "\n"
    output += f"🐺 MISSED OPPORTUNITIES - Last 30 Days\n"
    output += "=" * 60 + "\n\n"
    
    output += f"Total missed: {len(missed)}\n\n"
    
    output += "WHY YOU DIDN'T TRADE:\n"
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        output += f"  {reason}: {count}x\n"
    
    output += "\n"
    output += "RECENT MISSES:\n"
    for trade in missed[:5]:
        output += f"  {trade['timestamp'][:10]} - {trade['ticker']} @ ${trade['price']:.2f}\n"
        output += f"    {trade['reason']}\n"
        if trade['outcome']:
            output += f"    Result: {trade['outcome']}\n"
    
    output += "\n" + "=" * 60 + "\n"
    
    return output


# Test
if __name__ == '__main__':
    print("\n🐺 Testing Failed Trades Logger\n")
    
    # Example: Log a missed opportunity
    print("Example 1: Hesitation")
    log_hesitation('RGTI', 7.50, "Volume looked fake")
    
    print("\nExample 2: FOMO avoid")
    log_fomo_avoid('SMCI', 30.00, already_moved_pct=15.2)
    
    print("\nExample 3: PDT restricted")
    log_no_day_trades('ASTS', 115.00)
    
    print("\nAnalyzing missed trades...")
    print(analyze_missed_trades())
