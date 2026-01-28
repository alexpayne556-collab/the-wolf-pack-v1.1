# 🎯 PRE-POP SCANNER - INTEGRATED

## What It Does

Scores biotech stocks on **6 pre-explosion factors** to find setups BEFORE they pop:

### The 6 Factors

1. **📅 Catalyst Timing (2x weight)** - Binary event coming (FDA, data, etc.)
2. **📉 Float/Liquidity (1.5x weight)** - Low float = amplified moves
3. **❓ Uncertainty Discount (1.5x weight)** - Beaten down = upside potential
4. **📈 Technical Compression** - Coiled spring ready to break
5. **👔 Insider Buying (1.5x weight)** - Smart money accumulation
6. **🩳 Short Squeeze** - High short interest adds fuel

**Total Score: 0-100**
- 80+: 🔥 A+ (PRIME SETUP)
- 70+: 🎯 A (STRONG)
- 60+: ✅ B (GOOD)
- 50+: ⚡ C (WATCH)
- <50: ❌ D (PASS)

## Integration with Wolf Pack

✅ **Uses existing biotech_catalyst_scanner** (no duplication)  
✅ **Stores results in SQLite** for learning  
✅ **Integrated with master.py** command system  
✅ **Uses configured APIs** (yfinance, biotech scanner)

## How to Use

### From Master System
```bash
python master.py --prepop
```

### Standalone
```bash
# Scan all tickers
python prepop_scanner.py

# Check specific ticker
python prepop_scanner.py check PALI
```

## Current Results (Jan 21, 2026)

### Top Opportunities

**🎯 ACTIONABLE NOW (7-14 day window):**

**1. AQST @ $3.36 - Score: 54.1**
- 📅 CATALYST: 9/10 - PDUFA Jan 31 (9 days - SWEET SPOT!)
- 🩳 SQUEEZE: 8/10 - High short interest (22.7%)
- ❓ UNCERTAINTY: 7/10 - Heavily beaten down
- **Strategy**: Buy now, sell 1-2 days before PDUFA

**2. OCUL @ $11.42 - Score: 51.8**
- 📅 CATALYST: 10/10 - PDUFA Jan 28 (6 days - IMMINENT!)
- ⚠️ **Warning**: Too close - high risk
- **Strategy**: Watch only, too late to enter

**3. PALI @ $1.75 - Score: 51.2**
- 👔 INSIDER: 10/10 - 3 recent director buys
- ❓ UNCERTAINTY: 9/10 - Pre-revenue
- 📅 CATALYST: 1/10 - No known near-term catalyst
- **Strategy**: Longer-term hold for Phase 1b data (Q1)

## Why This Works

### The Pattern Before Biotech Explodes

Historically, stocks that pop 100%+ have:
1. **Binary catalyst coming** (creates urgency)
2. **Low float** (amplifies moves)
3. **Heavily beaten down** (max upside)
4. **Technical compression** (coiled spring)
5. **Smart money buying** (insider conviction)
6. **High shorts** (squeeze fuel)

### Timing is Everything

**PDUFA Runup Pattern:**
- 30-60 days before: Early (too soon)
- **7-14 days before: SWEET SPOT ✅**
- 1-6 days before: Risky (could run or dump)
- Day of: Binary gamble (approval = moon, rejection = crater)

**Scanner identifies the 7-14 day window automatically.**

## Database Storage

Results stored in `autonomous_memory.db`:

```sql
CREATE TABLE prepop_scans (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    ticker TEXT,
    price REAL,
    total_score REAL,
    catalyst_score REAL,
    float_score REAL,
    uncertainty_score REAL,
    compression_score REAL,
    insider_score REAL,
    squeeze_score REAL,
    catalyst_details TEXT,
    grade TEXT
)
```

This allows:
- Track which setups worked
- Learn patterns over time
- Backtest scoring accuracy

## Example Scan Output

```
🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
PRE-POP SCANNER - Scanning 24 tickers
🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺

🎯 TOP 10 PRE-POP CANDIDATES
================================================================================

RANK  TICKER   PRICE    SCORE    GRADE
--------------------------------------------------------------------------------
1     AQST     $3.36    54.1     ⚡ C (WATCH)
2     OCUL     $11.42   51.8     ⚡ C (WATCH)
3     PALI     $1.75    51.2     ⚡ C (WATCH)

DETAILED BREAKDOWN - TOP 3
================================================================================

📊 AQST - Score: 54.1/100 ⚡ C (WATCH)
   Price: $3.36
────────────────────────────────────────────────────────────

  📅 CATALYST: 9/10
     PDUFA: AQST-109
     SWEET SPOT (8-14 days)

  📉 FLOAT: 4/10 - LOW (>50M)
  ❓ UNCERTAINTY: 7/10 - ESTABLISHED + HEAVILY BEATEN
  📈 COMPRESSION: 2/10 - VOLATILE (>40%)
  👔 INSIDER: 1/10 - NO DATA
  🩳 SQUEEZE: 8/10 - HIGH (22.7%)

🎯 ACTIONABLE NOW (7-14 day window):
   AQST @ $3.36 - Score: 54.1
```

## Improvements from Original Code

### Before (Original)
- ❌ Hardcoded FDA calendar
- ❌ Manual insider buying data
- ❌ Standalone script
- ❌ No database storage
- ❌ No integration with other modules

### After (Integrated)
- ✅ Uses biotech_catalyst_scanner.py (live FDA data)
- ✅ Integrated with autonomous_brain.py
- ✅ Stores results in SQLite
- ✅ Works with master.py command system
- ✅ Uses existing APIs and config

## Next Steps

### Auto-Execution Integration
The scanner can feed opportunities to `autonomous_brain.py`:

```python
# In autonomous_brain.py
from prepop_scanner import PrePopScorer

scanner = PrePopScorer()
results = scanner.scan_universe(BIOTECH_UNIVERSE)

# Find high-scoring setups in 7-14 day window
buy_now = [r for r in results 
           if r['total_score'] >= 60 
           and 7 <= r['catalyst']['days_until'] <= 14]

for setup in buy_now:
    # Have Fenrir analyze
    analysis = self.think(f"Analyze this PDUFA setup: {json.dumps(setup)}")
    
    # Auto-execute if confidence high
    if confidence >= 0.75:
        self.execute_trade(...)
```

### Insider Buying Enhancement
Integrate with SEC Edgar scraper to get real-time Form 4 data:

```python
def _score_insider(self, ticker: str) -> Dict:
    # Use SEC Edgar API to fetch recent Form 4s
    recent_buys = self._fetch_sec_form4(ticker)
    # Score based on recency, volume, insider title
```

### Float/Volume Enhancement
Use Polygon API to get accurate float data:

```python
def _score_float(self, ticker: str) -> Dict:
    # Use Polygon /v3/reference/tickers/{ticker}
    polygon_data = self.polygon_api.get_ticker_details(ticker)
    float_shares = polygon_data['results']['share_class_shares_outstanding']
```

## Commands Cheat Sheet

```bash
# Full scan from master
python master.py --prepop

# Standalone full scan
python prepop_scanner.py

# Check specific ticker
python prepop_scanner.py check AQST

# Add to autonomous brain (future)
python master.py  # Will auto-scan and execute high-scoring setups
```

## The Wolf Pack Philosophy

**Hunt with patience:**
- ❌ Don't chase - wait for the 7-14 day window
- ✅ Enter with conviction when all factors align
- ✅ Let the setup come to you

**The scanner is your hunting scope** - it identifies prey before the pack moves.

---

Built with 🐺 by the Wolf Pack | Jan 21, 2026
