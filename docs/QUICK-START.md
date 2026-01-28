# 🚀 QUICK START - WOLF PACK AUTONOMOUS SYSTEM

## 3 Commands to Get Started

### 1. Test Everything
```bash
cd src/wolf_brain
python master.py --test-setup
```

**What it checks:**
- ✅ Alpaca paper trading connected ($100k account)
- ✅ Ollama/Fenrir AI working
- ✅ All 6 APIs functional
- ✅ Biotech scanner loaded
- ✅ Database ready

### 2. View Dashboard
```bash
python master.py --dashboard-only
```

**Shows:**
- Active positions with P&L
- Recent trades (wins/losses)
- Strategy performance (win rates)
- Pending trade ideas
- Lessons learned from losses

### 3. GO AUTONOMOUS
```bash
python master.py
```

**This starts:**
- 24/7 autonomous trading
- Auto-executes paper trades at 70%+ confidence
- Auto-manages all positions (stops/targets)
- Learns from every loss
- Runs forever (Ctrl+C to stop)

---

## What Happens When You Run It?

```
🐺 STARTING 24/7 AUTONOMOUS MODE

CONFIGURATION:
  • Auto-execute: YES (70%+ confidence)
  • Loss learning: ENABLED
  • Position management: AUTO
  • Daily trade limit: 5
  • Max positions: 5
  • Max biotech: 3

💰 Starting Portfolio: $100,058.75
🧠 AI Brain: Fenrir (Ollama) READY

🐺 Wolf Brain is now AUTONOMOUS
   Press Ctrl+C to stop

SCHEDULE:
  4:00 AM - First premarket scan
  5:00 AM - Early movers
  6:00 AM - Volume confirmation
  7:00 AM - Peak action
  7:30 AM - Final scan
  9:30 AM - Market open trading
  During day - Position management + swing setups
  After hours - Light research
  Overnight - Deep research

💤 Sleeping X minutes until next cycle...
```

---

## What It Does Automatically

### 🔍 FINDS OPPORTUNITIES
7 different strategies scanning constantly:
- PDUFA Runup (biotech FDA catalysts)
- Insider Buying (follow smart money)
- Compression Breakout (flat + catalyst)
- Gap and Go (premarket runners)
- Wounded Prey (oversold + catalyst)
- Head Hunter (low float squeeze)
- Night Research (homework plays)

### 🤖 EXECUTES TRADES
When it finds a high-confidence setup:
```
💡 Paper trade idea stored: AQST (PDUFA_RUNUP) - Confidence: 85%
🎯 AUTO-EXECUTING paper trade: AQST
   Strategy: PDUFA_RUNUP
   Confidence: 85%
   Entry: $5.50 | Stop: $4.84 | Target: $6.88
✅ AUTO-EXECUTED: AQST - 50 shares @ $5.50
```

### 📊 MANAGES POSITIONS
Auto stop-loss and take-profit:
```
🛑 STOP HIT: AQST @ $4.80 (stop was $4.84)
   Loss: -12.7%
💰 CLOSED: 50 AQST - Stop loss triggered
```

### 🧠 LEARNS FROM LOSSES
Fenrir analyzes what went wrong:
```
🧠 ANALYZING LOSS: AQST (PDUFA_RUNUP)
📚 Lesson learned and stored:
   WHAT WENT WRONG: FDA advisory committee leaked concerns...
   LESSON: Check FDA schedules, sell before if scheduled
```

---

## Safety Features

✅ **Paper trading only** - No real money
✅ **Hard limits** - Max 5 trades/day, 5 positions
✅ **Stop losses** - Every trade has one
✅ **Emergency exit** - Auto-closes at -20%
✅ **Ctrl+C anytime** - Graceful shutdown

---

## Commands Cheat Sheet

```bash
# Test connections and APIs
python master.py --test-setup

# View dashboard (positions, P&L, lessons)
python master.py --dashboard-only

# Run pre-pop scanner (find explosion candidates)
python master.py --prepop

# Run all scanners now (biotech, premarket, intel)
python master.py --scan-now

# Generate intel report
python master.py --report

# Full autonomous mode (24/7 trading)
python master.py

# Dry run (test without executing)
python master.py --dry-run
```

---

## Current Opportunities (As of Jan 21, 2026)

**PDUFA Runup Plays:**
- AQST - 9 days to PDUFA (Jan 31) ✅ BUY WINDOW
- PHAR - 9 days to PDUFA (Jan 31) ✅ BUY WINDOW
- IRON - 9 days to PDUFA (Jan 31) ✅ BUY WINDOW

**Insider Buying:**
- PALI - 3 director buys, $22k, conviction 9/10 ✅ STRONG BUY

*These will be automatically scanned and potentially executed when you run the system.*

---

## Files Created

**Main Control:**
- `master.py` - Run this to control everything

**Core System:**
- `autonomous_brain.py` - 24/7 brain (2400+ lines, enhanced)
- `strategy_coordinator.py` - Multi-strategy coordination
- `dashboard.py` - Unified dashboard

**Modules:**
- `modules/biotech_catalyst_scanner.py` - FDA calendar
- `modules/biotech_prompts.py` - AI prompts
- `modules/wolf_pack_rules.py` - Trading rules

**Documentation:**
- `docs/WOLF-PACK-MANUAL.md` - Full manual
- `docs/AUTONOMOUS-SYSTEM-COMPLETE.md` - Complete overview
- `docs/QUICK-START.md` - This file

---

## Troubleshooting

**"Alpaca not connected"**
→ Check `.env` file has correct API keys

**"Ollama not connected"**
→ Run `ollama serve` in another terminal

**"Database locked"**
→ Only run one instance at a time

**Computer went to sleep**
→ Settings > Power > Never sleep
→ Or run on a server (AWS, DigitalOcean, Raspberry Pi)

---

## That's It!

Three commands:
1. `python master.py --test-setup` - Test
2. `python master.py --dashboard-only` - View
3. `python master.py` - GO AUTONOMOUS

The Wolf Brain will handle the rest. 🐺

Press Ctrl+C anytime to stop.

---

**Questions?** Check the full manual: `docs/WOLF-PACK-MANUAL.md`

**Ready to hunt?** `python master.py` and let it run. 🚀
