"""
🐺 WOLF PACK MAIN RUNNER - THE ORCHESTRATOR
Built: January 20, 2026

This is the SINGLE ENTRY POINT that runs the entire Wolf Pack system.
One script to rule them all.

Schedule:
- 4:00 AM: Wake up, premarket scan
- 9:30 AM: Market open - execute best opportunities
- 12:00 PM: Midday check and position management
- 4:00 PM: Market close analysis
- 6:00 PM: After hours scan and learning review

Usage:
    python wolf_pack_runner.py              # Full autonomous mode
    python wolf_pack_runner.py --scan       # Just scan, no trades
    python wolf_pack_runner.py --dashboard  # Launch dashboards only
    python wolf_pack_runner.py --status     # Show current status
"""

import os
import sys
import time
import argparse
import schedule
from datetime import datetime, time as dtime
from typing import Dict, List, Optional
import json
import threading

# Add wolf_brain to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Wolf Pack components
try:
    from wolf_brain.brain_core import WolfBrain
    from wolf_brain.strategy_plugins import StrategyPluginManager
    from wolf_brain.memory_system import MemorySystem
    from wolf_brain.universe_scanner import UniverseScanner
    from wolf_brain.autonomous_trader import AutonomousTrader, TradeStrategy
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("   Make sure you're running from the src directory")


