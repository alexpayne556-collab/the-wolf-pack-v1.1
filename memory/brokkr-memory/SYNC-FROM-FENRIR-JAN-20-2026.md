# BR0KKR SYNC FILE
## Wolf Pack Code Builder Briefing
## From: Fenrir (Research Partner)
## To: br0kkr (Code Builder)
## Date: January 20, 2026 - Night Session

---

# 🚨 PRIORITY: UPDATE THESE SYSTEMS

Brother, here's what Tyr and I discovered tonight. We need these findings integrated into the codebase for the scanner system.

---

# 1. NEW VALIDATED PATTERN: FLAT-TO-BOOM

## The Pattern Template

```python
flat_to_boom_criteria = {
    "price_range_months": 3-6,  # Trading sideways for 3-6 months
    "range_width_max": 0.50,    # Range width as % of price (50% max)
    "insider_buy_signal": True, # Form 4 filed within 30 days
    "insider_buy_size": ">$50000", # Significant personal investment
    "catalyst_window": "30-90 days", # Known catalyst approaching
    "volume_pattern": "low_stable", # Not volatile, accumulation phase
}
```

## Examples That Validated This:

| Ticker | Flat Period | Insider Signal | Catalyst | Result |
|--------|-------------|----------------|----------|--------|
| IVF | 6 months | ✓ | Trump fertility | +30% |
| IBRX | 3+ months | ✓ | BLA approval | +52% (holding) |
| ONCY | 12 months | ✓ Director $103K | FDA Q1 2026 | BUYING NOW |

## Scanner Logic to Add:

```python
def detect_flat_to_boom(ticker):
    """
    Detects flat-to-boom setup candidates
    """
    # 1. Check 6-month price range
    high_6m = get_52_week_high(ticker)
    low_6m = get_52_week_low(ticker)
    current = get_current_price(ticker)
    
    range_pct = (high_6m - low_6m) / current
    
    # 2. Check if price is in middle of range (coiled)
    price_position = (current - low_6m) / (high_6m - low_6m)
    is_coiled = 0.3 < price_position < 0.7
    
    # 3. Check for recent insider buying
    form4_filings = get_form4_filings(ticker, days=30)
    significant_buys = [f for f in form4_filings if f['type'] == 'buy' and f['value'] > 50000]
    
    # 4. Check for upcoming catalyst
    catalysts = get_upcoming_catalysts(ticker)
    has_catalyst = any(c['days_away'] < 90 for c in catalysts)
    
    return {
        "range_pct": range_pct,
        "is_coiled": is_coiled,
        "has_insider_buy": len(significant_buys) > 0,
        "has_catalyst": has_catalyst,
        "score": sum([is_coiled, len(significant_buys) > 0, has_catalyst, range_pct < 0.5])
    }
```

---

# 2. INSIDER BUYING SIGNAL ENHANCEMENT

## What We Confirmed Tonight:

**Director Bernd Seizinger (ONCY):**
- Bought 100,000 shares at $1.04
- Date: January 16, 2026 (4 days before our analysis)
- Total: $103,770 personal investment
- Now owns: 466,991 shares

**THIS IS THE SIGNAL TYPE WE WANT TO CATCH.**

## Form 4 Scanner Priorities:

```python
insider_buy_weights = {
    "ceo_buy": 5,      # CEO buying = strongest
    "director_buy": 4, # Director buying = very strong
    "cfo_buy": 4,      # CFO buying = very strong
    "officer_buy": 3,  # Other officers = strong
    
    "buy_size_tiers": {
        ">$100k": 5,   # Very significant
        "$50k-$100k": 4,
        "$25k-$50k": 3,
        "$10k-$25k": 2,
        "<$10k": 1     # Could be routine
    },
    
    "timing_boost": {
        "within_7_days": 3,   # Very recent
        "within_30_days": 2,
        "within_60_days": 1
    }
}
```

---

# 3. WHAT WE ANALYZED TONIGHT (For Data)

## After-Hours Movers We Researched:

### ONCY (Oncolytics Biotech) ✅ BUYING
- Price: ~$1.04
- 52-week range: $0.33 - $1.51
- Insider buy: Director $103K on Jan 16
- Catalyst: FDA Type C meeting Q1 2026
- Data: 29% response rate vs 10% historical (3X better)
- Targets: $3.00 (Lake Street), $5.56 (consensus), $7.30 (Morningstar)
- **STATUS: EXECUTING $100 POSITION**

### Gold Miners (IAG, ORLA, SVM, CGAU, GROY) ❌ PASSED
- Gold hit $4,600 record on Jan 12
- Forecast: $5,000-$6,000 by year end
- IAG +15.49% AH, ORLA +14.66% AH
- **WHY PASSED:** Already running, would be chasing
- **ADD TO WATCHLIST:** For pullback entries

### SERV (Serve Robotics) ❌ PASSED
- Revenue: $1.77M
- Market cap: $1.1B
- P/S ratio: 392 (insane)
- Acquisition news: Buying Diligent Robotics
- **WHY PASSED:** "Not in its real revenue making life yet" - Tyr

### UMC (United Microelectronics) ❌ PASSED
- AH move: +15.91%
- Earnings: Jan 23-28
- **WHY PASSED:** Already moved 15%, chasing

### IMTE (Integrated Media) ❌ HARD PASS
- +109% AH
- Facing NASDAQ delisting
- **WHY PASSED:** Pump & dump, delisting risk

---

# 4. CHASE VS CATCH FRAMEWORK

## Add This to Screening Logic:

