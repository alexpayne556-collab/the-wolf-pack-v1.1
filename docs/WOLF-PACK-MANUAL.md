# 🐺 WOLF PACK AUTONOMOUS TRADING SYSTEM

## WHAT IS THIS?

This is a **fully autonomous paper trading system** that:
- ✅ **Automatically finds** trade setups using multiple strategies
- ✅ **Automatically executes** paper trades when confidence is high (70%+)
- ✅ **Automatically learns** from losses (asks Fenrir "what went wrong?")
- ✅ **Automatically manages** positions (stop losses, take profits)
- ✅ **Runs 24/7** with intelligent sleep schedules
- ✅ **Uses ALL free data** (6 APIs + yfinance)

## ONE COMMAND TO RUN EVERYTHING

```bash
python master.py
```

That's it. The Wolf Brain will:
1. Connect to Alpaca Paper Trading
2. Connect to Ollama (Fenrir AI)
3. Load all strategy modules
4. Start 24/7 autonomous trading
5. Scan premarket at 4-7:30 AM
6. Execute trades automatically
7. Manage positions with stops/targets
8. Learn from every loss

## QUICK START

### 1. Test Your Setup
```bash
python master.py --test-setup
```
This checks:
- ✅ Alpaca connection & portfolio value
- ✅ Ollama/Fenrir AI working
- ✅ All 6 APIs functional
- ✅ Database ready
- ✅ Modules loaded

### 2. View Dashboard
```bash
python master.py --dashboard-only
```
Shows:
- Active positions with P&L
- Recent trades (wins/losses)
- Strategy performance
- Pending trade ideas
- Lessons learned

### 3. Run a Test Scan
```bash
python master.py --scan-now
```
Scans:
- Biotech catalysts (PDUFA dates)
- Premarket gainers
- Generates intel report

### 4. GO FULLY AUTONOMOUS
```bash
python master.py
```
Runs 24/7. Press Ctrl+C to stop.

## STRATEGIES

The Wolf Brain uses **7 different strategies**:

### 1. PDUFA Runup (Biotech Catalyst)
- **Setup**: FDA decision date 7-14 days away
- **Entry**: Current price (buy in the window)
- **Target**: 15-30% (typical PDUFA runup)
- **Stop**: 12% (biotech can be volatile)
- **Position**: 3% (binary risk)
- **Example**: AQST, PHAR, IRON all have PDUFA Jan 31

### 2. Insider Buying
- **Setup**: 3+ director purchases in last 90 days
- **Entry**: Current price (follow smart money)
- **Target**: 30%
- **Stop**: 10%
- **Position**: 5% if conviction 9/10, 3% otherwise
- **Example**: PALI (3 buys, $22k, conviction 9/10)

### 3. Compression Breakout
- **Setup**: 10+ days flat + catalyst + volume spike
- **Entry**: 2% above compression (breakout)
- **Target**: 25%
- **Stop**: 5% (tight technical stop)
- **Position**: 5% (clear setup)

### 4. Gap and Go
- **Setup**: 5%+ premarket gap + 10x volume + holds at 6 AM
- **Entry**: On first pullback after 9:30 AM
- **Target**: 20-50%
- **Stop**: Below premarket low
- **Position**: 5%

### 5. Wounded Prey
- **Setup**: Down 20-40% from highs + positive catalyst
- **Entry**: On reversal signal
- **Target**: 30-50% (recovery)
- **Stop**: 10%
- **Position**: 4%

### 6. Head Hunter
- **Setup**: Low float <20M + catalyst + short interest >20%
- **Entry**: On volume spike
- **Target**: 50%+ (squeeze potential)
- **Stop**: 8%
- **Position**: 3% (volatile)

### 7. Night Research
- **Setup**: Overnight homework finds movers
- **Entry**: Before premarket spike
- **Target**: 20%
- **Stop**: 8%
- **Position**: 4%

## AUTO-EXECUTION RULES

The brain will **automatically execute** a paper trade if:

1. **Confidence >= 70%** (strategy-specific thresholds)
2. **Daily trade limit not hit** (max 5 per day)
3. **Position limit not hit** (max 5 total)
4. **Biotech limit not hit** (max 3 biotech)
5. **Risk management passed** (position sizing rules)

