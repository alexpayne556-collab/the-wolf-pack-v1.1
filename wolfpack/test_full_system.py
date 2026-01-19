#!/usr/bin/env python3
"""
WOLF PACK SYSTEM TEST
Tests ALL major components to verify everything is working
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Load .env from root
root_env = Path(__file__).parent.parent / '.env'
if root_env.exists():
    from dotenv import load_dotenv
    load_dotenv(root_env)

print("=" * 70)
print("🐺 WOLF PACK - COMPREHENSIVE SYSTEM TEST")
print("=" * 70)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

results = {}

# ============================================================================
# TEST 1: Core Imports
# ============================================================================
print("📦 TEST 1: Core Module Imports")
print("-" * 40)

modules = [
    ("wolf_pack", "WolfPack", "Main convergence engine"),
    ("wolf_pack_trader", "WolfPackTrader", "Alpaca trader bot"),
    ("services.convergence_service", "ConvergenceEngine", "7-signal convergence"),
    ("services.trade_learner", "TradeLearner", "Self-learning system"),
    ("services.trading_rules", "TenCommandments", "Market Wizards' rules"),
    ("services.risk_manager", "RiskManager", "Kelly Criterion"),
    ("services.pivotal_point_tracker", "PivotalPointTracker", "Livermore patterns"),
]

for module, class_name, description in modules:
    try:
        exec(f"from {module} import {class_name}")
        print(f"   ✅ {class_name}: {description}")
        results[class_name] = True
    except ImportError as e:
        print(f"   ❌ {class_name}: {e}")
        results[class_name] = False

print()

# ============================================================================
# TEST 2: Alpaca Connection
# ============================================================================
print("🔌 TEST 2: Alpaca Paper Trading Connection")
print("-" * 40)

try:
    from alpaca.trading.client import TradingClient
    
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_API_SECRET')
    
    if api_key and api_secret:
        client = TradingClient(api_key, api_secret, paper=True)
        account = client.get_account()
        
        print(f"   ✅ Connected to Alpaca")
        print(f"   💰 Portfolio Value: ${float(account.portfolio_value):,.2f}")
        print(f"   💵 Buying Power: ${float(account.buying_power):,.2f}")
        print(f"   📊 Account Status: {account.status}")
        results['Alpaca'] = True
    else:
        print("   ❌ API keys not found in .env")
        results['Alpaca'] = False
        
except Exception as e:
    print(f"   ❌ Alpaca connection failed: {e}")
    results['Alpaca'] = False

print()

# ============================================================================
# TEST 3: API Keys Validation
# ============================================================================
print("🔑 TEST 3: API Keys Configured")
print("-" * 40)

api_keys = [
    ("ALPACA_API_KEY", "Alpaca Trading"),
    ("ALPACA_SECRET_KEY", "Alpaca Secret"),
    ("FINNHUB_API_KEY", "Finnhub (Earnings)"),
    ("NEWSAPI_KEY", "NewsAPI (Sentiment)"),
    ("ALPHAVANTAGE_API_KEY", "Alpha Vantage"),
    ("POLYGON_API_KEY", "Polygon.io"),
]

for key, description in api_keys:
    value = os.getenv(key)
    if value and len(value) > 5:
        print(f"   ✅ {description}: Configured")
    else:
        print(f"   ⚠️ {description}: Not configured (optional)")

print()

# ============================================================================
# TEST 4: Data Fetching (yfinance)
# ============================================================================
print("📈 TEST 4: Market Data Fetching")
print("-" * 40)

try:
    import yfinance as yf
    
    # Test with IBRX (our validated trade)
    ticker = yf.Ticker("IBRX")
    hist = ticker.history(period="5d")
    
    if not hist.empty:
        current_price = hist['Close'].iloc[-1]
        print(f"   ✅ yfinance working")
        print(f"   📊 IBRX current price: ${current_price:.2f}")
        results['yfinance'] = True
    else:
        print("   ❌ yfinance returned empty data")
        results['yfinance'] = False
        
except Exception as e:
    print(f"   ❌ yfinance failed: {e}")
    results['yfinance'] = False

print()

# ============================================================================
# TEST 5: Trade Learner (Self-Learning)
# ============================================================================
print("🧠 TEST 5: Self-Learning System")
print("-" * 40)

try:
    from services.trade_learner import TradeLearner
    
    learner = TradeLearner()
    
    # Test should_enter method
    should_enter, reasoning = learner.should_enter(
        convergence=85,
        volume_ratio=2.5,
        consolidation_days=15,
        signal_count=5
    )
    
    print(f"   ✅ Trade Learner initialized")
    print(f"   🎯 Test signal (85 convergence): {'ENTER' if should_enter else 'SKIP'}")
    results['TradeLearner'] = True
    
except Exception as e:
    print(f"   ❌ Trade Learner failed: {e}")
    results['TradeLearner'] = False

print()

# ============================================================================
# TEST 6: 10 Commandments
# ============================================================================
print("📜 TEST 6: 10 Commandments (Market Wizards' Rules)")
print("-" * 40)

try:
    from services.trading_rules import TenCommandments
    
    tc = TenCommandments(account_value=100000)
    
    # Test with a sample trade (use correct parameter names)
    can_trade, checks = tc.check_all_commandments(
        ticker="TEST",
        entry_price=10.00,
        stop_price=9.00,  # 10% stop
        target_price=15.00,  # 50% target = 5:1 R/R
        shares=100
    )
    
    print(f"   ✅ 10 Commandments initialized")
    print(f"   🎯 Test trade (5:1 R/R, 100 shares): {'APPROVED' if can_trade else 'REJECTED'}")
    
    # Count passed/failed
    passed = sum(1 for c in checks if c.passed)
    print(f"   📊 Rules passed: {passed}/{len(checks)}")
    results['TenCommandments'] = True
    
except Exception as e:
    print(f"   ❌ 10 Commandments failed: {e}")
    results['TenCommandments'] = False

print()

# ============================================================================
# TEST 7: Logging System
# ============================================================================
print("📝 TEST 7: Logging System")
print("-" * 40)

logs_dir = Path(__file__).parent / 'logs'
if logs_dir.exists():
    log_files = list(logs_dir.glob('*.json')) + list(logs_dir.glob('*.log'))
    print(f"   ✅ Logs directory exists: {logs_dir}")
    print(f"   📁 Log files found: {len(log_files)}")
    results['Logging'] = True
else:
    print(f"   ⚠️ Creating logs directory...")
    logs_dir.mkdir(exist_ok=True)
    print(f"   ✅ Logs directory created: {logs_dir}")
    results['Logging'] = True

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 70)
print("📊 SYSTEM TEST SUMMARY")
print("=" * 70)

passed = sum(1 for v in results.values() if v)
total = len(results)

print(f"\n   Tests Passed: {passed}/{total}")
print()

for component, status in results.items():
    icon = "✅" if status else "❌"
    print(f"   {icon} {component}")

print()

if passed == total:
    print("🎉 ALL SYSTEMS OPERATIONAL!")
    print("   Ready for paper trading.")
else:
    print(f"⚠️ {total - passed} component(s) need attention")
    print("   Check the errors above.")

print()
print("=" * 70)
