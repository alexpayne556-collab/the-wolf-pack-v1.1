#!/usr/bin/env python3
"""
🐺 WOLF PACK DAILY TRADE JOURNAL
================================
For br0kkr to run at END OF EACH TRADING DAY

This is LIGHTWEIGHT - no API calls, no scanning.
Just logging decisions to feed the learning engine.

The brain gets smarter by learning from YOUR decisions,
not by running heavy processes.

Usage:
    python daily_journal.py              # Interactive mode
    python daily_journal.py --quick      # Quick log (minimal prompts)
    python daily_journal.py --review     # Review today's entries
"""

import json
import os
import sqlite3
from datetime import datetime, date
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

# Where to store journal entries
JOURNAL_DIR = Path("./data/journal")
DATABASE_PATH = Path("./data/wolfpack.db")

# Ensure directories exist
JOURNAL_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# JOURNAL ENTRY STRUCTURE
# =============================================================================

def create_trade_entry():
    """Create a structured trade entry through prompts."""
    print("\n" + "="*60)
    print("  WOLF PACK - LOG A TRADE")
    print("="*60)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'type': 'trade'
    }
    
    # Basic trade info
    entry['ticker'] = input("\n  Ticker symbol: ").upper().strip()
    entry['action'] = input("  Action (BUY/SELL/HOLD): ").upper().strip()
    
    if entry['action'] in ['BUY', 'SELL']:
        entry['shares'] = float(input("  Shares: ") or 0)
        entry['price'] = float(input("  Price: $") or 0)
        entry['account'] = input("  Account (RH/FID): ").upper().strip()
    
    # The important stuff - reasoning
    print("\n  --- REASONING (this is what the brain learns from) ---")
    entry['thesis'] = input("  What's your thesis? (why this trade): ").strip()
    entry['catalyst'] = input("  What catalyst? (or 'none'): ").strip()
    entry['convergence_estimate'] = input("  Convergence estimate (1-100, or 'unknown'): ").strip()
    
    # Context
    entry['sector_hot'] = input("  Is the sector hot today? (y/n): ").lower().strip() == 'y'
    entry['volume_strong'] = input("  Volume strong? (y/n): ").lower().strip() == 'y'
    
    # Plan
    if entry['action'] == 'BUY':
        entry['stop_loss'] = input("  Stop loss price: $") or 'none'
        entry['target'] = input("  Target price: $") or 'none'
        entry['timeframe'] = input("  Timeframe (day/swing/hold): ").lower().strip()
    
    # Confidence
    entry['confidence'] = input("  Confidence (1-10): ").strip()
    entry['notes'] = input("  Any other notes: ").strip()
    
    return entry

def create_decision_entry():
    """Log a decision that wasn't a trade (held, passed, etc.)."""
    print("\n" + "="*60)
    print("  WOLF PACK - LOG A DECISION")
    print("="*60)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'type': 'decision'
    }
    
    entry['ticker'] = input("\n  Ticker (or 'general'): ").upper().strip()
    entry['decision'] = input("  What did you decide? (held/passed/watched/etc): ").strip()
    entry['reasoning'] = input("  Why? (this is what the brain learns): ").strip()
    entry['outcome'] = input("  Outcome so far (if known): ").strip()
    entry['lesson'] = input("  What's the lesson here?: ").strip()
    
    return entry

