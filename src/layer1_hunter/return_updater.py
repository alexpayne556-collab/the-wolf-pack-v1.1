#!/usr/bin/env python3
"""
Return calculator for tracked events
Calculates 1d, 3d, 5d, 10d returns after events
Run daily to update pending returns
"""

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import time

DB_PATH = 'wolf_pack_events.db'

def get_pending_events(conn):
    """Get events that need return calculations"""
    
    cursor = conn.cursor()
    
    # Get events where returns are NULL and enough days have passed
    cursor.execute('''
    SELECT id, ticker, event_date, price_at_event
    FROM events
    WHERE (return_1d IS NULL OR return_3d IS NULL OR return_5d IS NULL OR return_10d IS NULL)
    AND event_date < ?
    ORDER BY event_date DESC
    ''', (datetime.now() - timedelta(days=1),))
    
    return cursor.fetchall()

def calculate_returns(ticker, event_date, event_price):
    """Calculate returns for 1d, 3d, 5d, 10d after event"""
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get historical data starting from event date
        start_date = event_date - timedelta(days=1)
        end_date = datetime.now()
        
        hist = stock.history(start=start_date, end=end_date)
        
        if len(hist) < 2:
            return None
        
        # Find event date in history
        event_idx = None
        for i, date in enumerate(hist.index):
            if date.date() >= event_date.date():
                event_idx = i
                break
        
        if event_idx is None:
            return None
        
        returns = {}
        
        # Calculate returns for different periods
        for days, label in [(1, 'return_1d'), (3, 'return_3d'), (5, 'return_5d'), (10, 'return_10d')]:
            target_idx = event_idx + days
            if target_idx < len(hist):
                future_price = hist['Close'].iloc[target_idx]
                returns[label] = ((future_price - event_price) / event_price) * 100
            else:
                returns[label] = None
        
        return returns
    
    except Exception as e:
        print(f"  ⚠️  Error calculating returns for {ticker}: {e}")
        return None

def update_event_returns(conn, event_id, returns):
    """Update returns in database"""
    
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE events
        SET return_1d = ?, return_3d = ?, return_5d = ?, return_10d = ?
        WHERE id = ?
        ''', (
            returns.get('return_1d'),
            returns.get('return_3d'),
            returns.get('return_5d'),
            returns.get('return_10d'),
            event_id
        ))
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f"  ❌ Error updating returns: {e}")
        return False

def update_returns():
    """Main return update function"""
    
    print("\n" + "📊"*30)
    print("WOLF PACK RETURN UPDATER")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    pending = get_pending_events(conn)
    
    if not pending:
        print("✅ No pending events to update\n")
        conn.close()
        return
    
    print(f"Found {len(pending)} events to update\n")
    
    updated = 0
    
    for event_id, ticker, event_date_str, event_price in pending:
        event_date = datetime.fromisoformat(event_date_str)
        days_since = (datetime.now() - event_date).days
        
        # Calculate returns
        returns = calculate_returns(ticker, event_date, event_price)
        
        if returns:
            # Update database
            if update_event_returns(conn, event_id, returns):
                updated += 1
                
                # Display update
                ret_str = ""
                if returns.get('return_1d') is not None:
                    ret_str += f"1d:{returns['return_1d']:+.1f}% "
                if returns.get('return_5d') is not None:
                    ret_str += f"5d:{returns['return_5d']:+.1f}% "
                if returns.get('return_10d') is not None:
                    ret_str += f"10d:{returns['return_10d']:+.1f}%"
                
                print(f"✅ {ticker:6} | {days_since:2}d ago | {ret_str}")
        
        # Rate limit
        time.sleep(0.5)
    
    conn.close()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Pending events: {len(pending)}")
    print(f"   Updated: {updated}")
    print(f"\n🐺 Update complete - LLHR\n")

if __name__ == '__main__':
    update_returns()