class WolfPackRunner:
    """
    🐺 THE WOLF PACK ORCHESTRATOR
    
    Coordinates all Wolf Pack components:
    - Brain (thinking/reasoning)
    - Scanner (finding opportunities)
    - Trader (executing trades)
    - Memory (learning from everything)
    """
    
    def __init__(self, paper_trading: bool = True, auto_trade: bool = False):
        """
        Initialize the Wolf Pack
        
        Args:
            paper_trading: Use paper trading (ALWAYS True for safety)
            auto_trade: If True, execute trades automatically
        """
        print("\n" + "="*80)
        print("🐺 INITIALIZING WOLF PACK SYSTEM")
        print("="*80 + "\n")
        
        self.paper_trading = paper_trading
        self.auto_trade = auto_trade
        self.running = False
        
        # Initialize components
        print("🧠 Loading Wolf Brain...")
        self.brain = WolfBrain()
        
        print("📚 Loading Strategy Plugins...")
        self.strategies = StrategyPluginManager()
        
        print("💾 Loading Memory System...")
        self.memory = MemorySystem()
        
        print("🔍 Loading Universe Scanner...")
        self.scanner = UniverseScanner()
        
        print("🤖 Loading Autonomous Trader...")
        self.trader = AutonomousTrader(paper_trading=paper_trading)
        
        # State tracking
        self.last_scan_results = None
        self.pending_opportunities = []
        self.session_stats = {
            'scans_run': 0,
            'opportunities_found': 0,
            'trades_executed': 0,
            'positions_managed': 0
        }
        
        print("\n✅ Wolf Pack System initialized!")
        print(f"   Mode: {'PAPER' if paper_trading else '⚠️ LIVE'}")
        print(f"   Auto-trade: {'ENABLED' if auto_trade else 'DISABLED'}")
        print(f"   Brain: {'🟢 ONLINE' if self.brain.ollama_connected else '🔴 OFFLINE'}")
    
    # ============ CORE OPERATIONS ============
    
    def morning_routine(self):
        """
        4:00 AM - Wake up and prepare
        - Scan for premarket movers
        - Get brain's game plan
        - Prepare watchlist
        """
        print("\n" + "="*80)
        print(f"🌅 MORNING ROUTINE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        # Brain planning
        if self.brain.ollama_connected:
            print("\n🧠 Brain generating morning game plan...")
            game_plan = self.brain.morning_planning()
            print(f"\n{game_plan[:500]}...")  # First 500 chars
        
        # Scan universe
        print("\n🔍 Running morning universe scan...")
        results = self.scanner.scan_for_opportunities(limit=20)
        self.last_scan_results = results
        self.session_stats['scans_run'] += 1
        
        # Summarize findings
        steady = results['steady_setups']
        head = results['head_hunter_setups']
        
        print(f"\n📊 MORNING SCAN RESULTS:")
        print(f"   Steady Hunter setups: {len(steady)}")
        print(f"   Head Hunter setups: {len(head)}")
        
        if steady:
            print(f"\n   Top Steady Setups:")
            for setup in steady[:5]:
                print(f"      {setup['ticker']}: Score {setup['score']} - {', '.join(setup['reasons'][:2])}")
        
        if head:
            print(f"\n   Top Head Hunter Setups:")
            for setup in head[:3]:
                print(f"      {setup['ticker']}: Score {setup['score']} - {', '.join(setup['reasons'][:2])}")
        
        self.session_stats['opportunities_found'] += len(steady) + len(head)
    
    def market_open_routine(self):
        """
        9:30 AM - Market opens
        - Evaluate best opportunities
        - Execute trades if auto_trade enabled
        """
        print("\n" + "="*80)
        print(f"🔔 MARKET OPEN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        if not self.last_scan_results:
            print("⚠️  No scan results available. Running quick scan...")
            self.last_scan_results = self.scanner.scan_for_opportunities(limit=10)
        
        steady = self.last_scan_results['steady_setups']
        head = self.last_scan_results['head_hunter_setups']
        
        # Get brain's picks
        if self.brain.ollama_connected and (steady or head):
            print("\n🧠 Brain analyzing top opportunities...")
            for setup in (steady + head)[:3]:
                ticker = setup['ticker']
                data = setup['data']
                
                analysis = self.brain.reason_about_opportunity(ticker, data)
                print(f"\n{ticker}: {analysis[:300]}...")
        
        # Execute trades if auto mode
        if self.auto_trade:
            print("\n🤖 Auto-trade mode - executing top picks...")
            
            # Execute top 2 steady
            for setup in steady[:2]:
                trade = self.trader.execute_opportunity(setup)
                if trade:
                    self.session_stats['trades_executed'] += 1
                    self.memory.store_trade_entry(
                        ticker=setup['ticker'],
                        strategy=setup['strategy'],
                        entry_price=setup['data']['current_price'],
                        position_size=trade.quantity,
                        setup_quality=setup['score'],
                        reasoning=str(setup['reasons'])
                    )
            
            # Execute top 1 head hunter (higher risk, fewer positions)
            for setup in head[:1]:
                trade = self.trader.execute_opportunity(setup)
                if trade:
                    self.session_stats['trades_executed'] += 1
        else:
            print("\n📋 Auto-trade disabled. Top opportunities for manual review:")
            for setup in (steady + head)[:5]:
                print(f"   {setup['ticker']}: {setup['strategy']} | Score {setup['score']}")
    
    def midday_check(self):
        """
        12:00 PM - Midday position management
        - Check all positions
        - Manage exits (stops, targets)
        - Look for new entries
        """
        print("\n" + "="*80)
        print(f"☀️ MIDDAY CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        # Manage existing positions
        print("\n📊 Managing positions...")
        self.trader.manage_positions()
        self.session_stats['positions_managed'] += 1
        
        # Quick scan for new opportunities
        print("\n🔍 Quick scan for new setups...")
        results = self.scanner.scan_for_opportunities(limit=10)
        self.last_scan_results = results
        self.session_stats['scans_run'] += 1
        
        # Show top new setups
        all_setups = results['steady_setups'] + results['head_hunter_setups']
        if all_setups:
            print(f"   Found {len(all_setups)} potential setups")
            for setup in all_setups[:3]:
                print(f"      {setup['ticker']}: {setup['strategy']} | Score {setup['score']}")
    
    def market_close_routine(self):
        """
        4:00 PM - Market close
        - Final position check
        - Day summary
        - Brain reflection
        """
        print("\n" + "="*80)
        print(f"🔔 MARKET CLOSE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        # Final position management
        self.trader.manage_positions()
        
        # Day summary
        print("\n📊 DAY SUMMARY:")
        print(f"   Scans run: {self.session_stats['scans_run']}")
        print(f"   Opportunities found: {self.session_stats['opportunities_found']}")
        print(f"   Trades executed: {self.session_stats['trades_executed']}")
        
        # Show open positions
        positions = self.trader.get_open_positions()
        if positions:
            print(f"\n   Open positions ({len(positions)}):")
            for ticker, pos in positions.items():
                print(f"      {ticker}: Entry ${pos['entry_price']:.2f} | Strategy: {pos['strategy']}")
        
        # Brain reflection
        if self.brain.ollama_connected:
            print("\n🧠 Brain generating evening review...")
            review = self.brain.evening_review()
            print(f"\n{review[:500]}...")
    
    def after_hours_routine(self):
        """
        6:00 PM - After hours
        - Scan AH movers
        - Learn from today's trades
        - Prepare for tomorrow
        """
        print("\n" + "="*80)
        print(f"🌙 AFTER HOURS - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        # Get learning insights
        print("\n📚 Memory system insights:")
        insights = self.memory.get_learning_insights()
        
        if insights['top_performing_setups']:
            print(f"   Best setup: {insights['top_performing_setups'][0] if insights['top_performing_setups'] else 'N/A'}")
        
        print(f"   Lessons learned: {insights['total_lessons']}")
        print(f"   Win rate: {insights.get('win_rate', 'N/A')}")
        
        print("\n✅ Wolf Pack ready for tomorrow!")
    
    # ============ MANUAL OPERATIONS ============
    
    def run_scan(self) -> Dict:
        """Run a manual scan"""
        print("\n🔍 Running manual scan...")
        results = self.scanner.scan_for_opportunities(limit=20)
        self.last_scan_results = results
        self.session_stats['scans_run'] += 1
        return results
    
    def analyze_ticker(self, ticker: str) -> Dict:
        """Get full analysis of a ticker"""
        print(f"\n🔎 Analyzing {ticker}...")
        
        # Get data
        ticker_data = self.scanner.scan_tickers([ticker])
        
        if ticker not in ticker_data:
            return {'error': f'Could not fetch data for {ticker}'}
        
        data = ticker_data[ticker]
        
        # Run through all strategies
        strategy_results = self.strategies.analyze_with_all(ticker, data['data'])
        
        # Get brain reasoning
        brain_analysis = None
        if self.brain.ollama_connected:
            brain_analysis = self.brain.reason_about_opportunity(ticker, data['data'])
        
        return {
            'ticker': ticker,
            'data': data,
            'strategy_results': strategy_results,
            'brain_analysis': brain_analysis
        }
    
    def execute_trade(self, ticker: str, strategy: str = 'steady') -> Dict:
        """Manually execute a trade"""
        print(f"\n🤖 Manual trade execution: {ticker}")
        
        # Get current data
        ticker_data = self.scanner.scan_tickers([ticker])
        if ticker not in ticker_data:
            return {'error': f'Could not fetch data for {ticker}'}
        
        data = ticker_data[ticker]['data']
        
        # Create opportunity format
        opportunity = {
            'ticker': ticker,
            'strategy': 'STEADY_HUNTER' if strategy == 'steady' else 'HEAD_HUNTER',
            'score': 60,  # Manual trades get moderate score
            'data': data,
            'reasons': ['Manual trade execution']
        }
        
        # Execute
        trade = self.trader.execute_opportunity(opportunity)
        
        if trade:
            self.session_stats['trades_executed'] += 1
            return {
                'success': True,
                'trade_id': trade.id,
                'ticker': ticker,
                'quantity': trade.quantity,
                'price': trade.price
            }
        else:
            return {'success': False, 'error': 'Trade execution failed'}
    
    def get_status(self) -> Dict:
        """Get full system status"""
        return {
            'system': {
                'running': self.running,
                'paper_trading': self.paper_trading,
                'auto_trade': self.auto_trade
            },
            'brain': {
                'connected': self.brain.ollama_connected,
                'model': self.brain.model_name
            },
            'trader': self.trader.get_status(),
            'scanner': {
                'universe_size': len(self.scanner.universe.get_full_universe())
            },
            'session': self.session_stats
        }
    
    # ============ SCHEDULED RUNNING ============
    
    def setup_schedule(self):
        """Setup the daily schedule"""
        # Morning prep (4:00 AM ET)
        schedule.every().day.at("04:00").do(self.morning_routine)
        
        # Market open (9:30 AM ET)
        schedule.every().day.at("09:30").do(self.market_open_routine)
        
        # Midday (12:00 PM ET)
        schedule.every().day.at("12:00").do(self.midday_check)
        
        # Market close (4:00 PM ET)
        schedule.every().day.at("16:00").do(self.market_close_routine)
        
        # After hours (6:00 PM ET)
        schedule.every().day.at("18:00").do(self.after_hours_routine)
        
        print("📅 Schedule configured:")
        print("   04:00 - Morning routine")
        print("   09:30 - Market open")
        print("   12:00 - Midday check")
        print("   16:00 - Market close")
        print("   18:00 - After hours")
    
    def run_forever(self):
        """Run the Wolf Pack continuously"""
        self.running = True
        self.setup_schedule()
        
        print("\n🐺 Wolf Pack running! Press Ctrl+C to stop.\n")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Wolf Pack shutting down...")
            self.running = False
    
    def run_now(self):
        """Run all routines immediately (for testing)"""
        print("\n🐺 Running all routines NOW (test mode)...\n")
        
        self.morning_routine()
        time.sleep(2)
        
        self.market_open_routine()
        time.sleep(2)
        
        self.midday_check()
        time.sleep(2)
        
        self.market_close_routine()
        time.sleep(2)
        
        self.after_hours_routine()
        
        print("\n✅ All routines complete!")


def launch_dashboards():
    """Launch the dashboards in separate processes"""
    import subprocess
    
    print("\n📊 Launching dashboards...")
    
    # Get paths
    wolf_brain_dir = os.path.dirname(os.path.abspath(__file__))
    portfolio_dash = os.path.join(wolf_brain_dir, 'dashboards', 'portfolio_dashboard.py')
    trading_dash = os.path.join(wolf_brain_dir, 'dashboards', 'trading_dashboard.py')
    
    # Launch portfolio dashboard
    print("   Launching Portfolio Dashboard (port 8050)...")
    subprocess.Popen([sys.executable, portfolio_dash], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
    
    # Launch trading dashboard
    print("   Launching Trading Dashboard (port 8051)...")
    subprocess.Popen([sys.executable, trading_dash],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
    
    print("\n🌐 Dashboards running at:")
    print("   Portfolio: http://localhost:8050")
    print("   Trading:   http://localhost:8051")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='🐺 Wolf Pack Trading System')
    parser.add_argument('--scan', action='store_true', help='Run a scan only')
    parser.add_argument('--dashboard', action='store_true', help='Launch dashboards')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--auto', action='store_true', help='Enable auto-trading')
    parser.add_argument('--test', action='store_true', help='Run all routines immediately')
    parser.add_argument('--ticker', type=str, help='Analyze specific ticker')
    
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🐺 W O L F   P A C K   T R A D I N G   S Y S T E M 🐺    ║
    ║                                                              ║
    ║     "The pack hunts as one, thinks as one, wins as one"      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    if args.dashboard:
        launch_dashboards()
        input("\nPress Enter to exit...")
        return
    
    # Initialize the Wolf Pack
    wolf_pack = WolfPackRunner(
        paper_trading=True,  # ALWAYS paper for safety
        auto_trade=args.auto
    )
    
    if args.status:
        status = wolf_pack.get_status()
        print("\n📊 WOLF PACK STATUS:")
        print(json.dumps(status, indent=2, default=str))
        return
    
    if args.scan:
        results = wolf_pack.run_scan()
        print(f"\n✅ Scan complete!")
        print(f"   Steady setups: {len(results['steady_setups'])}")
        print(f"   Head hunter setups: {len(results['head_hunter_setups'])}")
        return
    
    if args.ticker:
        analysis = wolf_pack.analyze_ticker(args.ticker)
        print(f"\n📊 ANALYSIS: {args.ticker}")
        print(json.dumps(analysis, indent=2, default=str)[:2000])
        return
    
    if args.test:
        wolf_pack.run_now()
        return
    
    # Default: run forever
    wolf_pack.run_forever()


if __name__ == "__main__":
    main()
