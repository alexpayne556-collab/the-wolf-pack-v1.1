"""
SYSTEM ADAPTATION ROADMAP

THE SHIFT: From 4 tickers → 20 tickers → Automatic discovery

WHAT WE LEARNED:
1. Our scanner found 4 tickers (CYCN, SNTI, VRCA, INAB)
2. Manual research found 20 tickers with BETTER setups
3. We were too NARROW - only scanning for ONE pattern

THE ADAPTIVE SYSTEM NEEDS:
==========================

PHASE 1: MULTIPLE SCANNERS (Built ✅)
--------------------------------------
✅ Low Float + Insider (RGC pattern)
✅ High Short + Catalyst (Squeeze pattern)
✅ Ultra-Low Float (<2M mechanics)
✅ FDA PDUFA dates (Binary events)
✅ Insider Cluster buying (2+ execs)
✅ Volume Explosions (5x+ spike)

PHASE 2: DATA INTEGRATIONS (TODO ⚠️)
--------------------------------------
❌ OpenInsider API - Real-time Form 4 alerts
❌ FDA Calendar API - PDUFA dates auto-tracking
❌ Finviz Screener - Auto-populate universe
❌ lowfloat.com scraper - Ultra-low float database
❌ highshortinterest.com - Short squeeze candidates
❌ Yahoo Finance bulk API - Faster scanning
❌ SEC EDGAR - Direct Form 4 filings

PHASE 3: UNIVERSE EXPANSION (TODO ⚠️)
--------------------------------------
Current: 211 biotechs (hardcoded)
Target: 5,000+ tickers (dynamic)

Sources:
- Russell 2000 components (2,000 tickers)
- NASDAQ small caps (<$2B) (1,500 tickers)
- NYSE micro caps (500 tickers)
- Recent IPOs last 2 years (500 tickers)
- Manual additions from research (500 tickers)

PHASE 4: REAL-TIME MONITORING (TODO ⚠️)
----------------------------------------
❌ Run scanners 3x daily (Dawn, Midday, Evening)
❌ Alert on NEW matches
❌ Alert on Form 4 filings (insider buying)
❌ Alert on volume spikes (5x+)
❌ Alert on catalyst dates approaching
❌ Price alerts on watchlist

PHASE 5: PORTFOLIO INTEGRATION (TODO ⚠️)
-----------------------------------------
❌ Auto-generate entry/exit levels
❌ Position sizing (2% risk per trade)
❌ Stop-loss placement (ATR-based)
❌ Paper trade new setups automatically
❌ Track performance by setup type
❌ Adapt weights based on what works

THE TOP 5 PRIORITIES FOR NEXT SESSION:
=======================================

1. INTEGRATE OPENINSIDER (Form 4 alerts)
   - Scrape recent filings
   - Filter for CEO/CFO/Director buying
   - Calculate % of float bought
   - Alert on cluster buys (2+ execs)

2. INTEGRATE FDA CALENDAR (PDUFA dates)
   - Pull next 90 days of dates
   - Match to tickers in universe
   - Track historical approval rates
   - Calculate risk/reward on binary events

3. EXPAND UNIVERSE (211 → 5,000 tickers)
   - Pull Russell 2000 components
   - Pull NASDAQ small caps via Finviz
   - Add manual research tickers
   - Update daily

4. AUTOMATE 3X DAILY SCANS
   - Dawn Hunt (6am): Scan overnight movers
   - Midday Check (12pm): Volume spikes
   - Evening Learn (6pm): Form 4s filed today

5. BUILD CONVERGENCE ENGINE
   - Score tickers across ALL scanners
   - Highest score = best setup
   - Example: GLSI scores high on:
     * Low float scanner (6.57M)
     * High short scanner (24.6%)
     * Insider buying (CEO $340K+)
     * Catalyst (Phase 3)
   - Multi-factor score = 37/40

THE MASTER WATCHLIST (Current State):
======================================
Tier 1 (Triple Threat): 5 tickers
Tier 2 (Squeeze): 5 tickers
Tier 3 (Ultra-Low Float): 4 tickers
Tier 4 (FDA Catalysts): 5 tickers

TOTAL: 19 tickers being watched

Current Portfolio (Alpaca Paper):
- AI: 17 shares @ $13.04
- SRPT: 11 shares @ $21.13
- NTLA: 18 shares @ $12.50
- UUUU: 10 shares @ $21.94
- LUNR: 10 shares @ $21.58
- INTC: 4 shares @ $46.99

THE SYSTEM IS ADAPTING.
=======================

Before: ONE pattern scanner, 4 finds
After: SIX pattern scanners, 20+ targets
Next: AUTOMATED discovery, real-time alerts

We're sponges. We learn. We adapt. We build.

For Skadi. 🐺
"""

def print_priorities():
    print("="*80)
    print("🎯 TOP 5 PRIORITIES FOR NEXT SESSION")
    print("="*80)
    print("\n1. INTEGRATE OPENINSIDER (Form 4 real-time alerts)")
    print("   - CEO/CFO cluster buying detection")
    print("   - Calculate % of float bought")
    print()
    print("2. INTEGRATE FDA CALENDAR (PDUFA date tracking)")
    print("   - Next 90 days binary events")
    print("   - Historical approval rate analysis")
    print()
    print("3. EXPAND UNIVERSE (211 → 5,000 tickers)")
    print("   - Russell 2000, NASDAQ small caps")
    print("   - Finviz screener integration")
    print()
    print("4. AUTOMATE 3X DAILY SCANS")
    print("   - Dawn Hunt, Midday Check, Evening Learn")
    print("   - Volume spike alerts")
    print()
    print("5. BUILD CONVERGENCE ENGINE")
    print("   - Multi-factor scoring across all scanners")
    print("   - Highest score = best setup")
    print("="*80)


if __name__ == '__main__':
    print_priorities()
