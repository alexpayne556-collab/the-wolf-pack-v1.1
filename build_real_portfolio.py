#!/usr/bin/env python3
"""
REAL PORTFOLIO - With YOUR $1,400 Capital
"""

import json
from wolfpack.portfolio_builder import PortfolioBuilder

# Load opportunities
with open('data/morning_opportunities.json', 'r') as f:
    data = json.load(f)
    opportunities = data['opportunities']

# Convert to format portfolio builder expects
scan_results = []
for opp in opportunities:
    if opp['adjusted_score'] >= 80:  # Only high scores
        scan_results.append({
            'ticker': opp['ticker'],
            'score': opp['adjusted_score'],
            'price': opp['price'],
            'reasoning': f"{opp['price_change_5d']:+.1f}% 5-day, {opp['volume_ratio']:.1f}x volume"
        })

print("🐺 BUILDING PORTFOLIO WITH YOUR REAL CAPITAL")
print("="*70)
print(f"Account: $1,400 (YOUR actual capital)")
print(f"Max positions: 6")
print(f"Risk per trade: 2% ($28)")
print()

# Build portfolio with REAL capital
builder = PortfolioBuilder(
    target_positions=6,  # Not 12
    max_position_size=0.18,  # 18% max (~$250)
    min_position_size=0.14   # 14% min (~$195)
)

portfolio = builder.build_portfolio(scan_results, account_value=1400.0)

if portfolio:
    builder.print_portfolio_summary(portfolio)
    builder.export_to_trader(portfolio, 'portfolio_orders_REAL.json')
    
    print("\n" + "="*70)
    print("💰 REALITY CHECK:")
    print("="*70)
    total_value = sum(p.shares * p.entry_price for p in portfolio)
    total_pct = sum(p.allocation_pct for p in portfolio)
    
    print(f"Total capital: $1,400")
    print(f"Total deployed: ${total_value:,.2f} ({total_pct*100:.1f}%)")
    print(f"Cash remaining: ${1400 - total_value:,.2f}")
    print()
    print(f"Positions: {len(portfolio)}")
    print(f"Avg position size: ${total_value/len(portfolio):,.2f}")
    print()
    print("✅ THIS is your REAL portfolio for tomorrow.")
    print("="*70)
else:
    print("❌ Could not build portfolio")
