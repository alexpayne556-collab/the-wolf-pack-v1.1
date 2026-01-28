# 🐺 AUTONOMOUS WOLF BRAIN - User Guide

**This is not a toy. This is a real autonomous trading system that makes real decisions with real money.**

---

## 🎯 What This Brain Does

### Autonomous Capabilities
1. **Scans** for opportunities using 7-signal convergence engine
2. **Decides** which trades to enter based on strict rules
3. **Executes** real orders in Alpaca (paper or live)
4. **Monitors** all positions every 5 minutes
5. **Exits** positions based on:
   - Stop loss hit
   - Profit target reached
   - Thesis broken (convergence drops >30 points)
   - Trailing stops for winners
6. **Learns** from every trade outcome
7. **Adapts** position sizing based on convergence scores

---

## 🚀 Getting Started

### Prerequisites
```bash
# Install dependencies
pip install alpaca-trade-api yfinance python-dotenv

# Set up .env file with your Alpaca keys
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
PAPER_TRADING=true  # Set to false for live trading (BE CAREFUL!)
```

### Running Modes

#### 1. Scan Mode (Safe - No Trading)
Just scan for opportunities, no execution:
```bash
python autonomous_wolf_brain.py --mode scan
```

**Output:**
```
TOP OPPORTUNITIES:
1. IBRX - 85/100
   Price: $5.90
   Volume: 2.8x
   Signals: biotech_catalyst, wounded_prey, volume_spike
   Thesis: BLA approval catalyst approaching
```

#### 2. Single Cycle Mode (Controlled)
Run one complete trading cycle: scan → decide → execute → monitor:
```bash
python autonomous_wolf_brain.py --mode cycle
```

**What happens:**
- Monitors existing positions
- Scans for new opportunities
- Evaluates top 3 opportunities
- Executes if rules pass
- Shows summary

#### 3. Autonomous Mode (24/7)
Run continuously, checking every 5 minutes:
```bash
python autonomous_wolf_brain.py --mode autonomous
```

**Custom interval:**
```bash
# Check every 10 minutes
python autonomous_wolf_brain.py --mode autonomous --interval 600
```

**To stop:** Press `Ctrl+C`

---

## 🛡️ Safety Features

### Built-In Risk Management
1. **Min Convergence:** Won't trade below 50/100 (configurable)
2. **Min Volume:** Won't trade below 1.5x average volume
3. **Max Positions:** Won't hold more than 10 positions
4. **Max Portfolio Risk:** Won't exceed 50% total risk
5. **Stop Losses:** Automatic 10% stop on every position
6. **Learning Filter:** Blocks setups that historically failed for YOU

### Position Sizing by Convergence
| Score | Max Position | Risk Per Trade | Example |
|-------|--------------|----------------|---------|
| 85-100 | 12% | 2.0% | IBRX (85) → $120 position on $1000 account |
| 70-84 | 8% | 1.5% | RDW (78) → $80 position |
| 50-69 | 4% | 1.0% | MRNO (55) → $40 position |
| <50 | 0% | 0% | DNN (45) → NO TRADE |

### Automatic Exit Rules
1. **Stop Loss Hit:** Immediate exit at 10% loss
2. **Profit Target:** Exit at 2:1 R/R (20% gain with 10% stop)
3. **Thesis Broken:** Exit if convergence drops >30 points
4. **Trailing Stops:**
   - +10% gain → move stop to breakeven
   - +20% gain → move stop to breakeven + 10%

---

## 📊 Live Monitoring

### What You See During Autonomous Mode

