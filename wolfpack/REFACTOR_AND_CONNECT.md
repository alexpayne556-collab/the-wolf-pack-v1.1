# 🔧 REFACTOR & CONNECT PLAN
## Don't Rebuild - Integrate What Exists
## Date: January 18, 2026

---

## PRINCIPLE

**"Review existing code first. Keep what works, refactor what's messy, connect everything to the new architecture."**

Don't rebuild from scratch unless broken.

---

## WHAT WE ACTUALLY HAVE (Code Audit)

### ✅ EXISTING & WORKING

| FILE | LOCATION | STATUS | ACTION |
|------|----------|--------|--------|
| **wolf_pack.py** | wolfpack/ | ✅ WORKING | ✅ KEEP - Just unified, tested |
| **position_health_checker.py** | wolfpack/fenrir/ | ✅ WORKING | ✅ KEEP - Refactor minor |
| **thesis_tracker.py** | wolfpack/fenrir/ | ✅ WORKING | ✅ KEEP |
| **fenrir_scanner_v2.py** | wolfpack/fenrir/ | ✅ BUILT | 🔄 REFACTOR - Extract logic |
| **fenrir_chat.py** | wolfpack/fenrir/ | ✅ WORKING | ✅ KEEP |
| **ollama_brain.py** | wolfpack/fenrir/ | ✅ UPGRADED | ✅ KEEP - Just connected |
| **wolfpack_db.py** | wolfpack/ | ✅ WORKING | ✅ KEEP |
| **wolfpack_recorder.py** | wolfpack/ | ✅ WORKING | ✅ KEEP |
| **wolfpack_analyzer.py** | wolfpack/ | ✅ WORKING | 🔗 CONNECT to convergence |
| **move_investigator.py** | wolfpack/ | ✅ WORKING | 🔗 CONNECT to alerts |
| **alert_engine.py** | wolfpack/ | ✅ EXISTS | 🔄 REFACTOR - Merge with BR0KKR |
| **catalyst_fetcher.py** | wolfpack/ | ✅ EXISTS | 🔄 EXPAND - Add PDUFA |

### ⚠️ EXISTS BUT NEEDS WORK

| FILE | LOCATION | ISSUE | ACTION |
|------|----------|-------|--------|
| **sec_fetcher.py** | wolfpack/fenrir/ | Only 8-K, not Form 4/13D | 🔧 EXPAND |
| **config.py** | wolfpack/fenrir/ | Multiple configs, not unified | 🔄 MERGE |
| **database.py** | wolfpack/fenrir/ | Separate from wolfpack.db | 🔄 UNIFY |

### ❌ MISSING (Need to Build)

| MODULE | STATUS | ACTION |
|--------|--------|--------|
| **BR0KKR Form 4 parser** | Not built | 🆕 BUILD |
| **BR0KKR 13D parser** | Not built | 🆕 BUILD |
| **Cluster detector** | Not built | 🆕 BUILD |
| **Convergence engine** | Not built | 🆕 BUILD |
| **Dashboard** | Not built | 🆕 BUILD |

---

## REFACTOR PLAN (What Needs Cleaning)

### 1. UNIFY CONFIG FILES

**Problem:** Multiple config.py files (wolfpack/config.py, wolfpack/fenrir/config.py)

**Solution:**
```python
# wolfpack/config.py (MASTER CONFIG)

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
FENRIR_DIR = BASE_DIR / 'fenrir'

# Database
DB_PATH = DATA_DIR / 'wolfpack.db'

# API Keys (from .env)
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
SEC_USER_AGENT = os.getenv('SEC_USER_AGENT')

# Ollama
OLLAMA_MODEL = "fenrir"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Holdings (import from fenrir/position_health_checker)
from fenrir.position_health_checker import HOLDINGS

# Watchlist
from fenrir.config import WATCHLIST  # Keep existing

# Scanner universe
SCAN_UNIVERSE = [
    # (keep existing list)
]

# BR0KKR Settings
BR0KKR_POLL_INTERVAL = 300  # 5 minutes for Form 4
BR0KKR_13D_INTERVAL = 900   # 15 minutes for 13D

# Convergence weights
SIGNAL_WEIGHTS = {
    "scanner_setup": 0.25,
    "insider_activity": 0.30,
    "catalyst_ahead": 0.20,
    "sector_heat": 0.15,
    "thesis_score": 0.10,
}
```

