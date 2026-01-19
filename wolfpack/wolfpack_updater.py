#!/usr/bin/env python3
"""
Wolf Pack Forward Return Updater
Calculates actual returns X days after each record
Run BEFORE recorder each day
"""

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

from config import DB_PATH, RATE_LIMIT_DELAY
from wolfpack_db import get_records_needing_forward_returns, update_forward_returns

def calculate_forward_return(ticker, record_date, record_price, days_forward):
    """Calculate actual return X days after record date"""
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get data from record date forward
        start_date = datetime.strptime(record_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=days_forward + 5)  # Extra buffer
        
        hist = stock.history(start=start_date, end=end_date)
        
        if len(hist) <= days_forward:
            return None  # Not enough data yet
        
        future_price = hist['Close'].iloc[days_forward]
        forward_return = ((future_price - record_price) / record_price) * 100
        
        return forward_return
    
    except Exception as e:
        return None

def update_all_forward_returns():
    """Main updater function"""
    
    print("\n" + "📊"*30)
    print("WOLF PACK FORWARD RETURN UPDATER")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    timeframes = [
        (1, 'forward_1d'),
        (3, 'forward_3d'),
        (5, 'forward_5d'),
        (10, 'forward_10d'),
        (20, 'forward_20d')
    ]
    
    total_updates = 0
    
    for days, field in timeframes:
        print(f"\n{'='*60}")
        print(f"Updating {days}-day forward returns...")
        print(f"{'='*60}\n")
        
        # Get records needing this timeframe
        pending = get_records_needing_forward_returns(conn, days, field)
        
        if not pending:
            print(f"  ✅ No pending {days}d updates\n")
            continue
        
        print(f"Found {len(pending)} records to update\n")
        
        updated = 0
        
        for ticker, date, close in pending[:50]:  # Limit to 50 per timeframe to avoid rate limits
            
            # Calculate forward return
            forward_ret = calculate_forward_return(ticker, date, close, days)
            
            if forward_ret is not None:
                # Update database
                kwargs = {f'forward_{days}d': forward_ret}
                if update_forward_returns(conn, ticker, date, **kwargs):
                    updated += 1
                    print(f"  ✅ {ticker:6} | {date} | {days}d: {forward_ret:+6.1f}%")
            
            # Rate limit
            time.sleep(RATE_LIMIT_DELAY)
        
        total_updates += updated
        print(f"\n  Updated {updated} records for {days}d timeframe")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY:")
    print(f"   Total updates: {total_updates}")
    print(f"\n🐺 Update complete - LLHR\n")

if __name__ == '__main__':
    update_all_forward_returns()
