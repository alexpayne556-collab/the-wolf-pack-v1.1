# 🐺 WOLF PACK - SETUP GUIDE

**How to get the system running on your machine.**

---

## PREREQUISITES

### Required
- **Python 3.12+** (3.10+ might work, but 3.12 recommended)
- **Git** (for cloning the repo)
- **Windows/Mac/Linux** (tested on Windows 11)

### Optional but Recommended
- **VS Code** with GitHub Copilot (how we develop)
- **Ollama** for local AI models (Qwen, Llama)
- **Alpaca Account** for paper trading (free)

---

## STEP 1: CLONE THE REPO

```bash
git clone https://github.com/alexpayne556-collab/the-wolf-pack.git
cd the-wolf-pack
```

---

## STEP 2: SET UP PYTHON ENVIRONMENT

### Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

**If requirements.txt doesn't exist yet (it will), install manually:**

```bash
pip install yfinance
pip install finnhub-python
pip install requests
pip install python-dotenv
pip install alpaca-py
pip install pandas numpy
```

---

## STEP 3: SET UP API KEYS

### Create .env File

Copy the example:
```bash
cp .env.example .env
```

**Or create manually:**
```bash
# .env file
ALPACA_PAPER_KEY_ID=your_paper_key
ALPACA_PAPER_SECRET_KEY=your_paper_secret
FINNHUB_API_KEY=your_finnhub_key
NEWS_API_KEY=your_newsapi_key
```

### Get API Keys (All FREE)

**1. Alpaca (Paper Trading - FREE)**
- Go to: https://alpaca.markets/
- Sign up for paper trading account
- Get API key + secret
- Add to .env

**2. Finnhub (Earnings, Fundamentals - FREE)**
- Go to: https://finnhub.io/
- Sign up for free tier
- Get API key
- Add to .env

**3. NewsAPI (Sentiment Analysis - FREE)**
- Go to: https://newsapi.org/
- Sign up for developer tier (FREE)
- Get API key
- Add to .env

**NEVER commit your .env file to git. It's in .gitignore.**

---

## STEP 4: TEST THE SYSTEM

### Run Scanner

```bash
cd wolfpack
python wolf_pack.py
```

**Expected output:**
- Scans for wounded prey patterns
- Checks 100+ stocks
- Returns convergence scores

**If it works, you'll see:**
```
🐺 WOLF PACK SCANNER v2.0
Running wounded prey detection...
[Stock data, scores, reasoning]
```

### Run Risk Manager

```bash
python services/risk_manager.py
```

**Expected output:**
- Position sizing calculations
- Kelly Criterion examples
- Risk validation

### Run Trading Rules Test

```bash
python services/trading_rules.py
```

**Expected output:**
- 10 Commandments enforcement test
- 4 test scenarios (should all pass/block correctly)

---

## STEP 5: SET UP TRADER BOT (Optional)

**If you want to test paper trading:**

1. Make sure Alpaca keys are in .env
2. Run trader bot:

```bash
python wolf_pack_trader.py
```

**Expected output:**
- Connects to Alpaca paper trading
- Shows account value
- Shows max risk per trade
- Initializes commandments

**The bot won't execute trades unless you enable it in daily_monitor.py**

---

## STEP 6: RUN DAILY WORKFLOW

```bash
python daily_monitor.py
```

**What this does:**
- System health check
- Runs wolf pack scan
- Shows convergence results
- Checks pivotal points
- Shows learning status (if any trades recorded)
- Monitors exits (if positions exist)

**Trade execution is DISABLED by default. You control when to enable.**

---

## COMMON ISSUES

### "Module not found" errors
```bash
pip install <missing-module>
```

### "API key invalid"
- Check .env file syntax
- Make sure keys are correct
- Some APIs need 24h activation

### "No data returned"
- Check internet connection
- Some stocks might not have data
- Try different tickers

### Import errors
Make sure you're in the right directory:
```bash
cd wolfpack  # Most scripts expect to run from here
```

---

## FOLDER STRUCTURE

```
the-wolf-pack/
├── README.md                     # Main documentation
├── CONTRIBUTING.md               # How to contribute
├── SETUP.md                      # This file
├── LICENSE                       # MIT License
├── .gitignore                    # What not to commit
├── .env.example                  # API key template
├── wolfpack/
│   ├── wolf_pack.py              # Core scanner
│   ├── wolf_pack_trader.py       # Automated trader
│   ├── daily_monitor.py          # Daily workflow
│   ├── THE_LEONARD_FILE.md       # Complete documentation
│   └── services/
│       ├── risk_manager.py       # Position sizing
│       ├── trading_rules.py      # 10 Commandments
│       ├── trade_learner.py      # Self-learning
│       ├── pivotal_point_tracker.py  # Livermore patterns
│       └── [other services]
├── data/                         # Data storage (optional)
├── logs/                         # Trade logs
└── docs/                         # Additional documentation
```

---

## NEXT STEPS

### After Setup

1. **Read THE_LEONARD_FILE.md** - Understand the philosophy
2. **Run some scans** - Get familiar with output
3. **Test with paper trading** - No real money
4. **Document what you learn** - Wins AND losses
5. **Join the pack** - Email if you want to contribute

---

## SAFETY REMINDERS

**NEVER:**
- Commit .env file (API keys)
- Share your API keys
- Start with large capital
- Override the system without testing
- Trade real money until you understand the system

**ALWAYS:**
- Start with paper trading
- Test thoroughly
- Document everything
- Follow max 2% risk rule
- Share learnings with pack

---

## SUPPORT

**Issues with setup?**

1. Check this file again
2. Search GitHub Issues
3. Create new issue with details
4. Email: alexpayne556@gmail.com

**We respond to serious inquiries.**

---

## PACK MENTALITY

Remember:
- This is a learning system
- We're testing with real money (small amounts)
- We share wins AND losses
- We build together
- LLHR = Love, Loyalty, Honor, Respect

🐺 **AWOOOO**

---

**Last Updated:** January 18, 2026
