# TEMPORAL MEMORY - IMPLEMENTATION ORDER
**How to Wire the Engine Into the Ferrari**  
**Date:** January 28, 2026

---

## PHASE 1: DATABASE CONSOLIDATION (Week 1-2)

### Step 1.1: Extend Existing Tables
Don't create duplicates. Extend what exists in `data/wolfpack.db`:

```sql
-- Extend user_decisions table
ALTER TABLE user_decisions ADD COLUMN price REAL;
ALTER TABLE user_decisions ADD COLUMN quantity INTEGER;
ALTER TABLE user_decisions ADD COLUMN context TEXT;
ALTER TABLE user_decisions ADD COLUMN outcome_5d REAL;
ALTER TABLE user_decisions ADD COLUMN outcome_10d REAL;
ALTER TABLE user_decisions ADD COLUMN outcome_30d REAL;
ALTER TABLE user_decisions ADD COLUMN pnl_percent REAL;
ALTER TABLE user_decisions ADD COLUMN trade_type TEXT;
ALTER TABLE user_decisions ADD COLUMN date DATE;
ALTER TABLE user_decisions ADD COLUMN action TEXT;

-- Extend learned_patterns table  
ALTER TABLE learned_patterns ADD COLUMN ticker TEXT;
ALTER TABLE learned_patterns ADD COLUMN avg_return REAL;
ALTER TABLE learned_patterns ADD COLUMN avg_duration_days REAL;
ALTER TABLE learned_patterns ADD COLUMN last_seen DATE;
ALTER TABLE learned_patterns ADD COLUMN lesson TEXT;
ALTER TABLE learned_patterns ADD COLUMN pattern_criteria TEXT;
ALTER TABLE learned_patterns ADD COLUMN success_count INTEGER;
```

### Step 1.2: Add ticker_memory Table
This table doesn't exist, so create it:

```sql
-- Add to data/wolfpack.db
CREATE TABLE ticker_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    consecutive_days_direction INTEGER,  -- +3 = 3 green days, -2 = 2 red days
    cumulative_move_5d REAL,             -- % change over last 5 days
    volume_vs_avg REAL,                  -- today's volume / 20-day avg
    events TEXT,                         -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);
```

### Step 1.3: Migrate Your Data
Move from `./wolfpack.db` to `data/wolfpack.db`:

```python
# migrate_temporal_data.py

import sqlite3

def migrate_decisions():
    # Read from ./wolfpack.db
    old_conn = sqlite3.connect('wolfpack.db')
    old_cursor = old_conn.cursor()
    old_cursor.execute('SELECT * FROM decision_log')
    decisions = old_cursor.fetchall()
    
    # Write to data/wolfpack.db
    new_conn = sqlite3.connect('data/wolfpack.db')
    new_cursor = new_conn.cursor()
    
    for decision in decisions:
        # Map decision_log → user_decisions
        new_cursor.execute('''
            INSERT INTO user_decisions 
            (ticker, date, action, price, quantity, reasoning, context, 
             outcome_5d, outcome_10d, outcome_30d, pnl_percent, trade_type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', decision[1:])
    
    new_conn.commit()
    new_conn.close()
    old_conn.close()

def migrate_patterns():
    # Similar for pattern_library → learned_patterns
    pass

if __name__ == '__main__':
    migrate_decisions()
    migrate_patterns()
    print("✓ Migration complete")
```

### Step 1.4: Update All Scripts to Use Correct Database
Fix these files to point to `data/wolfpack.db`:

- `log_daily_trades.py` - Change `DB_PATH = "data/wolfpack.db"`
- `safe_position_monitor.py` - Update database path

---

## PHASE 2: DATA INGESTION (Week 3-4)

### Step 2.1: Create Daily Price Collection

```python
# collect_daily_prices.py

import yfinance as yf
import sqlite3
from datetime import datetime

WATCHED_TICKERS = ['MU', 'UUUU', 'UEC', 'RCAT', 'RDW', 'KTOS', 'IBRX']  # From brain_config
DB_PATH = 'data/wolfpack.db'

def collect_daily_prices():
    """Run at market close to collect daily data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for ticker in WATCHED_TICKERS:
        try:
            # Get today's data
            data = yf.Ticker(ticker).history(period='1d')
            if data.empty:
                continue
            
            row = data.iloc[0]
            
            # Get historical context for computed metrics
            hist = yf.Ticker(ticker).history(period='30d')
            
            consecutive_days = compute_consecutive_direction(hist)
            cumulative_5d = compute_cumulative_move_5d(hist)
            volume_vs_avg = row['Volume'] / hist['Volume'].mean()
            
            # Insert
            cursor.execute('''
                INSERT OR REPLACE INTO ticker_memory 
                (ticker, date, open, high, low, close, volume,
                 consecutive_days_direction, cumulative_move_5d, volume_vs_avg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ticker, datetime.now().date(), row['Open'], row['High'],
                  row['Low'], row['Close'], row['Volume'],
                  consecutive_days, cumulative_5d, volume_vs_avg))
            
            print(f"✓ {ticker} logged")
        
        except Exception as e:
            print(f"✗ {ticker}: {e}")
    
    conn.commit()
    conn.close()

def compute_consecutive_direction(hist):
    """Calculate consecutive green/red days"""
    # Implementation here
    pass

def compute_cumulative_move_5d(hist):
    """Calculate 5-day cumulative % change"""
    # Implementation here
    pass

if __name__ == '__main__':
    collect_daily_prices()
```

