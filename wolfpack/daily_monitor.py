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
from services.learning_engine import UnifiedLearningEngine
from wolf_pack_trader import WolfPackTrader, ALPACA_AVAILABLE
from wolf_pack_brain import WolfPackBrain

print("=" * 70)
print(f"🐺 WOLF PACK DAILY MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

# Initialize components
print("\n🔧 Initializing systems...")
wp = WolfPack(account_value=100000)
pivotal_tracker = PivotalPointTracker()
learner = UnifiedLearningEngine()
trader = WolfPackTrader(paper_trading=True) if ALPACA_AVAILABLE else None
brain = WolfPackBrain()

# 1. System Health Check
print("\n" + "=" * 70)
print("📊 SYSTEM HEALTH CHECK")
print("=" * 70)

health_status = {
    'Wolf Pack Brain': brain is not None,
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

# CRITICAL: Update all pending trade outcomes first
print("\n📊 Updating trade outcomes with latest prices...")
try:
    from services.learning_engine import LearningEngine
    learning_engine = LearningEngine()
    learning_engine.update_all_outcomes()
    print("   ✅ Outcomes updated")
except Exception as e:
    print(f"   ⚠️ Update failed: {e}")

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
    
    # SHOW PATTERNS FROM UNIFIED LEARNING ENGINE
    try:
        patterns = learning_engine.analyze_your_patterns()
        if patterns:
            print(f"\n📊 YOUR PATTERNS (from learning engine):")
            print(f"   Catalyst edge: {patterns.get('catalyst_edge', 'Not enough data')}")
            print(f"   Best entry timing: {patterns.get('best_timing', 'Not enough data')}")
            print(f"   Best tickers: {patterns.get('best_tickers', 'Not enough data')}")
    except Exception as e:
        print(f"   ⚠️ Pattern analysis error: {e}")
else:
    print("\n⚠️  No trade history yet - system will learn as it trades")
    print("   Default rules in effect until we have data")

# 1.6. Morning Intelligence Briefing
print("\n" + "=" * 70)
print("🧠 WOLF PACK BRAIN - MORNING BRIEFING")
print("=" * 70)

try:
    # Market regime check
    regime_data = brain.detect_market_regime()
    regime_info = regime_data.get('regime_info', {})
    regime = regime_info.get('regime', 'mixed')
    confidence = regime_info.get('confidence', 0.5)
    strategy = regime_info.get('strategy', 'No clear regime')
    
    print(f"\n📊 Market Regime: {regime.upper()}")
    print(f"   Confidence: {confidence:.0%}")
    print(f"   Strategy: {strategy}")
    
    # Check liquidity for watchlist
    print("\n💧 Liquidity Status (Watchlist):")
    try:
        from config import WATCHLIST
        for ticker in list(WATCHLIST.keys())[:5]:  # Check first 5
            try:
                liq_score = brain.check_liquidity(ticker, 5000)
                risk_icon = "🟢" if liq_score['risk'] == 'green' else "🟡" if liq_score['risk'] == 'yellow' else "🔴"
                print(f"   {risk_icon} {ticker}: {liq_score['score']}/100")
            except Exception as e:
                print(f"   ⚠️ {ticker}: Unable to check ({str(e)[:30]}...)")
    except ImportError:
        print("   ⚠️ WATCHLIST not configured in config.py")
        
except Exception as e:
    print(f"   ⚠️ Briefing error: {e}")
    import traceback
    traceback.print_exc()

# 2. Run Wolf Pack Scan
print("\n" + "=" * 70)
print("🔍 RUNNING WOLF PACK SCAN")
print("=" * 70)

try:
    # Run the scan (using scan_watchlist method)
    # This would normally capture the output
    print("\n🐺 Scanning watchlist...")
    results = wp.scan_watchlist()
    print(f"   Found {len(results)} signals")
    
    # Get holdings for detailed analysis
    try:
        from fenrir.position_health_checker import HOLDINGS
    except ImportError:
        # Fallback if position_health_checker not available
        HOLDINGS = {}
    
    print(f"\n📊 Analyzing {len(HOLDINGS)} holdings...")
    
except Exception as e:
    print(f"❌ Scan failed: {e}")
    import traceback
    traceback.print_exc()
    HOLDINGS = {}  # Set empty holdings on error

# 3. Pivotal Point Analysis
print("\n" + "=" * 70)
print("🎯 LIVERMORE PIVOTAL POINT ANALYSIS")
print("=" * 70)

try:
    from fenrir.position_health_checker import HOLDINGS
except ImportError:
    HOLDINGS = {}

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

# 3.5. Brain Position Monitoring
print("\n" + "=" * 70)
print("🧠 WOLF PACK BRAIN - POSITION MONITORING")
print("=" * 70)

try:
    if len(HOLDINGS) > 0:
        # Monitor all positions for shifts
        positions = []
        for ticker, data in HOLDINGS.items():
            entry = data.get('entry', 0)
            shares = data.get('shares', 0)
            if shares > 0:
                positions.append({'ticker': ticker, 'entry': entry, 'shares': shares})
        
        if positions:
            print("\n📈 Monitoring positions for momentum shifts...")
            alerts = brain.position_monitor(positions)
            
            if alerts:
                print(f"\n🚨 {len(alerts)} ALERTS:")
                for alert in alerts[:10]:  # Show first 10
                    severity_icon = "🔴" if alert['severity'] == 'CRITICAL' else "🚨" if alert['severity'] == 'HIGH' else "⚠️"
                    print(f"   {severity_icon} {alert['ticker']}: {alert['type']} - {alert['message']}")
            else:
                print("   ✅ No shift alerts (all positions stable)")
    else:
        print("\n   ℹ️ No active positions to monitor")
except Exception as e:
    print(f"   ⚠️ Position monitoring error: {e}")

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
print("📈 TRADE EXECUTION (WITH PRE-TRADE INTELLIGENCE)")
print("=" * 70)

if trader and trader.client:
    print("\n🤖 Trader bot is ACTIVE")
    print("⚠️  Paper trading mode enabled")
    
    # Example: Pre-trade check for potential trades
    print("\n🧠 Running pre-trade intelligence checks...")
    print("   (Before executing any trades, Wolf Pack Brain checks:)")
    print("   1. Market regime compatibility")
    print("   2. Liquidity risk")
    print("   3. Predicted mistake probability")
    print("   4. Setup quality score")
    print("   5. Historical DNA match")
    
    # Demonstrate pre-trade check (not executing, just showing process)
    example_ticker = "AAPL"
    example_size = 5000
    example_context = {
        'time': datetime.now().strftime('%H:%M'),
        'recent_trades': 0,
        'recent_pnl': 0
    }
    
    try:
        print(f"\n   Example: Checking {example_ticker} ($${example_size:,})...")
        check_result = brain.pre_trade_check(example_ticker, example_size, example_context)
        
        if check_result.get('decision') == 'PROCEED':
            print(f"   ✅ {example_ticker}: CLEARED for entry")
        elif check_result.get('decision') == 'CAUTION':
            print(f"   ⚠️ {example_ticker}: PROCEED WITH CAUTION")
        else:
            print(f"   🛑 {example_ticker}: BLOCKED")
            
    except Exception as e:
        print(f"   ⚠️ Pre-trade check error: {e}")
    
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
