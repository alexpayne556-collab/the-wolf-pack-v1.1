#!/usr/bin/env python3
"""
Wolf Pack V2 - Decision Logger
Simple CLI to log YOUR trading decisions
"""

from datetime import datetime
from wolfpack_db_v2 import log_user_decision, get_recent_moves
import sys

def show_recent_moves():
    """Show recent moves to help user remember context"""
    
    print("\n📊 RECENT MOVES (Last 24 hours):")
    print("-" * 70)
    
    moves = get_recent_moves(hours=24)
    
    if not moves:
        print("  No recent moves detected")
        return
    
    for ticker, timestamp, move_pct, price in moves:
        direction = "📈" if move_pct > 0 else "📉"
        print(f"  {direction} {ticker:6} {move_pct:+.1f}% @ ${price:.2f}  ({timestamp})")
    
    print("-" * 70)

def log_decision_interactive():
    """Interactive CLI to log a decision"""
    
    print("\n" + "="*70)
    print("🐺 WOLF PACK V2 - DECISION LOGGER")
    print("="*70)
    
    show_recent_moves()
    
    print("\n💬 Log your trading decision:\n")
    
    # Get ticker
    ticker = input("Ticker: ").strip().upper()
    if not ticker:
        print("❌ Cancelled")
        return
    
    # Get action
    print("\nAction:")
    print("  1. BUY")
    print("  2. SELL")
    print("  3. WATCH (interested but didn't act)")
    print("  4. HOLD (no action)")
    
    action_choice = input("Choose (1-4): ").strip()
    action_map = {'1': 'BUY', '2': 'SELL', '3': 'WATCH', '4': 'HOLD'}
    action = action_map.get(action_choice, 'UNKNOWN')
    
    if action == 'UNKNOWN':
        print("❌ Invalid choice")
        return
    
    # Get price and quantity if buying/selling
    price = None
    quantity = None
    
    if action in ['BUY', 'SELL']:
        try:
            price = float(input(f"\nPrice per share: $"))
            quantity = int(input("Quantity: "))
        except ValueError:
            print("❌ Invalid price/quantity")
            return
    
    # Get reasoning
    print(f"\nWhy did you {action} {ticker}?")
    reasoning = input("Reasoning: ").strip()
    
    # Confirm
    print(f"\n📝 LOGGING:")
    print(f"  Ticker: {ticker}")
    print(f"  Action: {action}")
    if price:
        print(f"  Price: ${price:.2f}")
    if quantity:
        print(f"  Quantity: {quantity}")
    print(f"  Reasoning: {reasoning}")
    
    confirm = input("\nLog this decision? (y/n): ").strip().lower()
    
    if confirm == 'y':
        decision = {
            'ticker': ticker,
            'action': action,
            'price': price,
            'quantity': quantity,
            'reasoning': reasoning
        }
        
        decision_id = log_user_decision(decision)
        
        if decision_id:
            print(f"\n✅ Decision logged (ID: {decision_id})")
            print(f"📊 Outcome tracking will update automatically")
        else:
            print(f"\n❌ Failed to log decision")
    else:
        print("\n❌ Cancelled")

def log_decision_quick(ticker, action, price=None, quantity=None, reasoning=""):
    """Quick logging via command line args"""
    
    decision = {
        'ticker': ticker.upper(),
        'action': action.upper(),
        'price': float(price) if price else None,
        'quantity': int(quantity) if quantity else None,
        'reasoning': reasoning
    }
    
    decision_id = log_user_decision(decision)
    
    if decision_id:
        print(f"✅ Logged: {action} {ticker} @ ${price} x{quantity}")
        return True
    else:
        print(f"❌ Failed to log decision")
        return False

if __name__ == '__main__':
    # Check if command line args provided
    if len(sys.argv) > 2:
        # Quick mode: python decision_logger.py TICKER ACTION [PRICE] [QUANTITY] [REASONING]
        ticker = sys.argv[1]
        action = sys.argv[2]
        price = sys.argv[3] if len(sys.argv) > 3 else None
        quantity = sys.argv[4] if len(sys.argv) > 4 else None
        reasoning = ' '.join(sys.argv[5:]) if len(sys.argv) > 5 else ""
        
        log_decision_quick(ticker, action, price, quantity, reasoning)
    
    else:
        # Interactive mode
        log_decision_interactive()
