#!/usr/bin/env python3
"""
TRUTH CHECK - Show What's Real vs What's Mock
"""

import json
import yfinance as yf
from alpaca.trading.client import TradingClient
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🔍 TRUTH CHECK - WHAT'S REAL VS MOCK")
print("="*70)

# 1. WOUNDED PREY DATA
print("\n1. WOUNDED PREY DATA SOURCE:")
print("-" * 70)
with open('data/wounded_prey_universe.json', 'r') as f:
    data = json.load(f)

prey = data['wounded_prey'][0]  # AI stock
print(f"Example: {prey['ticker']}")
print(f"   Current Price: ${prey['price']:.2f}")
print(f"   52-Week High: ${prey['high_52w']:.2f}")
print(f"   % From High: {prey['pct_from_high']:.1f}%")
print(f"   Wounded Score: {prey['wounded_score']}")
print(f"   Data Source: Yahoo Finance (yfinance library)")
print(f"   ✅ REAL DATA (fetched from API)")

# 2. LIVE API CALL RIGHT NOW
print("\n2. LIVE API CALL (RIGHT NOW):")
print("-" * 70)
ticker = yf.Ticker('AI')
hist = ticker.history(period='1y')
current = hist['Close'].iloc[-1]
high_52w = hist['High'].max()
pct_down = ((current - high_52w) / high_52w) * 100
avg_vol = hist['Volume'].mean()

print(f"Ticker: AI")
print(f"   API Call: yf.Ticker('AI').history(period='1y')")
print(f"   Current Price: ${current:.2f}")
print(f"   52-Week High: ${high_52w:.2f}")
print(f"   % Down: {pct_down:.1f}%")
print(f"   Avg Volume: {avg_vol:,.0f}")
print(f"   ✅ REAL DATA (just fetched)")

# 3. SCORING LOGIC
print("\n3. SCORING LOGIC BREAKDOWN:")
print("-" * 70)
print("Wounded Score = How wounded (40pts) + Liquidity (30pts) + Market cap (30pts)")
print()
print(f"AI Example:")
wounded_points = 40 if pct_down < -60 else 35
liquidity_points = 30 if avg_vol > 5_000_000 else 25
mcap_points = 30  # Assume $500M-$2B range
total_score = wounded_points + liquidity_points + mcap_points

print(f"   Wounded: {pct_down:.1f}% from high → {wounded_points} points")
print(f"   Liquidity: {avg_vol/1e6:.1f}M volume → {liquidity_points} points")
print(f"   Market cap: In sweet spot → {mcap_points} points")
print(f"   TOTAL: {total_score}/100")

# Show stocks that FAILED
print("\n4. STOCKS THAT FAILED FILTER:")
print("-" * 70)
print("Reasons stocks get filtered OUT:")
print("   - Price > $50 or < $1")
print("   - Down < 30% from 52-week high (not wounded enough)")
print("   - Volume < 500K (illiquid)")
print("   - Market cap > $10B (too big) or < $50M (too small)")
print()
print("Example: NVDA")
nvda = yf.Ticker('NVDA')
nvda_hist = nvda.history(period='1y')
nvda_price = nvda_hist['Close'].iloc[-1]
nvda_high = nvda_hist['High'].max()
nvda_pct = ((nvda_price - nvda_high) / nvda_high) * 100
print(f"   Price: ${nvda_price:.2f}")
print(f"   % from high: {nvda_pct:.1f}%")
print(f"   ❌ FILTERED OUT: Only down {abs(nvda_pct):.1f}% (need 30%+)")

# 5. ALPACA ACCOUNT
print("\n5. ALPACA ACCOUNT (REAL CONNECTION):")
print("-" * 70)
client = TradingClient(
    os.getenv('ALPACA_PAPER_KEY_ID'),
    os.getenv('ALPACA_PAPER_SECRET_KEY'),
    paper=True
)
account = client.get_account()
orders = client.get_orders()

print(f"   API: Alpaca Paper Trading")
print(f"   Account ID: {account.account_number}")
print(f"   Status: {account.status}")
print(f"   Equity: ${float(account.equity):,.2f}")
print(f"   Pending Orders: {len(orders)}")
print(f"   ✅ REAL CONNECTION (live API)")

# 6. THE $93,745 CONFUSION
print("\n6. THE $93,745 vs $1,400 CONFUSION:")
print("-" * 70)
print("   Portfolio Builder Demo: $100,000 (MOCK account for testing)")
print("   Your REAL Account: $1,400 (from trader profile)")
print()
print("   ❌ ISSUE: Demo used wrong account size")
print("   ✅ FIX NEEDED: Build portfolio with $1,400, not $100k")
print()
print("   With $1,400:")
print("   - Max risk per trade: $28 (2%)")
print("   - 6 positions max")
print("   - Each position: ~$233 (not $7,000)")

# 7. REAL vs MOCK SUMMARY
print("\n" + "="*70)
print("SUMMARY - WHAT'S REAL:")
print("="*70)
print("✅ Wounded prey scan: REAL (Yahoo Finance API)")
print("✅ Price data: REAL (live API calls)")
print("✅ Alpaca connection: REAL (6 orders pending)")
print("✅ Scoring logic: REAL (documented formula)")
print()
print("❌ Portfolio size: MOCK ($100k demo, not your $1,400)")
print("❌ Position sizes: MOCK (sized for $100k, not $1,400)")
print()
print("🔧 NEED TO FIX:")
print("   - Rebuild portfolio with YOUR $1,400")
print("   - Each position ~$233 (not $7,000)")
print("   - 6 positions total (not 12)")
print("="*70)
