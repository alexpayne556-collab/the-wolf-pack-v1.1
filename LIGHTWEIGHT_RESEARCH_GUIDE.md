# 🔬 LIGHTWEIGHT RESEARCH SYSTEM

**Created:** January 27, 2026

---

## 🎯 PURPOSE

This is a **research-only** version of the Wolf Pack system designed for:
- ✅ Low RAM usage (4-8GB)
- ✅ No trading execution (just intelligence gathering)
- ✅ No heavy AI models (no Ollama)
- ✅ Cloud-ready (can run on cheap VPS)
- ✅ Exports data for manual review

---

## 📦 WHAT'S INCLUDED

### Single File System: `lightweight_researcher.py`

**Features:**
- Scans stock universe for wounded prey patterns
- Calculates convergence scores (0-100)
- Analyzes 5 core signals:
  1. Volume spike
  2. Price decline from highs
  3. RSI oversold
  4. Recent reversal patterns
  5. News sentiment (optional)
- Exports results to JSON + CSV
- **NO trading execution**
- **NO RAM-heavy dependencies**

---

## 🚀 QUICK START

### Step 1: Install Dependencies
```bash
pip install yfinance pandas
pip install finnhub-python newsapi-python  # Optional but recommended
```

### Step 2: Set API Keys (Optional)
```bash
# Windows
set FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
set NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8

# Linux/Mac
export FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
export NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8
```

**Note:** System works without API keys, but news sentiment won't be available.

### Step 3: Run a Scan
```bash
python lightweight_researcher.py
```

---

## 📊 OUTPUT

### Console Output
```
🐺 WOLF PACK LIGHTWEIGHT RESEARCH SCAN
==================================================
🔍 Analyzing IBRX...
✅ IBRX: 73.2/100 - 🟢 STRONG BUY

📊 TOP OPPORTUNITIES:
--------------------------------------------------
1. IBRX   -  73.2/100 - 🟢 STRONG BUY
   Price: $5.42 | Down 45.8% from high | RSI: 32.1
2. RXRX   -  68.5/100 - 🟡 BUY
   Price: $3.21 | Down 52.3% from high | RSI: 28.4
...

💾 JSON saved: research_output/scan_20260127_143022.json
💾 CSV saved: research_output/scan_20260127_143022.csv
✅ Scan complete!
```

### JSON Export (research_output/scan_*.json)
```json
[
  {
    "symbol": "IBRX",
    "timestamp": "2026-01-27T14:30:22",
    "convergence_score": 73.2,
    "recommendation": "🟢 STRONG BUY",
    "signals": {
      "volume_spike": 18.5,
      "decline": 15.3,
      "rsi_oversold": 20.0,
      "reversal": 10.0,
      "news_sentiment": 9.4
    },
    "data": {
      "current_price": 5.42,
      "high_52w": 10.00,
      "decline_from_high": 45.8,
      "volume_ratio": 1.85,
      "rsi": 32.1,
      "avg_volume": 1234567,
      "recent_volume": 2284149
    }
  }
]
```

### CSV Export (research_output/scan_*.csv)
Easy to open in Excel/Google Sheets:
```
symbol,score,recommendation,price,decline_pct,volume_ratio,rsi,timestamp
IBRX,73.2,🟢 STRONG BUY,5.42,45.8,1.85,32.1,2026-01-27T14:30:22
RXRX,68.5,🟡 BUY,3.21,52.3,2.12,28.4,2026-01-27T14:30:22
```

---

## 🎛️ CUSTOMIZATION

### Use Your Own Stock Universe

Create `data/research_universe.json`:
```json
{
  "symbols": [
    "IBRX", "RXRX", "RNAZ", "SAVA", "ABCL",
    "TSLA", "PLTR", "SNOW", "NET"
  ]
}
```

Or just a simple list:
```json
["IBRX", "RXRX", "TSLA", "PLTR"]
```

### Change Number of Results
```python
researcher = LightweightResearcher()
results = researcher.run_scan(top_n=20)  # Return top 20 instead of 10
```

### Manual Analysis (No Auto-Export)
```python
researcher = LightweightResearcher()
result = researcher.analyze_wounded_prey("IBRX")
print(result)
```

---

## 🔧 ADVANCED USAGE

### Run as a Scheduled Job (Windows)

**Option 1: Task Scheduler**
1. Create `run_research.bat`:
```bat
@echo off
set FINNHUB_API_KEY=d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0
set NEWSAPI_KEY=e6f793dfd61f473786f69466f9313fe8
cd C:\Users\alexp\Desktop\brokkr
python lightweight_researcher.py
```
2. Schedule in Task Scheduler to run daily at 4 AM

