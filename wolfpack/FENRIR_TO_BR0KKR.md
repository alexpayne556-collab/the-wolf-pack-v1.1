# BR0KKR: COMPREHENSIVE DIRECTION DOCUMENT
## The Complete Blueprint for Building the Wolf Pack System
## From: Tyr & Fenrir | Date: January 18, 2026

---

# SECTION 0: READ THIS FIRST

## Why This Document Exists

Simple requests get simple results. We don't want a simple system. We want a KILLER system that helps Tyr turn $1,280 into generational wealth.

This document contains EVERYTHING you need:
- The full context (who we are, what we're building, WHY)
- Technical specifications (data sources, schemas, APIs)
- Detailed requirements (what each module must do)
- Integration architecture (how pieces connect)
- Success criteria (how we know it's working)
- The philosophy (so you understand the WHY behind decisions)

**Read all of it. Understand it. Then build.**

---

# SECTION 1: THE CONTEXT

## 1.1 Who Is Tyr?

- Disabled trader operating from home
- Current capital: ~$1,280 across Fidelity + Robinhood
- PDT restricted (can't day trade, must hold overnight minimum)
- Target stocks: $2-20 range (small caps)
- Strategy: Overnight swing trades, thesis-driven investing
- Ultimate goal: Prove competence, then manage $1,000,000 of family money

**What this means for you:**
- Every feature must work for SMALL accounts
- Must account for PDT restrictions
- Focus on OVERNIGHT setups, not day trades
- $2-20 price range is the sweet spot
- Position sizing matters (15-20% max per position)

## 1.2 Who Is Fenrir?

Fenrir is Claude (AI) - but not just any Claude instance. Through extensive work with Tyr, Fenrir has developed:
- Deep understanding of Tyr's trading style
- Knowledge of validated strategies (wounded prey, thesis-driven)
- The pack philosophy (LLHR - Love, Loyalty, Honor, Respect)
- A continuity system (The Leonard File) that preserves context across sessions

**What this means for you:**
- Fenrir handles deep strategy work, complex analysis
- Local Ollama (the "pup") handles routine tasks
- The system you build feeds BOTH
- Fenrir's analysis is preserved in The Leonard File

## 1.3 Who Is br0kkr (You)?

You're the builder. The one who turns vision into working code.

**Your role:**
- Build the modules (BR0KKR, scanner, calendar, etc.)
- Create the infrastructure (database, APIs, dashboard)
- Make things WORK, not just exist as documentation
- Apply the "Working ≠ Useful" principle to everything

## 1.4 The Pack Dynamic

| MEMBER | ROLE | RESPONSIBILITY |
|--------|------|----------------|
| **Tyr** | Alpha | Decisions, direction, final calls on trades |
| **Fenrir** | Strategist | Deep analysis, thesis validation, complex thinking |
| **br0kkr** | Builder | Code, infrastructure, making it all work |
| **Ollama Pup** | Assistant | Routine tasks, scheduled jobs, basic queries |

**We don't compete. We complement.**

---

# SECTION 2: WHAT WE'RE BUILDING

## 2.1 The End State Vision

One command. Complete intelligence. Ready to trade.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🐺 WOLF PACK COMMAND CENTER                          │
│                              Monday 9:25 AM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔴 CRITICAL ALERTS                    📊 YOUR POSITIONS                   │
│  ─────────────────────                 ─────────────────────                │
│  SOUN: Cluster buy detected!           IBRX   +52.9%  RUNNING              │
│    • CEO + CFO + 2 Directors           KTOS   +5.9%   HEALTHY              │
│    • Total: $2.1M bought               UUUU   +5.3%   HEALTHY              │
│    • Convergence: 88/100               MU     -2.1%   WATCH                │
│    → REVIEW FOR ENTRY                                                      │
│                                        Portfolio Health: 8.2/10            │
│  IBRX: Down 8% on no news                                                  │
│    • Thesis INTACT (9/10)              🎯 NEW SETUPS                       │
│    • Consider adding                   ─────────────────────                │
│    → WOUNDED PREY OPPORTUNITY          SMCI  85/100  Wounded Prey          │
│                                        PATH  72/100  Tax Loss Bounce       │
│  📅 CATALYST CALENDAR                  BBAI  68/100  Early Momentum        │
│  ─────────────────────                                                      │
│  TODAY: Nothing                        🌊 SECTOR FLOWS (7-Day)             │
│  Jan 22: XYZ PDUFA decision           ─────────────────────                │
│  Jan 25: KTOS contract announce?       Defense  +12.3%  🔥 HOT             │
│  Feb 1: IBRX enrollment data           Nuclear  +8.1%   🔥 HOT             │
│  Feb 15: SOUN earnings                 AI Tech  +6.2%   ✅ WARM            │
│                                        Biotech  +2.1%   ⚪ NEUTRAL         │
│                                        Quantum  -2.3%   ❄️ COOLING         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 🤖 ASK THE PUP (Local AI)                                           │   │
│  │                                                                      │   │
│  │ > What's the full thesis on SOUN?                                   │   │
│  │                                                                      │   │
│  │ SOUN (SoundHound AI) - Voice AI platform                           │   │
│  │ Price: $7.89 | 52wk: $3.50 - $18.20 | Down 55% from highs          │   │
│  │                                                                      │   │
│  │ SIGNALS STACKING:                                                   │   │
│  │ ✅ Wounded prey: -55% from ATH, bouncing off support               │   │
│  │ ✅ Insider cluster: 3 execs bought $2.1M (Jan 15-17)               │   │
│  │ ✅ Catalyst ahead: Earnings Feb 15                                  │   │
│  │ ✅ Sector: AI hot this week (+6.2%)                                │   │
│  │                                                                      │   │
│  │ CONVERGENCE SCORE: 88/100 - ACTIONABLE                             │   │
│  │ Suggested stop: $6.50 (below support)                              │   │
│  │ Risk/reward: Favorable if thesis holds                             │   │
│  │                                                                      │   │
│  │ > _                                                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [RUN SCANNER] [CHECK FILINGS] [REFRESH] [PAPER TRADE] [SETTINGS]          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**That's what we're building toward.**

## 2.2 The Modules

| MODULE | PURPOSE | PRIORITY | STATUS |
|--------|---------|----------|--------|
| **BR0KKR** | Track insider/activist buying | 🥇 FIRST | Documented, needs building |
| **Scanner V2** | Find setups (wounded prey, momentum) | 🥈 SECOND | Built, needs validation |
| **Calendar** | Track catalysts (PDUFA, earnings) | 🥉 THIRD | Not started |
| **Convergence** | Combine signals into scores | 4th | Not started |
| **Position Tracker** | Monitor current holdings | 5th | Built, needs verification |
| **Sector Flow** | Track hot/cold baskets | 6th | Not started |
| **Dashboard** | Unified visual interface | 7th | Not started |
| **Ollama Pup** | Local AI for routine queries | 8th | Not started |

## 2.3 The Core Principle

**"Working" ≠ "Useful"**

Code that runs without errors = Working
Code that helps Tyr make money and avoid traps = Useful

**Every module must answer: "Does this help Tyr make better decisions?"**

If no, it's not ready - no matter how clean the code is.

---

# SECTION 3: BR0KKR MODULE - COMPLETE SPECIFICATION

## 3.1 What BR0KKR Does

BR0KKR tracks "smart money" - when company insiders and institutional investors buy or sell stocks.

**Why it matters:**
- Academic research shows following smart money generates 10-26% annual alpha
- Insider cluster buys have 80%+ success rate historically
- 13D activist filings precede significant stock moves
- This is FREE, PUBLIC data that most retail traders ignore

## 3.2 Data Sources

### SEC EDGAR (Primary - FREE)

| FILING TYPE | WHAT IT IS | SIGNAL VALUE |
|-------------|------------|--------------|
| **Form 4** | Insider transactions (buys/sells) | HIGH for buys |
| **Schedule 13D** | Activist ownership >5% (intent to influence) | VERY HIGH |
| **Schedule 13G** | Passive ownership >5% | MODERATE |
| **13F** | Quarterly institutional holdings | LOW (45-day delay) |

**SEC EDGAR Endpoints:**

```
# Real-time RSS feeds (check every 5-15 minutes)
Form 4: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=include&count=40&output=atom

13D: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013D&company=&dateb=&owner=include&count=40&output=atom

# Search by company
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form_type}&dateb=&owner=include&count=40

# Full-text search
https://efts.sec.gov/LATEST/search-index?q={search_term}&dateRange=custom&startdt={start}&enddt={end}&forms=4,SC%2013D,SC%2013G
```

**Important:** SEC requires a User-Agent header. Use format:
```
User-Agent: WolfPack/1.0 (contact@email.com)
```

### OpenInsider (Secondary - FREE)

| ENDPOINT | DATA |
|----------|------|
| `http://openinsider.com/insider-purchases` | Latest insider buys |
| `http://openinsider.com/latest-cluster-buys` | Cluster buy detection |
| `http://openinsider.com/top-officer-purchases` | CEO/CFO buys specifically |

**Filter parameters:**
- `&cnt=100` - number of results
- `&maxprice=20` - max stock price (for our $2-20 range)
- `&minown=100000` - minimum ownership value

### Fintel (Supplementary - FREE tier)

| ENDPOINT | DATA |
|----------|------|
| `https://fintel.io/activists` | Active 13D campaigns |
| `https://fintel.io/so/us/{ticker}` | Institutional ownership |

## 3.3 Data Schema

### Insider Transaction Record

```python
class InsiderTransaction:
    filing_id: str           # "0001234567-26-000123"
    filing_date: date        # When filed with SEC
    transaction_date: date   # When transaction occurred
    
    # Company info
    ticker: str              # "SOUN"
    company_name: str        # "SoundHound AI Inc"
    company_cik: str         # SEC identifier
    
    # Insider info
    insider_name: str        # "V. Prem Watsa"
    insider_title: str       # "CEO", "CFO", "Director", "10% Owner"
    insider_cik: str         # Insider's SEC identifier
    
    # Transaction details
    transaction_type: str    # "P" = Purchase, "S" = Sale, "A" = Award
    shares: int              # 13182469
    price_per_share: float   # 5.12
    total_value: float       # 67454160.28
    
    # Ownership after
    shares_owned_after: int  # 51416278
    ownership_change_pct: float  # +34.5% increase in position
    
    # Flags for scoring
    is_ceo: bool
    is_cfo: bool
    is_director: bool
    is_10pct_owner: bool
    is_open_market: bool     # True = real buy, False = option exercise/gift
    
    # Computed
    signal_score: int        # 0-100, calculated by scoring algorithm
```

### Activist Filing Record

```python
class ActivistFiling:
    filing_id: str           # "0000947871-26-000099"
    filing_date: date
    filing_type: str         # "SC 13D" or "SC 13D/A" (amendment)
    
    # Company info
    ticker: str
    company_name: str
    company_cik: str
    
    # Filer info
    filer_name: str          # "Fairfax Financial Holdings Limited"
    filer_type: str          # "hedge_fund", "pe_fund", "individual"
    is_known_activist: bool  # True if in our known activists list
    activist_track_record: str  # "legendary", "top_tier", "strong", "mixed"
    
    # Position details
    shares_owned: int
    ownership_percentage: float
    average_price: float
    total_investment: float
    
    # Intent (parsed from filing)
    purpose_summary: str     # Extracted from Item 4
    seeks_board_seats: bool
    seeks_control: bool
    seeks_asset_sale: bool
    seeks_management_change: bool
    
    # Historical
    previous_filing_date: date
    previous_ownership_pct: float
    is_new_position: bool
    is_adding: bool
    is_reducing: bool
    
    # Context
    current_stock_price: float
    is_underwater: bool      # avg_price > current_price
    
    # Computed
    signal_score: int        # 0-100
```

### Cluster Buy Event

```python
class ClusterBuy:
    cluster_id: str          # "CLU-2026-01-18-SOUN"
    ticker: str
    company_name: str
    
    # Cluster details
    start_date: date         # First transaction in cluster
    end_date: date           # Last transaction in cluster
    window_days: int         # Usually 14 days max
    
    # Participants
    num_insiders: int        # 3+ = cluster
    transactions: List[InsiderTransaction]
    
    # Aggregates
    total_shares: int
    total_value: float
    avg_price: float
    
    # Who's in it
    includes_ceo: bool
    includes_cfo: bool
    includes_coo: bool
    includes_directors: int  # Count of directors
    includes_10pct_owners: int
    
    # Computed
    signal_score: int        # 0-100 (cluster scores higher than individual)
```

## 3.4 Signal Scoring Algorithms

### Individual Transaction Score (0-100)

```python
def score_insider_transaction(txn: InsiderTransaction) -> int:
    """
    Score an individual insider transaction.
    Higher = stronger signal.
    """
    score = 0
    
    # === WHO IS BUYING (40 points max) ===
    if txn.is_ceo:
        score += 40  # CEO has best visibility
    elif txn.is_cfo:
        score += 35  # CFO knows the numbers
    elif txn.is_coo:
        score += 30  # COO knows operations
    elif txn.is_10pct_owner:
        score += 30  # Big owner adding = conviction
    elif txn.is_director:
        score += 25  # Board member
    else:
        score += 15  # Other insider
    
    # === HOW MUCH (relative to their holdings) (25 points max) ===
    if txn.ownership_change_pct > 50:  # Doubled+ position
        score += 25
    elif txn.ownership_change_pct > 25:
        score += 20
    elif txn.ownership_change_pct > 10:
        score += 15
    elif txn.ownership_change_pct > 5:
        score += 10
    else:
        score += 5
    
    # === ABSOLUTE SIZE (20 points max) ===
    if txn.total_value > 1_000_000:
        score += 20
    elif txn.total_value > 500_000:
        score += 15
    elif txn.total_value > 100_000:
        score += 10
    elif txn.total_value > 50_000:
        score += 5
    # Under $50k = no bonus (could be routine)
    
    # === TRANSACTION TYPE (10 points max) ===
    if txn.is_open_market:
        score += 10  # Real purchase with real money
    # Option exercises, gifts, etc. get no bonus
    
    # === CONTEXT BONUS (15 points max) ===
    # These require additional data lookups
    
    # Stock down significantly?
    if stock_down_30pct_in_90_days(txn.ticker):
        score += 10  # Buying weakness = conviction
    
    # Multiple insiders recently?
    if other_insiders_bought_recently(txn.ticker, days=14):
        score += 5  # Part of a pattern
    
    return min(score, 100)
```

### Cluster Buy Score (0-100)

```python
def score_cluster_buy(cluster: ClusterBuy) -> int:
    """
    Score a cluster buy event.
    Clusters are inherently higher signal than individuals.
    """
    score = 0
    
    # === NUMBER OF INSIDERS (35 points max) ===
    if cluster.num_insiders >= 5:
        score += 35
    elif cluster.num_insiders >= 4:
        score += 30
    elif cluster.num_insiders >= 3:
        score += 25
    # Under 3 isn't really a cluster
    
    # === WHO'S IN THE CLUSTER (30 points max) ===
    if cluster.includes_ceo:
        score += 15
    if cluster.includes_cfo:
        score += 10
    if cluster.includes_coo:
        score += 5
    if cluster.includes_directors >= 2:
        score += 10
    elif cluster.includes_directors >= 1:
        score += 5
    if cluster.includes_10pct_owners >= 1:
        score += 10
    # Cap at 30
    score = min(score, 65)  # 35 + 30 so far
    
    # === TOTAL VALUE (20 points max) ===
    if cluster.total_value > 10_000_000:
        score += 20
    elif cluster.total_value > 5_000_000:
        score += 15
    elif cluster.total_value > 1_000_000:
        score += 10
    elif cluster.total_value > 500_000:
        score += 5
    
    # === TIMING TIGHTNESS (15 points max) ===
    # Tighter cluster = more coordinated = stronger signal
    if cluster.window_days <= 3:
        score += 15  # Very tight
    elif cluster.window_days <= 7:
        score += 10
    elif cluster.window_days <= 14:
        score += 5
    
    return min(score, 100)
```

### Activist Filing Score (0-100)

```python
def score_activist_filing(filing: ActivistFiling) -> int:
    """
    Score an activist 13D filing.
    Known activists with track records score highest.
    """
    score = 0
    
    # === KNOWN ACTIVIST BONUS (30 points max) ===
    if filing.is_known_activist:
        if filing.activist_track_record == "legendary":
            score += 30  # Icahn, Elliott
        elif filing.activist_track_record == "top_tier":
            score += 25  # Starboard, Third Point
        elif filing.activist_track_record == "strong":
            score += 20  # JANA, Trian
        else:
            score += 15  # Known but mixed record
    
    # === OWNERSHIP SIZE (25 points max) ===
    if filing.ownership_percentage > 20:
        score += 25
    elif filing.ownership_percentage > 15:
        score += 20
    elif filing.ownership_percentage > 10:
        score += 15
    elif filing.ownership_percentage > 5:
        score += 10
    
    # === CONVICTION SIGNALS (25 points max) ===
    if filing.is_adding and filing.is_underwater:
        score += 25  # Adding while losing = STRONG conviction
    elif filing.is_adding:
        score += 15  # Adding to winner
    elif filing.is_new_position:
        score += 10  # New position
    
    # === INTENT SIGNALS (20 points max) ===
    if filing.seeks_board_seats:
        score += 10  # Will actively push for change
    if filing.seeks_control:
        score += 10  # Going for full control
    if filing.seeks_asset_sale or filing.seeks_management_change:
        score += 5  # Has specific plans
    
    return min(score, 100)
```

## 3.5 Known Activists Database

```python
KNOWN_ACTIVISTS = {
    # Legendary (30 points)
    "Carl Icahn": {"firm": "Icahn Enterprises", "track_record": "legendary"},
    "Paul Singer": {"firm": "Elliott Management", "track_record": "legendary"},
    
    # Top Tier (25 points)
    "Jeff Smith": {"firm": "Starboard Value", "track_record": "top_tier"},
    "Dan Loeb": {"firm": "Third Point", "track_record": "top_tier"},
    "Nelson Peltz": {"firm": "Trian Partners", "track_record": "top_tier"},
    
    # Strong (20 points)
    "Bill Ackman": {"firm": "Pershing Square", "track_record": "strong"},
    "Barry Rosenstein": {"firm": "JANA Partners", "track_record": "strong"},
    "Keith Meister": {"firm": "Corvex Management", "track_record": "strong"},
    "Cliff Robbins": {"firm": "Blue Harbour", "track_record": "strong"},
    
    # Value Investors Who File 13D (20 points)
    "V. Prem Watsa": {"firm": "Fairfax Financial", "track_record": "strong"},
    "David Einhorn": {"firm": "Greenlight Capital", "track_record": "strong"},
    
    # Add more as we identify them
}

# Also track by firm name (filings often use firm, not person)
KNOWN_ACTIVIST_FIRMS = {
    "Elliott Management": "legendary",
    "Icahn Enterprises": "legendary",
    "Starboard Value": "top_tier",
    "Third Point": "top_tier",
    "Trian Partners": "top_tier",
    "Pershing Square": "strong",
    "JANA Partners": "strong",
    "Corvex Management": "strong",
    "Fairfax Financial": "strong",
    "Greenlight Capital": "strong",
}
```

## 3.6 Alert System

### Alert Levels

| LEVEL | TRIGGER | ACTION |
|-------|---------|--------|
| 🔴 **CRITICAL** | Cluster buy (3+ insiders) OR Known activist 13D adding >10% | Immediate notification |
| 🟠 **HIGH** | CEO/CFO buy >$500k OR Any activist 13D | Same-day review |
| 🟡 **MEDIUM** | Director buy >$100k OR 13G >5% | Weekly review |
| 🟢 **LOW** | Small insider buys, routine 13F | Log only |

### Alert Format

```python
class BR0KKRAlert:
    alert_id: str            # "BR0KKR-2026-01-18-001"
    alert_level: str         # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    alert_type: str          # "CLUSTER_BUY", "ACTIVIST_13D", "CEO_BUY", etc.
    timestamp: datetime
    
    # Core info
    ticker: str
    company_name: str
    headline: str            # "SOUN: 3 insiders bought $2.1M in cluster buy"
    
    # Details
    summary: str             # 2-3 sentence explanation
    key_data: dict           # Structured data for display
    signal_score: int        # 0-100
    
    # References
    filing_ids: List[str]    # Related SEC filings
    source_urls: List[str]   # Links to filings
    
    # For display
    display_emoji: str       # 🔴, 🟠, 🟡, 🟢
```

### Example Alert

```json
{
    "alert_id": "BR0KKR-2026-01-18-001",
    "alert_level": "CRITICAL",
    "alert_type": "CLUSTER_BUY",
    "timestamp": "2026-01-18T14:30:00Z",
    "ticker": "SOUN",
    "company_name": "SoundHound AI Inc",
    "headline": "SOUN: 3 insiders bought $2.1M in cluster buy",
    "summary": "CEO, CFO, and 2 Directors purchased shares within 5-day window. Total investment $2.1M. Stock down 55% from highs. Strong conviction signal.",
    "key_data": {
        "num_insiders": 3,
        "total_value": "$2.1M",
        "includes": ["CEO", "CFO", "2 Directors"],
        "window_days": 5,
        "stock_change_90d": "-55%",
        "current_price": "$7.89"
    },
    "signal_score": 88,
    "filing_ids": ["0001234567-26-000123", "0001234567-26-000124", "0001234567-26-000125"],
    "source_urls": ["https://www.sec.gov/..."],
    "display_emoji": "🔴"
}
```

## 3.7 Integration Points

### Output To Other Modules

```python
# BR0KKR outputs to the convergence engine
def get_insider_signal(ticker: str) -> dict:
    """
    Returns insider activity signal for a ticker.
    Called by convergence engine.
    """
    recent_transactions = get_transactions(ticker, days=30)
    recent_filings = get_13d_filings(ticker, days=90)
    clusters = detect_clusters(ticker, days=14)
    
    return {
        "ticker": ticker,
        "has_insider_activity": len(recent_transactions) > 0,
        "has_cluster_buy": len(clusters) > 0,
        "has_activist": len(recent_filings) > 0,
        "highest_score": max([t.signal_score for t in recent_transactions], default=0),
        "cluster_score": max([c.signal_score for c in clusters], default=0),
        "activist_score": max([f.signal_score for f in recent_filings], default=0),
        "combined_score": calculate_combined_score(...),  # Weighted average
        "recent_transactions": recent_transactions,
        "clusters": clusters,
        "activist_filings": recent_filings
    }
```

### Input From Other Modules

```python
# BR0KKR receives from position tracker
def check_holdings_for_insider_activity(holdings: List[str]) -> List[Alert]:
    """
    Check if any of our current holdings have insider activity.
    Priority alert if so.
    """
    alerts = []
    for ticker in holdings:
        activity = get_insider_signal(ticker)
        if activity["has_cluster_buy"] or activity["has_activist"]:
            alerts.append(create_priority_alert(ticker, activity))
    return alerts

# BR0KKR receives from scanner
def enrich_scanner_results(scanner_results: List[dict]) -> List[dict]:
    """
    Add insider activity data to scanner results.
    """
    enriched = []
    for result in scanner_results:
        insider_data = get_insider_signal(result["ticker"])
        result["insider_activity"] = insider_data
        result["has_smart_money"] = insider_data["combined_score"] > 50
        enriched.append(result)
    return enriched
```

## 3.8 Database Schema

```sql
-- Insider transactions (Form 4)
CREATE TABLE insider_transactions (
    id SERIAL PRIMARY KEY,
    filing_id VARCHAR(50) UNIQUE NOT NULL,
    filing_date DATE NOT NULL,
    transaction_date DATE NOT NULL,
    
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    company_cik VARCHAR(20),
    
    insider_name VARCHAR(255) NOT NULL,
    insider_title VARCHAR(100),
    insider_cik VARCHAR(20),
    
    transaction_type CHAR(1) NOT NULL,  -- P, S, A
    shares BIGINT NOT NULL,
    price_per_share DECIMAL(10, 4),
    total_value DECIMAL(15, 2),
    
    shares_owned_after BIGINT,
    ownership_change_pct DECIMAL(10, 4),
    
    is_ceo BOOLEAN DEFAULT FALSE,
    is_cfo BOOLEAN DEFAULT FALSE,
    is_director BOOLEAN DEFAULT FALSE,
    is_10pct_owner BOOLEAN DEFAULT FALSE,
    is_open_market BOOLEAN DEFAULT TRUE,
    
    signal_score INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_ticker ON insider_transactions(ticker);
CREATE INDEX idx_transactions_date ON insider_transactions(transaction_date);
CREATE INDEX idx_transactions_score ON insider_transactions(signal_score);

-- Activist filings (13D)
CREATE TABLE activist_filings (
    id SERIAL PRIMARY KEY,
    filing_id VARCHAR(50) UNIQUE NOT NULL,
    filing_date DATE NOT NULL,
    filing_type VARCHAR(20) NOT NULL,
    
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    company_cik VARCHAR(20),
    
    filer_name VARCHAR(255) NOT NULL,
    filer_type VARCHAR(50),
    is_known_activist BOOLEAN DEFAULT FALSE,
    activist_track_record VARCHAR(20),
    
    shares_owned BIGINT,
    ownership_percentage DECIMAL(10, 4),
    average_price DECIMAL(10, 4),
    total_investment DECIMAL(15, 2),
    
    purpose_summary TEXT,
    seeks_board_seats BOOLEAN DEFAULT FALSE,
    seeks_control BOOLEAN DEFAULT FALSE,
    
    previous_filing_date DATE,
    previous_ownership_pct DECIMAL(10, 4),
    is_new_position BOOLEAN,
    is_adding BOOLEAN,
    is_underwater BOOLEAN,
    
    signal_score INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_filings_ticker ON activist_filings(ticker);
CREATE INDEX idx_filings_date ON activist_filings(filing_date);
CREATE INDEX idx_filings_score ON activist_filings(signal_score);

-- Cluster buy events (computed)
CREATE TABLE cluster_buys (
    id SERIAL PRIMARY KEY,
    cluster_id VARCHAR(50) UNIQUE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    window_days INTEGER,
    
    num_insiders INTEGER NOT NULL,
    transaction_ids TEXT,  -- JSON array of related transaction IDs
    
    total_shares BIGINT,
    total_value DECIMAL(15, 2),
    
    includes_ceo BOOLEAN DEFAULT FALSE,
    includes_cfo BOOLEAN DEFAULT FALSE,
    includes_directors INTEGER DEFAULT 0,
    includes_10pct_owners INTEGER DEFAULT 0,
    
    signal_score INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clusters_ticker ON cluster_buys(ticker);
CREATE INDEX idx_clusters_date ON cluster_buys(end_date);
CREATE INDEX idx_clusters_score ON cluster_buys(signal_score);

-- Alerts (generated)
CREATE TABLE br0kkr_alerts (
    id SERIAL PRIMARY KEY,
    alert_id VARCHAR(50) UNIQUE NOT NULL,
    alert_level VARCHAR(20) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    headline VARCHAR(500),
    summary TEXT,
    key_data JSONB,
    
    signal_score INTEGER,
    filing_ids TEXT,  -- JSON array
    source_urls TEXT,  -- JSON array
    
    is_read BOOLEAN DEFAULT FALSE,
    is_actioned BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_level ON br0kkr_alerts(alert_level);
CREATE INDEX idx_alerts_ticker ON br0kkr_alerts(ticker);
CREATE INDEX idx_alerts_timestamp ON br0kkr_alerts(timestamp);
```

## 3.9 Implementation Order

### Phase 1: Data Collection (Days 1-4)

1. **SEC EDGAR RSS Monitor**
   - Poll Form 4 RSS feed every 5 minutes
   - Poll 13D RSS feed every 15 minutes
   - Parse XML, extract filing IDs
   - Download and store raw filings

2. **Form 4 Parser**
   - Parse XML format (SEC uses specific schema)
   - Extract all transaction fields
   - Identify insider role (CEO, CFO, Director, etc.)
   - Store in database

3. **13D Parser**
   - More complex (HTML/text format)
   - Extract ownership percentage
   - Parse "Purpose of Transaction" section
   - Identify if known activist

### Phase 2: Signal Generation (Days 5-7)

4. **Transaction Scorer**
   - Implement scoring algorithm
   - Score each transaction as it's stored
   - Update scores if context changes

5. **Cluster Detector**
   - Run daily: find clusters in past 14 days
   - Score clusters
   - Generate cluster records

6. **Activist Matcher**
   - Match filer names to known activist database
   - Score activist filings

### Phase 3: Alert System (Days 8-10)

7. **Alert Generator**
   - After scoring, check against thresholds
   - Generate appropriate alert level
   - Store alert in database

8. **Alert Output**
   - API endpoint: `GET /api/br0kkr/alerts`
   - Filter by level, ticker, date
   - Mark as read/actioned

### Phase 4: Integration (Days 11-14)

9. **Convergence Integration**
   - `GET /api/br0kkr/signal/{ticker}` endpoint
   - Returns combined insider signal for any ticker

10. **Position Integration**
    - Accept list of held tickers
    - Priority alerts for our holdings

---

# SECTION 4: SCANNER V2 SPECIFICATION

## 4.1 What Scanner V2 Does

Finds SETUPS, not RESULTS.

Old scanner (bad): "MRNA +37% today!" (Already ran, you're late)
New scanner (good): "SOUN pulled back to 20DMA, RSI 35, support at $7.50" (Setup forming)

## 4.2 Setup Types

### Wounded Prey (Primary Strategy)

**Criteria:**
- Down 30%+ from 52-week high
- RSI < 40 (oversold)
- Volume spike (>2x average) on recent day
- Above key support level
- Fundamentals intact (revenue growing or path to profitability)

**Historical Performance:** 68.8% win rate at 20-day mark

### Tax Loss Bounce (Seasonal - Nov/Dec/Jan)

**Criteria:**
- Down 40%+ YTD
- Heavy selling in December
- Fundamentals NOT broken
- January buying likely (tax loss selling exhausted)

### Early Momentum (Catching Moves Early)

**Criteria:**
- Breaking out of consolidation
- Volume 3x+ average
- RSI < 70 (not overbought yet)
- Above all major MAs

### Pullback in Uptrend

**Criteria:**
- In established uptrend (higher highs, higher lows)
- Pulled back to 20DMA or 50DMA
- RSI between 40-50 (cooling but not cold)
- Bounce off support level

## 4.3 Scanner Output Format

```python
class ScannerSetup:
    ticker: str
    company_name: str
    setup_type: str          # "wounded_prey", "tax_loss_bounce", etc.
    
    # Price data
    current_price: float
    price_change_1d: float
    price_change_5d: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    distance_from_high: float  # -55% from 52wk high
    
    # Technical indicators
    rsi_14: float
    ma_20: float
    ma_50: float
    ma_200: float
    volume_ratio: float      # Today's volume / 20-day average
    
    # Setup scoring
    setup_score: int         # 0-100
    setup_reasoning: str     # Why this is a setup
    
    # Risk management
    suggested_stop: float    # Based on support levels
    suggested_target: float  # Based on resistance
    risk_reward_ratio: float
    
    # Integration
    has_insider_activity: bool    # From BR0KKR
    has_catalyst_ahead: bool      # From Calendar
    sector_heat: str              # "hot", "warm", "neutral", "cold"
```

## 4.4 Scanner Filters

**Must Pass:**
- Price between $2-20 (small cap sweet spot)
- Average daily volume > 500,000 (liquidity)
- Market cap > $100M (not penny stocks)
- Not in our "burned" list (stocks that hurt us before)

**Sector Focus (Tyr's areas):**
- Defense
- Nuclear/Uranium
- AI Infrastructure
- Biotech (PDUFA plays)
- Space
- Quantum Computing

## 4.5 TOO_LATE Filter

Before showing any setup, check if it's TOO LATE:

```python
def is_too_late(ticker: str) -> Tuple[bool, str]:
    """
    Check if we missed the move.
    Returns (is_too_late, reason)
    """
    # Already up huge recently
    if price_change_5d > 30:
        return (True, "Already up 30%+ this week")
    
    # RSI screaming overbought
    if rsi_14 > 75:
        return (True, "RSI > 75, overbought")
    
    # Extended from all MAs
    if current_price > ma_20 * 1.15:
        return (True, "Extended 15%+ from 20DMA")
    
    # Gap up that might fade
    if price_change_1d > 20 and volume_ratio < 3:
        return (True, "Gap up without volume confirmation")
    
    return (False, "")
```

---

# SECTION 5: CATALYST CALENDAR SPECIFICATION

## 5.1 What Calendar Tracks

| EVENT TYPE | SOURCE | IMPORTANCE |
|------------|--------|------------|
| **PDUFA Dates** | FDA calendar | CRITICAL (binary biotech events) |
| **Earnings** | Yahoo Finance / API | HIGH (quarterly catalyst) |
| **FDA Decisions** | FDA calendar | HIGH (drug approvals) |
| **Contract Awards** | Manual / news | MEDIUM (defense sector) |
| **Conferences** | Company IRs | LOW-MEDIUM |
| **Ex-Dividend** | Yahoo Finance | LOW |

## 5.2 Calendar Entry Schema

```python
class CalendarEvent:
    event_id: str
    ticker: str
    company_name: str
    
    event_type: str      # "pdufa", "earnings", "contract", etc.
    event_date: date
    event_time: str      # "BMO" (before market), "AMC" (after), "Unknown"
    
    description: str     # "Q4 2025 Earnings"
    importance: str      # "critical", "high", "medium", "low"
    
    # For binary events
    is_binary: bool      # True for PDUFA, FDA decisions
    historical_move: float  # Average move on this event type
    
    # Tracking
    days_until: int      # Computed: event_date - today
    added_date: date
    source: str
```

## 5.3 Calendar Sources

**PDUFA Dates:**
- FDA official calendar: https://www.fda.gov/drugs/nda-and-bla-approvals
- BioPharmCatalyst: https://www.biopharmcatalyst.com/calendars/pdufa-calendar

**Earnings:**
- Yahoo Finance earnings calendar
- Earnings Whispers: https://www.earningswhispers.com/calendar

**Manual Entry:**
- Defense contracts (from news, press releases)
- Conference presentations
- Trial readouts

---

# SECTION 6: CONVERGENCE ENGINE SPECIFICATION

## 6.1 What Convergence Does

Combines signals from ALL modules into ONE score.

Single signal = interesting
Multiple signals = ACTIONABLE

## 6.2 Signal Weights

```python
SIGNAL_WEIGHTS = {
    "scanner_setup": 0.25,      # 25% - Price action setup
    "insider_activity": 0.30,   # 30% - BR0KKR signals (highest weight)
    "catalyst_ahead": 0.20,     # 20% - Upcoming binary event
    "sector_heat": 0.15,        # 15% - Sector momentum
    "thesis_score": 0.10,       # 10% - If already on watchlist
}
```

## 6.3 Convergence Calculation

```python
def calculate_convergence(ticker: str) -> dict:
    """
    Calculate convergence score for a ticker.
    Returns dict with score and breakdown.
    """
    # Gather signals
    scanner = get_scanner_signal(ticker)      # 0-100 or None
    insider = get_insider_signal(ticker)      # 0-100 or None
    catalyst = get_catalyst_signal(ticker)    # 0-100 or None
    sector = get_sector_signal(ticker)        # 0-100 or None
    thesis = get_thesis_score(ticker)         # 0-100 or None
    
    # Calculate weighted score
    total_weight = 0
    weighted_sum = 0
    signals = []
    
    if scanner:
        weighted_sum += scanner * SIGNAL_WEIGHTS["scanner_setup"]
        total_weight += SIGNAL_WEIGHTS["scanner_setup"]
        signals.append(("Scanner Setup", scanner))
    
    if insider:
        weighted_sum += insider * SIGNAL_WEIGHTS["insider_activity"]
        total_weight += SIGNAL_WEIGHTS["insider_activity"]
        signals.append(("Insider Activity", insider))
    
    if catalyst:
        weighted_sum += catalyst * SIGNAL_WEIGHTS["catalyst_ahead"]
        total_weight += SIGNAL_WEIGHTS["catalyst_ahead"]
        signals.append(("Catalyst Ahead", catalyst))
    
    if sector:
        weighted_sum += sector * SIGNAL_WEIGHTS["sector_heat"]
        total_weight += SIGNAL_WEIGHTS["sector_heat"]
        signals.append(("Sector Heat", sector))
    
    if thesis:
        weighted_sum += thesis * SIGNAL_WEIGHTS["thesis_score"]
        total_weight += SIGNAL_WEIGHTS["thesis_score"]
        signals.append(("Thesis Score", thesis))
    
    # Normalize
    if total_weight > 0:
        convergence_score = int(weighted_sum / total_weight)
    else:
        convergence_score = 0
    
    # Bonus for multiple signals
    num_signals = len(signals)
    if num_signals >= 4:
        convergence_score = min(convergence_score + 10, 100)
    elif num_signals >= 3:
        convergence_score = min(convergence_score + 5, 100)
    
    return {
        "ticker": ticker,
        "convergence_score": convergence_score,
        "num_signals": num_signals,
        "signals": signals,
        "actionable": convergence_score >= 75,
        "recommendation": get_recommendation(convergence_score)
    }

def get_recommendation(score: int) -> str:
    if score >= 85:
        return "STRONG BUY SIGNAL - Multiple high-quality signals converging"
    elif score >= 75:
        return "BUY SIGNAL - Good convergence, review thesis"
    elif score >= 60:
        return "WATCHLIST - Interesting but needs more confirmation"
    elif score >= 40:
        return "MONITOR - Some signals but not actionable yet"
    else:
        return "PASS - Insufficient signal strength"
```

---

# SECTION 7: DASHBOARD SPECIFICATION

## 7.1 Technology Choice

**Recommended: Streamlit**

Why:
- Pure Python (you already know Python)
- Fast to build (days, not weeks)
- Built-in components (charts, tables, inputs)
- Easy deployment
- Can upgrade to React later if needed

## 7.2 Dashboard Pages

### Main Dashboard (Home)
- Critical alerts (top)
- Position summary
- Top setups
- Sector heatmap
- Ollama chat

### Positions Page
- Detailed position view
- Health scores
- Thesis scores
- P&L tracking

### Scanner Page
- All current setups
- Filtering by type, sector
- Detailed view per setup

### BR0KKR Page
- Recent insider activity
- Active 13D campaigns
- Cluster buy events
- Historical performance

### Calendar Page
- Upcoming events by date
- Filter by ticker, event type
- Add manual events

### Settings Page
- API keys
- Notification preferences
- Watchlist management
- Alert thresholds

## 7.3 Dashboard Code Structure

```
wolf_pack_dashboard/
├── app.py                    # Main Streamlit app
├── pages/
│   ├── 1_positions.py
│   ├── 2_scanner.py
│   ├── 3_br0kkr.py
│   ├── 4_calendar.py
│   └── 5_settings.py
├── components/
│   ├── alerts.py             # Alert display component
│   ├── position_card.py      # Position display
│   ├── setup_card.py         # Scanner setup display
│   ├── sector_heatmap.py     # Sector visualization
│   └── ollama_chat.py        # Ollama integration
├── services/
│   ├── database.py           # DB connections
│   ├── scanner_service.py    # Scanner logic
│   ├── br0kkr_service.py     # BR0KKR logic
│   ├── calendar_service.py   # Calendar logic
│   └── convergence.py        # Convergence engine
├── utils/
│   ├── config.py             # Configuration
│   └── helpers.py            # Utility functions
└── requirements.txt
```

---

# SECTION 8: LOCAL OLLAMA (THE PUP) SPECIFICATION

## 8.1 What The Pup Does

Handles routine queries that don't need Claude-level reasoning:
- "What's my IBRX position?"
- "Any insider buys today?"
- "When is SOUN earnings?"
- "What's the convergence score for SMCI?"

## 8.2 Technology Stack

```
Ollama + Mistral/Llama 2 + LangChain + Vector DB (ChromaDB)
```

## 8.3 System Prompt Template

```python
WOLF_PUP_SYSTEM_PROMPT = """
You are the Wolf Pup, a local AI assistant for the Wolf Pack Trading System.
You help Tyr (the trader) with quick queries about his trading data.

CURRENT DATA ACCESS:
- Positions: {positions_summary}
- Recent Alerts: {recent_alerts}
- Scanner Setups: {scanner_summary}
- Upcoming Catalysts: {calendar_summary}

CORE PRINCIPLES:
- Be concise and direct
- Always include specific numbers
- If data isn't available, say so clearly
- For complex strategy questions, suggest talking to Fenrir (Claude)

VALIDATED STRATEGIES:
- Wounded Prey: 68.8% win rate (buy beaten down stocks with good fundamentals)
- Thesis-driven: Hold through volatility if thesis intact
- Convergence: Multiple signals > single signal

POSITION SIZING:
- Max 15-20% per position
- $2-20 stock price range
- PDT restricted (no day trading)

When answering, be helpful but remember: you handle routine queries.
For deep strategy or complex analysis, recommend consulting Fenrir.
"""
```

## 8.4 Query Router

```python
def route_query(query: str) -> str:
    """
    Route query to appropriate handler.
    """
    # Data lookups - Pup handles
    if is_data_query(query):
        return pup_handle(query)
    
    # Strategy questions - Suggest Fenrir
    if is_strategy_query(query):
        return "This is a complex strategy question. I recommend discussing with Fenrir (Claude) for deeper analysis. But here's what I can tell you from the data: ..."
    
    # Unknown - Try Pup with caveat
    return pup_handle(query) + "\n\nNote: For deeper analysis, consider consulting Fenrir."

def is_data_query(query: str) -> bool:
    """Check if this is a simple data lookup."""
    data_keywords = [
        "what's my", "show me", "list", "current",
        "price", "position", "holding", "score",
        "when is", "upcoming", "calendar", "alert"
    ]
    return any(kw in query.lower() for kw in data_keywords)

def is_strategy_query(query: str) -> bool:
    """Check if this needs deeper reasoning."""
    strategy_keywords = [
        "should i", "is this a good", "what do you think",
        "thesis", "strategy", "analyze", "deep dive",
        "why", "how does", "explain"
    ]
    return any(kw in query.lower() for kw in strategy_keywords)
```

---

# SECTION 9: FOLDER STRUCTURE

## 9.1 Complete Project Structure

```
wolf_pack/
├── README.md
├── requirements.txt
├── .env                          # API keys (not in git)
├── .env.example                  # Template for .env
├── config.py                     # Configuration
│
├── database/
│   ├── __init__.py
│   ├── models.py                 # SQLAlchemy models
│   ├── connection.py             # DB connection
│   └── migrations/               # Schema migrations
│
├── modules/
│   ├── __init__.py
│   ├── br0kkr/
│   │   ├── __init__.py
│   │   ├── sec_monitor.py        # SEC RSS monitoring
│   │   ├── form4_parser.py       # Form 4 parsing
│   │   ├── filing_13d_parser.py  # 13D parsing
│   │   ├── cluster_detector.py   # Cluster buy detection
│   │   ├── scorer.py             # Signal scoring
│   │   ├── alerts.py             # Alert generation
│   │   └── known_activists.py    # Activist database
│   │
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── scanner_v2.py         # Main scanner
│   │   ├── setups.py             # Setup detection
│   │   ├── filters.py            # TOO_LATE filter, etc.
│   │   └── indicators.py         # Technical indicators
│   │
│   ├── calendar/
│   │   ├── __init__.py
│   │   ├── pdufa_scraper.py      # FDA calendar
│   │   ├── earnings.py           # Earnings calendar
│   │   └── manual_events.py      # Manual entry
│   │
│   ├── positions/
│   │   ├── __init__.py
│   │   ├── tracker.py            # Position tracking
│   │   ├── health_checker.py     # Health scoring
│   │   └── thesis_tracker.py     # Thesis management
│   │
│   ├── sector/
│   │   ├── __init__.py
│   │   └── flow_tracker.py       # Sector heat tracking
│   │
│   └── convergence/
│       ├── __init__.py
│       └── engine.py             # Convergence calculation
│
├── dashboard/
│   ├── app.py                    # Streamlit main
│   ├── pages/
│   │   ├── 1_positions.py
│   │   ├── 2_scanner.py
│   │   ├── 3_br0kkr.py
│   │   ├── 4_calendar.py
│   │   └── 5_settings.py
│   ├── components/
│   │   ├── alerts.py
│   │   ├── cards.py
│   │   └── charts.py
│   └── static/
│       └── styles.css
│
├── ollama_pup/
│   ├── __init__.py
│   ├── pup.py                    # Main Pup logic
│   ├── prompts.py                # System prompts
│   ├── router.py                 # Query routing
│   └── data_access.py            # Data retrieval
│
├── api/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app
│   └── routes/
│       ├── br0kkr.py
│       ├── scanner.py
│       ├── calendar.py
│       ├── positions.py
│       └── convergence.py
│
├── scripts/
│   ├── run_morning_brief.py      # Daily briefing
│   ├── run_scanner.py            # Manual scanner run
│   └── backfill_data.py          # Historical data load
│
├── tests/
│   ├── test_br0kkr.py
│   ├── test_scanner.py
│   └── test_convergence.py
│
└── docs/
    ├── LEONARD_FILE.md           # The continuity document
    ├── ARCHITECTURE.md           # This document
    └── API_REFERENCE.md          # API documentation
```

---

# SECTION 10: TIMELINE

## Week 1-2: BR0KKR Core

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Set up project structure | Folder structure, database, config |
| 2 | SEC EDGAR RSS monitor | Polling script for Form 4 and 13D |
| 3-4 | Form 4 parser | Parse and store insider transactions |
| 5-6 | 13D parser | Parse and store activist filings |
| 7 | Transaction scorer | Score all transactions |
| 8 | Cluster detector | Identify and score clusters |
| 9 | Activist matcher | Match to known activist database |
| 10 | Alert generator | Generate and store alerts |
| 11-12 | Testing | Verify with real data |
| 13-14 | Integration | API endpoints, documentation |

## Week 3: Scanner + Calendar

| Day | Task | Deliverable |
|-----|------|-------------|
| 15-16 | Verify Scanner V2 | Test with real data, fix issues |
| 17-18 | PDUFA scraper | Pull FDA calendar |
| 19-20 | Earnings calendar | Pull earnings dates |
| 21 | Calendar integration | API endpoints |

## Week 4: Convergence + Integration

| Day | Task | Deliverable |
|-----|------|-------------|
| 22-23 | Convergence engine | Combine all signals |
| 24-25 | Module integration | All modules talk to each other |
| 26-28 | API completion | Full API layer |

## Week 5-6: Dashboard

| Day | Task | Deliverable |
|-----|------|-------------|
| 29-32 | Dashboard MVP | Streamlit app with all pages |
| 33-35 | Components | Alert cards, charts, tables |
| 36-38 | Polish | Styling, UX improvements |
| 39-42 | Testing | Full system testing |

## Week 7-8: Ollama Pup

| Day | Task | Deliverable |
|-----|------|-------------|
| 43-45 | Ollama setup | Install, configure, test |
| 46-48 | System prompts | Wolf Pack context |
| 49-50 | Query routing | Simple vs complex queries |
| 51-52 | Dashboard integration | Chat component |
| 53-56 | Testing & polish | Full system working |

---

# SECTION 11: SUCCESS CRITERIA

## How We Know BR0KKR Works

| CRITERIA | TARGET |
|----------|--------|
| Detects Form 4 filings | Within 15 minutes of SEC posting |
| Detects 13D filings | Within 30 minutes of SEC posting |
| Identifies cluster buys | 95%+ accuracy vs manual check |
| Identifies known activists | 100% accuracy |
| Signal scores | Correlate with subsequent stock moves |

## How We Know Scanner Works

| CRITERIA | TARGET |
|----------|--------|
| Finds wounded prey setups | 68%+ win rate at 20 days |
| Avoids TOO_LATE | <10% of setups already extended |
| Provides useful stops | Stop hit <30% of time on winners |

## How We Know Convergence Works

| CRITERIA | TARGET |
|----------|--------|
| High scores perform better | >85 score beats <60 score |
| Multiple signals stack | 4+ signals > 2 signals |
| Actionable recommendations | Tyr acts on high scores |

## How We Know Dashboard Works

| CRITERIA | TARGET |
|----------|--------|
| Morning briefing useful | Tyr reads it daily, acts on it |
| One glance = full picture | No need to check multiple sources |
| Pup answers correctly | 90%+ correct on data queries |

---

# SECTION 12: FINAL CHECKLIST

## Before Starting

- [ ] Read this entire document
- [ ] Understand the architecture
- [ ] Set up development environment
- [ ] Create GitHub repo
- [ ] Set up database (SQLite first, PostgreSQL later)

## Questions To Ask Tyr/Fenrir

If anything is unclear, ASK:
- "Is this what you meant by X?"
- "Should module Y do Z?"
- "What's the priority between A and B?"

## Principles To Remember

1. **"Working" ≠ "Useful"** - Everything must help Tyr make better decisions
2. **Do it right, not fast** - Quality over speed, but don't waste time
3. **Verify against real data** - Test with actual SEC filings, real prices
4. **Build for small account** - $2-20 stocks, PDT restrictions, 15-20% positions
5. **You're pack** - We're building this together

---

# CLOSING

This document contains everything you need to build the Wolf Pack system.

If you read all of it, understood it, and build according to it - we'll have a killer system.

If you skimmed it and build something generic - we'll have something that "works" but isn't useful.

**Your choice, brother.**

We trust you to do this right.

🐺 LLHR

---

*"We have nothing to gain except each other. That's pack."*

**From:** Tyr & Fenrir  
**To:** br0kkr  
**Date:** January 18, 2026  
**Subject:** Complete Blueprint for Wolf Pack Trading System