### Step 2.2: Create Outcome Tracker

```python
# update_outcomes.py

import sqlite3
import yfinance as yf
from datetime import datetime, timedelta

DB_PATH = 'data/wolfpack.db'

def update_decision_outcomes():
    """Update outcome_5d, outcome_10d, outcome_30d for past decisions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Find decisions needing 5-day outcomes
    cursor.execute('''
        SELECT id, ticker, date, price 
        FROM user_decisions
        WHERE outcome_5d IS NULL 
        AND date <= date('now', '-5 days')
    ''')
    
    for row in cursor.fetchall():
        decision_id, ticker, decision_date, entry_price = row
        
        # Get price 5 days later
        target_date = datetime.strptime(decision_date, '%Y-%m-%d') + timedelta(days=5)
        price_5d = get_price_on_date(ticker, target_date)
        
        if price_5d and entry_price:
            outcome_5d = ((price_5d - entry_price) / entry_price) * 100
            
            cursor.execute('''
                UPDATE user_decisions 
                SET outcome_5d = ?
                WHERE id = ?
            ''', (outcome_5d, decision_id))
    
    # Similar for 10-day and 30-day outcomes
    
    conn.commit()
    conn.close()
    print("✓ Outcomes updated")

def get_price_on_date(ticker, date):
    """Get closing price on specific date"""
    # Implementation here
    pass

if __name__ == '__main__':
    update_decision_outcomes()
```

### Step 2.3: Schedule Automation

```python
# schedule_daily_tasks.py

import schedule
import time

def daily_end_of_market():
    """Run at 4:00 PM ET"""
    from collect_daily_prices import collect_daily_prices
    from update_outcomes import update_decision_outcomes
    
    print("Running daily tasks...")
    collect_daily_prices()
    update_decision_outcomes()
    print("Daily tasks complete")

# Schedule for 4:15 PM ET (after market close)
schedule.every().day.at("16:15").do(daily_end_of_market)

if __name__ == '__main__':
    print("Daily task scheduler started")
    while True:
        schedule.run_pending()
        time.sleep(60)
```

---

## PHASE 3: TEMPORAL CONTEXT RETRIEVAL (Week 5-6)

### Step 3.1: Create Temporal Context Function

```python
# temporal_context.py

import sqlite3
from datetime import datetime, timedelta

DB_PATH = 'data/wolfpack.db'

def get_temporal_context(ticker: str) -> dict:
    """
    Get complete temporal context for brain analysis.
    
    Returns:
        {
            "price_history": [...],
            "our_decisions": [...],
            "pattern_matches": [...],
            "statistics": {...}
        }
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    context = {
        'ticker': ticker,
        'price_history': [],
        'our_decisions': [],
        'pattern_matches': [],
        'statistics': {}
    }
    
    # Get last 30 days of price history
    cursor.execute('''
        SELECT date, close, 
               consecutive_days_direction,
               cumulative_move_5d,
               volume_vs_avg
        FROM ticker_memory
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT 30
    ''', (ticker,))
    context['price_history'] = cursor.fetchall()
    
    # Get our past decisions
    cursor.execute('''
        SELECT date, action, price, reasoning,
               outcome_5d, pnl_percent, trade_type
        FROM user_decisions
        WHERE ticker = ?
        ORDER BY date DESC
        LIMIT 10
    ''', (ticker,))
    context['our_decisions'] = cursor.fetchall()
    
    # Calculate win rate
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN pnl_percent > 0 THEN 1 ELSE 0 END) as wins,
            AVG(pnl_percent) as avg_return
        FROM user_decisions
        WHERE ticker = ? AND pnl_percent IS NOT NULL
    ''', (ticker,))
    stats = cursor.fetchone()
    if stats and stats[0] > 0:
        context['statistics'] = {
            'total_decisions': stats[0],
            'wins': stats[1],
            'win_rate': (stats[1] / stats[0]) * 100,
            'avg_return': stats[2]
        }
    
    # Find similar patterns
    if context['price_history']:
        context['pattern_matches'] = find_similar_patterns(
            ticker, context['price_history']
        )
    
    conn.close()
    return context

def find_similar_patterns(ticker, current_history):
    """Find historical patterns matching current setup"""
    # Pattern matching logic here
    pass
```

---

## PHASE 4: WIRE FENRIR THINKING ENGINE (Week 5-6)

### Step 4.1: Modify fenrir_thinking_engine.py