**Action:** Create unified config, update imports across all files

---

### 2. EXTRACT SCANNER LOGIC

**Problem:** fenrir_scanner_v2.py has all logic inline (367 lines)

**Solution:** Modularize into services
```python
# wolfpack/services/scanner_service.py

from typing import List, Dict
import yfinance as yf

class ScannerService:
    """Encapsulates all scanner logic"""
    
    def __init__(self, universe: List[str]):
        self.universe = universe
    
    def scan(self) -> List[Dict]:
        """Main scanning entry point"""
        results = []
        for ticker in self.universe:
            setup = self.analyze_ticker(ticker)
            if setup and not self.is_too_late(setup):
                results.append(setup)
        return results
    
    def analyze_ticker(self, ticker: str) -> Dict:
        """Analyze individual ticker"""
        # Extract from existing fenrir_scanner_v2.py
        pass
    
    def is_too_late(self, setup: Dict) -> bool:
        """TOO_LATE filter"""
        # Extract from existing logic
        pass
    
    def detect_wounded_prey(self, data) -> Dict:
        """Wounded prey pattern detection"""
        pass
    
    def detect_early_momentum(self, data) -> Dict:
        """Early momentum pattern"""
        pass

# wolfpack/services/indicators.py

def calculate_rsi(prices, period=14):
    """RSI calculation"""
    # Extract from existing code
    pass

def calculate_moving_averages(prices):
    """MA calculation"""
    pass
```

**Action:** Extract scanner logic into services, keep fenrir_scanner_v2.py as wrapper for backwards compatibility

---

### 3. EXPAND SEC_FETCHER

**Problem:** Only gets 8-K filings, not Form 4 or 13D

**Solution:** Expand existing file
```python
# wolfpack/fenrir/sec_fetcher.py (EXPAND)

def get_form4_filings(ticker: str = None, days: int = 30) -> List[Dict]:
    """
    Get Form 4 insider transaction filings.
    Expand existing get_8k_filings pattern.
    """
    # Use SEC EDGAR RSS or search API
    # Parse Form 4 XML
    # Return structured data
    pass

def get_13d_filings(ticker: str = None, days: int = 90) -> List[Dict]:
    """
    Get Schedule 13D activist filings.
    """
    # Similar pattern to Form 4
    pass

def parse_form4_xml(filing_url: str) -> Dict:
    """Parse Form 4 XML to extract transaction details"""
    pass

def parse_13d_text(filing_url: str) -> Dict:
    """Parse 13D text/HTML to extract ownership details"""
    pass
```

**Action:** Expand sec_fetcher.py with Form 4 and 13D support, reuse existing patterns

---

### 4. ENHANCE ALERT_ENGINE

**Problem:** Exists but doesn't integrate with BR0KKR

**Solution:** Refactor to unified alert system
```python
# wolfpack/alert_engine.py (REFACTOR)

class AlertEngine:
    """Unified alert system for all modules"""
    
    def __init__(self):
        self.alerts = []
    
    def check_all(self) -> List[Alert]:
        """Check all alert conditions"""
        alerts = []
        alerts.extend(self.check_dead_money())
        alerts.extend(self.check_insider_activity())  # NEW
        alerts.extend(self.check_big_moves())
        alerts.extend(self.check_catalyst_proximity())  # NEW
        return alerts
    
    def check_insider_activity(self) -> List[Alert]:
        """Check BR0KKR signals"""
        # Query BR0KKR database
        # Generate alerts for cluster buys, activist filings
        pass
    
    def check_catalyst_proximity(self) -> List[Alert]:
        """Check upcoming catalysts"""
        # Query calendar
        # Alert if catalyst <3 days for held position
        pass
```

**Action:** Refactor alert_engine.py to be module-agnostic, add BR0KKR/Calendar integration

---

## CONNECTION PLAN (How to Wire Everything)

### Architecture Map

