#!/usr/bin/env python3
"""
PRE-MARKET SETUP - Automated Portfolio Builder 🐺🌅

THE WOLF HUNTS AT DAWN.

WHAT IT DOES:
1. Runs wolf_pack.py scan at 8:30am ET (pre-market)
2. Builds 10-15 position portfolio (diversified)
3. Generates order queue
4. Ready to execute at 9:30am market open

AUTOMATION:
- Schedule: Daily at 8:30am ET (or run manually)
- Scan time: ~5-10 minutes
- Output: portfolio_orders.json for trader to execute

HOW TO USE:
1. Manual: python pre_market_setup.py
2. Scheduled: Use Windows Task Scheduler or cron

THE PACK DOESN'T SCRAMBLE AFTER THE OPEN. THE PACK IS READY AT THE OPEN.
"""

import os
import sys
import json
from datetime import datetime, time
from typing import List, Dict
import pytz

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our systems
from wolfpack.wolf_pack import WolfPack
from wolfpack.portfolio_builder import PortfolioBuilder, PortfolioPosition

class PreMarketSetup:
    """
    Pre-market automation for portfolio building
    
    WORKFLOW:
    1. Check if market is today (M-F)
    2. Run wolf_pack scan
    3. Build diversified portfolio
    4. Export orders to JSON
    5. Report to console (or notification)
    """
    
    def __init__(self):
        self.wolf_pack = WolfPack()
        self.portfolio_builder = PortfolioBuilder(
            target_positions=12,
            max_sector_allocation=0.30,  # 30% max per sector
            max_position_size=0.12,      # 12% max per position
            min_position_size=0.05       # 5% min per position
        )
        self.eastern = pytz.timezone('America/New_York')
        
    def is_market_day(self) -> bool:
        """Check if today is a market day (M-F, exclude holidays)"""
        now = datetime.now(self.eastern)
        
        # Check if weekend
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            print(f"⏸️  Weekend detected ({now.strftime('%A')}). Market closed.")
            return False
        
        # TODO: Add holiday check (NYSE calendar)
        # For now, assume M-F are market days
        
        return True
    
    def is_pre_market_time(self) -> bool:
        """Check if it's pre-market time (7:00am - 9:30am ET)"""
        now = datetime.now(self.eastern)
        current_time = now.time()
        
        # Pre-market: 7:00am - 9:30am ET
        pre_market_start = time(7, 0)
        market_open = time(9, 30)
        
        if pre_market_start <= current_time < market_open:
            return True
        else:
            print(f"⏰ Current time: {now.strftime('%I:%M %p')} ET")
            if current_time < pre_market_start:
                print(f"   Too early. Pre-market starts at 7:00am ET.")
            else:
                print(f"   Market already open. Run this before 9:30am ET.")
            return False
    
    def get_account_value(self) -> float:
        """
        Get current account value from Alpaca
        
        TODO: Integrate with Alpaca API
        For now, return default
        """
        # TODO: Connect to Alpaca and get real account value
        default_value = 100000.0
        print(f"💰 Account value: ${default_value:,.2f} (default)")
        return default_value
    
    def run_scan(self) -> List[Dict]:
        """
        Run wolf_pack scan to find opportunities
        
        Returns:
            List of opportunities with scores, prices, reasoning
        """
        print("\n" + "="*70)
        print("🔍 RUNNING WOLF PACK SCAN")
        print("="*70)
        
        # Initialize wolf pack
        print("Initializing wolf pack...")
        self.wolf_pack.initialize()
        
        # Run scan
        print("\nScanning universe...")
        opportunities = self.wolf_pack.run_convergence_scan()
        
        # Filter and format results
        scan_results = []
        
        if opportunities:
            print(f"\n✅ Found {len(opportunities)} opportunities")
            
            for opp in opportunities:
                # Extract data
                ticker = opp.get('ticker', 'UNKNOWN')
                score = opp.get('convergence_score', 0)
                
                # Get current price (from opportunity or fetch)
                price = opp.get('current_price', 0)
                if price == 0:
                    # Try to get from market data
                    try:
                        import yfinance as yf
                        ticker_data = yf.Ticker(ticker)
                        price = ticker_data.info.get('currentPrice', 0)
                    except:
                        print(f"   ⚠️  Could not get price for {ticker}")
                        continue
                
                reasoning = opp.get('reasoning', 'Convergence detected')
                
                scan_results.append({
                    'ticker': ticker,
                    'score': score,
                    'price': price,
                    'reasoning': reasoning
                })
        else:
            print("⚠️  No opportunities found in scan")
        
        return scan_results
    
    def build_portfolio(self, scan_results: List[Dict], account_value: float) -> List[PortfolioPosition]:
        """
        Build diversified portfolio from scan results
        
        Args:
            scan_results: Opportunities from scan
            account_value: Total account value
            
        Returns:
            List of portfolio positions
        """
        print("\n" + "="*70)
        print("🏗️  BUILDING PORTFOLIO")
        print("="*70)
        
        portfolio = self.portfolio_builder.build_portfolio(scan_results, account_value)
        
        if portfolio:
            self.portfolio_builder.print_portfolio_summary(portfolio)
        else:
            print("❌ Could not build portfolio (insufficient opportunities)")
        
        return portfolio
    
    def export_orders(self, portfolio: List[PortfolioPosition]) -> str:
        """
        Export portfolio to orders JSON
        
        Returns:
            Path to orders file
        """
        if not portfolio:
            print("❌ No portfolio to export")
            return None
        
        orders_file = self.portfolio_builder.export_to_trader(portfolio, 'portfolio_orders.json')
        
        return orders_file
    
    def run(self, force: bool = False):
        """
        Run complete pre-market setup
        
        Args:
            force: If True, skip time/day checks (for testing)
        """
        print("="*70)
        print("🐺 PRE-MARKET SETUP")
        print("="*70)
        print(f"Time: {datetime.now(self.eastern).strftime('%Y-%m-%d %I:%M %p')} ET")
        
        # Check if market day
        if not force and not self.is_market_day():
            return
        
        # Check if pre-market time
        if not force and not self.is_pre_market_time():
            print("\n💡 TIP: Run this between 7:00am - 9:30am ET for market open execution")
            return
        
        # Get account value
        account_value = self.get_account_value()
        
        # Run scan
        scan_results = self.run_scan()
        
        if not scan_results:
            print("\n❌ No opportunities found. No portfolio built.")
            return
        
        # Build portfolio
        portfolio = self.build_portfolio(scan_results, account_value)
        
        if not portfolio:
            print("\n❌ Could not build portfolio.")
            return
        
        # Export orders
        orders_file = self.export_orders(portfolio)
        
        # Final report
        print("\n" + "="*70)
        print("✅ PRE-MARKET SETUP COMPLETE")
        print("="*70)
        print(f"Portfolio: {len(portfolio)} positions")
        print(f"Orders file: {orders_file}")
        print(f"Total value: ${sum(p.shares * p.entry_price for p in portfolio):,.2f}")
        print("\n🎯 NEXT STEP:")
        print(f"   python wolf_pack_trader.py --execute {orders_file}")
        print("\n🐺 THE WOLF IS READY. MARKET OPENS AT 9:30AM ET.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pre-market portfolio setup')
    parser.add_argument('--force', action='store_true', 
                       help='Force run (skip time/day checks)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode (uses mock data)')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 TEST MODE: Using mock scan results\n")
        
        # Mock scan results
        mock_results = [
            {'ticker': 'NVDA', 'score': 95, 'price': 450.0, 'reasoning': '7-signal convergence + AI boom'},
            {'ticker': 'PLTR', 'score': 92, 'price': 25.0, 'reasoning': 'Government contracts + AI integration'},
            {'ticker': 'IONQ', 'score': 88, 'price': 15.0, 'reasoning': 'Quantum breakthrough'},
            {'ticker': 'MRNA', 'score': 85, 'price': 110.0, 'reasoning': 'Cancer vaccine trial'},
            {'ticker': 'RKLB', 'score': 83, 'price': 8.5, 'reasoning': 'Launch success'},
            {'ticker': 'CCJ', 'score': 81, 'price': 45.0, 'reasoning': 'Uranium demand'},
            {'ticker': 'CRWD', 'score': 80, 'price': 300.0, 'reasoning': 'Cybersecurity growth'},
            {'ticker': 'MARA', 'score': 78, 'price': 20.0, 'reasoning': 'Bitcoin rally'},
            {'ticker': 'AMD', 'score': 77, 'price': 180.0, 'reasoning': 'AI chip demand'},
            {'ticker': 'SNOW', 'score': 75, 'price': 180.0, 'reasoning': 'Cloud growth'},
            {'ticker': 'TSM', 'score': 74, 'price': 120.0, 'reasoning': 'Semiconductor demand'},
            {'ticker': 'IBRX', 'score': 73, 'price': 4.5, 'reasoning': 'Clinical trial data'}
        ]
        
        builder = PortfolioBuilder()
        portfolio = builder.build_portfolio(mock_results, 100000.0)
        builder.print_portfolio_summary(portfolio)
        builder.export_to_trader(portfolio)
        
    else:
        # Real run
        setup = PreMarketSetup()
        setup.run(force=args.force)


if __name__ == "__main__":
    main()
