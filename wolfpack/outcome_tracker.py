#!/usr/bin/env python3
"""
Wolf Pack V2 - Outcome Tracker
Tracks what happened AFTER your decisions
Runs daily to update Day 2, Day 3, Day 5 results
"""

import sqlite3
from datetime import datetime, timedelta
import yfinance as yf
from wolfpack_db_v2 import DB_PATH_V2

def update_decision_outcomes():
    """Update outcomes for all logged decisions"""
    
    print("\n" + "📊"*30)
    print("WOLF PACK V2 - OUTCOME TRACKER")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📊"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    # Get all decisions that don't have complete outcomes yet
    cursor.execute('''
    SELECT id, ticker, timestamp, action, price, quantity
    FROM user_decisions
    WHERE outcome_10d IS NULL
    ORDER BY timestamp DESC
    ''')
    
    decisions = cursor.fetchall()
    
    if not decisions:
        print("✅ No pending outcomes to update\n")
        conn.close()
        return
    
    print(f"Updating {len(decisions)} decisions...\n")
    
    for decision_id, ticker, timestamp, action, entry_price, quantity in decisions:
        decision_date = datetime.fromisoformat(timestamp)
        days_since = (datetime.now() - decision_date).days
        
        print(f"📈 {ticker} - {action} @ ${entry_price:.2f} ({days_since} days ago)")
        
        # Get price history since decision
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=decision_date.strftime('%Y-%m-%d'), period='1mo')
            
            if len(hist) == 0:
                print(f"  ⚠️  No price data available")
                continue
            
            # Calculate outcomes
            outcomes = {}
            
            for days, col in [(1, 'outcome_1d'), (3, 'outcome_3d'), (5, 'outcome_5d'), (10, 'outcome_10d')]:
                if days_since >= days and len(hist) > days:
                    future_price = hist['Close'].iloc[min(days, len(hist)-1)]
                    
                    if entry_price:
                        return_pct = ((future_price - entry_price) / entry_price) * 100
                        outcomes[col] = return_pct
                        
                        status = "✅" if return_pct > 0 else "❌"
                        print(f"  {status} Day {days}: {return_pct:+.1f}%")
            
            # Update database
            if outcomes:
                update_query = "UPDATE user_decisions SET "
                update_query += ", ".join([f"{col} = ?" for col in outcomes.keys()])
                update_query += " WHERE id = ?"
                
                cursor.execute(update_query, list(outcomes.values()) + [decision_id])
                conn.commit()
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    conn.close()
    print(f"\n✅ Outcome update complete\n")

def show_decision_performance():
    """Show performance of your decisions"""
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("📊 YOUR DECISION PERFORMANCE")
    print("="*70 + "\n")
    
    # Overall stats
    cursor.execute('''
    SELECT 
        action,
        COUNT(*) as total,
        AVG(outcome_5d) as avg_5d_return,
        SUM(CASE WHEN outcome_5d > 0 THEN 1 ELSE 0 END) as winners
    FROM user_decisions
    WHERE outcome_5d IS NOT NULL
    GROUP BY action
    ''')
    
    stats = cursor.fetchall()
    
    if not stats:
        print("No completed decisions yet (need at least 5 days of data)\n")
        conn.close()
        return
    
    for action, total, avg_return, winners in stats:
        win_rate = (winners / total * 100) if total > 0 else 0
        print(f"{action}:")
        print(f"  Total trades: {total}")
        print(f"  Win rate: {win_rate:.1f}%")
        print(f"  Avg 5-day return: {avg_return:+.1f}%")
        print()
    
    # Recent decisions
    print("="*70)
    print("RECENT DECISIONS:")
    print("="*70 + "\n")
    
    cursor.execute('''
    SELECT ticker, timestamp, action, price, outcome_1d, outcome_3d, outcome_5d
    FROM user_decisions
    ORDER BY timestamp DESC
    LIMIT 10
    ''')
    
    recent = cursor.fetchall()
    
    for ticker, timestamp, action, price, d1, d3, d5 in recent:
        date = datetime.fromisoformat(timestamp).strftime('%m/%d')
        print(f"{date} | {ticker:6} | {action:5} @ ${price:.2f}")
        
        if d1 is not None:
            status = "✅" if d1 > 0 else "❌"
            print(f"       Day 1: {status} {d1:+.1f}%", end="")
        if d3 is not None:
            status = "✅" if d3 > 0 else "❌"
            print(f" | Day 3: {status} {d3:+.1f}%", end="")
        if d5 is not None:
            status = "✅" if d5 > 0 else "❌"
            print(f" | Day 5: {status} {d5:+.1f}%", end="")
        print("\n")
    
    conn.close()

if __name__ == '__main__':
    # Update all pending outcomes
    update_decision_outcomes()
    
    # Show performance summary
    show_decision_performance()
