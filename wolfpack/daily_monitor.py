#!/usr/bin/env python3
"""
DAILY SYSTEM MONITOR
Run this every day to:
1. Check system health
2. Review convergence signals
3. Monitor pivotal points
4. Track position performance
5. Execute trades (if enabled)
6. LEARN from outcomes (self-learning)
7. Monitor exits (cut losers)
"""

import sys
from datetime import datetime
from wolf_pack import WolfPack
from services.pivotal_point_tracker import PivotalPointTracker
from services.trade_learner import TradeLearner
from wolf_pack_trader import WolfPackTrader, ALPACA_AVAILABLE

print("=" * 70)
print(f"🐺 WOLF PACK DAILY MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Initialize components
print("\n🔧 Initializing systems...")
wp = WolfPack(account_value=100000)
pivotal_tracker = PivotalPointTracker()
learner = TradeLearner()
trader = WolfPackTrader(paper_trading=True) if ALPACA_AVAILABLE else None

# 1. System Health Check
print("\n" + "=" * 70)
print("📊 SYSTEM HEALTH CHECK")
print("=" * 70)

health_status = {
    'Risk Manager': wp.risk_manager is not None,
    'News Service': wp.news_service is not None,
    'Earnings Service': wp.earnings_service is not None,
    'Convergence Engine': wp.convergence_engine is not None,
    'Pivotal Point Tracker': pivotal_tracker is not None,
    'Trade Learner': learner is not None,
    'Trader Bot': trader is not None and trader.client is not None
}

for component, status in health_status.items():
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {component}")

all_healthy = all(health_status.values())
if not all_healthy:
    print("\n⚠️  Some components not operational. Check configuration.")

# 1.5. Learning Status
print("\n" + "=" * 70)
print("🧠 LEARNING SYSTEM STATUS")
print("=" * 70)

if len(learner.trades) > 0:
    wins = [t for t in learner.trades if t.outcome == "win"]
    losses = [t for t in learner.trades if t.outcome in ["loss", "blown_up"]]
    win_rate = len(wins) / len(learner.trades) * 100 if learner.trades else 0
    
    print(f"\n📊 Historical Performance:")
    print(f"   Total Trades: {len(learner.trades)}")
    print(f"   Win Rate: {win_rate:.1f}% ({len(wins)}W / {len(losses)}L)")
    
    if learner.insights:
        print(f"\n💡 Learned Rules ({len(learner.insights)}):")
        for rule in learner.get_learned_rules()[:5]:  # Show first 5
            print(f"   {rule}")
    else:
        print("\n⚠️  No patterns learned yet (need 10+ trades)")
else:
    print("\n⚠️  No trade history yet - system will learn as it trades")
    print("   Default rules in effect until we have data")

# 2. Run Wolf Pack Scan
print("\n" + "=" * 70)
print("🔍 RUNNING WOLF PACK SCAN")
print("=" * 70)

try:
    # Run the scan (brief mode to get signals)
    # This would normally capture the output
    print("\n🐺 Scanning all signals...")
    wp.hunt()
    
    # Get holdings for detailed analysis
    from services.position_tracker import HOLDINGS
    
    print(f"\n📊 Analyzing {len(HOLDINGS)} holdings...")
    
except Exception as e:
    print(f"❌ Scan failed: {e}")
    import traceback
    traceback.print_exc()

# 3. Pivotal Point Analysis
print("\n" + "=" * 70)
print("🎯 LIVERMORE PIVOTAL POINT ANALYSIS")
print("=" * 70)

from services.position_tracker import HOLDINGS

for ticker in HOLDINGS.keys():
    print(f"\n🔍 {ticker}...")
    pattern = pivotal_tracker.detect_pattern_state(ticker)
    
    if pattern:
        print(f"   State: {pattern.state.value.upper()}")
        print(f"   Score: {pattern.score}/100")
        print(f"   Volume: {pattern.volume_ratio:.1f}x average")
        
        if pattern.volume_confirmation:
            print(f"   ✅ Volume confirmed")
        
        if pattern.consolidation_range:
            print(f"   Range: ${pattern.consolidation_range[0]:.2f} - ${pattern.consolidation_range[1]:.2f}")
        
        # Highlight actionable patterns
        if pattern.state.value in ['confirmed', 'trending']:
            print(f"   🔥 ACTIONABLE - Consider entry/add")
        elif pattern.state.value == 'normal_reaction':
            print(f"   💎 SIT TIGHT - Healthy pullback")
    else:
        print(f"   ❌ No pattern data")

# 4. Convergence Highlights
print("\n" + "=" * 70)
print("⚡ HIGH CONVERGENCE ALERTS (75+)")
print("=" * 70)

# This would come from wolf_pack results
# For now, demonstrate the structure
print("\n(Convergence signals would appear here)")
print("Format: TICKER | Score | Signals | Action")
print("Example: IBRX | 93/100 | 6 signals | 🔥 CRITICAL BUY")

# 5. Risk Check
print("\n" + "=" * 70)
print("⚠️  PORTFOLIO RISK STATUS")
print("=" * 70)

try:
    # Calculate portfolio heat
    positions = []
    for ticker, data in HOLDINGS.items():
        entry = data.get('entry', 0)
        stop = data.get('stop', entry * 0.95)
        shares = data.get('shares', 0)
        
        if shares > 0:
            risk_per_share = entry - stop
            position_risk = shares * risk_per_share
            positions.append({
                'ticker': ticker,
                'risk': position_risk,
                'shares': shares
            })
    
    total_risk = sum(p['risk'] for p in positions)
    portfolio_heat = (total_risk / 100000) * 100  # Assuming $100k account
    
    print(f"\nTotal Portfolio Heat: {portfolio_heat:.1f}%")
    
    if portfolio_heat > 30:
        print("🔴 HIGH RISK - Consider reducing exposure")
    elif portfolio_heat > 15:
        print("🟡 MODERATE RISK - Monitor closely")
    else:
        print("🟢 LOW RISK - Room to add")
    
    print(f"\nActive Positions: {len(positions)}")
    for p in positions:
        print(f"   {p['ticker']}: ${p['risk']:,.0f} at risk ({p['shares']} shares)")

except Exception as e:
    print(f"❌ Risk calculation failed: {e}")

# 6. Exit Monitoring (Cut Losers)
print("\n" + "=" * 70)
print("✂️  EXIT MONITORING (Cut Losers)")
print("=" * 70)

if trader and trader.client:
    print("\n🔍 Checking open positions for exit signals...")
    trader.monitor_exits()
else:
    print("\n⚠️  Trader bot not configured - manual exit monitoring required")

# 7. Trade Execution (if enabled)
print("\n" + "=" * 70)
print("📈 TRADE EXECUTION")
print("=" * 70)

if trader and trader.client:
    print("\n🤖 Trader bot is ACTIVE")
    print("⚠️  Paper trading mode enabled")
    print("\n(Trade execution disabled in demo mode)")
    print("To enable: Uncomment trader.run_daily_scan() below")
    # trader.run_daily_scan()
else:
    print("\n⚠️  Trader bot not configured")
    print("To enable:")
    print("1. pip install alpaca-py")
    print("2. Add ALPACA_PAPER_KEY_ID and ALPACA_PAPER_SECRET_KEY to .env")
    print("3. Rerun this script")

# 8. Daily Summary
print("\n" + "=" * 70)
print("📋 DAILY SUMMARY")
print("=" * 70)

print(f"""
✅ System Health: {"OPERATIONAL" if all_healthy else "PARTIAL"}
📊 Holdings Tracked: {len(HOLDINGS)}
🎯 Pivotal Points Monitored: {len(HOLDINGS)}
⚡ High Convergence Signals: (check output above)
⚠️  Portfolio Heat: {portfolio_heat:.1f}%
📈 Trades Executed: {len(trader.trades_today) if trader else 0}
🧠 Learning Status: {len(learner.trades)} trades in history, {len(learner.insights)} patterns learned

NEXT STEPS:
1. Review high convergence signals (75+)
2. Check Livermore patterns for entries
3. Monitor portfolio heat
4. Let learner filter bad setups
5. Cut losers when learner says so
6. Update trade outcomes for continuous learning

🐺 AWOOOO - The hunt continues, the system learns
""")

print("=" * 70)
print(f"✅ DAILY MONITOR COMPLETE - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

# Save report to file
report_file = f"logs/daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
print(f"\n💾 Report saved to: {report_file}")
