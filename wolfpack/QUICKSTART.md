# 🐺 WOLF PACK - QUICK START

## First Time Setup

### 1. Run Setup (ONE TIME ONLY)

**Double-click:** [SETUP.bat](SETUP.bat)

This will:
- Check if Python is installed
- Install Python packages automatically
- Set everything up

**If Python is NOT installed**, the script will tell you exactly how to get it:
- **Option 1:** Microsoft Store (search "Python 3.12" - easiest)
- **Option 2:** Download from python.org

Then run SETUP.bat again after installing Python.

### 2. Verify Your API Keys
Open [.env](.env) and make sure your API keys are there:
- ✅ Finnhub: d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
- ✅ Alpha Vantage: 6N85IHTP3ZNW9M3Z
- ✅ Polygon: nmJowLVpeQPrvBf31mSo8WiwnR5riIUT

---

## Daily Usage (EASY MODE)

### Option 1: Double-Click the Batch File
**Just double-click:** [RUN_WOLFPACK.bat](RUN_WOLFPACK.bat)

That's it. The system will:
1. Initialize database
2. Update forward returns
3. Record today's data (99 stocks)
4. Investigate big moves
5. Check for alerts
6. Generate daily report

### Option 2: Right-Click → Run with PowerShell
Right-click [RUN_WOLFPACK.ps1](RUN_WOLFPACK.ps1) → **Run with PowerShell**

---

## Manual Mode (If You Want Control)

```bash
# Run individual components
python wolfpack_updater.py       # Update returns
python wolfpack_recorder.py      # Capture data
python move_investigator.py      # Investigate moves
python alert_engine.py           # Check alerts
python wolfpack_daily_report.py  # Generate report
```

---

## Where's My Data?

- **Database:** `data/wolfpack.db` (SQLite)
- **Daily Reports:** `reports/daily_YYYYMMDD.txt`
- **Investigations:** Stored in database

---

## Troubleshooting

### "Python not found"
Install Python 3.10+ from [python.org](https://python.org)

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API rate limit exceeded"
The system has built-in rate limiting. If you hit limits:
- Finnhub: 60 calls/min (free tier)
- Alpha Vantage: 25 calls/day (free tier)
- Polygon: 5 calls/min (free tier)

Just run it again later or upgrade to paid tiers.

---

## What Gets Tracked?

**99 stocks across 11 sectors:**
- Your Holdings: MU, UEC, KTOS, SLV, SRTA, BBAI
- Defense: KTOS, AVAV, RCAT, LMT, NOC, RTX, etc.
- Space: LUNR, RKLB, ASTS, BKSY, etc.
- Nuclear: UEC, UUUU, CCJ, LEU, etc.
- Semis: MU, AMD, NVDA, INTC, etc.
- AI/Tech: AAPL, MSFT, GOOGL, META, etc.
- Biotech: EDIT, BEAM, CRSP, NTLA, etc.
- Quantum: QUBT, QBTS, RGTI, IONQ
- Crypto: RIOT, MARA, COIN, MSTR, etc.
- Materials: SLV, GLD, FCX, MP, etc.
- EVs: RIVN, LCID, NIO, etc.
- Energy: FCEL, PLUG, BE, etc.

---

## 🐺 LLHR - Ready to Hunt

**Just double-click RUN_WOLFPACK.bat every day after market close (4:30 PM ET).**