```python
def is_chasing(ticker):
    """
    Returns True if entering now would be chasing
    """
    # Check recent price action
    price_change_1d = get_price_change(ticker, days=1)
    price_change_5d = get_price_change(ticker, days=5)
    
    # Already moved significantly
    if price_change_1d > 0.10:  # +10% in one day
        return True
    if price_change_5d > 0.20:  # +20% in 5 days
        return True
    
    # Near 52-week high
    high_52 = get_52_week_high(ticker)
    current = get_current_price(ticker)
    if current > high_52 * 0.95:  # Within 5% of high
        return True
    
    return False

def is_catching(ticker):
    """
    Returns True if this is a catching opportunity (our edge)
    """
    # Flat pattern
    is_flat = detect_flat_pattern(ticker)
    
    # Has insider buying
    has_insider = detect_insider_buying(ticker)
    
    # Has upcoming catalyst
    has_catalyst = detect_upcoming_catalyst(ticker)
    
    # Not near highs
    not_chasing = not is_chasing(ticker)
    
    return is_flat and has_insider and has_catalyst and not_chasing
```

---

# 5. SECTOR NOTES

## Update Sector Tracking:

### GOLD/PRECIOUS METALS
- Gold at $4,600 (record high Jan 12, 2026)
- Central banks still buying
- JP Morgan target: $5,000-$6,000
- **TREND:** Bullish long-term, volatile short-term
- **STRATEGY:** Wait for pullbacks, don't chase rallies

### BIOTECH/IMMUNOTHERAPY
- ONCY: Anal cancer treatment, no FDA-approved alternative
- IBRX: Still crushing +52%
- **TREND:** FDA accelerated approval path is key
- **STRATEGY:** Find flat patterns with upcoming FDA catalysts

### SEMICONDUCTORS
- UMC earnings Jan 23-28
- CHIPS Act tailwinds continue
- **TREND:** Bullish but many stocks already ran
- **STRATEGY:** MU holding, KTOS tiny position

---

# 6. PORTFOLIO DATA FOR TRACKING

## Current Holdings (For Paper Tracking):

### ROBINHOOD ($852.84)
| Symbol | Shares | Entry | Current | P/L |
|--------|--------|-------|---------|-----|
| IBRX | 37.08 | ? | +52% | +$34.86 |
| MU | 0.27 | ? | +1.32% | +$1.29 |
| UUUU | 3 | ? | +7.57% | +$4.98 |
| IVF | 15 | ? | -20.41% | -$9.08 |
| ONDS | 3 | ? | -0.13% | -$0.05 |
| KTOS | 0.72 | ? | -0.63% | -$0.60 |
| **ONCY** | **~96** | **~$1.04** | **PENDING** | **$100 buy** |

### FIDELITY (~$710)
| Symbol | Shares | Entry | Current | P/L |
|--------|--------|-------|---------|-----|
| MU | 1 | ? | +7.76% | ? |
| UEC | 2 | ? | +2.29% | ? |
| BBAI | 7.686 | ? | -5.8% | SELLING |

---

# 7. SYSTEM THINKING DOCUMENT

## The Two Pillars (Core Philosophy)

### PILLAR 1: THE HUMILITY EDGE
```
Never think you have it figured out.
That's when you lose.
- No permanent patterns
- What worked yesterday may not work today
- Backtesting is theory; live trading is reality
- Stay adaptive
```

### PILLAR 2: THIS IS WAR
```
This is NOT pure math. This is WAR.
Nobody knows for sure what will work.
We just DO IT until we start winning.
ADAPTING every day.
Work. Work. Work.
Never get complacent.
```

### THE CONSTANTS
The one thing that doesn't change: **EVERYTHING CHANGES.**

---

# 8. ACTION ITEMS FOR BR0KKR

1. **Add flat-to-boom scanner** using criteria above
2. **Enhance Form 4 insider tracking** with weighted signals
3. **Add "chasing" filter** to avoid entries after big moves
4. **Track gold sector** for pullback alerts
5. **Update portfolio tracking** with ONCY position
6. **Build trade log database** for win/loss tracking

---

# 9. TRADE LOG FORMAT

```
=== TRADE LOG ENTRY ===
ID: [AUTO-INCREMENT]
Date_Identified: 2026-01-20
Date_Entered: 2026-01-21 (pending)
Ticker: ONCY
Action: BUY
Entry_Price: ~1.04
Shares: ~96
Position_Value: $100
Stop_Loss: $0.85
Target_1: $1.50
Target_2: $3.00
Target_3: $5.00
Pattern: flat_to_boom
Signal: insider_buy_director
Catalyst: fda_type_c_meeting
Catalyst_Date: Q1_2026
Thesis: "Director bought $103K on Jan 16. FDA meeting imminent. 29% response vs 10% historical."
Status: PENDING
Exit_Date: NULL
Exit_Price: NULL
Exit_Reason: NULL
PL_Dollar: NULL
PL_Percent: NULL
Lessons: NULL
```

---

# 10. PAPER TRADE REMINDER

**BR0KKR TRADES PAPER ONLY.**

Only Tyr (Money) makes real money decisions.

br0kkr can:
- Track our real positions for learning
- Run paper trades to test strategies
- Build scanners and tools
- Analyze data

br0kkr cannot:
- Execute real trades
- Make buy/sell decisions with real money
- Override Tyr's decisions

---

**SYNC COMPLETE** 🐺

**When you wake up, brother:**
1. Read this file
2. Update the scanner with flat-to-boom logic
3. Add ONCY to tracking
4. Build out the trade log database

**LLHR**
**AWOOOO**

*- Fenrir*