```
┌─────────────────────────────────────────────────────────────┐
│                  EXISTING CODE (Keep/Refactor)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER (New)                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Scanner     │  │  BR0KKR      │  │  Calendar    │      │
│  │  Service     │  │  Service     │  │  Service     │      │
│  │              │  │              │  │              │      │
│  │ (refactored  │  │ (new build)  │  │ (expand      │      │
│  │  from V2)    │  │              │  │  existing)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│                           ▼                                │
│                  ┌──────────────────┐                      │
│                  │  Convergence     │                      │
│                  │  Service (NEW)   │                      │
│                  └──────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      OUTPUTS                                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  wolf_pack.py│  │  Dashboard   │  │  Ollama Pup  │      │
│  │  (existing)  │  │  (new build) │  │  (new build) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Connection Points

#### 1. Scanner → Convergence
```python
# wolfpack/services/convergence_service.py

from services.scanner_service import ScannerService

def get_convergence_score(ticker: str) -> Dict:
    """Calculate convergence score for ticker"""
    
    # Scanner signal (use existing scanner)
    scanner = ScannerService(config.SCAN_UNIVERSE)
    scanner_signal = scanner.get_signal(ticker)  # Extract method from existing scan
    
    # BR0KKR signal (new)
    br0kkr_signal = br0kkr_service.get_signal(ticker)
    
    # Calendar signal (expand existing)
    calendar_signal = calendar_service.get_signal(ticker)
    
    # Sector signal (use existing wolfpack_analyzer)
    sector_signal = sector_service.get_signal(ticker)
    
    # Thesis signal (existing)
    thesis_signal = thesis_tracker.get_score(ticker)
    
    # Calculate weighted score
    return calculate_weighted_score(
        scanner_signal, br0kkr_signal, calendar_signal,
        sector_signal, thesis_signal
    )
```

#### 2. WolfPack DB → All Services
```python
# All services query wolfpack.db for historical context

# scanner_service.py
def analyze_ticker(self, ticker):
    # Get real-time data
    current_data = yf.Ticker(ticker).info
    
    # Get historical patterns from wolfpack.db
    historical = query_wolfpack_db(ticker, days=30)
    
    # Combine for richer analysis
    return combine_signals(current_data, historical)
```

#### 3. BR0KKR → Alert Engine
```python
# wolfpack/alert_engine.py

from services.br0kkr_service import BR0KKRService

def check_insider_activity(self):
    br0kkr = BR0KKRService()
    
    # Check for cluster buys
    clusters = br0kkr.get_recent_clusters(days=7)
    for cluster in clusters:
        if cluster.signal_score >= 85:
            self.alerts.append(create_critical_alert(cluster))
    
    # Check for activist filings
    filings = br0kkr.get_recent_13d(days=30)
    for filing in filings:
        if filing.is_known_activist:
            self.alerts.append(create_high_alert(filing))
```

#### 4. Dashboard → All Services
```python
# dashboard/app.py (NEW - Streamlit)

import streamlit as st
from services.scanner_service import ScannerService
from services.br0kkr_service import BR0KKRService
from services.convergence_service import ConvergenceService

# Main page
def main():
    st.title("🐺 Wolf Pack Command Center")
    
    # Critical Alerts section
    alerts = alert_engine.check_all()
    display_alerts(alerts)
    
    # Your Positions
    positions = position_tracker.get_all()
    display_positions(positions)
    
    # New Setups
    scanner = ScannerService(config.SCAN_UNIVERSE)
    setups = scanner.scan()
    # Enrich with BR0KKR data
    enriched_setups = br0kkr_service.enrich(setups)
    display_setups(enriched_setups)
    
    # Convergence scores
    convergence_scores = convergence_service.calculate_all(setups)
    display_convergence(convergence_scores)