```
🐺 TRADING CYCLE - 2026-01-27 14:30:00
======================================================================

👁️ MONITORING 3 POSITIONS...

   IBRX: $5.95 (+1.2%)
      Entry: $5.88 | Stop: $5.29 | Target: $7.05
      
   RDW: $5.20 (+0.6%)
      Entry: $5.17 | Stop: $4.65 | Target: $6.21
      
   MRNO: $2.15 (-3.2%)
      Entry: $2.22 | Stop: $2.00 | Target: $2.66

🔍 SCANNING FOR OPPORTUNITIES (45 tickers)...
   ✅ UEC: 72/100 | Vol 2.1x | $19.50
   ✅ LUNR: 68/100 | Vol 1.8x | $8.30
   ⏭️  DNN: Learning engine says NO - Low win rate on this ticker (30%)

   Found 2 opportunities

🤔 DECISION: UEC
   Convergence: 72/100
   Volume: 2.1x
   Thesis: Nuclear sector momentum + uranium demand
   Decision: ✅ ENTER
   Reason: APPROVED - Convergence 72, Volume 2.1x, Risk 1.5%

💰 EXECUTING BUY: UEC
   Price: $19.50
   Shares: 4
   Position: $78.00 (7.8%)
   Stop Loss: $17.55
   Target: $23.40
   Risk: $15.00 (1.5%)
   ✅ Order submitted: abc123
   ✅ FILLED at $19.48
   🛡️ Stop loss placed at $17.55
   🎉 Position opened successfully

📊 CYCLE COMPLETE
   Portfolio: $1,002.50
   Positions: 4/10
   Buying Power: $922.50

   💤 Sleeping for 300 seconds...
   Next check: 14:35:00
```

---

## 🧠 How It Makes Decisions

### Entry Decision Flow
```
1. Is convergence >= 50? 
   ❌ → PASS
   ✅ → Continue
   
2. Is volume >= 1.5x?
   ❌ → PASS
   ✅ → Continue
   
3. Does learning engine approve?
   ❌ → PASS (shows historical win rate)
   ✅ → Continue
   
4. Do trading rules pass?
   ❌ → PASS (violates 10 Commandments)
   ✅ → Continue
   
5. Is portfolio risk < 50%?
   ❌ → PASS (would exceed risk limit)
   ✅ → EXECUTE TRADE
```

### Exit Decision Flow (Every 5 Minutes)
```
For each position:

1. Price <= Stop Loss?
   ✅ → SELL IMMEDIATELY
   ❌ → Continue
   
2. Price >= Profit Target?
   ✅ → SELL (Take Profit)
   ❌ → Continue
   
3. Has convergence dropped >30 points?
   ✅ → SELL (Thesis Broken)
   ❌ → Continue
   
4. Is position up 10%+?
   ✅ → Move stop to breakeven
   ❌ → Continue
   
5. Is position up 20%+?
   ✅ → Move stop to breakeven + 10%
   ❌ → Hold
```

---

## 📝 Real Examples

### Example 1: DNN Lesson Applied
**Before (Manual):**
- Convergence: 45 (LOW)
- Volume: 1.2x (WEAK)
- Intel: Stale
- Human Decision: BUY (mistake)
- Result: -3.78%, panic sold

**Now (Autonomous Brain):**
```
🤔 DECISION: DNN
   Convergence: 45/100
   Volume: 1.2x
   Decision: ❌ PASS
   Reason: Convergence 45 < 50
```

**Result:** Avoided the loss automatically

### Example 2: IBRX Perfect Setup
**Autonomous Detection:**
- Convergence: 85 (CRITICAL)
- Volume: 2.8x (STRONG)
- Signals: biotech_catalyst, wounded_prey, volume_spike
- Learning engine: "This setup has 68% win rate"

**Execution:**
```
💰 EXECUTING BUY: IBRX
   Position: $120 (12% of portfolio)
   Stop Loss: $3.42
   Target: $4.56
   Risk: $20 (2%)
   ✅ FILLED at $3.80
```

**Monitoring (Day 18):**
```
IBRX: $5.90 (+55.3%)
   Entry: $3.80 | Stop: $4.18 | Target: $4.56
   📈 Trailing stop to $4.18 (breakeven + 10%)
   Status: Still holding, let it run
```

### Example 3: MRNO Speculative Win
**Autonomous Detection:**
- Convergence: 55 (MEDIUM)
- Volume: 3.5x (EXTREME)
- Signals: momentum_play, volume_spike

**Position Sizing (Conservative):**
```
💰 EXECUTING BUY: MRNO
   Position: $40 (4% of portfolio - small speculative)
   Stop Loss: $0.95
   Target: $1.26
   Risk: $10 (1%)
```

**Result:**
- Hit +20% → Stop moved to breakeven
- Hit +50% → Stop moved to +10%
- Currently: +111%, trailing stop protecting gains

---

## ⚙️ Configuration

### Edit `BrainConfig` class to customize:

