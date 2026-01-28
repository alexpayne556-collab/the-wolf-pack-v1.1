#!/usr/bin/env python3
"""
TEST PAPER TRADES - Execute trades on scanner finds
Testing the system with REAL paper trading execution
"""

import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Load environment variables
load_dotenv()

# Scanner finds from tonight (Jan 19)
SCANNER_FINDS = {
    'VRCA': {'reason': '2.7x volume spike'},
    'COSM': {'reason': '2.5x volume, insider buying'},
    'OCUL': {'reason': '2.0x volume, PDUFA Jan 28'},
    'GLSI': {'reason': '47/70 score, CEO buying $340K+, 24% short'},
    'BTAI': {'reason': '42/70 score, sNDA Q1 2026'},
    'PMCB': {'reason': '38/70 score, trading below cash'}
}

# Position sizes (small test amounts)
POSITION_SIZES = {
    'VRCA': 5,   # $5-10 stocks
    'COSM': 5,
    'OCUL': 10,
    'GLSI': 1,   # $24 stock
    'BTAI': 20,  # $1.84 stock  
    'PMCB': 30   # $0.94 stock
}

def execute_test_trades():
    """Execute paper trades for scanner finds"""
    
    # Get API keys from environment
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not api_secret:
        print("❌ Missing Alpaca API keys in .env")
        return
    
    # Initialize Alpaca client (PAPER trading)
    client = TradingClient(api_key, api_secret, paper=True)
    
    # Get account info
    account = client.get_account()
    print(f"\n💰 ALPACA PAPER ACCOUNT:")
    print(f"   Account: {account.account_number}")
    print(f"   Cash: ${float(account.cash):,.2f}")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
    
    # Check current positions
    positions = client.get_all_positions()
    print(f"\n📊 CURRENT POSITIONS: {len(positions)}")
    for pos in positions:
        pl_pct = float(pos.unrealized_plpc) * 100
        print(f"   {pos.symbol}: {pos.qty} shares @ ${pos.avg_entry_price} | P/L: {pl_pct:+.2f}%")
    
    # Execute test orders
    print(f"\n🐺 EXECUTING TEST ORDERS (Scanner Finds):\n")
    
    results = []
    
    for ticker, shares in POSITION_SIZES.items():
        try:
            reason = SCANNER_FINDS[ticker]['reason']
            print(f"   {ticker}: Buying {shares} shares ({reason})")
            
            # Create market order
            order_data = MarketOrderRequest(
                symbol=ticker,
                qty=shares,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = client.submit_order(order_data=order_data)
            
            results.append({
                'ticker': ticker,
                'shares': shares,
                'order_id': order.id,
                'status': order.status,
                'success': True
            })
            
            print(f"      ✅ Order submitted: {order.id} ({order.status})")
            
        except Exception as e:
            results.append({
                'ticker': ticker,
                'shares': shares,
                'error': str(e),
                'success': False
            })
            print(f"      ❌ Error: {e}")
    
    # Summary
    print(f"\n📈 EXECUTION SUMMARY:")
    success_count = sum(1 for r in results if r['success'])
    print(f"   Successful: {success_count}/{len(results)}")
    print(f"   Total tickers tested: {len(SCANNER_FINDS)}")
    
    # Show pending orders
    print(f"\n📋 CHECKING ORDERS:")
    orders = client.get_orders()
    for order in orders[:10]:  # Show last 10
        print(f"   {order.symbol}: {order.qty} shares | {order.status} | {order.created_at}")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("🐺 WOLF PACK PAPER TRADING TEST")
    print("Testing system with scanner finds")
    print("=" * 60)
    
    results = execute_test_trades()
    
    print("\n✅ TEST COMPLETE")
    print("=" * 60)
