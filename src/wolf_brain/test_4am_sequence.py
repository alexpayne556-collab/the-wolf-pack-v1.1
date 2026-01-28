#!/usr/bin/env python3
"""
🐺 4 AM PREMARKET MONITOR - TEST RUN
====================================
Shows exactly what the brain will do tomorrow at 4 AM

Run this to see the full sequence before going live
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from autonomous_brain import AutonomousBrain
from datetime import datetime

print("""
╔══════════════════════════════════════════════════════════════╗
║  🌅 4 AM PREMARKET SEQUENCE - WHAT WILL HAPPEN TOMORROW      ║
╚══════════════════════════════════════════════════════════════╝
""")

print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print("📅 TOMORROW'S SCHEDULE:")
print("=" * 60)
print("4:00 AM → First scan + Biotech catalysts + Intel report")
print("5:00 AM → Early movers scan")
print("5:30 AM → Building momentum scan")
print("6:00 AM → Volume confirmation scan")
print("6:30 AM → Prime time scan")
print("7:00 AM → Peak action scan")
print("7:30 AM → Final premarket scan")
print("9:30 AM → Market open - Execute top setups")
print("\nAll scans run AUTOMATICALLY every 2 minutes between 4-7:30 AM")
print("=" * 60)

print("\n🔍 WHAT EACH SCAN DOES:")
print("-" * 60)
print("1. Scan premarket gainers (>3% gap, >2x volume)")
print("2. Check biotech catalysts (PDUFA, data, partnerships)")
print("3. Classify each runner (RUNNER vs FADER)")
print("4. Get news from 6 APIs (Finnhub, NewsAPI, Polygon, etc.)")
print("5. Check insider buying (Form 4s)")
print("6. Analyze with Fenrir AI")
print("7. Store in database for learning")
print("8. Generate reports for review")

print("\n🤖 AUTO-EXECUTION LOGIC:")
print("-" * 60)
print("IF:")
print("  • Confidence >= 70%")
print("  • Position limits OK (max 5 positions, max 3 biotech)")
print("  • Daily trade limit OK (max 5 trades/day)")
print("  • Risk management passed (proper stop loss, position size)")
print("\nTHEN:")
print("  ✅ AUTO-EXECUTE paper trade")
print("  ✅ Set stop loss & take profit orders")
print("  ✅ Monitor every 2 minutes during market")
print("  ✅ Auto-close on stop hit")
print("  ✅ Auto-analyze if loss occurs")

print("\n📊 POSITION MANAGEMENT:")
print("-" * 60)
print("• Check positions every 2 minutes during market")
print("• Auto-close on stop loss hit")
print("• Take partial profits at Target 1")
print("• Move stop to breakeven after T1")
print("• Emergency exit at -20%")
print("• Fenrir analyzes all losses")

print("\n🧠 LEARNING SYSTEM:")
print("-" * 60)
print("When a trade loses money:")
print("  1. Fenrir asks: 'What went wrong?'")
print("  2. Analyzes news, price action, catalyst")
print("  3. Stores lesson in database")
print("  4. Adjusts strategy multipliers")
print("  5. Avoids same mistake next time")

print("\n🎯 CURRENT TOP OPPORTUNITIES:")
print("=" * 60)

# Initialize brain
brain = AutonomousBrain(dry_run=True)

if brain.biotech_scanner:
    # Get PDUFA plays in sweet spot
    catalysts = brain.biotech_scanner.get_upcoming_catalysts(days_ahead=14)
    
    pdufa_plays = []
    for cat in catalysts:
        days = cat.get('days_until', 0)
        if 7 <= days <= 14:
            pdufa_plays.append(cat)
    
    if pdufa_plays:
        print("\n🔥 PDUFA PLAYS (7-14 day window - SWEET SPOT):")
        for play in pdufa_plays:
            print(f"  • {play['ticker']}: {play['drug']} - PDUFA {play['date']} ({play['days_until']} days)")
            print(f"    Strategy: Buy now, sell 1-2 days before PDUFA")
    
    # Get imminent catalysts
    imminent = [c for c in catalysts if c.get('days_until', 99) < 7]
    if imminent:
        print("\n⚠️ IMMINENT CATALYSTS (<7 days - HIGH RISK):")
        for play in imminent:
            print(f"  • {play['ticker']}: {play['drug']} - {play['days_until']} days")
            print(f"    ⚠️  Too close - binary risk high, watch only")

print("\n📁 WHERE TO FIND RESULTS:")
print("=" * 60)
print("• data/wolf_brain/LATEST_INTEL_REPORT.txt")
print("• data/wolf_brain/PREMARKET_SCANS_YYYYMMDD.txt")
print("• data/wolf_brain/autonomous_memory.db (all trades/lessons)")
print("• data/wolf_brain/autonomous_YYYYMMDD.log (detailed logs)")

print("\n🚀 TO START AUTONOMOUS MODE:")
print("=" * 60)
print("cd src/wolf_brain")
print("python master.py")
print("\nThe brain will:")
print("  • Run 24/7")
print("  • Auto-scan at 4 AM, 5 AM, 5:30 AM, 6 AM, 6:30 AM, 7 AM, 7:30 AM")
print("  • Auto-execute high-confidence setups")
print("  • Auto-manage all positions")
print("  • Auto-learn from losses")
print("  • Never sleep, never panic, always learn")

print("\n✅ SYSTEM STATUS:")
print("=" * 60)
if brain.alpaca_connected:
    account = brain.trading_client.get_account()
    print(f"💰 Alpaca: CONNECTED (${float(account.portfolio_value):,.2f})")
else:
    print("❌ Alpaca: NOT CONNECTED")

if brain.ollama_connected:
    print("🧠 Fenrir (Ollama): CONNECTED")
else:
    print("❌ Fenrir: NOT CONNECTED")

if brain.biotech_scanner:
    print("🧬 Biotech Scanner: LOADED")
else:
    print("❌ Biotech Scanner: NOT LOADED")

print("\n🐺 WOLF PACK IS READY TO HUNT AT 4 AM! 🐺\n")
