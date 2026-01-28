# 🐺 WOLF BRAIN QUICK REFERENCE

## RUNNING THE BRAIN

```powershell
# From brokkr folder:

# 24/7 AUTONOMOUS MODE (normal)
python src\wolf_brain\autonomous_brain.py

# BACKGROUND MODE (hidden, runs forever)
.\start_wolf_brain.ps1 --background

# 🔥 GENERATE INTEL REPORT NOW
python src\wolf_brain\autonomous_brain.py --report

# 🔥 SCAN FOR REAL PREMARKET GAINERS
python src\wolf_brain\autonomous_brain.py --gainers

# FORCE 4AM SCAN NOW (test runner detection)
python src\wolf_brain\autonomous_brain.py --scan

# ANALYZE A SPECIFIC TICKER
python src\wolf_brain\autonomous_brain.py --analyze AQST
python src\wolf_brain\autonomous_brain.py --analyze IBRX

# DRY RUN (no real trades)
python src\wolf_brain\autonomous_brain.py --dry-run

# ONE CYCLE THEN EXIT
python src\wolf_brain\autonomous_brain.py --once
```

## 🔥 4 AM AUTO-START SETUP

Run ONCE as Administrator to schedule 4 AM auto-scan:
```powershell
.\setup_4am_scheduler.ps1
```

This creates a Windows Task that:
- Wakes the brain at 4:00 AM
- Scans ALL premarket gainers  
- Classifies RUNNERS vs FADERS
- Generates INTEL REPORT
- Saves to `data\wolf_brain\LATEST_INTEL_REPORT.txt`

**When you wake up at 7 AM, just open the report!**

## BRAIN SCHEDULE

| Time | Status | What Brain Does |
|------|--------|-----------------|
| 4:00 AM | `PREMARKET_EARLY` | **FIRST SCAN** - Find overnight gaps |
| 4:30-6:00 AM | `PREMARKET` | Light monitoring |
| 6:00-9:00 AM | `PREMARKET_PRIME` | **VOLUME CHECK** - Confirm runners |
| 9:00-9:30 AM | `PREMARKET_FINAL` | **FINAL DECISIONS** - Entry planning |
| 9:30-4:00 PM | `OPEN` | **EXECUTE & MANAGE** - Trade + manage positions |
| 4:00 PM+ | `AFTER_HOURS` | Review, learn, adjust |
| Night | `OVERNIGHT` | Light research |
| Weekend | `CLOSED_WEEKEND` | Rest |

## FDA CALENDAR (Loaded in Brain)

| Ticker | Date | Catalyst | Potential |
|--------|------|----------|-----------|
| **AQST** | Jan 31, 2025 | Libervant approval | +176% analyst target |
| **PHAR** | Jan 31, 2025 | Rare disease | HIGH |
| **IRON** | Jan 31, 2025 | Schizophrenia | HIGH |
| **VNDA** | Feb 21, 2025 | Motion sickness | MEDIUM |
| **ETON** | Feb 25, 2025 | Rare disease | MEDIUM |

## THE BIOTECH FORMULA

```
LOW FLOAT (<20M) + FDA CATALYST + POSITIVE NEWS = 100-500% in ONE DAY
```

### What Makes a RUNNER:
- ✅ Low float (<20M shares)
- ✅ Real catalyst (FDA, earnings, partnership)
- ✅ Heavy volume (3x+ normal)
- ✅ Gap 10-30% (not too extended)
- ✅ News from reputable source

### What Makes a FADER:
- ❌ High float (>100M)
- ❌ No clear catalyst
- ❌ Light volume
- ❌ Gap 50%+ (too extended)
- ❌ Pump from newsletter/social

## UNIVERSE SECTORS

| Sector | Tickers | Why |
|--------|---------|-----|
| **FDA Plays** | AQST, PHAR, IRON, VNDA, ETON | Catalyst dates |
| **Core Watchlist** | GLSI, BTAI, PMCB, ONCY, IBRX, SNGX, TNXP | Researched |
| **Low Float Biotech** | SNGX, TNXP, BTAI, OCGN, MNMD, IBRX... | Biggest runners |
| **Defense/Space** | KTOS, RKLB, LUNR, ASTS, PLTR, GILT | Policy momentum |
| **Nuclear** | SMR, OKLO, NNE, BWXT, LEU, UEC | Energy thesis |
| **AI/Quantum** | IONQ, QBTS, RGTI, SOUN, BBAI | Tech momentum |

## LOG FILES

All activity logged to:
```
c:\Users\alexp\Desktop\brokkr\data\wolf_brain\
  - autonomous_YYYYMMDD.log    (daily log)
  - wolf_brain.db              (decisions, trades, learnings)
```

## SAFETY LIMITS

- **Max Position**: 10% of portfolio
- **Max Daily Trades**: 10
- **Paper Trading Only**: Yes (configurable)
- **Always use stops**: 8% default

## CONNECTIONS

| Service | Status |
|---------|--------|
| **Ollama (fenrir:latest)** | http://localhost:11434 |
| **Alpaca Paper** | $100,029.56 portfolio |
| **Finnhub** | News API |
| **yfinance** | Price data |

## EXAMPLE OUTPUT

```
🌅 4AM PREMARKET SCANNER ACTIVATED
📊 Scanning 28 targets...
🚀 GAP DETECTED: AQST +5.1%
✅ RUNNER CANDIDATE: AQST - LOW FLOAT: 111.9M | Heavy volume: 2.3x
🎯 PREMARKET SUMMARY:
   RUNNERS: 3
      AQST: +5.1% gap | 72% confidence
      BTAI: +8.3% gap | 68% confidence
   FADERS: 5 (avoiding)
```

---

**THE WOLF HUNTS AT 4AM** 🐺
