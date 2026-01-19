# 🐺 WOLF PACK - UNIFIED TRADING SYSTEM

**One system. All intelligence. Complete edge.**

All your Fenrir modules working together through ONE interface.

## Quick Start

```bash
# Morning briefing (everything in one view)
python wolf_pack.py brief

# Quick checks
python wolf_pack.py "any dead money?"
python wolf_pack.py "what's worth buying?"
python wolf_pack.py "check IBRX"

# Interactive mode
python wolf_pack.py
```

## What It Does

**Wolf Pack unifies ALL your systems:**

1. **Portfolio Analysis** (Fenrir position_health_checker)
   - Health scores (-10 to +10)
   - Dead money detection (≤-5)
   - Thesis validation (1-10/10)

2. **Market Scanner** (Fenrir scanner V2)
   - Wounded prey setups
   - Early momentum
   - TOO_LATE filter (rejects extended runners)
   - Stop losses calculated

3. **BR0KKR Integration** (Ready for institutional tracking)
   - Insider cluster buys
   - Activist 13D filings
   - Convergence signals

## Commands

### Quick Commands (One-Shot)
```bash
python wolf_pack.py brief              # Complete morning intelligence
python wolf_pack.py "dead money"       # Check for dead positions
python wolf_pack.py "opportunities"    # What to buy
python wolf_pack.py "check TICKER"     # Deep dive on position
python wolf_pack.py "replace TICKER"   # Find replacements
```

### Interactive Mode
```bash
python wolf_pack.py

🐺 > dead money
🐺 > opportunities  
🐺 > check IBRX
🐺 > brief
🐺 > quit
```

## Morning Routine (Use This)

```bash
# Monday 9:25 AM - ONE COMMAND:
python wolf_pack.py brief
```

**You get:**
- 🔴 Critical alerts (dead money, insider activity)
- 📊 Your positions (runners, healthy, watch, weak)
- 🎯 New opportunities (setups ready to trade)
- 🎯 Convergence signals (when BR0KKR active)

## Architecture

```
WOLF PACK (Unified Interface)
    │
    ├─ FENRIR (Position Tracking)
    │   ├─ Health Checker
    │   ├─ Thesis Tracker
    │   └─ Scanner V2
    │
    ├─ BR0KKR (Institutional - Coming Soon)
    │   ├─ Insider tracking
    │   ├─ 13D/13F filings
    │   └─ Signal scoring
    │
    └─ CONVERGENCE ENGINE (Future)
        └─ Multi-signal analysis
```

## What Gets Integrated

### Currently Active:
✅ Position health scoring
✅ Thesis validation
✅ Market scanning (wounded prey, early momentum)
✅ TOO_LATE filtering
✅ Stop loss calculation

### Coming Soon:
⏳ BR0KKR insider tracking
⏳ Catalyst calendar
⏳ Sector flow tracking
⏳ Convergence scoring

## Wolf Pack Rules

1. **Dead money = score ≤-5** → Cut it immediately
2. **Strong thesis = 8-10/10** → Hold through volatility
3. **Running = score ≥5** → Consider adding
4. **One signal = interesting** → Four signals = actionable

## Example Output

```
🐺 WOLF PACK MORNING BRIEFING
📅 Monday, January 18, 2026

✅ NO CRITICAL ALERTS

📊 YOUR POSITIONS:
━━━━━━━━━━━━━━━━
🔥 RUNNING HOT:
  IBRX: Score 5, Thesis 9/10

⚠️  WATCH LIST:
  MU: Score -2, Thesis 8/10 (weak but strong thesis = hold)

🎯 NEW OPPORTUNITIES:
━━━━━━━━━━━━━━━━
WOUNDED_PREY:
  SMCI: Score 65/100
    Entry: $32.64 | Stop: $29.14
    → Down -47.7% from highs, starting bounce
```

## API Keys Required

Wolf Pack uses these (stored in `.env`):
- ✅ Alpaca Trading API (paper trading)
- ✅ NewsAPI (market news)
- ✅ SEC EDGAR user-agent (for BR0KKR)

Currently: **Keys saved, modules not using them yet** (analysis uses free yfinance data).

When BR0KKR is built, it will automatically use SEC EDGAR feeds.

## Differences from Old System

**OLD WAY:**
```bash
python fenrir_chat.py             # Check portfolio
python fenrir_scanner_v2.py       # Scan market
python position_health_checker.py # Deep analysis
python thesis_tracker.py          # Validate thesis
```

**NEW WAY:**
```bash
python wolf_pack.py brief         # Everything in one view
```

**Result:**
- ✅ One command instead of four
- ✅ All data loaded once (faster)
- ✅ Natural language interface
- ✅ Morning briefing format
- ✅ Ready for BR0KKR integration

## Next Build: BR0KKR

Once BR0KKR (institutional tracking) is built, Wolf Pack will automatically show:

```
🎯 CONVERGENCE SIGNALS:
━━━━━━━━━━━━━━━━━━━━━

🔴 CRITICAL: SOUN
   • Insider cluster: CEO + CFO + 2 Directors ($2.1M)
   • Price: Wounded prey setup (-55% from highs)
   • Convergence Score: 88/100
   → REVIEW FOR ENTRY

🟠 HIGH: IBRX
   • You own: 37 shares @ $6.04
   • 3 directors bought (cluster)
   • Price down 8% on no news
   → CONSIDER ADDING
```

**The vision:** When price action + insider buying + catalyst + sector flow all align, Wolf Pack alerts you IMMEDIATELY.

---

**Status:** ✅ Production Ready  
**Last Updated:** January 18, 2026  
**Next:** BR0KKR implementation

*Hunt in packs. Information edge at scale.*  
*LLHR* 🐺