**Option 2: PowerShell**
```powershell
# run_research.ps1
$env:FINNHUB_API_KEY = "d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0"
$env:NEWSAPI_KEY = "e6f793dfd61f473786f69466f9313fe8"
cd C:\Users\alexp\Desktop\brokkr
python lightweight_researcher.py
```

### Run on Cloud/VPS

**Replit, PythonAnywhere, AWS Lambda, etc:**
1. Upload `lightweight_researcher.py`
2. Install dependencies: `pip install yfinance pandas finnhub-python newsapi-python`
3. Set environment variables
4. Run: `python lightweight_researcher.py`

**Cron (Linux):**
```bash
# Run daily at 4 AM
0 4 * * * cd /path/to/brokkr && python lightweight_researcher.py >> research.log 2>&1
```

---

## 📈 CONVERGENCE SCORE GUIDE

| Score | Meaning | Action |
|-------|---------|--------|
| 70-100 | 🟢 STRONG BUY | High convergence, multiple signals aligned |
| 50-69 | 🟡 BUY | Good setup, worth watching |
| 30-49 | ⚪ WATCH | Some interest, monitor |
| 0-29 | 🔴 PASS | Not enough signals |

---

## 🔍 SIGNAL BREAKDOWN

Each signal contributes 0-20 points:

1. **Volume Spike (0-20)** - Is trading activity unusually high?
2. **Decline (0-20)** - How much has it fallen from highs? (wounded prey)
3. **RSI Oversold (0-20)** - Is momentum at extremes?
4. **Reversal (0-20)** - Recent bounce attempt?
5. **News Sentiment (0-20)** - What's the news saying?

**Total = 100 points possible**

---

## ⚡ PERFORMANCE

**RAM Usage:** ~200-500MB (vs 8-32GB for full system with Ollama)  
**Speed:** ~5-10 seconds per stock  
**Universe Size:** Recommend 20-50 stocks (takes 2-8 minutes)  
**API Limits:** Respects free tier limits (60 calls/min Finnhub, 100/day NewsAPI)

---

## 🆚 VS FULL SYSTEM

| Feature | Lightweight | Full System |
|---------|-------------|-------------|
| RAM Usage | 0.5GB | 8-32GB |
| Trading | ❌ No | ✅ Paper + Live |
| AI Models | ❌ No Ollama | ✅ Ollama |
| Memory/Learning | ❌ Basic | ✅ Advanced |
| Signals | 5 core | 7+ advanced |
| Output | JSON/CSV | Full logs + dashboards |
| Use Case | Research only | Full trading system |

---

## 🎯 PERFECT FOR

- ✅ Finding opportunities to research manually
- ✅ Running on low-RAM machines
- ✅ Cloud/VPS scanning
- ✅ Daily morning scans (no trading)
- ✅ Exporting to Excel for analysis
- ✅ Learning the wounded prey pattern

---

## 🚫 NOT FOR

- ❌ Automated trading (use full system)
- ❌ Real-time execution
- ❌ Portfolio management
- ❌ Advanced machine learning
- ❌ Trade logging/tracking

---

## 🔑 API KEYS NEEDED

See [YOUR_API_KEYS.md](YOUR_API_KEYS.md) for your keys.

**Required:** None (system works without APIs)  
**Recommended:** Finnhub + NewsAPI (free tiers sufficient)  
**Not Needed:** Alpaca (no trading in this version)

---

## 📚 NEXT STEPS

1. **Test Run:** `python lightweight_researcher.py`
2. **Review Output:** Check `research_output/` folder
3. **Customize Universe:** Edit `data/research_universe.json`
4. **Schedule Daily:** Set up Task Scheduler/cron
5. **Manual Trading:** Use results to make your own trading decisions

---

## 🆘 TROUBLESHOOTING

**"No module named 'yfinance'"**
```bash
pip install yfinance pandas
```

**"No data returned"**
- Check internet connection
- Stock might be delisted/invalid
- Try different symbols

**"Rate limit exceeded"**
- Reduce universe size
- Add delays between API calls
- Upgrade API tier (if needed)

**Need help?**
- Read [SYSTEM_OVERVIEW_SIMPLE.md](SYSTEM_OVERVIEW_SIMPLE.md)
- Check full documentation in [docs/](docs/)

---

**Author:** Wolf Pack Team  
**Version:** 1.0  
**Last Updated:** January 27, 2026
