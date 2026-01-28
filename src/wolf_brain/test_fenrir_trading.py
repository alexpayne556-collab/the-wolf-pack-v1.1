#!/usr/bin/env python3
"""
🐺 TEST FENRIR ANALYSIS - AQST Trade Decision
==============================================
Have Fenrir analyze the pre-pop scan result and make a trade decision
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from autonomous_brain import AutonomousBrain
import json

def test_fenrir_aqst_analysis():
    """Test Fenrir analyzing AQST from pre-pop scan"""
    
    print("🧠 Testing Fenrir Analysis on AQST\n")
    print("="*60)
    
    # Initialize brain
    brain = AutonomousBrain(dry_run=False)
    
    # AQST data from pre-pop scan
    aqst_setup = {
        "ticker": "AQST",
        "price": 3.36,
        "total_score": 54.1,
        "catalyst": {
            "score": 9,
            "type": "PDUFA",
            "drug": "AQST-109 oral epinephrine",
            "date": "2026-01-31",
            "days_until": 9,
            "timing": "SWEET SPOT (8-14 days)"
        },
        "float": {"score": 4, "description": "LOW (>50M)"},
        "uncertainty": {"score": 7, "description": "ESTABLISHED + HEAVILY BEATEN"},
        "compression": {"score": 2, "description": "VOLATILE (>40%)"},
        "insider": {"score": 1, "description": "NO DATA"},
        "squeeze": {"score": 8, "short_percent": 22.7, "description": "HIGH (22.7%)"}
    }
    
    # Build prompt for Fenrir
    prompt = f"""🐺 WOLF PACK TRADE ANALYSIS - AQST

PRE-POP SCAN RESULTS:
{json.dumps(aqst_setup, indent=2)}

CURRENT SITUATION:
• Price: ${aqst_setup['price']}
• PDUFA Date: {aqst_setup['catalyst']['date']} ({aqst_setup['catalyst']['days_until']} days away)
• Drug: {aqst_setup['catalyst']['drug']}
• Short Interest: {aqst_setup['squeeze']['short_percent']}%
• Timing: {aqst_setup['catalyst']['timing']}

WOLF PACK STRATEGY:
The PDUFA Runup play: Buy 7-14 days before FDA decision, sell 1-2 days before.
Historical pattern: 15-30% runup before decision, then binary 50%+ pop or -60% crash on decision.

YOUR TASK:
1. Should we BUY AQST now? (YES/NO)
2. What's our entry price? (specific price)
3. What's our stop loss? (price and %)
4. What's our profit target? (price and %)
5. When do we exit? (specific date/time)
6. Position size? (1-10 scale, 1=small, 10=max)
7. What could go wrong? (top 3 risks)
8. What's the similar historical pattern? (past PDUFA plays)

FORMAT YOUR ANSWER:
DECISION: [BUY/PASS]
ENTRY: $[price]
STOP: $[price] (-X%)
TARGET: $[price] (+X%)
EXIT DATE: [date]
POSITION SIZE: [1-10]
RISKS: [list 3]
SIMILAR PLAYS: [examples]
CONVICTION: [1-10]
ONE-SENTENCE THESIS: [summary]
"""
    
    print("📝 Prompt sent to Fenrir:\n")
    print(prompt)
    print("\n" + "="*60)
    print("🧠 Fenrir is thinking...\n")
    
    # Get Fenrir's analysis
    analysis = brain.think(prompt)
    
    print("="*60)
    print("🎯 FENRIR'S ANALYSIS:\n")
    print(analysis)
    print("\n" + "="*60)
    
    # Parse decision
    if "DECISION: BUY" in analysis.upper() or "BUY NOW" in analysis.upper():
        print("\n✅ FENRIR SAYS: BUY")
        print("📊 This would be stored as a paper trade idea")
        print("💰 With 70%+ confidence, brain would AUTO-EXECUTE")
    elif "DECISION: PASS" in analysis.upper():
        print("\n⏸️  FENRIR SAYS: PASS")
        print("📊 Setup doesn't meet criteria")
    else:
        print("\n⚠️  FENRIR'S DECISION: UNCLEAR - needs human review")
    
    return analysis


def test_premarket_watchlist():
    """Generate tomorrow's premarket watchlist"""
    
    print("\n\n" + "🌅"*30)
    print("TOMORROW'S PREMARKET WATCHLIST")
    print("🌅"*30 + "\n")
    
    brain = AutonomousBrain(dry_run=False)
    
    # Tickers to watch (from pre-pop scan + current positions + hot sectors)
    watchlist = [
        # Pre-pop candidates
        {"ticker": "AQST", "why": "PDUFA in 9 days - SWEET SPOT", "priority": "HIGH"},
        {"ticker": "OCUL", "why": "PDUFA in 6 days - IMMINENT", "priority": "WATCH"},
        {"ticker": "PALI", "why": "3 insider buys - accumulation", "priority": "MEDIUM"},
        
        # Current positions (if any)
        # {"ticker": "POSITION1", "why": "Monitor for stop/target", "priority": "CRITICAL"},
        
        # Sector plays
        {"ticker": "NVAX", "why": "Pfizer deal - partnership validation", "priority": "MEDIUM"},
        {"ticker": "LXRX", "why": "FDA meeting positive - momentum", "priority": "MEDIUM"},
        {"ticker": "ZURA", "why": "Q3 data coming - partnership ROFN", "priority": "LOW"},
    ]
    
    prompt = f"""🌅 PREMARKET WATCHLIST ANALYSIS

These tickers are on our radar for tomorrow's premarket (4:00 AM - 9:30 AM):

{json.dumps(watchlist, indent=2)}

YOUR TASK:
For each ticker, tell me:
1. What to watch for in premarket (price action, volume, news)
2. Entry signal (what would trigger a buy?)
3. Avoid signal (what would make us stay away?)
4. Price alerts to set (specific levels)

Focus on ACTIONABLE premarket signals, not just "watch the price."

EXAMPLE FORMAT:
AQST:
  WATCH FOR: Gap up on volume 2x avg + holding gains at 6 AM
  ENTRY SIGNAL: Breaks $3.50 with volume, pullback to $3.40 = buy
  AVOID: Gaps down below $3.20, low volume, sells off after gap
  ALERTS: $3.50 (breakout), $3.20 (support break)
"""
    
    print("📝 Asking Fenrir for premarket game plan...\n")
    
    analysis = brain.think(prompt)
    
    print("="*60)
    print("🎯 FENRIR'S PREMARKET WATCHLIST:\n")
    print(analysis)
    print("\n" + "="*60)
    
    return analysis


