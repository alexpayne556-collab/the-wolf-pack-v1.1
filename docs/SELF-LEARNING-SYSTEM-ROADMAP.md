# SELF-LEARNING SYSTEM ROADMAP
## Building a Pattern Recognition Engine That Learns What Actually Works

---

## THE VISION

A system that:
1. **Tracks every alert** (SEC filings, gap-ups, volume spikes)
2. **Records what happens next** (did it move 10%+? 20%+? or collapse?)
3. **Extracts features** (float size, volume ratio, catalyst type, time of day)
4. **Learns patterns** (what features predict winners vs traps)
5. **Improves over time** (more data = better predictions)

---

## PHASE 1: DATA COLLECTION (FREE - START HERE)

### What You Need to Track

**For every stock alert, log:**

```json
{
  "ticker": "ABCD",
  "timestamp": "2026-01-14 09:35:00",
  "source": "SEC_8K",
  "catalyst": "Government contract - $45M",
  
  // Initial state (T+0)
  "price_at_alert": 3.45,
  "volume_at_alert": 150000,
  "normal_volume": 50000,
  "volume_ratio": 3.0,
  "float": 8500000,
  "market_cap": 29000000,
  "time_of_day": "09:35",
  
  // Trap detection scores
  "reverse_split_12mo": false,
  "dilution_history": "low",
  "insider_ownership_pct": 15,
  "short_interest_pct": 8,
  "days_to_cover": 2.1,
  "otc_status": false,
  "52week_high_distance": -35,  // -35% from high
  
  // What happened (labels for ML)
  "price_15min": 3.62,
  "price_30min": 3.78,
  "price_60min": 3.95,
  "price_eod": 4.12,
  "price_day2": 4.35,
  "price_day5": 3.20,
  
  "max_gain_intraday": 19.4,  // Hit 4.12 intraday
  "held_overnight": true,
  "outcome": "winner",  // winner/trap/whipsaw
  "profit_t30_entry": 9.6,  // If entered at T+30min
  "profit_eod_exit": 9.0    // If exited EOD
}
```

### Free Data Sources

**Real-time/Intraday (Free Tiers):**
- **Finnhub**: 60 calls/min (you have key already)
- **Alpha Vantage**: 25 calls/day (you have key already)
- **Polygon.io**: 5 calls/min (you have key already)
- **Yahoo Finance**: Unlimited via `yfinance` Python library (no key needed)

**Historical Data (Free):**
- **Yahoo Finance**: 10+ years history, free
- **SEC EDGAR**: All filings free
- **FINRA**: Short interest data free
- **OTC Markets**: Basic data free

**Volume/Price Data:**
```python
import yfinance as yf

# Get intraday data (last 7 days, 1-min intervals)
ticker = yf.Ticker("AAPL")
df = ticker.history(period="7d", interval="1m")

# Free, unlimited, no API key needed
```

### Storage (Free)

**Option 1: SQLite Database (Recommended)**
- Built into Python
- No server needed
- Fast queries
- Handles millions of rows

**Option 2: CSV Files**
- Simple
- Excel-compatible
- Good for small datasets (<10k rows)

**Option 3: JSON Files**
- Human-readable
- Good for starting out
- Slow for large datasets

---

## PHASE 2: AUTOMATED LOGGING SYSTEM

### The Data Collection Loop