When a trade is executed, you'll see:
```
🎯 AUTO-EXECUTING paper trade: AQST
   Strategy: PDUFA_RUNUP
   Confidence: 85%
   Entry: $5.50 | Stop: $4.84 | Target: $6.88
✅ AUTO-EXECUTED: AQST - 50 shares @ $5.50
```

## POSITION MANAGEMENT

The brain **automatically manages** positions:

### Stop Loss Hit
```
🛑 STOP HIT: AQST @ $4.80 (stop was $4.84)
   Loss: -12.7%
🧠 ANALYZING LOSS: AQST (PDUFA_RUNUP)
📚 Lesson learned and stored:
   WHAT WENT WRONG: FDA meeting leaked negative...
```

### Target Hit
```
🎯 TARGET HIT: AQST @ $6.90
   Profit: +25.5%
   📈 Moved stop to breakeven, holding 25 shares
```

### Emergency Exit
```
🚨 EMERGENCY EXIT: TICKER down -20.5%
```

## LEARNING FROM LOSSES

When a trade loses money, Fenrir automatically analyzes it:

1. **What went wrong?** (Specific cause)
2. **Could it be avoided?** (Warning signs?)
3. **Lesson learned** (Key takeaway)
4. **Strategy adjustment** (Change needed?)

All lessons stored in database and used to improve future trades.

## DATA SOURCES

The brain uses **ALL free data sources**:

| Source | Purpose | Rate Limit |
|--------|---------|------------|
| Finnhub | News + Insider trades | 60/min |
| NewsAPI | Breaking news | 100/day |
| Polygon | Fundamentals + News | 5/min |
| Alpha Vantage | PE ratios + Analyst targets | 25/day |
| SEC Edgar | Form 4 insider filings | Unlimited |
| yfinance | Price data | Unlimited |

## 24/7 SCHEDULE

The Wolf Brain has a **smart sleep schedule**:

| Time | Status | Activity | Check Interval |
|------|--------|----------|----------------|
| 12 AM - 4 AM | Overnight | Deep research | 1 hour |
| 4:00 AM | Premarket Early | **First scan** + biotech catalysts | 1 minute |
| 5:00 AM | Premarket Early | **Second scan** | 1 minute |
| 5:30 AM | Premarket Early | **Building scan** | 1 minute |
| 6:00 AM | Premarket Prime | **Volume confirmation** | 1 minute |
| 6:30 AM | Premarket Prime | **Prime time** | 1 minute |
| 7:00 AM | Premarket Prime | **Peak action** | 1 minute |
| 7:30 AM | Premarket Prime | **Final scan** | 1 minute |
| 9:00-9:30 AM | Premarket Final | Final positioning | 5 minutes |
| 9:30 AM - 4 PM | Market Open | **Active trading** | 2 minutes |
| 4 PM - 8 PM | After Hours | Light research | 15 minutes |

## RISK MANAGEMENT

Hard-coded limits:

- ✅ **Max 5 daily trades** (prevents overtrading)
- ✅ **Max 5 open positions** (diversification)
- ✅ **Max 3 biotech positions** (binary risk)
- ✅ **Max 2 per strategy** (prevent concentration)
- ✅ **Position sizing**:
  - Test trades: 2%
  - Proven setups: 5%
  - Binary (biotech): 3%
  - High conviction: 5%

## FILES

### Core System
- `master.py` - **RUN THIS** - Main orchestrator
- `autonomous_brain.py` - 24/7 brain (2300+ lines)
- `strategy_coordinator.py` - Multi-strategy coordination
- `dashboard.py` - Unified dashboard

### Modules
- `modules/biotech_catalyst_scanner.py` - FDA calendar + PDUFA tracking
- `modules/biotech_prompts.py` - Fenrir analysis prompts
- `modules/wolf_pack_rules.py` - All trading rules documented

### Support
- `night_research.py` - Overnight homework
- `test_apis.py` - Test all APIs

