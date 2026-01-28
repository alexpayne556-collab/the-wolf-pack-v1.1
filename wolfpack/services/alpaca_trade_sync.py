#!/usr/bin/env python3
"""
🐺 ALPACA TRADE SYNC MODULE
Pulls your ENTIRE trade history from Alpaca and imports into learning engine

WHY THIS MATTERS:
- You've been trading manually on Alpaca/Robinhood
- That history contains YOUR patterns, YOUR edges, YOUR mistakes
- Instead of starting from zero, system starts SMART on Day 1
- Analyzes 50-100+ historical trades to know YOUR style immediately

The wolf learns from the WHOLE pack's history, not just future trades.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import yfinance as yf

# Alpaca imports
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import GetOrdersRequest
    from alpaca.trading.enums import OrderSide, QueryOrderStatus
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  Alpaca not installed. Run: pip install alpaca-py")

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.learning_engine import LearningEngine
from database import get_connection


class AlpacaTradeSync:
    """
    Syncs your Alpaca trade history into the learning engine
    
    What it does:
    1. Connects to Alpaca API
    2. Pulls ALL filled orders (last 90 days or more)
    3. Matches buy/sell pairs to reconstruct complete trades
    4. Calculates outcomes (profit/loss, hold time)
    5. Imports into learning engine database
    6. System immediately knows YOUR patterns
    """
    
    def __init__(self, paper_trading: bool = False):
        """
        Initialize Alpaca trade sync
        
        Args:
            paper_trading: If True, use paper trading account (default: False for live)
        """
        self.paper_trading = paper_trading
        self.client = None
        self.learning_engine = LearningEngine()
        
        # Load API keys
        load_dotenv()
        
        if paper_trading:
            api_key = os.getenv('ALPACA_PAPER_KEY_ID')
            secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
        else:
            api_key = os.getenv('ALPACA_LIVE_KEY_ID')
            secret_key = os.getenv('ALPACA_LIVE_SECRET_KEY')
        
        if not api_key or not secret_key:
            print(f"⚠️  Alpaca {'paper' if paper_trading else 'live'} API keys not found in .env")
            return
        
        if not ALPACA_AVAILABLE:
            print("⚠️  Alpaca library not installed")
            return
        
        try:
            self.client = TradingClient(api_key, secret_key, paper=paper_trading)
            print(f"✅ Connected to Alpaca {'paper' if paper_trading else 'live'} trading")
        except Exception as e:
            print(f"❌ Alpaca connection failed: {e}")
    
    def fetch_order_history(self, days_back: int = 90) -> List[Dict]:
        """
        Fetch all filled orders from Alpaca
        
        Args:
            days_back: How many days of history to fetch (default: 90)
        
        Returns:
            List of order dictionaries
        """
        
        if not self.client:
            print("❌ Alpaca not connected")
            return []
        
        try:
            # Get all filled orders - use string 'closed' for filled/closed orders
            request = GetOrdersRequest(
                status='closed',  # 'closed' includes all filled orders
                after=datetime.now() - timedelta(days=days_back)
            )
            
            orders = self.client.get_orders(filter=request)
            
            # Filter for only filled orders (exclude cancelled)
            orders = [o for o in orders if hasattr(o, 'filled_qty') and float(o.filled_qty) > 0]
            
            print(f"\n📊 Fetched {len(orders)} filled orders from last {days_back} days")
            
            # Convert to dictionaries
            order_list = []
            for order in orders:
                order_list.append({
                    'id': str(order.id),
                    'ticker': order.symbol,
                    'side': order.side.value,
                    'qty': float(order.filled_qty),
                    'price': float(order.filled_avg_price),
                    'timestamp': order.filled_at,
                    'order_type': order.type.value
                })
            
            return order_list
        
        except Exception as e:
            print(f"❌ Error fetching orders: {e}")
            return []
    
    def match_trades(self, orders: List[Dict]) -> List[Dict]:
        """
        Match buy/sell pairs to reconstruct complete trades
        
        Args:
            orders: List of order dictionaries
        
        Returns:
            List of complete trade dictionaries (entry + exit)
        """
        
        # Sort by timestamp
        orders = sorted(orders, key=lambda x: x['timestamp'])
        
        trades = []
        positions = {}  # Track open positions by ticker
        
        for order in orders:
            ticker = order['ticker']
            
            if order['side'] == 'buy':
                # Opening or adding to position
                if ticker not in positions:
                    positions[ticker] = []
                
                positions[ticker].append({
                    'entry_date': order['timestamp'],
                    'entry_price': order['price'],
                    'shares': order['qty'],
                    'order_id': order['id']
                })
            
            elif order['side'] == 'sell':
                # Closing position
                if ticker not in positions or not positions[ticker]:
                    print(f"⚠️  Sell without buy detected for {ticker} - skipping")
                    continue
                
                # FIFO: Match with oldest buy
                entry = positions[ticker].pop(0)
                
                # Calculate outcome
                entry_price = entry['entry_price']
                exit_price = order['price']
                shares = min(entry['shares'], order['qty'])  # Handle partial fills
                
                return_pct = ((exit_price - entry_price) / entry_price) * 100
                return_dollars = (exit_price - entry_price) * shares
                
                hold_time = (order['timestamp'] - entry['entry_date']).days
                if hold_time == 0:
                    hold_time_str = f"{(order['timestamp'] - entry['entry_date']).seconds // 3600}h"
                else:
                    hold_time_str = f"{hold_time}d"
                
                # Determine outcome
                if return_pct > 2:
                    outcome = "win"
                elif return_pct < -2:
                    outcome = "loss"
                else:
                    outcome = "breakeven"
                
                trades.append({
                    'ticker': ticker,
                    'entry_date': entry['entry_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    'entry_price': entry_price,
                    'exit_date': order['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'exit_price': exit_price,
                    'shares': shares,
                    'return_pct': return_pct,
                    'return_dollars': return_dollars,
                    'hold_time': hold_time,
                    'hold_time_str': hold_time_str,
                    'outcome': outcome,
                    'entry_order_id': entry['order_id'],
                    'exit_order_id': order['id']
                })
        
        # Report open positions
        open_positions = sum(len(v) for v in positions.values())
        if open_positions > 0:
            print(f"\n📌 {open_positions} open positions not included (still holding)")
        
        return trades
    
    def import_to_learning_engine(self, trades: List[Dict]) -> int:
        """
        Import matched trades into learning engine database
        
        Args:
            trades: List of complete trade dictionaries
        
        Returns:
            Number of trades imported
        """
        
        conn = get_connection()
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        
        for trade in trades:
            # Check if already imported (by entry date + ticker)
            cursor.execute('''
            SELECT COUNT(*) FROM trades
            WHERE ticker = ? AND date = ?
            ''', (trade['ticker'], trade['entry_date'][:10]))
            
            if cursor.fetchone()[0] > 0:
                skipped += 1
                continue
            
            # Import as new trade
            try:
                cursor.execute('''
                INSERT INTO trades (
                    date, ticker, action, shares, price,
                    thesis, notes, quality_score,
                    day2_pct, day5_pct, day10_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade['entry_date'][:10],
                    trade['ticker'],
                    'BUY',
                    trade['shares'],
                    trade['entry_price'],
                    f"Alpaca import - {trade['outcome']}",
                    f"Exit: {trade['exit_date'][:10]} at ${trade['exit_price']:.2f} ({trade['return_pct']:+.1f}%) - Held {trade['hold_time_str']}",
                    None,  # quality_score unknown
                    trade['return_pct'] if trade['hold_time'] >= 2 else None,
                    trade['return_pct'] if trade['hold_time'] >= 5 else None,
                    trade['return_pct'] if trade['hold_time'] >= 10 else None
                ))
                
                imported += 1
            
            except Exception as e:
                print(f"❌ Error importing {trade['ticker']}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Imported {imported} trades")
        if skipped > 0:
            print(f"⏭️  Skipped {skipped} duplicates")
        
        return imported
    
    def sync_all(self, days_back: int = 90) -> Dict:
        """
        Complete sync: Fetch → Match → Import
        
        Args:
            days_back: How many days of history to fetch
        
        Returns:
            Summary dictionary with stats
        """
        
        print(f"\n{'='*70}")
        print(f"🐺 ALPACA TRADE SYNC - IMPORTING YOUR HISTORY")
        print(f"{'='*70}\n")
        
        # Step 1: Fetch orders
        print("1️⃣ Fetching order history from Alpaca...")
        orders = self.fetch_order_history(days_back=days_back)
        
        if not orders:
            print("\n❌ No orders found or connection failed")
            return {'success': False}
        
        # Step 2: Match trades
        print("\n2️⃣ Matching buy/sell pairs...")
        trades = self.match_trades(orders)
        
        print(f"   ✅ Matched {len(trades)} complete trades")
        
        if not trades:
            print("\n⚠️  No complete trades found (all positions still open?)")
            return {'success': True, 'trades': 0}
        
        # Step 3: Import
        print("\n3️⃣ Importing to learning engine...")
        imported = self.import_to_learning_engine(trades)
        
        # Step 4: Analyze
        print("\n4️⃣ Analyzing your trading patterns...")
        patterns = self.analyze_imported_trades(trades)
        
        print(f"\n{'='*70}")
        print("✅ SYNC COMPLETE - SYSTEM KNOWS YOUR PATTERNS NOW")
        print(f"{'='*70}\n")
        
        return {
            'success': True,
            'orders_fetched': len(orders),
            'trades_matched': len(trades),
            'trades_imported': imported,
            'patterns': patterns
        }
    
    def analyze_imported_trades(self, trades: List[Dict]) -> Dict:
        """
        Analyze imported trades to discover YOUR patterns immediately
        
        Returns:
            Dictionary of discovered patterns
        """
        
        if not trades:
            return {}
        
        # Calculate stats
        wins = [t for t in trades if t['outcome'] == 'win']
        losses = [t for t in trades if t['outcome'] == 'loss']
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        
        avg_win = sum(t['return_pct'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['return_pct'] for t in losses) / len(losses) if losses else 0
        
        avg_hold_time = sum(t['hold_time'] for t in trades) / len(trades) if trades else 0
        
        # Find best tickers
        ticker_performance = {}
        for trade in trades:
            ticker = trade['ticker']
            if ticker not in ticker_performance:
                ticker_performance[ticker] = {'wins': 0, 'losses': 0, 'total_return': 0}
            
            if trade['outcome'] == 'win':
                ticker_performance[ticker]['wins'] += 1
            elif trade['outcome'] == 'loss':
                ticker_performance[ticker]['losses'] += 1
            
            ticker_performance[ticker]['total_return'] += trade['return_pct']
        
        # Sort by win rate
        best_tickers = sorted(
            [(ticker, data['wins'], data['losses'], data['total_return']) 
             for ticker, data in ticker_performance.items()
             if data['wins'] + data['losses'] >= 2],  # At least 2 trades
            key=lambda x: x[1] / (x[1] + x[2]) if x[1] + x[2] > 0 else 0,
            reverse=True
        )
        
        # Display results
        print(f"\n📊 YOUR TRADING PATTERNS (from {len(trades)} trades):")
        print(f"\n   Overall Stats:")
        print(f"   • Win Rate: {win_rate:.1f}% ({len(wins)}W / {len(losses)}L)")
        print(f"   • Avg Winner: {avg_win:+.1f}%")
        print(f"   • Avg Loser: {avg_loss:.1f}%")
        print(f"   • Avg Hold Time: {avg_hold_time:.1f} days")
        
        if best_tickers:
            print(f"\n   Your Best Tickers:")
            for ticker, wins, losses, total_return in best_tickers[:5]:
                ticker_win_rate = wins / (wins + losses) * 100
                print(f"   • {ticker}: {ticker_win_rate:.0f}% win rate ({wins}W/{losses}L), {total_return:+.1f}% total")
        
        print(f"\n   💡 Insights:")
        if win_rate > 60:
            print(f"   ✅ Strong win rate - system will prioritize your style")
        elif win_rate < 40:
            print(f"   ⚠️  Low win rate - system will learn to avoid your mistakes")
        
        if avg_win > abs(avg_loss) * 1.5:
            print(f"   ✅ You cut losers well - good risk management")
        elif avg_win < abs(avg_loss):
            print(f"   ⚠️  Winners smaller than losers - system will tighten stops")
        
        if avg_hold_time < 1:
            print(f"   📌 Day trader style - quick in/out")
        elif avg_hold_time > 5:
            print(f"   📌 Swing trader style - multi-day holds")
        
        return {
            'total_trades': len(trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_hold_time': avg_hold_time,
            'best_tickers': best_tickers[:5]
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print("🐺 ALPACA TRADE SYNC - IMPORT YOUR TRADING HISTORY")
    print(f"{'='*70}\n")
    
    print("This will:")
    print("1. Connect to your Alpaca account")
    print("2. Pull your trade history (last 90 days)")
    print("3. Match buy/sell pairs")
    print("4. Import into learning engine")
    print("5. Analyze YOUR patterns immediately")
    print()
    print("💡 After this, the system starts SMART - knows YOUR style from Day 1")
    print()
    
    # Ask paper or live
    choice = input("Import from (1) Paper Trading or (2) Live Trading? [1]: ").strip()
    paper = choice != '2'
    
    # Ask days back
    days_input = input("How many days of history? [90]: ").strip()
    days_back = int(days_input) if days_input else 90
    
    print()
    
    # Run sync
    syncer = AlpacaTradeSync(paper_trading=paper)
    
    if syncer.client:
        result = syncer.sync_all(days_back=days_back)
        
        if result['success']:
            print(f"\n🎉 SUCCESS! System now knows YOUR trading patterns")
            print(f"\n📊 Summary:")
            print(f"   • {result.get('orders_fetched', 0)} orders fetched")
            print(f"   • {result.get('trades_matched', 0)} trades matched")
            print(f"   • {result.get('trades_imported', 0)} trades imported")
            print()
            print("✅ Next: Run daily_monitor.py to see your patterns in action")
            print("✅ Learning engine now filters based on YOUR historical performance")
    else:
        print("\n❌ Sync failed - check API keys in .env")
        print("\nAdd to .env:")
        print("   ALPACA_PAPER_KEY_ID=your_key")
        print("   ALPACA_PAPER_SECRET_KEY=your_secret")
        print("   (or ALPACA_LIVE_KEY_ID / ALPACA_LIVE_SECRET_KEY for live)")
    
    print(f"\n{'='*70}")
    print("🐺 The wolf learns from the WHOLE pack's history, not just future trades")
    print(f"{'='*70}\n")
