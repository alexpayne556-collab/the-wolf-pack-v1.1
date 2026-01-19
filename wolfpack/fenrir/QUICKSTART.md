🐺 FENRIR V2 - Quick Start Guide

═══════════════════════════════════════════════════════════════

✅ INSTALLATION COMPLETE

All Python files created and packages installed!

═══════════════════════════════════════════════════════════════

📋 NEXT STEPS:

1. CREATE FENRIR OLLAMA MODEL
   
   Open a new terminal and run:
   
   ollama create fenrir -f Modelfile
   
   (If ollama is not recognized, you may need to restart your terminal
   or add Ollama to your PATH)

2. TEST THE SYSTEM
   
   python main.py test
   
   This will verify all systems are working

3. START USING FENRIR

   Morning routine:
   
   python main.py scan              # Find movers
   python main.py holdings          # Check your P&L
   python main.py analyze KTOS      # Deep dive on any stock
   
   Before a trade:
   
   python main.py buy IBRX          # Should I buy this?
   python main.py sell KTOS         # Should I sell this?
   
   After a trade:
   
   python main.py log               # Log your decision
   
   Ask anything:
   
   python main.py ask "Is MU earnings a buy-the-dip setup?"
   python main.py chat              # Interactive mode

═══════════════════════════════════════════════════════════════

📁 FILES CREATED:

Core System:
✅ config.py          - Your holdings and watchlist
✅ market_data.py     - Price/volume data (yfinance)
✅ news_fetcher.py    - News from Finnhub
✅ sec_fetcher.py     - SEC filings (8-K, Form 4)
✅ database.py        - Trade logging (SQLite)
✅ ollama_brain.py    - AI engine (NO GUARDRAILS)
✅ alerts.py          - Notifications
✅ main.py            - CLI commands

Supporting Files:
✅ requirements.txt   - Python packages
✅ .env               - API keys (Finnhub key already added)
✅ Modelfile          - Fenrir personality definition
✅ README.md          - Full documentation
✅ QUICKSTART.md      - This file

Data:
✅ data/              - Directory for database
✅ data/fenrir.db     - SQLite database (auto-created)

═══════════════════════════════════════════════════════════════

🔑 API KEYS:

Finnhub: Already configured in .env
SEC EDGAR: No key needed (public data)
Ollama: Local model (no API)

═══════════════════════════════════════════════════════════════

⚠️ KNOWN ISSUES:

1. If "ollama create" doesn't work:
   - Restart your terminal
   - Or use full path: C:\Users\alexp\AppData\Local\Programs\Ollama\ollama.exe
   - Or create the model from Ollama's UI

2. If Ollama responses include disclaimers:
   - The Fenrir model adds the "NO GUARDRAILS" system prompt
   - Make sure you created the fenrir model (step 1 above)
   - Check with: ollama list (should show "fenrir" model)

3. Desktop notifications might not work:
   - Console alerts will always work
   - win10toast was installed but may need pywin32 setup
   - Not critical - console output is the main interface

═══════════════════════════════════════════════════════════════

🐺 WHAT FENRIR DOES:

✅ Real-time alerts when your stocks move >3%
✅ Auto-fetch catalysts (news + SEC filings)
✅ AI opinions via Ollama (NO "not financial advice" disclaimers)
✅ Decision logging (track what YOU actually did)
✅ Pattern learning (what works for YOUR style)

This is IRREPLACEABLE data you can't recreate later.

═══════════════════════════════════════════════════════════════

🎯 CURRENT SCAN RESULTS:

Based on the test scan just now:

Holdings Moving:
• MU: +5.25% ($354.30) - Micron up big
• KTOS: +5.80% ($131.79) - Kratos Defense up big
• SLV: -3.22% ($80.64) - Silver ETF down

These are above your 3% threshold for holdings.

═══════════════════════════════════════════════════════════════

💡 TIP: Run "python main.py analyze MU" to get Fenrir's full take
on why MU is up 5% today (news, SEC filings, sector context, and
AI opinion on what to do).

═══════════════════════════════════════════════════════════════

Questions? Check README.md for full documentation.

The wolf pack is ready. 🐺
