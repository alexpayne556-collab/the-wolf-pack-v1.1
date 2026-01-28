"""
Daily Trade Logger for Temporal Memory System
Run this at the end of each session to log trades to wolfpack.db

Usage:
    python log_daily_trades.py
    
Then answer the prompts, or edit the trades list at the bottom and run it.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "wolfpack.db"

def log_trade(ticker, action, price, quantity, reasoning, context_dict, pnl_percent, trade_type):
    """
    Log a single trade to decision_log table
    
    Args:
        ticker: Stock symbol (e.g., "MU")
        action: BUY, SELL, HOLD, ADD, CUT
        price: Trade price
        quantity: Number of shares
        reasoning: Full text explanation of why we did this
        context_dict: Dict with market_state, thesis_status, etc
        pnl_percent: Percentage gain/loss (use None if not closed)
        trade_type: thesis, momentum, no_thesis, wounded_prey
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    context_json = json.dumps(context_dict)
    
    cursor.execute("""
        INSERT INTO decision_log (
            ticker, date, action, price, quantity, reasoning, context,
            pnl_percent, trade_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticker, today, action, price, quantity, reasoning, context_json, pnl_percent, trade_type))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Logged {ticker}: {action} at ${price} ({trade_type})")


def log_pattern(pattern_name, criteria_dict, ticker, occurrences, success_count, avg_return, lesson):
    """
    Log or update a pattern in pattern_library
    
    Args:
        pattern_name: Name of pattern (e.g., "momentum_small_position")
        criteria_dict: Dict defining the pattern
        ticker: Specific ticker or None for universal pattern
        occurrences: How many times we've seen this
        success_count: How many were profitable
        avg_return: Average return %
        lesson: What we learned
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    criteria_json = json.dumps(criteria_dict)
    
    # Check if pattern exists
    cursor.execute("SELECT id, occurrences, success_count FROM pattern_library WHERE pattern_name = ? AND (ticker = ? OR (ticker IS NULL AND ? IS NULL))", 
                   (pattern_name, ticker, ticker))
    existing = cursor.fetchone()
    
    if existing:
        # Update existing pattern
        old_occur = existing[1]
        old_success = existing[2]
        new_occur = old_occur + occurrences
        new_success = old_success + success_count
        
        cursor.execute("""
            UPDATE pattern_library 
            SET occurrences = ?, success_count = ?, avg_return = ?, last_seen = ?, lesson = ?
            WHERE id = ?
        """, (new_occur, new_success, avg_return, today, lesson, existing[0]))
        
        print(f"✓ Updated pattern: {pattern_name} (now {new_success}/{new_occur} wins)")
    else:
        # Insert new pattern
        cursor.execute("""
            INSERT INTO pattern_library (
                pattern_name, pattern_criteria, ticker, occurrences, success_count,
                avg_return, last_seen, lesson
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pattern_name, criteria_json, ticker, occurrences, success_count, avg_return, today, lesson))
        
        print(f"✓ New pattern: {pattern_name} ({success_count}/{occurrences} wins)")
    
    conn.commit()
    conn.close()


def show_memory_stats():
    """Display current memory statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("TEMPORAL MEMORY - CURRENT STATE")
    print("="*60)
    
    # Decision log stats
    cursor.execute("SELECT COUNT(*), AVG(pnl_percent) FROM decision_log WHERE pnl_percent IS NOT NULL")
    total_trades, avg_return = cursor.fetchone()
    print(f"\n📊 Total logged trades: {total_trades}")
    if avg_return:
        print(f"📊 Average return: {avg_return:+.2f}%")
    
    # Recent trades
    cursor.execute("""
        SELECT ticker, action, pnl_percent, trade_type, date 
        FROM decision_log 
        ORDER BY date DESC, id DESC 
        LIMIT 5
    """)
    print("\n📝 Recent trades:")
    for row in cursor.fetchall():
        ticker, action, pnl, trade_type, date = row
        pnl_str = f"{pnl:+.2f}%" if pnl else "open"
        print(f"  {date}: {ticker} {action} ({pnl_str}) [{trade_type}]")
    
    # Pattern stats
    cursor.execute("SELECT COUNT(*) FROM pattern_library")
    pattern_count = cursor.fetchone()[0]
    print(f"\n🧠 Identified patterns: {pattern_count}")
    
    cursor.execute("""
        SELECT pattern_name, success_count, occurrences, avg_return 
        FROM pattern_library 
        ORDER BY occurrences DESC
    """)
    for row in cursor.fetchall():
        name, success, occur, avg_ret = row
        win_rate = (success / occur * 100) if occur > 0 else 0
        print(f"  - {name}: {success}/{occur} ({win_rate:.0f}% win, avg {avg_ret:+.2f}%)")
    
    conn.close()
    print("="*60 + "\n")


# =============================================================================
# EDIT THIS SECTION TO LOG TODAY'S TRADES
# =============================================================================

def log_todays_session():
    """
    Edit this function to log today's trades
    Copy the template and fill in your trades
    """
    
    # =================================================================
    # TOMORROW: Uncomment and edit these templates for new trades
    # =================================================================
    
    # TEMPLATE: Log a trade
    # log_trade(
    #     ticker="TICKER",
    #     action="BUY/SELL/HOLD/ADD/CUT",
    #     price=0.00,
    #     quantity=0,
    #     reasoning="Full explanation of WHY we did this",
    #     context_dict={
    #         "market_state": "describe market",
    #         "thesis_status": "intact/broken/none",
    #         "catalyst": "what's driving this"
    #     },
    #     pnl_percent=0.0,  # or None if position still open
    #     trade_type="thesis/momentum/no_thesis/wounded_prey"
    # )
    
    # TEMPLATE: Log a pattern
    # log_pattern(
    #     pattern_name="descriptive_name",
    #     criteria_dict={"key": "value"},
    #     ticker=None,  # or specific ticker
    #     occurrences=1,
    #     success_count=1,
    #     avg_return=0.0,
    #     lesson="What did we learn?"
    # )
    
    print("No new trades to log (edit log_todays_session() function to add trades)")
    print("Or use interactive mode: python log_daily_trades.py --interactive")


def interactive_mode():
    """Interactive prompts for logging trades"""
    print("\n" + "="*60)
    print("INTERACTIVE TRADE LOGGER")
    print("="*60 + "\n")
    
    while True:
        ticker = input("Ticker (or 'done' to finish): ").strip().upper()
        if ticker == 'DONE':
            break
        
        action = input("Action (BUY/SELL/HOLD/ADD/CUT): ").strip().upper()
        price = float(input("Price: "))
        quantity = int(input("Quantity: "))
        reasoning = input("Reasoning (why did we do this?): ").strip()
        trade_type = input("Trade type (thesis/momentum/no_thesis/wounded_prey): ").strip().lower()
        
        pnl_input = input("P&L % (leave blank if position still open): ").strip()
        pnl_percent = float(pnl_input) if pnl_input else None
        
        context_dict = {
            "market_state": input("Market state: ").strip(),
            "thesis_status": input("Thesis status: ").strip(),
            "trade_type": trade_type
        }
        
        log_trade(ticker, action, price, quantity, reasoning, context_dict, pnl_percent, trade_type)
        print()


if __name__ == "__main__":
    import sys
    
    print("DAILY TRADE LOGGER - Temporal Memory System")
    print("="*60)
    
    if "--interactive" in sys.argv or "-i" in sys.argv:
        interactive_mode()
    else:
        log_todays_session()
    
    show_memory_stats()
    
    print("✓ Session logged to wolfpack.db")
    print("🐺 Brain memory updated\n")
