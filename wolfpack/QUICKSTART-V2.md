# 🐺 WOLF PACK V2 - QUICKSTART

## ✅ SETUP (One Time)

### 1. Install Missing Package
```bash
pip install pytz
```

### 2. Initialize V2 Database
```bash
python wolfpack_db_v2.py
```

---

## 🚀 DAILY WORKFLOW

### MORNING (Before Market)
Double-click: **START_MONITOR.bat**
- Starts real-time monitoring at 9:30 AM ET
- Scans all 99 stocks every 2 minutes
- Alerts when moves >3% detected
- Auto-fetches catalysts (news + SEC filings)
- Runs until 4:00 PM ET

**Leave it running all day in background**

---

### WHEN YOU TRADE
Double-click: **LOG_TRADE.bat**
- Quick decision logger
- Records: ticker, action (BUY/SELL/WATCH), price, quantity, reasoning
- Links to detected moves and catalysts

**Example:**
```
Ticker: KTOS
Action: 1 (BUY)
Price: $118.50
Quantity: 10
Reasoning: DOD contract 8-K, volume confirmed, sector strong
```

---

### AFTER MARKET
Double-click: **UPDATE_OUTCOMES.bat**
- Updates Day 1, 2, 3, 5, 10 results for all your trades
- Shows what happened AFTER your decisions
- Validates your thesis

---

### WEEKLY REVIEW
Double-click: **VIEW_PATTERNS.bat**
- Analyzes YOUR trading patterns
- Shows YOUR win rate, avg returns
- Reveals what works for YOU specifically
- "You bought 8 DOD contract plays → 75% win rate, +12% avg"

---

## 🎯 THE WORKFLOW IN ACTION

**10:15 AM** - Monitor detects: "🚨 KTOS up 5.2% on 3.1x volume"
**10:16 AM** - Catalyst fetcher finds: "8-K filed 10:05 AM - DOD contract announcement"
**10:20 AM** - You review alert, decide to BUY
**10:21 AM** - Run LOG_TRADE.bat, log decision: "Bought 10 @ $118.50"
**Next Day** - Run UPDATE_OUTCOMES.bat: "KTOS: Day 1 +2.3%"
**5 Days Later** - Run UPDATE_OUTCOMES.bat: "KTOS: Day 5 +8.1% ✅"
**Next Week** - Run VIEW_PATTERNS.bat: "DOD contract plays: 75% win rate"

---

## 📁 FILES YOU CARE ABOUT

### Active Scripts:
- **START_MONITOR.bat** - Real-time scanner (run during market hours)
- **LOG_TRADE.bat** - Record your decisions
- **UPDATE_OUTCOMES.bat** - Update trade results (daily after close)
- **VIEW_PATTERNS.bat** - See your edge (weekly)

### Database:
- **data/wolfpack_v2.db** - All your data (moves, catalysts, decisions, outcomes)

### Old Files (Ignore):
- wolfpack_recorder.py, wolfpack_updater.py, etc. (V1 - useless price recording)

---

## 🔥 THE DIFFERENCE

**V1 (OLD):** Records prices after market close → Can get this from yfinance anytime → Zero value

**V2 (NEW):**
- ✅ Catches moves DURING market hours (can't go back in time)
- ✅ Fetches catalysts IMMEDIATELY (news gets buried)
- ✅ Logs YOUR decisions (only you know what you did)
- ✅ Tracks YOUR outcomes (validates your thesis)
- ✅ Learns YOUR patterns (your actual edge)

---

## 💰 EXPECTED RESULTS

**Week 1:** Get used to logging trades, start building decision history

**Week 2-4:** Outcome data starts populating, see what's working

**Month 2-3:** Patterns emerge - "I win 70% when I buy DOD contracts with volume confirmation"

**Month 6+:** Clear edge - know exactly what YOU're good at, backed by YOUR actual data

---

## 🐺 READY TO START

1. `pip install pytz`
2. `python wolfpack_db_v2.py`
3. Tomorrow morning: Double-click **START_MONITOR.bat**
4. When you trade: Double-click **LOG_TRADE.bat**
5. After close: Double-click **UPDATE_OUTCOMES.bat**
6. Weekly: Double-click **VIEW_PATTERNS.bat**

**That's it. No fluff. Pure signal.**

🐺 LLHR
