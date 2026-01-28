"""
AUTO-TRADER: Execute paper trades on ALL buy signals from scanner
This will TEST the theories by placing orders on everything the system recommends

Usage: python auto_execute_scanner_results.py
"""

import sys
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from datetime import datetime

# Add src/core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'core'))
from convergence_engine_v2 import ConvergenceEngine

# Load environment
load_dotenv()
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_API_SECRET')

if not api_key or not api_secret:
    print("❌ ERROR: Alpaca API keys not found in .env file")
    sys.exit(1)

# Initialize
client = TradingClient(api_key, api_secret, paper=True)
engine = ConvergenceEngine()

def get_account_status():
    """Get current account info"""
    account = client.get_account()
    return {
        'account_number': account.account_number,
        'cash': float(account.cash),
        'portfolio_value': float(account.portfolio_value),
        'buying_power': float(account.buying_power)
    }

def calculate_position_size(price: float, cash_available: float, max_per_position: int = 100) -> int:
    """
    Calculate shares to buy based on available cash
    Conservative: $100 max per position for testing
    """
    target_dollars = min(max_per_position, cash_available * 0.01)  # 1% of cash max
    shares = int(target_dollars / price)
    return max(1, shares)  # Minimum 1 share

def place_paper_trade(ticker: str, shares: int, price: float, reason: str):
    """Execute paper trade on Alpaca"""
    try:
        order_data = MarketOrderRequest(
            symbol=ticker,
            qty=shares,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        
        order = client.submit_order(order_data=order_data)
        
        return {
            'success': True,
            'order_id': order.id,
            'ticker': ticker,
            'shares': shares,
            'estimated_cost': shares * price,
            'reason': reason,
            'status': order.status
        }
    except Exception as e:
        return {
            'success': False,
            'ticker': ticker,
            'error': str(e)
        }

def main():
    print("\n" + "="*80)
    print("🐺 WOLF PACK AUTO-TRADER: TESTING ALL THEORIES")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get account status
    account = get_account_status()
    print(f"📊 ALPACA PAPER ACCOUNT: {account['account_number']}")
    print(f"   Cash Available: ${account['cash']:,.2f}")
    print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
    print()
    
    # Run scanner
    print("🔍 RUNNING FULL SCANNER (100+ tickers)...")
    print()
    results = engine.scan_all()
    
    # Filter for BUY signals
    buy_signals = []
    
    # Criteria for BUY:
    # 1. TIER 1 FLAT-TO-BOOM (is_catching = True)
    # 2. Score >= 40 (Tier 1-2) AND not chasing
    for r in results:
        is_buy = False
        reason = ""
        
        if r.get('is_catching'):
            is_buy = True
            reason = f"FLAT-TO-BOOM SETUP ⚡ ({r['total_score']}/70 pts)"
        elif r['total_score'] >= 40 and not r.get('chase_check', {}).get('is_chasing'):
            is_buy = True
            reason = f"HIGH SCORE ({r['total_score']}/70 pts)"
        
        if is_buy:
            buy_signals.append({
                'ticker': r['ticker'],
                'score': r['total_score'],
                'price': r.get('price', 0),
                'reason': reason,
                'tier': r['tier']
            })
    
    print("\n" + "="*80)
    print(f"🎯 BUY SIGNALS FOUND: {len(buy_signals)} tickers")
    print("="*80)
    
    if not buy_signals:
        print("\n⚠️  No buy signals found. Criteria:")
        print("   - FLAT-TO-BOOM setups (is_catching)")
        print("   - OR Score >= 40 and not chasing")
        return
    
    # Display buy signals
    for i, signal in enumerate(buy_signals, 1):
        print(f"\n{i}. ${signal['ticker']}: {signal['score']}/70 pts")
        print(f"   Price: ${signal['price']:.2f}")
        print(f"   Reason: {signal['reason']}")
        print(f"   Tier: {signal['tier']}")
    
    # Confirm execution
    print("\n" + "="*80)
    print(f"💰 READY TO EXECUTE {len(buy_signals)} PAPER TRADES")
    print("="*80)
    print(f"Max per position: $100")
    print(f"Available cash: ${account['cash']:,.2f}")
    print()
    
    user_input = input("Execute trades? (yes/no): ").strip().lower()
    
    if user_input != 'yes':
        print("\n❌ Execution cancelled by user")
        return
    
    # Execute trades
    print("\n" + "="*80)
    print("🚀 EXECUTING PAPER TRADES")
    print("="*80)
    
    executed = []
    failed = []
    total_cost = 0
    
    for signal in buy_signals:
        ticker = signal['ticker']
        price = signal['price']
        
        if price <= 0:
            print(f"\n❌ ${ticker}: Invalid price (${price:.2f})")
            failed.append({'ticker': ticker, 'reason': 'Invalid price'})
            continue
        
        shares = calculate_position_size(price, account['cash'] - total_cost)
        
        if shares <= 0:
            print(f"\n⚠️  ${ticker}: Insufficient cash remaining")
            failed.append({'ticker': ticker, 'reason': 'Insufficient cash'})
            continue
        
        print(f"\n📤 ${ticker}: Buying {shares} shares @ ${price:.2f} = ${shares * price:.2f}")
        
        result = place_paper_trade(ticker, shares, price, signal['reason'])
        
        if result['success']:
            print(f"   ✅ Order ID: {result['order_id']} - Status: {result['status']}")
            executed.append(result)
            total_cost += result['estimated_cost']
        else:
            print(f"   ❌ Failed: {result['error']}")
            failed.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("📋 EXECUTION SUMMARY")
    print("="*80)
    print(f"Successful: {len(executed)}/{len(buy_signals)}")
    print(f"Failed: {len(failed)}/{len(buy_signals)}")
    print(f"Total Capital Deployed: ${total_cost:.2f}")
    
    if executed:
        print(f"\n✅ EXECUTED POSITIONS ({len(executed)}):")
        for e in executed:
            print(f"   ${e['ticker']}: {e['shares']} shares (${e['estimated_cost']:.2f}) - {e['reason']}")
    
    if failed:
        print(f"\n❌ FAILED ({len(failed)}):")
        for f in failed:
            reason = f.get('error', f.get('reason', 'Unknown'))
            print(f"   ${f['ticker']}: {reason}")
    
    print("\n" + "="*80)
    print("🐺 AUTO-TRADER COMPLETE")
    print("="*80)
    print(f"Results saved: Check Alpaca paper account")
    print(f"Next: Track performance over 30 days to prove theories")
    print()

if __name__ == "__main__":
    main()