def create_daily_summary():
    """Create end-of-day summary."""
    print("\n" + "="*60)
    print("  WOLF PACK - DAILY SUMMARY")
    print("="*60)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'type': 'daily_summary'
    }
    
    # Portfolio status
    print("\n  --- PORTFOLIO STATUS ---")
    summary['robinhood_value'] = float(input("  Robinhood total value: $") or 0)
    summary['fidelity_value'] = float(input("  Fidelity total value: $") or 0)
    summary['total_value'] = summary['robinhood_value'] + summary['fidelity_value']
    summary['day_change'] = float(input("  Day P/L: $") or 0)
    
    # What happened
    print("\n  --- WHAT HAPPENED ---")
    summary['trades_made'] = int(input("  How many trades today?: ") or 0)
    summary['winners'] = int(input("  How many winners?: ") or 0)
    summary['losers'] = int(input("  How many losers?: ") or 0)
    
    # Analysis
    print("\n  --- ANALYSIS (this builds intelligence) ---")
    summary['what_worked'] = input("  What worked today?: ").strip()
    summary['what_failed'] = input("  What failed today?: ").strip()
    summary['biggest_lesson'] = input("  Biggest lesson learned?: ").strip()
    summary['would_do_differently'] = input("  What would you do differently?: ").strip()
    
    # Tomorrow
    print("\n  --- TOMORROW ---")
    summary['watchlist'] = input("  Watchlist for tomorrow (comma separated): ").strip()
    summary['plan'] = input("  Plan for tomorrow: ").strip()
    summary['key_levels'] = input("  Key levels to watch: ").strip()
    
    # Market context
    print("\n  --- MARKET CONTEXT ---")
    summary['market_sentiment'] = input("  Market sentiment (bullish/bearish/neutral): ").strip()
    summary['sector_rotation'] = input("  Hot sectors today: ").strip()
    summary['catalysts_tomorrow'] = input("  Catalysts tomorrow (FOMC, earnings, etc): ").strip()
    
    return summary

def create_lesson_entry():
    """Log a specific lesson learned."""
    print("\n" + "="*60)
    print("  WOLF PACK - LOG A LESSON")
    print("="*60)
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'type': 'lesson'
    }
    
    entry['category'] = input("\n  Category (entry/exit/sizing/timing/thesis/emotion): ").strip()
    entry['ticker'] = input("  Related ticker (or 'general'): ").upper().strip()
    entry['situation'] = input("  What was the situation?: ").strip()
    entry['mistake_or_success'] = input("  Was this a MISTAKE or SUCCESS?: ").upper().strip()
    entry['lesson'] = input("  What's the lesson?: ").strip()
    entry['rule'] = input("  New rule to add? (or 'none'): ").strip()
    entry['applies_to'] = input("  This applies to (specific ticker / sector / all trades): ").strip()
    
    return entry

# =============================================================================
# STORAGE FUNCTIONS
# =============================================================================

def save_entry(entry):
    """Save entry to daily JSON file and optionally to database."""
    
    # Save to daily JSON file
    today = date.today().isoformat()
    filename = JOURNAL_DIR / f"journal_{today}.json"
    
    # Load existing entries for today
    if filename.exists():
        with open(filename, 'r') as f:
            entries = json.load(f)
    else:
        entries = []
    
    # Add new entry
    entries.append(entry)
    
    # Save
    with open(filename, 'w') as f:
        json.dump(entries, f, indent=2)
    
    print(f"\n  [OK] Saved to {filename}")
    
    # Also save to database if it exists
    if DATABASE_PATH.exists():
        try:
            save_to_database(entry)
            print(f"  [OK] Saved to learning database")
        except Exception as e:
            print(f"  [WARN] Could not save to database: {e}")
    
    return filename