```python
# src/core/data_logger.py

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import json

class PatternLogger:
    """
    Logs every alert and tracks what happens next.
    This is your training data.
    """
    
    def __init__(self, db_path="data/pattern_history.db"):
        self.db = sqlite3.connect(db_path)
        self.setup_database()
    
    def setup_database(self):
        """Create tables if they don't exist"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                ticker TEXT,
                timestamp TEXT,
                source TEXT,
                catalyst TEXT,
                
                -- Initial state
                price_at_alert REAL,
                volume_at_alert INTEGER,
                normal_volume INTEGER,
                volume_ratio REAL,
                float INTEGER,
                market_cap REAL,
                
                -- Trap detection
                reverse_split_12mo INTEGER,
                dilution_score REAL,
                insider_ownership REAL,
                short_interest REAL,
                otc_status INTEGER,
                distance_from_52w_high REAL,
                
                -- Outcomes (filled later)
                price_15min REAL,
                price_30min REAL,
                price_60min REAL,
                price_eod REAL,
                price_day2 REAL,
                price_day5 REAL,
                
                max_gain_intraday REAL,
                outcome TEXT,  -- winner/trap/whipsaw
                profit_if_entered_t30 REAL
            )
        """)
        self.db.commit()
    
    def log_alert(self, ticker, source, catalyst, trap_scores):
        """
        Log a new alert when it first appears.
        This captures T+0 state.
        """
        
        # Get current price/volume from Yahoo Finance (free)
        stock = yf.Ticker(ticker)
        current = stock.history(period="1d", interval="1m")
        
        if current.empty:
            return None
        
        price = current['Close'].iloc[-1]
        volume = int(current['Volume'].sum())
        
        # Get average volume (last 30 days)
        hist = stock.history(period="30d")
        avg_volume = int(hist['Volume'].mean())
        
        # Insert into database
        cursor = self.db.execute("""
            INSERT INTO alerts (
                ticker, timestamp, source, catalyst,
                price_at_alert, volume_at_alert, normal_volume, volume_ratio,
                float, market_cap,
                reverse_split_12mo, dilution_score, insider_ownership,
                short_interest, otc_status, distance_from_52w_high
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            datetime.now().isoformat(),
            source,
            catalyst,
            price,
            volume,
            avg_volume,
            volume / avg_volume if avg_volume > 0 else 0,
            trap_scores.get('float', 0),
            trap_scores.get('market_cap', 0),
            trap_scores.get('reverse_split_12mo', 0),
            trap_scores.get('dilution_score', 0),
            trap_scores.get('insider_ownership', 0),
            trap_scores.get('short_interest', 0),
            trap_scores.get('otc_status', 0),
            trap_scores.get('distance_from_52w_high', 0)
        ))
        
        self.db.commit()
        return cursor.lastrowid
    
    def update_outcomes(self, alert_id, ticker):
        """
        Called later (after 15min, 30min, EOD, etc)
        to record what actually happened.
        """
        
        stock = yf.Ticker(ticker)
        
        # Get alert timestamp
        alert = self.db.execute(
            "SELECT timestamp, price_at_alert FROM alerts WHERE id = ?",
            (alert_id,)
        ).fetchone()
        
        if not alert:
            return
        
        alert_time = datetime.fromisoformat(alert[0])
        alert_price = alert[1]
        
        # Get price at various intervals
        hist = stock.history(
            start=alert_time.date(),
            end=(alert_time + timedelta(days=6)).date(),
            interval="1m"
        )
        
        if hist.empty:
            return
        
        # Find prices at key times
        price_15min = self._get_price_at_time(hist, alert_time + timedelta(minutes=15))
        price_30min = self._get_price_at_time(hist, alert_time + timedelta(minutes=30))
        price_60min = self._get_price_at_time(hist, alert_time + timedelta(minutes=60))
        price_eod = hist['Close'].iloc[-1] if not hist.empty else None
        
        # Calculate max intraday gain
        max_price = hist['High'].max()
        max_gain = ((max_price - alert_price) / alert_price * 100) if max_price else 0
        
        # Determine outcome
        outcome = self._classify_outcome(max_gain, price_eod, alert_price)
        
        # Calculate profit if entered at T+30
        profit_t30 = None
        if price_30min and price_eod:
            profit_t30 = ((price_eod - price_30min) / price_30min * 100)
        
        # Update database
        self.db.execute("""
            UPDATE alerts SET
                price_15min = ?,
                price_30min = ?,
                price_60min = ?,
                price_eod = ?,
                max_gain_intraday = ?,
                outcome = ?,
                profit_if_entered_t30 = ?
            WHERE id = ?
        """, (
            price_15min, price_30min, price_60min, price_eod,
            max_gain, outcome, profit_t30, alert_id
        ))
        
        self.db.commit()
    
    def _get_price_at_time(self, hist, target_time):
        """Get price closest to target time"""
        if hist.empty:
            return None
        
        # Find closest timestamp
        closest_idx = (hist.index - target_time).abs().argmin()
        return hist['Close'].iloc[closest_idx]
    
    def _classify_outcome(self, max_gain, price_eod, price_alert):
        """Classify the outcome"""
        
        if max_gain >= 15:
            return "winner"
        elif max_gain < 5:
            return "trap"
        else:
            # Check if it held gains
            eod_gain = ((price_eod - price_alert) / price_alert * 100) if price_eod else 0
            
            if max_gain >= 10 and eod_gain < max_gain * 0.3:
                return "whipsaw"  # Spiked then faded
            else:
                return "moderate"
```