### Data Files (Auto-Generated)
- `data/wolf_brain/autonomous_memory.db` - SQLite database
- `data/wolf_brain/LATEST_INTEL_REPORT.txt` - Daily intel
- `data/wolf_brain/DASHBOARD.txt` - Latest dashboard
- `data/wolf_brain/PREMARKET_SCANS_*.txt` - Scan results

## DATABASE TABLES

### trades
- All paper trades (entry, exit, P&L)
- Status: 'open', 'closed_win', 'closed_loss'

### paper_trade_ideas
- Fenrir's trade ideas
- Status: 'PENDING', 'EXECUTED', 'REJECTED'
- Includes confidence scores

### lessons_learned
- All loss analyses
- Fenrir's reasoning
- Lessons extracted

### decisions
- All brain decisions
- Confidence scores
- Outcomes tracked

### research
- Ticker research cache
- Prevents redundant API calls

### scan_results
- Historical scan results
- Tracks what was found when

## COMMAND LINE OPTIONS

```bash
# Full autonomous mode (DEFAULT)
python master.py

# Test setup only
python master.py --test-setup

# Dashboard only
python master.py --dashboard-only

# Run all scanners now
python master.py --scan-now

# Generate intel report
python master.py --report

# Dry run mode (no actual trades)
python master.py --dry-run
```

## TROUBLESHOOTING

### "Alpaca not connected"
Check `.env` file has:
```
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

### "Ollama not connected"
1. Make sure Ollama is running: `ollama serve`
2. Check model exists: `ollama list`
3. If not, pull Fenrir: `ollama pull fenrir:latest`

### "Database locked"
Only run one instance of the brain at a time.

### Computer went to sleep (missed 4 AM scan)
**Solution**: Keep computer awake or run on a server/VPS.

Windows: Settings > Power > Screen and sleep > Never

### APIs not working
Run test: `python test_apis.py`

Check rate limits:
- Finnhub: 60/min
- NewsAPI: 100/day (resets midnight UTC)
- Alpha Vantage: 25/day (use sparingly)

## WHAT MAKES THIS AUTONOMOUS?

Traditional trading bots require:
- ❌ Manual setup of each trade
- ❌ Manual monitoring of positions
- ❌ Manual analysis of losses
- ❌ Manual strategy adjustments

**Wolf Brain does it ALL automatically:**
- ✅ Finds setups → Analyzes with AI → Executes if confident
- ✅ Monitors positions → Hits stop → Closes → Analyzes why
- ✅ Learns from losses → Adjusts strategy multipliers → Improves
- ✅ Coordinates multiple strategies → Ranks opportunities → Diversifies

## PERFORMANCE TRACKING

View anytime with:
```bash
python master.py --dashboard-only
```

Dashboard shows:
- Total P&L
- Win rate (by strategy)
- Open positions
- Recent trades
- Lessons learned

## SAFETY FEATURES

1. **Paper trading only** (no real money)
2. **Hard limits** (5 trades/day, 5 positions max)
3. **Stop losses** (every trade has one)
4. **Emergency exit** (auto-closes at -20%)
5. **Dry run mode** (test without executing)
6. **Ctrl+C anytime** (graceful shutdown)

## NEXT STEPS

### To run 24/7 on a server:
1. Set up AWS EC2 / DigitalOcean / Raspberry Pi
2. Install dependencies
3. Keep awake (no sleep)
4. Run: `nohup python master.py > wolf.log 2>&1 &`

### To add more strategies:
1. Create new module in `modules/`
2. Add to `strategy_coordinator.py`
3. Add auto-execution logic to `autonomous_brain.py`

### To improve AI analysis:
1. Fine-tune Fenrir on your win/loss data
2. Add more context to prompts
3. Adjust confidence thresholds

## PHILOSOPHY

**The Wolf Pack way:**
- Hunt in packs (multiple strategies)
- Patience (wait for 7-14 day windows)
- Learn from mistakes (analyze every loss)
- Follow the smart money (insider buying)
- Strike when ready (auto-execute high confidence)
- Protect the pack (risk management)

---

Built with 🐺 by the Wolf Pack

**Remember: Paper trading only. This is for learning and testing strategies.**
