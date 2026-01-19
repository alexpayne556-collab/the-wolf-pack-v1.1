#!/usr/bin/env python3
"""
Wolf Pack V2 - Pattern Learner
Learns from YOUR actual trading patterns and outcomes
"""

import sqlite3
from wolfpack_db_v2 import DB_PATH_V2

def analyze_patterns():
    """Analyze your trading patterns and outcomes"""
    
    print("\n" + "🧠"*30)
    print("WOLF PACK V2 - PATTERN LEARNER")
    print("Learning from YOUR actual trades")
    print("🧠"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH_V2)
    cursor = conn.cursor()
    
    # Pattern 1: Buying moves with catalysts vs without
    print("="*70)
    print("PATTERN: BUY decisions with vs without catalysts")
    print("="*70)
    
    cursor.execute('''
    SELECT 
        CASE WHEN d.catalyst_link IS NOT NULL THEN 'With Catalyst' ELSE 'No Catalyst' END as has_catalyst,
        COUNT(*) as trades,
        AVG(d.outcome_5d) as avg_return,
        SUM(CASE WHEN d.outcome_5d > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
    FROM user_decisions d
    WHERE d.action = 'BUY' AND d.outcome_5d IS NOT NULL
    GROUP BY has_catalyst
    ''')
    
    results = cursor.fetchall()
    for catalyst_status, trades, avg_return, win_rate in results:
        print(f"\n{catalyst_status}:")
        print(f"  Trades: {trades}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Avg 5-day Return: {avg_return:+.1f}%")
    
    # Pattern 2: Day 1 buys vs Day 2 confirmation buys
    print("\n" + "="*70)
    print("PATTERN: Immediate entry vs waiting for confirmation")
    print("="*70)
    
    cursor.execute('''
    SELECT 
        CASE 
            WHEN time(d.timestamp) < '11:00:00' THEN 'Morning Entry'
            WHEN time(d.timestamp) < '14:00:00' THEN 'Midday Entry'
            ELSE 'Late Day Entry'
        END as entry_timing,
        COUNT(*) as trades,
        AVG(d.outcome_5d) as avg_return,
        SUM(CASE WHEN d.outcome_5d > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
    FROM user_decisions d
    WHERE d.action = 'BUY' AND d.outcome_5d IS NOT NULL
    GROUP BY entry_timing
    ''')
    
    results = cursor.fetchall()
    for timing, trades, avg_return, win_rate in results:
        print(f"\n{timing}:")
        print(f"  Trades: {trades}")
        print(f"  Win Rate: {win_rate:.1f}%")
        print(f"  Avg 5-day Return: {avg_return:+.1f}%")
    
    # Pattern 3: Your best tickers
    print("\n" + "="*70)
    print("PATTERN: Your best performing tickers")
    print("="*70)
    
    cursor.execute('''
    SELECT 
        ticker,
        COUNT(*) as trades,
        AVG(outcome_5d) as avg_return,
        SUM(CASE WHEN outcome_5d > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
    FROM user_decisions
    WHERE action = 'BUY' AND outcome_5d IS NOT NULL
    GROUP BY ticker
    HAVING COUNT(*) >= 2
    ORDER BY avg_return DESC
    LIMIT 10
    ''')
    
    results = cursor.fetchall()
    print("\nTop 10 tickers (min 2 trades):\n")
    for ticker, trades, avg_return, win_rate in results:
        print(f"{ticker:6} | {trades} trades | Win: {win_rate:.0f}% | Avg: {avg_return:+.1f}%")
    
    # Pattern 4: Watch vs Act comparison
    print("\n" + "="*70)
    print("PATTERN: Stocks you WATCHED vs stocks you BOUGHT")
    print("="*70)
    
    cursor.execute('''
    SELECT 
        action,
        COUNT(*) as count,
        AVG(outcome_5d) as avg_move
    FROM user_decisions
    WHERE action IN ('WATCH', 'BUY') AND outcome_5d IS NOT NULL
    GROUP BY action
    ''')
    
    results = cursor.fetchall()
    print("\nWhat happens to stocks you watch vs buy?\n")
    for action, count, avg_move in results:
        status = "You acted" if action == 'BUY' else "You passed"
        print(f"{status:12} | {count:2} times | Avg 5d move: {avg_move:+.1f}%")
    
    conn.close()
    
    print("\n" + "="*70)
    print("🧠 Keep logging your decisions - patterns get clearer with more data")
    print("="*70 + "\n")

if __name__ == '__main__':
    analyze_patterns()