```python
class BrainConfig:
    # Trading constraints
    MIN_CONVERGENCE = 50  # Minimum to trade (increase for safety)
    OPTIMAL_CONVERGENCE = 70  # Ideal threshold
    MIN_VOLUME_RATIO = 1.5  # Minimum volume (increase for confirmation)
    
    # Position management
    MAX_POSITIONS = 10  # Max open positions
    MAX_PORTFOLIO_RISK = 0.50  # 50% max total risk
    CHECK_INTERVAL = 300  # 5 minutes
    
    # Risk settings
    STOP_LOSS_PCT = 0.10  # 10% stop loss
    PROFIT_TARGET_MULTIPLIER = 2.0  # 2:1 R/R
    
    # Scan universe (add/remove tickers)
    SCAN_UNIVERSE = [
        'IBRX', 'DNN', 'RDW', 'MRNO',
        'UUUU', 'UEC', 'LEU', 'UROY',
        # ... add your watchlist
    ]
```

---

## 🚨 IMPORTANT WARNINGS

### Before Going Live
1. ✅ Test in paper trading for 30+ days
2. ✅ Verify stop losses are working
3. ✅ Confirm exit logic is sound
4. ✅ Check all API keys are correct
5. ✅ Start with small capital ($100-500)

### When Running Autonomous
- ⚠️ Check every few hours first week
- ⚠️ Verify stop losses are being placed
- ⚠️ Monitor for any API errors
- ⚠️ Keep buying power available (don't go all-in)

### Transition to Live Trading
```bash
# Change in .env file:
PAPER_TRADING=false  # ⚠️ DANGER ZONE

# Start with SMALL positions:
# In BrainConfig, reduce:
MAX_POSITIONS = 3  # Start with max 3 positions
MAX_PORTFOLIO_RISK = 0.20  # Only risk 20% total
```

---

## 📈 Performance Tracking

### All trades logged to `data/wolfpack.db`

**Query your performance:**
```python
import sqlite3
conn = sqlite3.connect('data/wolfpack.db')
cursor = conn.cursor()

# See all trades
cursor.execute('''
    SELECT ticker, action, shares, price, timestamp 
    FROM trades 
    ORDER BY timestamp DESC 
    LIMIT 10
''')
```

**Learning engine tracks:**
- Win rate by setup type
- Avg hold time
- Best convergence thresholds
- Which signals work for YOU
- Patterns that fail for YOU

---

## 🎯 Next Steps

### Week 1: Paper Trading
1. Run in `--mode cycle` daily
2. Review decisions manually
3. Log all trades
4. Verify stop losses work

### Week 2-4: Autonomous Paper
1. Run in `--mode autonomous`
2. Check 2-3x per day
3. Verify exits are working
4. Track win rate

### Month 2+: Consider Live
1. Review paper trading results
2. If win rate >60%, consider live
3. Start with tiny positions
4. Scale up slowly

---

## 🆘 Troubleshooting

### "Convergence score too low"
**Fix:** Stock doesn't meet minimum threshold. Either lower `MIN_CONVERGENCE` or wait for better setups.

### "At max positions"
**Fix:** Brain won't add more until existing positions close. Increase `MAX_POSITIONS` or wait.

### "Portfolio risk exceeded"
**Fix:** Too much capital at risk. Increase `MAX_PORTFOLIO_RISK` or close some positions.

### "Learning engine says NO"
**Fix:** This setup failed historically for you. Trust the system or override in code.

### "API Error"
**Fix:** Check Alpaca credentials in `.env`, verify internet connection, check rate limits.

---

## 🐺 The Philosophy

This brain embodies everything we learned from DNN, IBRX, RDW, MRNO:

**From DNN we learned:**
- Don't trade low convergence (<50)
- Don't trade weak volume (<1.5x)
- Verify all intel is fresh

**From IBRX we learned:**
- High convergence (85+) = big positions
- Strong volume (2x+) = confirmation
- Hold through noise if thesis intact

**From Learning Engine:**
- Some setups work FOR YOU, some don't
- Block historically failing patterns
- Adapt based on YOUR outcomes

**The Result:**
A brain that thinks like you, trades like you, but without emotions, FOMO, or panic.

---

**🐺 The wolf that AUTOMATES is the wolf that SCALES.**

**Let the brain do the work. You just monitor and learn.**
