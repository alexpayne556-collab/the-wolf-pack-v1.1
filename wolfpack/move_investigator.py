#!/usr/bin/env python3
"""
Wolf Pack Move Investigator
Auto-investigates big moves (>5%) to find WHY they happened
"""

import sqlite3
from datetime import datetime, timedelta
import json

from config import DB_PATH, BIG_MOVE_THRESHOLD

def investigate_move(ticker, date, move_pct, sector):
    """
    When a stock moves >5%, investigate WHY
    Returns investigation findings
    """
    
    print(f"\n🔍 INVESTIGATING: {ticker} {move_pct:+.1f}% on {date}")
    
    investigation = {
        'ticker': ticker,
        'date': date,
        'move_pct': move_pct,
        'sector': sector,
        'investigation_timestamp': datetime.now().isoformat(),
        'catalyst_type': None,
        'catalyst_confidence': 0.0,
        'news_found': None,
        'sec_filings': None,
        'analyst_actions': None,
        'sector_correlation': False,
        'volume_confirmed': False,
        'notes': []
    }
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # =============================================================================
    # 1. CHECK SECTOR CORRELATION
    # =============================================================================
    
    cursor.execute('''
    SELECT ticker, daily_return_pct
    FROM daily_records
    WHERE date = ? AND sector = ? AND ticker != ?
    ''', (date, sector, ticker))
    
    sector_stocks = cursor.fetchall()
    
    if sector_stocks:
        sector_avg = sum([ret for _, ret in sector_stocks]) / len(sector_stocks)
        investigation['sector_avg_move'] = sector_avg
        
        # If sector moved >3% same direction, likely sector correlation
        if abs(sector_avg) > 3.0 and (sector_avg * move_pct > 0):
            investigation['sector_correlation'] = True
            investigation['catalyst_type'] = 'sector_momentum'
            investigation['catalyst_confidence'] = 0.75
            investigation['notes'].append(f"Sector {sector} moved {sector_avg:+.1f}% avg - likely sector correlation")
    
    # =============================================================================
    # 2. CHECK VOLUME CONFIRMATION
    # =============================================================================
    
    cursor.execute('''
    SELECT volume_ratio
    FROM daily_records
    WHERE ticker = ? AND date = ?
    ''', (ticker, date))
    
    result = cursor.fetchone()
    if result:
        volume_ratio = result[0]
        if volume_ratio and volume_ratio >= 2.0:
            investigation['volume_confirmed'] = True
            investigation['notes'].append(f"Volume confirmed: {volume_ratio:.1f}x average")
            
            # Increase confidence if volume confirms
            if investigation['catalyst_confidence'] > 0:
                investigation['catalyst_confidence'] = min(0.95, investigation['catalyst_confidence'] + 0.15)
    
    # =============================================================================
    # 3. CHECK FOR RECENT SIMILAR MOVES (Pattern recognition)
    # =============================================================================
    
    cursor.execute('''
    SELECT date, daily_return_pct, forward_5d
    FROM daily_records
    WHERE ticker = ? 
    AND date < ?
    AND ABS(daily_return_pct) >= ?
    ORDER BY date DESC
    LIMIT 5
    ''', (ticker, date, BIG_MOVE_THRESHOLD))
    
    recent_moves = cursor.fetchall()
    
    if recent_moves:
        investigation['notes'].append(f"Found {len(recent_moves)} similar big moves in recent history")
        
        # Check if this is a repeat runner
        if len(recent_moves) >= 3:
            investigation['pattern_tags'] = ['repeat_runner']
            investigation['notes'].append("REPEAT RUNNER - moves big frequently")
    
    # =============================================================================
    # 4. MANUAL INVESTIGATION PROMPTS
    # =============================================================================
    
    if investigation['catalyst_type'] is None:
        investigation['catalyst_type'] = 'unknown'
        investigation['catalyst_confidence'] = 0.3
        investigation['notes'].append("⚠️  MANUAL CHECK NEEDED: No obvious catalyst found")
        investigation['notes'].append(f"   - Check news for {ticker}")
        investigation['notes'].append(f"   - Check SEC EDGAR for filings")
        investigation['notes'].append(f"   - Check Twitter/StockTwits sentiment")
    
    conn.close()
    
    return investigation

def store_investigation(investigation):
    """Store investigation in database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO investigations (
            ticker, date, move_pct, catalyst_type, catalyst_confidence,
            news_found, sec_filings, analyst_actions,
            sector_correlation, volume_confirmed, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            investigation['ticker'],
            investigation['date'],
            investigation['move_pct'],
            investigation['catalyst_type'],
            investigation['catalyst_confidence'],
            investigation['news_found'],
            investigation['sec_filings'],
            investigation['analyst_actions'],
            investigation['sector_correlation'],
            investigation['volume_confirmed'],
            '\n'.join(investigation['notes'])
        ))
        
        conn.commit()
        print(f"  ✅ Investigation stored")
    
    except Exception as e:
        print(f"  ❌ Error storing investigation: {e}")
    
    finally:
        conn.close()

def investigate_all_big_moves(date):
    """Find and investigate all big moves for a given date"""
    
    print("\n" + "🔍"*30)
    print("WOLF PACK MOVE INVESTIGATOR")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔍"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find all big moves
    cursor.execute('''
    SELECT ticker, date, daily_return_pct, sector
    FROM daily_records
    WHERE date = ? AND is_big_move = 1
    ORDER BY ABS(daily_return_pct) DESC
    ''', (date,))
    
    big_moves = cursor.fetchall()
    conn.close()
    
    if not big_moves:
        print(f"✅ No big moves (>{BIG_MOVE_THRESHOLD}%) on {date}\n")
        return
    
    print(f"Found {len(big_moves)} big moves on {date}\n")
    
    for ticker, move_date, move_pct, sector in big_moves:
        investigation = investigate_move(ticker, move_date, move_pct, sector)
        
        # Print summary
        print(f"\n  Catalyst: {investigation['catalyst_type']} (confidence: {investigation['catalyst_confidence']:.0%})")
        print(f"  Sector correlation: {'YES' if investigation['sector_correlation'] else 'NO'}")
        print(f"  Volume confirmed: {'YES' if investigation['volume_confirmed'] else 'NO'}")
        
        if investigation['notes']:
            print(f"  Notes:")
            for note in investigation['notes']:
                print(f"    {note}")
        
        # Store investigation
        store_investigation(investigation)
    
    print(f"\n🔍 Investigation complete - LLHR\n")

if __name__ == '__main__':
    # Investigate today's moves (or most recent date in database)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM daily_records')
    latest_date = cursor.fetchone()[0]
    conn.close()
    
    if latest_date:
        investigate_all_big_moves(latest_date)
    else:
        print("❌ No data in database yet. Run wolfpack_recorder.py first.\n")