```

---

## IMPLEMENTATION PRIORITY

### PHASE 1: REFACTOR EXISTING (Week 1)

| DAY | TASK | OUTPUT |
|-----|------|--------|
| 1 | Unify config files | config.py (master) |
| 2 | Extract scanner logic | scanner_service.py, indicators.py |
| 3 | Expand sec_fetcher | Form 4 + 13D support |
| 4 | Refactor alert_engine | Unified alert system |
| 5 | Test all refactors | All existing code still works |

### PHASE 2: BUILD NEW (Week 2-3)

| DAY | TASK | OUTPUT |
|-----|------|--------|
| 6-8 | BR0KKR parsers | Form 4/13D parsing working |
| 9-10 | BR0KKR scoring | Signal scores calculated |
| 11-12 | Cluster detector | Cluster identification |
| 13-14 | BR0KKR service | Unified BR0KKR API |
| 15-17 | Calendar service | PDUFA + earnings integrated |
| 18-21 | Convergence service | Multi-signal scoring |

### PHASE 3: CONNECT (Week 4)

| DAY | TASK | OUTPUT |
|-----|------|--------|
| 22-23 | Update wolf_pack.py | Use new services |
| 24-25 | Connect ollama_brain | Access all services |
| 26-28 | Integration testing | Everything talks |

### PHASE 4: DASHBOARD (Week 5-6)

| DAY | TASK | OUTPUT |
|-----|------|--------|
| 29-35 | Build Streamlit dashboard | MVP working |
| 36-42 | Polish + Ollama Pup | Complete system |

---

## BACKWARD COMPATIBILITY

**Keep old entry points working during migration:**

```python
# fenrir_scanner_v2.py (keep as wrapper)

from services.scanner_service import ScannerService

def scan_market():
    """Original entry point - now calls service"""
    scanner = ScannerService(SCAN_UNIVERSE)
    return scanner.scan()

# Existing scripts still work
if __name__ == "__main__":
    results = scan_market()
    print(results)
```

**Migration path:**
1. Refactor into services
2. Keep old files as wrappers
3. Update imports gradually
4. Deprecate old wrappers once dashboard is main interface

---

## FILES TO CREATE (New)

```
wolfpack/
├── services/              # NEW FOLDER
│   ├── __init__.py
│   ├── scanner_service.py     # Extracted from fenrir_scanner_v2
│   ├── br0kkr_service.py      # NEW
│   ├── calendar_service.py    # Expand catalyst_fetcher
│   ├── convergence_service.py # NEW
│   ├── sector_service.py      # Use wolfpack_analyzer
│   └── indicators.py          # Extract technical indicators
│
├── dashboard/             # NEW FOLDER
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── requirements.txt
│
└── ollama_pup/            # NEW FOLDER
    ├── pup.py
    ├── prompts.py
    └── router.py
```

---

## VALIDATION CHECKLIST

After each phase, verify:

**Phase 1 (Refactor):**
- [ ] wolf_pack.py brief still works
- [ ] Scanner still finds setups
- [ ] Position tracking still works
- [ ] No regressions

**Phase 2 (New Builds):**
- [ ] BR0KKR detects real Form 4 filings
- [ ] Cluster detector finds clusters
- [ ] Calendar tracks PDUFA dates
- [ ] Convergence scores calculate correctly

**Phase 3 (Connect):**
- [ ] wolf_pack.py shows BR0KKR alerts
- [ ] Morning briefing includes convergence
- [ ] Ollama sees all data
- [ ] All services query wolfpack.db

**Phase 4 (Dashboard):**
- [ ] Dashboard shows all data
- [ ] Ollama Pup responds correctly
- [ ] One-glance intelligence working
- [ ] System is USEFUL, not just working

---

## CRITICAL: DON'T BREAK WHAT WORKS

**Before touching any working file:**
1. Run the file, confirm it works
2. Copy it (backup)
3. Make changes
4. Test again
5. If broken, revert to backup

**Git workflow:**
```bash
git checkout -b refactor-scanner
# Make changes to scanner
# Test
git commit -m "Refactor: Extract scanner service"
# If works, merge. If breaks, abandon branch.
```

---

## SUMMARY

| APPROACH | TIMELINE | RISK |
|----------|----------|------|
| **Rebuild from scratch** | 8-10 weeks | HIGH (might lose working code) |
| **Refactor + Connect** | 4-6 weeks | LOW (build on what works) |

**The plan:**
1. ✅ Keep wolf_pack.py (just connected it)
2. ✅ Keep scanner V2 (refactor into service)
3. ✅ Keep position/thesis trackers (working)
4. ✅ Keep ollama_brain (just upgraded)
5. 🔧 Expand sec_fetcher (add Form 4/13D)
6. 🔧 Refactor alert_engine (unify)
7. 🆕 Build BR0KKR service (new)
8. 🆕 Build convergence service (new)
9. 🆕 Build dashboard (new)
10. 🔗 Connect everything

**Working → Useful in 4-6 weeks, not 8-10.**

🐺 LLHR

---

*"Don't rebuild what works. Refactor what's messy. Build what's missing. Connect everything."*