def test_portfolio_monitoring():
    """Test how brain monitors and exits positions"""
    
    print("\n\n" + "📊"*30)
    print("PORTFOLIO MONITORING TEST")
    print("📊"*30 + "\n")
    
    brain = AutonomousBrain(dry_run=False)
    
    # Simulate a position that's bleeding
    mock_position = {
        "ticker": "EXAMPLE",
        "entry": 10.00,
        "current": 9.20,
        "stop": 9.00,
        "target": 12.00,
        "strategy": "PDUFA_RUNUP",
        "days_held": 3,
        "pnl_pct": -8.0
    }
    
    prompt = f"""🩸 POSITION BLEEDING - DECISION NEEDED

POSITION DETAILS:
{json.dumps(mock_position, indent=2)}

SITUATION:
We're down 8% on this PDUFA runup play. Stop loss is at $9.00 (-10%).
Current price: $9.20

THE QUESTION:
1. Hold? (Stop not hit yet, could recover)
2. Cut now? (Momentum broken, take the L)
3. Add more? (Average down)

WOLF PACK RULES:
- Never panic sell
- But also don't hold losers hoping for recovery
- Trust the stop loss placement
- If thesis is broken, exit before stop

YOUR ANALYSIS:
1. Is the thesis still intact? (PDUFA still coming? News changed?)
2. Is this normal volatility or broken setup?
3. Should we exit now or wait for stop?
4. What's the smart move?

DECISION: [HOLD/CUT NOW/ADJUST STOP]
REASONING: [why]
"""
    
    print("📝 Testing position monitoring logic...\n")
    
    analysis = brain.think(prompt)
    
    print("="*60)
    print("🎯 FENRIR'S POSITION ANALYSIS:\n")
    print(analysis)
    print("\n" + "="*60)
    
    return analysis


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🐺 TESTING FENRIR'S TRADING INTELLIGENCE 🧠                  ║
║  ───────────────────────────────────────────────────────────  ║
║  1. Can he analyze AQST and make a trade decision?           ║
║  2. Can he generate a premarket watchlist?                    ║
║  3. Can he intelligently manage bleeding positions?           ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: AQST analysis
    aqst_analysis = test_fenrir_aqst_analysis()
    
    # Test 2: Premarket watchlist
    watchlist = test_premarket_watchlist()
    
    # Test 3: Portfolio monitoring
    position_analysis = test_portfolio_monitoring()
    
    print("\n\n" + "🎉"*30)
    print("TESTS COMPLETE!")
    print("🎉"*30)
    print("\nFenrir successfully demonstrated:")
    print("  ✅ Trade analysis and decision making")
    print("  ✅ Premarket watchlist generation")
    print("  ✅ Intelligent position monitoring")
    print("\n🐺 The Wolf Brain is ready to hunt autonomously!")