---

## PHASE 3: FEATURE EXTRACTION

### What Features Matter?

**From research, track these:**

1. **Volume dynamics**
   - Volume ratio (current / average)
   - Volume pattern (sustained vs spiking)
   - Time since volume spike started

2. **Float characteristics**
   - Float size
   - Float rotation (volume / float)
   - Insider ownership %
   - Short interest %

3. **Catalyst quality**
   - Type (contract / M&A / FDA / etc)
   - Dollar amount (if mentioned)
   - Keyword density

4. **Technical position**
   - Distance from 52-week high
   - Price above/below VWAP
   - Recent price action (up 3 days straight? flat?)

5. **Trap indicators**
   - Reverse splits in 12 months
   - Dilution history
   - OTC status
   - Market maker count

6. **Timing**
   - Time of day (9:30-10:30 = prime time)
   - Day of week
   - Market conditions (VIX, SPY direction)

7. **Options activity** (if available)
   - Unusual call volume
   - IV changes
   - Put/call ratio

---

## PHASE 4: PATTERN ANALYSIS (FREE ML)

### Free Machine Learning Tools

**Scikit-learn (Python)**
- Free, open source
- Random Forest, XGBoost, SVM
- Perfect for tabular data

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

# Load your logged data
df = pd.read_sql("SELECT * FROM alerts WHERE outcome IS NOT NULL", db)

# Features
features = [
    'volume_ratio', 'float', 'market_cap',
    'reverse_split_12mo', 'dilution_score', 'insider_ownership',
    'short_interest', 'otc_status', 'distance_from_52w_high'
]

X = df[features]
y = (df['outcome'] == 'winner').astype(int)  # Binary: winner or not

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train Random Forest
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# See what features matter most
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance)

# Accuracy on test set
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.1%}")
```

**What This Tells You:**
- Which features actually predict winners
- What to focus on in trap detection
- What doesn't matter (save time, skip it)

### Expected Results (Research-Based)

From academic papers:
- **Random Forest on daily patterns**: 60-95% accuracy
- **Real trading (after execution costs)**: 40-60% of model accuracy
- **Key features** (from research): Volume ratio, float size, catalyst type, 52w high distance

**Your goal**: 
- Collect 100+ examples
- Train model
- See which features have highest importance
- Refine trap detection system based on what model finds

---

## PHASE 5: CONTINUOUS LEARNING LOOP

### The System Flow

```
1. SEC Scanner finds alert
   ↓
2. Log initial state to database
   ↓
3. Run trap detection (50 questions)
   ↓
4. If passes: Log "considered" flag
   ↓
5. Track price for next 5 days
   ↓
6. Label outcome (winner/trap/whipsaw)
   ↓
7. Every 100 examples: Retrain model
   ↓
8. Model tells you: "Volume ratio matters more than you thought"
   ↓
9. Adjust trap detection thresholds
   ↓
10. Repeat
```

### Automation Script

```python
# src/core/learning_loop.py

import schedule
import time
from pattern_logger import PatternLogger
from sec_speed_scanner import scan_once

logger = PatternLogger()

def check_for_new_alerts():
    """Run every minute during market hours"""
    alerts = scan_once(seen_ids={})
    
    for alert in alerts:
        # Log the alert
        alert_id = logger.log_alert(
            ticker=alert['ticker'],
            source='SEC_8K',
            catalyst=alert['matches'],
            trap_scores={}  # Get from trap detector
        )
        
        print(f"Logged alert {alert_id}: {alert['ticker']}")

def update_all_pending():
    """Run every 30 minutes to update outcomes"""
    
    # Get alerts from today that don't have outcomes yet
    pending = db.execute("""
        SELECT id, ticker FROM alerts
        WHERE date(timestamp) = date('now')
        AND price_eod IS NULL
    """).fetchall()
    
    for alert_id, ticker in pending:
        logger.update_outcomes(alert_id, ticker)
        print(f"Updated outcomes for {ticker}")

