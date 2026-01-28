# 🚀 QUICK START: Alpaca Trade Sync

## Start SMART Instead of Starting From Zero

### The Problem:
Traditional learning systems start with zero data. You need 10-50-100 trades before patterns emerge. **That's slow.**

### The Solution:
You've been trading manually on Alpaca/Robinhood. **That history contains YOUR patterns!**

**Import it. Learn from it. Start smart on Day 1.**

---

## 📥 How to Import Your Trading History

### Step 1: Install Alpaca Library
```bash
pip install alpaca-py
```

### Step 2: Add API Keys to .env
Create or edit `.env` in your wolfpack directory:

```bash
# For paper trading account:
ALPACA_PAPER_KEY_ID=your_paper_key_here
ALPACA_PAPER_SECRET_KEY=your_paper_secret_here

# For live trading account:
ALPACA_LIVE_KEY_ID=your_live_key_here
ALPACA_LIVE_SECRET_KEY=your_live_secret_here
```

**Where to get keys:**
1. Go to [alpaca.markets](https://alpaca.markets)
2. Login to your account
3. Navigate to API Keys section
4. Generate new keys (paper or live)
5. Copy to .env file

### Step 3: Run the Sync
```bash
cd wolfpack
python services/alpaca_trade_sync.py
```

**You'll be asked:**
- Import from Paper or Live? (choose 1 or 2)
- How many days of history? (default: 90)

---

## 🎯 What Happens During Sync

### 1. **Fetch Orders**
```
📊 Fetched 142 filled orders from last 90 days
```
Pulls all your filled buy/sell orders from Alpaca.

### 2. **Match Trades**
```
✅ Matched 47 complete trades
📌 2 open positions not included (still holding)
```
Matches buy/sell pairs to reconstruct complete trades.

### 3. **Import to Database**
```
✅ Imported 47 trades
⏭️  Skipped 0 duplicates
```
Adds all trades to learning engine database with:
- Entry/exit dates and prices
- Profit/loss percentages
- Hold times
- Win/loss outcomes

### 4. **Analyze Your Patterns**
```
📊 YOUR TRADING PATTERNS (from 47 trades):

   Overall Stats:
   • Win Rate: 68.1% (32W / 15L)
   • Avg Winner: +12.3%
   • Avg Loser: -6.2%
   • Avg Hold Time: 3.2 days

   Your Best Tickers:
   • IBRX: 80% win rate (4W/1L), +34.5% total
   • MU: 75% win rate (3W/1L), +28.3% total
   • KTOS: 67% win rate (2W/1L), +15.7% total

   💡 Insights:
   ✅ Strong win rate - system will prioritize your style
   ✅ You cut losers well - good risk management
   📌 Swing trader style - multi-day holds
```

**System now knows YOUR patterns from 47 trades!**

---

## 🧠 What the System Learns

### From Your 47 Imported Trades:

**✅ Your Best Tickers:**
- IBRX: 80% win rate → **PRIORITIZE**
- MU: 75% win rate → **PRIORITIZE**
- KTOS: 67% win rate → **PRIORITIZE**

**❌ Your Worst Tickers:**
- XYZ: 20% win rate (1W/4L) → **AVOID**
- ABC: 25% win rate (1W/3L) → **AVOID**

**📈 Your Win/Loss Profile:**
- Avg winner: +12.3%
- Avg loser: -6.2%
- **Rule:** Cut at -5%, take profit at +12-15%

**⏱️ Your Hold Behavior:**
- Avg hold: 3.2 days (swing trader)
- **Rule:** Optimize for 2-5 day holds, not day trades

**🎯 Your Risk Management:**
- You cut losers at -6.2% avg (GOOD)
- You let winners run to +12.3% (GOOD)
- **Rule:** Your risk management is solid, keep it

---

## 🔥 Impact: Day 1 vs Day 50

### Without Alpaca Sync (Starting from Zero):

**Day 1:**
- System has no data
- Takes all convergence signals
- No filtering based on YOUR style
- Generic rules apply

**Day 10:**
- 5-8 trades executed
- Basic patterns emerging
- "Not enough data yet"

**Day 50:**
- 20-30 trades executed
- Patterns identified
- System finally knows YOUR style

### With Alpaca Sync (Starting with History):

**Day 1:**
- System has 47 trades of YOUR history
- **Already knows:**
  - Your best tickers (IBRX, MU, KTOS)
  - Your worst tickers (XYZ, ABC)
  - Your hold time (3.2 days avg)
  - Your win/loss profile (+12.3% / -6.2%)
  - Your risk management style
- **Blocks XYZ trade** (even though convergence 88/100)
  - Reason: "You lose 80% on XYZ historically"
- **Prioritizes IBRX trade** (convergence 82/100)
  - Reason: "You win 80% on IBRX historically"

**Result:** System is 50 days ahead from Day 1! 🚀

---

## 📊 Example: Pre-Trade Filter on Day 1

### Signal: XYZ Convergence 88/100

**Without History Sync:**
```
🧠 Learning Engine: No historical data yet - building experience
✅ Trade APPROVED
```
Takes the trade. Later: -8% loss. You historically lose on XYZ.

**With History Sync (47 trades imported):**
```
🧠 Learning Engine: XYZ has 20% win rate for you (1W/4L)
🚫 Trade BLOCKED
   Reason: You lose 80% on XYZ historically
   Historical win rate: 20%
```
**Trade rejected. Avoided another -8% loss.**

---

### Signal: IBRX Convergence 82/100

**Without History Sync:**
```
🧠 Learning Engine: No historical data yet - building experience
✅ Trade APPROVED (no preference)
```

**With History Sync (47 trades imported):**
```
🧠 Learning Engine: IBRX has 80% win rate for you (4W/1L)
✅ Trade APPROVED
   🔥 PRIORITY: Strong historical edge on this ticker!
   Historical win rate: 80%
   Avg return: +8.6%
```
**Trade prioritized with larger position size (Kelly Criterion).**

---

## 🎯 Recommended Workflow

### Week 0 (Before Day 1):
```bash
# Import your Alpaca history
python services/alpaca_trade_sync.py
```
**Result:** System starts smart with YOUR 50-100 historical trades

### Week 1-4 (System-Executed Trades):
```bash
# Run daily
python daily_monitor.py
```
**System:**
- Executes 1-3 new trades per day
- Filters based on imported + new data
- Refines patterns continuously

### Week 4+ (Fully Optimized):
**System knows:**
- Your complete trading history (imported + new)
- Your evolving patterns
- Your current vs historical behavior
- **Optimized to YOUR exact style**

---

## 🔧 Troubleshooting

### "API keys not found in .env"
- Check .env file exists in wolfpack directory
- Verify keys are spelled correctly:
  - `ALPACA_PAPER_KEY_ID` (not PAPER_API_KEY_ID)
  - `ALPACA_PAPER_SECRET_KEY` (not PAPER_SECRET_KEY_ID)

### "No orders found"
- Verify account has trade history
- Try longer timeframe: 180 days instead of 90
- Check you're using correct account (paper vs live)

### "Alpaca library not installed"
```bash
pip install alpaca-py
```

### "No complete trades found (all positions still open?)"
- Your orders are all buys with no sells
- Open positions are not imported (need both entry + exit)
- Close some positions, then re-run sync

---

## 📈 What's Next?

After syncing, you can:

1. **View your patterns:**
   ```bash
   python services/learning_engine.py
   ```

2. **Run system with learned filters:**
   ```bash
   python daily_monitor.py
   ```

3. **See pre-trade checks in action:**
   - System will reference YOUR imported history
   - Blocks tickers you historically lose on
   - Prioritizes tickers you historically win on

4. **Watch it get smarter:**
   - Every new trade adds to knowledge base
   - Imported history + new trades = complete picture
   - Fully personalized to YOUR trading style

---

## 🐺 The Advantage

**Traditional bot:** Starts dumb, learns slowly, makes YOUR mistakes for 50 trades before adapting.

**Wolf Pack:** Starts smart, already knows YOUR edges and mistakes from Day 1, optimizes immediately.

**You've already done the work. Now let the system learn from it.** 🚀

---

**Ready to import?**
```bash
cd wolfpack
python services/alpaca_trade_sync.py
```

**The wolf learns from the WHOLE pack's history, not just future trades.** 🐺
