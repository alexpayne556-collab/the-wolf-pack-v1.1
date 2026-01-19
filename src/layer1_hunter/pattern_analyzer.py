#!/usr/bin/env python3
"""
Pattern analyzer for Wolf Pack event database
Query and analyze what event types move stocks
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'wolf_pack_events.db'

def analyze_by_event_type(conn, timeframe='5d'):
    """Analyze returns by event type"""
    
    return_col = f'return_{timeframe}'
    
    query = f'''
    SELECT 
        event_type,
        COUNT(*) as count,
        AVG({return_col}) as avg_return,
        MEDIAN({return_col}) as median_return,
        SUM(CASE WHEN {return_col} > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate,
        SUM(CASE WHEN {return_col} > 20 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as big_winner_rate,
        SUM(CASE WHEN {return_col} < -20 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as big_loser_rate
    FROM events
    WHERE {return_col} IS NOT NULL
    GROUP BY event_type
    HAVING count >= 5
    ORDER BY avg_return DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    return df

def analyze_by_market_cap(conn, timeframe='5d'):
    """Analyze returns by market cap bucket"""
    
    return_col = f'return_{timeframe}'
    
    query = f'''
    SELECT 
        CASE 
            WHEN market_cap_at_event < 100000000 THEN 'Micro (<100M)'
            WHEN market_cap_at_event < 500000000 THEN 'Small (100-500M)'
            WHEN market_cap_at_event < 2000000000 THEN 'Mid (500M-2B)'
            WHEN market_cap_at_event < 10000000000 THEN 'Large (2-10B)'
            ELSE 'Mega (>10B)'
        END as cap_bucket,
        COUNT(*) as count,
        AVG({return_col}) as avg_return,
        SUM(CASE WHEN {return_col} > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
    FROM events
    WHERE {return_col} IS NOT NULL
    GROUP BY cap_bucket
    ORDER BY avg_return DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    return df

def analyze_by_volume(conn, timeframe='5d'):
    """Analyze returns by volume spike magnitude"""
    
    return_col = f'return_{timeframe}'
    
    query = f'''
    SELECT 
        CASE 
            WHEN volume_ratio < 1.5 THEN 'Normal (<1.5x)'
            WHEN volume_ratio < 3.0 THEN 'Elevated (1.5-3x)'
            WHEN volume_ratio < 5.0 THEN 'High (3-5x)'
            ELSE 'Extreme (>5x)'
        END as volume_bucket,
        COUNT(*) as count,
        AVG({return_col}) as avg_return,
        SUM(CASE WHEN {return_col} > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
    FROM events
    WHERE {return_col} IS NOT NULL AND volume_ratio IS NOT NULL
    GROUP BY volume_bucket
    ORDER BY avg_return DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    return df

def analyze_recent_events(conn, days=7):
    """Show recent high-return events"""
    
    query = f'''
    SELECT 
        ticker,
        event_type,
        event_date,
        return_1d,
        return_3d,
        return_5d,
        headline
    FROM events
    WHERE event_date >= date('now', '-{days} days')
    AND return_5d IS NOT NULL
    ORDER BY return_5d DESC
    LIMIT 20
    '''
    
    df = pd.read_sql_query(query, conn)
    return df

def run_analysis():
    """Run complete analysis"""
    
    print("\n" + "🔬"*30)
    print("WOLF PACK PATTERN ANALYZER")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔬"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Check how many events we have
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM events')
    total_events = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM events WHERE return_5d IS NOT NULL')
    events_with_returns = cursor.fetchone()[0]
    
    print(f"📊 DATABASE STATUS:")
    print(f"   Total events: {total_events}")
    print(f"   Events with 5d returns: {events_with_returns}")
    print()
    
    if events_with_returns < 10:
        print("⚠️  Not enough data yet. Run daily_collector and return_updater first.\n")
        conn.close()
        return
    
    # Analyze by event type
    print("=" * 80)
    print("📈 RETURNS BY EVENT TYPE (5-day)")
    print("=" * 80)
    df_type = analyze_by_event_type(conn, '5d')
    if not df_type.empty:
        print(df_type.to_string(index=False))
    print()
    
    # Analyze by market cap
    print("=" * 80)
    print("📈 RETURNS BY MARKET CAP (5-day)")
    print("=" * 80)
    df_cap = analyze_by_market_cap(conn, '5d')
    if not df_cap.empty:
        print(df_cap.to_string(index=False))
    print()
    
    # Analyze by volume
    print("=" * 80)
    print("📈 RETURNS BY VOLUME SPIKE (5-day)")
    print("=" * 80)
    df_vol = analyze_by_volume(conn, '5d')
    if not df_vol.empty:
        print(df_vol.to_string(index=False))
    print()
    
    # Recent high performers
    print("=" * 80)
    print("🔥 TOP PERFORMERS (Last 7 Days)")
    print("=" * 80)
    df_recent = analyze_recent_events(conn, 7)
    if not df_recent.empty:
        for _, row in df_recent.iterrows():
            print(f"{row['ticker']:6} | {row['event_type']:15} | 5d: {row['return_5d']:+6.1f}% | {row['headline'][:60]}")
    print()
    
    conn.close()
    
    print("🐺 Analysis complete - LLHR\n")

if __name__ == '__main__':
    run_analysis()
