#!/usr/bin/env python3
"""
PORTFOLIO EXECUTOR - Executes Multiple Orders at Market Open 🐺⚡

THE PROBLEM:
- wolf_pack_trader.py was designed for 1-2 trades
- We need to execute 10-15 orders FAST at market open

THE SOLUTION:
- Load portfolio_orders.json
- Submit all orders to Alpaca simultaneously
- Track execution status
- Log everything for learning

THE WOLF PACK STRIKES AS ONE.
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# Alpaca imports
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  Alpaca not installed. Run: pip install alpaca-py")

@dataclass
class OrderExecution:
    """Single order execution result"""
    ticker: str
    shares: int
    order_id: Optional[str]
    success: bool
    error: Optional[str]
    timestamp: datetime

class PortfolioExecutor:
    """
    Executes portfolio orders in Alpaca
    
    FEATURES:
    - Batch order submission (all at once)
    - Market orders (fast execution)
    - Error handling (track failures)
    - Execution logging (for learning)
    """
    
    def __init__(self, paper_trading: bool = True):
        """
        Initialize executor
        
        Args:
            paper_trading: Use paper trading (default True)
        """
        self.paper_trading = paper_trading
        self.client = None
        self.executions = []
        
        # Load .env from parent directory
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        if ALPACA_AVAILABLE:
            self._initialize_alpaca()
    
    def _initialize_alpaca(self):
        """Initialize Alpaca client"""
        try:
            if self.paper_trading:
                api_key = os.getenv('ALPACA_PAPER_KEY_ID')
                api_secret = os.getenv('ALPACA_PAPER_SECRET_KEY')
            else:
                api_key = os.getenv('ALPACA_LIVE_KEY_ID')
                api_secret = os.getenv('ALPACA_LIVE_SECRET_KEY')
            
            if not api_key or not api_secret:
                raise ValueError("Alpaca API keys not found in .env")
            
            self.client = TradingClient(api_key, api_secret, paper=self.paper_trading)
            
            # Test connection
            account = self.client.get_account()
            equity = float(account.equity)
            print(f"✅ Alpaca connected")
            print(f"   Account value: ${equity:,.2f}")
            print(f"   Buying power: ${float(account.buying_power):,.2f}")
            
        except Exception as e:
            print(f"❌ Alpaca initialization failed: {e}")
            self.client = None
    
    def load_orders(self, orders_file: str) -> List[Dict]:
        """
        Load orders from JSON file
        
        Args:
            orders_file: Path to portfolio_orders.json
            
        Returns:
            List of order dictionaries
        """
        if not os.path.exists(orders_file):
            print(f"❌ Orders file not found: {orders_file}")
            return []
        
        try:
            with open(orders_file, 'r') as f:
                orders = json.load(f)
            
            print(f"📋 Loaded {len(orders)} orders from {orders_file}")
            return orders
            
        except Exception as e:
            print(f"❌ Failed to load orders: {e}")
            return []
    
    def execute_order(self, order: Dict) -> OrderExecution:
        """
        Execute single order in Alpaca
        
        Args:
            order: Order dictionary with ticker, shares, etc.
            
        Returns:
            OrderExecution result
        """
        ticker = order['ticker']
        shares = order['shares']
        action = order.get('action', 'BUY')
        
        if not self.client:
            return OrderExecution(
                ticker=ticker,
                shares=shares,
                order_id=None,
                success=False,
                error="Alpaca not connected",
                timestamp=datetime.now()
            )
        
        try:
            # Create market order (fast execution at market open)
            order_side = OrderSide.BUY if action == 'BUY' else OrderSide.SELL
            
            market_order_data = MarketOrderRequest(
                symbol=ticker,
                qty=shares,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            alpaca_order = self.client.submit_order(order_data=market_order_data)
            
            return OrderExecution(
                ticker=ticker,
                shares=shares,
                order_id=alpaca_order.id,
                success=True,
                error=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return OrderExecution(
                ticker=ticker,
                shares=shares,
                order_id=None,
                success=False,
                error=str(e),
                timestamp=datetime.now()
            )
    
    def execute_portfolio(self, orders: List[Dict]) -> List[OrderExecution]:
        """
        Execute all orders in portfolio
        
        Args:
            orders: List of order dictionaries
            
        Returns:
            List of execution results
        """
        print("\n" + "="*70)
        print("⚡ EXECUTING PORTFOLIO ORDERS")
        print("="*70)
        print(f"Total orders: {len(orders)}")
        
        executions = []
        
        for i, order in enumerate(orders, 1):
            ticker = order['ticker']
            shares = order['shares']
            
            print(f"\n{i}. {ticker}: {shares} shares")
            
            # Execute
            execution = self.execute_order(order)
            executions.append(execution)
            
            if execution.success:
                print(f"   ✅ Order submitted: {execution.order_id}")
            else:
                print(f"   ❌ FAILED: {execution.error}")
        
        self.executions = executions
        return executions
    
    def print_execution_summary(self, executions: List[OrderExecution]):
        """Print summary of executions"""
        print("\n" + "="*70)
        print("📊 EXECUTION SUMMARY")
        print("="*70)
        
        successful = [e for e in executions if e.success]
        failed = [e for e in executions if not e.success]
        
        print(f"\n✅ Successful: {len(successful)}/{len(executions)}")
        for ex in successful:
            print(f"   {ex.ticker}: {ex.shares} shares (Order: {ex.order_id})")
        
        if failed:
            print(f"\n❌ Failed: {len(failed)}/{len(executions)}")
            for ex in failed:
                print(f"   {ex.ticker}: {ex.error}")
        
        print("\n" + "="*70)
    
    def save_execution_log(self, executions: List[OrderExecution], log_file: str = 'logs/execution_log.json'):
        """
        Save execution results to log file
        
        Args:
            executions: List of execution results
            log_file: Path to log file
        """
        # Create logs directory if needed
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Load existing log
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []
        
        # Add new executions
        for ex in executions:
            log_entry = {
                'timestamp': ex.timestamp.isoformat(),
                'ticker': ex.ticker,
                'shares': ex.shares,
                'order_id': str(ex.order_id) if ex.order_id else None,
                'success': ex.success,
                'error': ex.error
            }
            log_data.append(log_entry)
        
        # Save
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\n💾 Execution log saved: {log_file}")
    
    def run(self, orders_file: str = 'portfolio_orders.json'):
        """
        Complete execution workflow
        
        Args:
            orders_file: Path to orders JSON file
        """
        print("="*70)
        print("🐺 PORTFOLIO EXECUTOR")
        print("="*70)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
        
        # Load orders
        orders = self.load_orders(orders_file)
        
        if not orders:
            print("\n❌ No orders to execute")
            return
        
        # Execute
        executions = self.execute_portfolio(orders)
        
        # Summary
        self.print_execution_summary(executions)
        
        # Save log
        self.save_execution_log(executions)
        
        # Done
        successful = len([e for e in executions if e.success])
        print(f"\n🎯 EXECUTION COMPLETE: {successful}/{len(executions)} orders filled")
        
        if successful > 0:
            print(f"\n🐺 THE PACK IS IN POSITION. NOW WE WATCH. AWOOOO.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Execute portfolio orders')
    parser.add_argument('--orders', default='portfolio_orders.json',
                       help='Path to orders JSON file')
    parser.add_argument('--live', action='store_true',
                       help='Use LIVE trading (default: paper)')
    
    args = parser.parse_args()
    
    # Confirm if live trading
    if args.live:
        print("\n⚠️  WARNING: LIVE TRADING MODE")
        confirm = input("Are you sure? Type 'YES' to continue: ")
        if confirm != 'YES':
            print("Cancelled.")
            return
    
    # Execute
    executor = PortfolioExecutor(paper_trading=not args.live)
    executor.run(args.orders)


if __name__ == "__main__":
    main()