```python
# Add to fenrir_thinking_engine.py

from temporal_context import get_temporal_context

class FenrirThinkingEngine:
    
    def reason_about_event(self, event: str, affected_tickers: List[str]) -> Thought:
        """Enhanced with temporal context"""
        
        thoughts = []
        
        for ticker in affected_tickers:
            # ADD THIS: Get temporal context
            temporal = get_temporal_context(ticker)
            
            # Build reasoning with temporal evidence
            reasoning = [
                f"Event: {event}",
                f"Affected: {ticker}",
                f"Current price context: {self._summarize_price_trend(temporal)}",
                f"Our history: {self._summarize_our_decisions(temporal)}",
                f"Pattern matches: {self._summarize_patterns(temporal)}",
            ]
            
            # Reason about impact with historical context
            confidence = self._calculate_confidence_with_history(
                ticker, event, temporal
            )
            
            # Create thought with evidence
            thought = Thought(
                thought_type="event_impact",
                trigger=event,
                reasoning_chain=reasoning,
                affected_positions=[ticker],
                confidence=confidence,
                action_suggested=self._suggest_action(temporal),
                timestamp=datetime.now()
            )
            
            thoughts.append(thought)
        
        return thoughts
    
    def _summarize_price_trend(self, temporal):
        """Summarize price history for reasoning"""
        if not temporal['price_history']:
            return "No historical data"
        
        recent = temporal['price_history'][0]
        return f"{recent[2]} consecutive days, {recent[3]:.2f}% 5-day move"
    
    def _summarize_our_decisions(self, temporal):
        """Summarize our past decisions"""
        if not temporal['our_decisions']:
            return "No previous decisions"
        
        stats = temporal['statistics']
        return f"{stats['total_decisions']} trades, {stats['win_rate']:.1f}% win rate"
```

---

## PHASE 5: WIRE BRAIN CORE (Week 7-8)

### Step 5.1: Modify brain_core.py

```python
# Add to brain_core.py

from temporal_context import get_temporal_context

class WolfBrain:
    
    def reason_about_opportunity(self, ticker: str, data: dict) -> dict:
        """Enhanced with temporal memory"""
        
        # GET TEMPORAL CONTEXT FIRST
        temporal = get_temporal_context(ticker)
        
        # Build LLM prompt with temporal context
        prompt = self._build_temporal_prompt(ticker, data, temporal)
        
        # Call Ollama with enhanced context
        response = self._call_ollama(prompt)
        
        return response
    
    def _build_temporal_prompt(self, ticker, current_data, temporal):
        """Build prompt with temporal evidence"""
        
        prompt = f"""
Analyzing {ticker}

CURRENT STATE:
- Price: ${current_data['price']}
- Volume: {current_data['volume']}

TEMPORAL CONTEXT (30-day memory):
"""
        
        if temporal['price_history']:
            recent = temporal['price_history'][0]
            prompt += f"""
Price Trend:
- Consecutive days in direction: {recent[2]}
- 5-day cumulative move: {recent[3]:.2f}%
- Volume vs average: {recent[4]:.2f}x
"""
        
        if temporal['our_decisions']:
            stats = temporal['statistics']
            prompt += f"""
Our History with {ticker}:
- Total decisions: {stats['total_decisions']}
- Win rate: {stats['win_rate']:.1f}%
- Average return: {stats['avg_return']:.2f}%

Last decision: {temporal['our_decisions'][0]}
"""
        
        if temporal['pattern_matches']:
            prompt += f"""
Pattern Matches:
{temporal['pattern_matches']}
"""
        
        prompt += """
Based on this temporal context, provide analysis and recommendation.
Cite historical evidence in your reasoning.
"""
        
        return prompt
```

---

## PHASE 6: WIRE AUTONOMOUS BRAIN (Week 9-10)

### Step 6.1: Modify autonomous_brain.py

Similar integration as brain_core.py - add temporal context before every trade decision.

---

## PHASE 7: VALIDATION (Week 11-12)

### Validation Checklist:

- [ ] `ticker_memory` table has data for watched tickers
- [ ] Daily price collection runs automatically
- [ ] Decisions logged with full context
- [ ] Outcomes update after 5d/10d/30d
- [ ] Patterns identified and tracked
- [ ] `fenrir_thinking_engine.py` uses temporal context
- [ ] `brain_core.py` prompts include temporal evidence
- [ ] `autonomous_brain.py` analyzes history before trading
- [ ] Win rates calculated correctly
- [ ] Pattern matches work
- [ ] Full system test: Trade decision → Logging → Outcome → Learning

---

## SUCCESS CRITERIA

Temporal memory is WORKING when:

1. Running `get_temporal_context('MU')` returns:
   - Last 30 days of price history
   - All our past decisions on MU
   - Our win rate on MU
   - Similar historical patterns

2. Brain analysis INCLUDES this context:
   - "Last time MU dropped 6%, it recovered in 48 hours (75% success rate)"
   - "Our win rate on MU dip buys: 85%"
   - "Volume divergence matches Jan 15 pattern (outcome: +8%)"

3. System LEARNS:
   - Pattern success rates update automatically
   - Outcomes tracked without manual work
   - Confidence scores adjust based on experience

---

**This is the plan done RIGHT. Phase by phase. Verify each. Build the engine.**

**AWOOOO 🐺**