def retrain_model_weekly():
    """Run every Sunday to retrain model"""
    
    # Get all labeled data
    df = pd.read_sql("SELECT * FROM alerts WHERE outcome IS NOT NULL", db)
    
    if len(df) < 50:
        print("Not enough data yet (need 50+ examples)")
        return
    
    # Train model
    model = train_model(df)
    
    # Save feature importance
    save_feature_importance(model)
    
    print(f"Model retrained on {len(df)} examples")

# Schedule tasks
schedule.every(1).minutes.do(check_for_new_alerts)
schedule.every(30).minutes.do(update_all_pending)
schedule.every().sunday.at("18:00").do(retrain_model_weekly)

# Run forever
while True:
    schedule.run_pending()
    time.sleep(30)
```

---

## START HERE: MINIMAL VIABLE LOGGER

### Day 1 Setup (30 minutes)

```python
# quick_logger.py - Start collecting data TODAY

import yfinance as yf
import json
from datetime import datetime

alerts_file = "data/alerts_log.json"

def log_alert(ticker, catalyst):
    """
    Manual logging - run this every time you see an alert
    """
    
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="1m")
    
    if hist.empty:
        print("No data available")
        return
    
    price = hist['Close'].iloc[-1]
    volume = int(hist['Volume'].sum())
    
    alert = {
        'ticker': ticker,
        'timestamp': datetime.now().isoformat(),
        'catalyst': catalyst,
        'price_at_alert': price,
        'volume': volume,
        'logged_manually': True
    }
    
    # Append to file
    try:
        with open(alerts_file, 'r') as f:
            data = json.load(f)
    except:
        data = []
    
    data.append(alert)
    
    with open(alerts_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Logged {ticker} at ${price:.2f}")

# Usage:
# log_alert("ABCD", "Government contract - $45M")
```

**Start doing this NOW:**
- Every time you see a gap-up or SEC filing
- Log it manually
- Track what happens over next 5 days
- After 20-30 examples, you'll see patterns

---

## FREE RESOURCES

**Python Libraries (All Free):**
```bash
pip install yfinance          # Yahoo Finance data
pip install pandas            # Data manipulation
pip install scikit-learn      # Machine learning
pip install schedule          # Task scheduling
pip install requests          # API calls
```

**Data Sources (Free Tiers):**
- Yahoo Finance: Unlimited
- SEC EDGAR: Unlimited
- Finnhub: 60 calls/min
- Alpha Vantage: 25 calls/day
- Polygon.io: 5 calls/min

**Learning Resources (Free):**
- Scikit-learn documentation
- Kaggle competitions (learn from others)
- YouTube: "Sentdex" channel (Python finance tutorials)
- Academic papers (you already have research)

---

## TIMELINE TO WORKING SYSTEM

**Week 1: Manual Logging**
- Set up quick_logger.py
- Log 10-20 alerts manually
- Track outcomes in spreadsheet

**Week 2-4: Build Automated Logger**
- Integrate SEC scanner
- Auto-log alerts to SQLite
- Auto-update outcomes daily

**Month 2: Accumulate Data**
- Let system run
- Goal: 100+ labeled examples
- Don't touch the code, just let it collect

**Month 3: First ML Model**
- Train Random Forest on your data
- See feature importance
- Adjust trap detection based on findings

**Month 4+: Continuous Improvement**
- Retrain weekly
- Add new features
- Refine thresholds
- System gets smarter over time

---

## THE HONEST ANSWER

**You asked: "How do we begin this process for free?"**

**Answer:**
1. Start logging TODAY (manual is fine)
2. Use Yahoo Finance (free, unlimited)
3. Store in SQLite or JSON (built into Python)
4. After 50-100 examples, train Random Forest (free)
5. Model tells you what matters
6. Adjust your system
7. Repeat

**Cost: $0**

**Time to working ML system: 2-3 months** (because you need data first)

**The bottleneck isn't money or tools. It's DATA.**

Start collecting NOW. Every day you wait = one more day of missing training data.

---

## NEXT STEP

Run this command:

```bash
cd c:\Users\alexp\Desktop\brokkr
mkdir data
python -c "import json; json.dump([], open('data/alerts_log.json', 'w'))"
```

Then create `quick_logger.py` from above and start logging EVERY alert you see for the next 30 days.

That's the beginning.