def save_to_database(entry):
    """Save entry to the learning engine database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create journal table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            date TEXT,
            type TEXT,
            data TEXT
        )
    ''')
    
    # Insert entry
    cursor.execute('''
        INSERT INTO journal_entries (timestamp, date, type, data)
        VALUES (?, ?, ?, ?)
    ''', (entry['timestamp'], entry['date'], entry['type'], json.dumps(entry)))
    
    conn.commit()
    conn.close()

def review_today():
    """Review all entries from today."""
    today = date.today().isoformat()
    filename = JOURNAL_DIR / f"journal_{today}.json"
    
    print("\n" + "="*60)
    print(f"  JOURNAL ENTRIES FOR {today}")
    print("="*60)
    
    if not filename.exists():
        print("\n  No entries for today yet.")
        return
    
    with open(filename, 'r') as f:
        entries = json.load(f)
    
    for i, entry in enumerate(entries, 1):
        print(f"\n  --- Entry {i}: {entry['type'].upper()} ---")
        print(f"  Time: {entry['timestamp']}")
        
        if entry['type'] == 'trade':
            print(f"  {entry['action']} {entry.get('shares', '')} {entry['ticker']} @ ${entry.get('price', 'N/A')}")
            print(f"  Thesis: {entry.get('thesis', 'N/A')}")
            print(f"  Catalyst: {entry.get('catalyst', 'N/A')}")
        elif entry['type'] == 'decision':
            print(f"  {entry['ticker']}: {entry['decision']}")
            print(f"  Reasoning: {entry.get('reasoning', 'N/A')}")
            print(f"  Lesson: {entry.get('lesson', 'N/A')}")
        elif entry['type'] == 'lesson':
            print(f"  Category: {entry.get('category', 'N/A')}")
            print(f"  Lesson: {entry.get('lesson', 'N/A')}")
            print(f"  Rule: {entry.get('rule', 'N/A')}")
        elif entry['type'] == 'daily_summary':
            print(f"  Portfolio: ${entry.get('total_value', 0):,.2f}")
            print(f"  Day P/L: ${entry.get('day_change', 0):,.2f}")
            print(f"  What worked: {entry.get('what_worked', 'N/A')}")
            print(f"  Biggest lesson: {entry.get('biggest_lesson', 'N/A')}")
    
    print("\n" + "="*60)

# =============================================================================
# QUICK LOG MODE
# =============================================================================

def quick_trade_log():
    """Minimal prompts for fast logging during trading."""
    print("\n  QUICK TRADE LOG")
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'date': str(date.today()),
        'type': 'trade'
    }
    
    # One-liner input: "BUY MU 1 410.50 thesis here"
    raw = input("  Format: ACTION TICKER SHARES PRICE THESIS\n  > ").strip()
    parts = raw.split(' ', 4)
    
    if len(parts) >= 4:
        entry['action'] = parts[0].upper()
        entry['ticker'] = parts[1].upper()
        entry['shares'] = float(parts[2])
        entry['price'] = float(parts[3])
        entry['thesis'] = parts[4] if len(parts) > 4 else ''
        
        save_entry(entry)
    else:
        print("  Invalid format. Use: BUY MU 1 410.50 thesis here")

# =============================================================================
# MAIN MENU
# =============================================================================

def main():
    print("\n" + "="*60)
    print("  🐺 WOLF PACK DAILY JOURNAL")
    print("  Building intelligence through documentation")
    print("="*60)
    
    while True:
        print("\n  What do you want to log?")
        print("  1. Trade (buy/sell)")
        print("  2. Decision (held/passed/watched)")
        print("  3. Lesson learned")
        print("  4. Daily summary (end of day)")
        print("  5. Quick trade log (minimal prompts)")
        print("  6. Review today's entries")
        print("  7. Exit")
        
        choice = input("\n  Choice (1-7): ").strip()
        
        if choice == '1':
            entry = create_trade_entry()
            save_entry(entry)
        elif choice == '2':
            entry = create_decision_entry()
            save_entry(entry)
        elif choice == '3':
            entry = create_lesson_entry()
            save_entry(entry)
        elif choice == '4':
            entry = create_daily_summary()
            save_entry(entry)
        elif choice == '5':
            quick_trade_log()
        elif choice == '6':
            review_today()
        elif choice == '7':
            print("\n  AWOOOO! 🐺")
            break
        else:
            print("  Invalid choice.")

if __name__ == "__main__":
    import sys
    
    if '--quick' in sys.argv:
        quick_trade_log()
    elif '--review' in sys.argv:
        review_today()
    else:
        main()
