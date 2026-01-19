# 🐺 FENRIR V2 - QUICK START GUIDE

**Your AI trading secretary is ready!**

## Today - Right Now

Run your first command:

```powershell
cd c:\Users\alexp\Desktop\brokkr\wolfpack\fenrir
python fenrir_secretary.py briefing
```

This shows:
- Pre-market gaps on your positions
- Overnight news
- Risk status
- Day trades available
- What to focus on today

## Daily Commands

**Morning (6 AM):**
```powershell
python fenrir_secretary.py briefing
```

**During Market:**
```powershell
python main.py scan              # Find movers
python main.py holdings          # Check P/L
python fenrir_secretary.py risk  # Risk check
```

**Market Close (4:15 PM):**
```powershell
python fenrir_secretary.py eod
```

**After Hours (5-8 PM):**
```powershell
python fenrir_secretary.py afterhours
```

**Anytime:**
```powershell
python fenrir_secretary.py catalysts     # Upcoming events
python fenrir_secretary.py levels IBRX   # Key levels
python fenrir_secretary.py correlation MU # Sympathy plays
```

## All Available Commands

### Secretary Commands (fenrir_secretary.py)
- `risk` - PDT usage, concentration, position sizing
- `premarket` - Pre-market gaps
- `afterhours` - After-hours moves and news
- `briefing` - Morning summary
- `catalysts` - Upcoming earnings/events
- `levels [TICKER]` - Support/resistance
- `eod` - End of day report
- `correlation [TICKER]` - Sympathy plays
- `missed` - Analyze missed opportunities

### Main Commands (main.py)
- `test` - Check system is working
- `holdings` - Show positions with live P/L
- `scan` - Scan market for movers
- `analyze TICKER` - Deep dive on ticker
- `buy TICKER` - Should I buy this?
- `sell TICKER` - Should I sell this?
- `chat` - Interactive mode (Ollama required)

## Examples

**Check risk before trading:**
```powershell
python fenrir_secretary.py risk
```
Shows: 0/3 day trades used, position concentration, warnings

**See what moved yesterday:**
```powershell
python fenrir_secretary.py eod
```
Shows: P/L per position, news, what to watch after hours

**Check for upcoming catalysts:**
```powershell
python fenrir_secretary.py catalysts
```
Shows: Earnings dates, ex-dividend dates for next 2 weeks

**Find sympathy plays:**
```powershell
python fenrir_secretary.py correlation MU
```
Shows: When MU moves, watch NVDA, AMD, SMCI

**Analyze a ticker:**
```powershell
python main.py analyze IBRX
```
Shows: Price, volume, news, Fenrir's opinion

## Your Portfolio

Current holdings ($1,450.13 value, +9.31% P/L):
- KTOS: 2.717 shares @ $117.83
- IBRX: 37.082 shares @ $4.69
- MU: 1.268 shares @ $334.48
- UUUU: 3 shares @ $22.09
- BBAI: 7.686 shares @ $6.50
- UEC: 2 shares @ $17.29

Cash: $279.38 across 2 brokers
Day trades: 0/3 used this week

## Quick Launch

Double-click `fenrir.bat` to see the menu.

Or create a desktop shortcut to:
```
c:\Users\alexp\Desktop\brokkr\wolfpack\fenrir\fenrir.bat
```

## Troubleshooting

**"Ollama not running":**
- Chat mode needs Ollama
- Secretary commands work without it
- To fix: Run `ollama serve` in another terminal

**"ModuleNotFoundError":**
- Run: `pip install yfinance requests python-dotenv ollama win10toast`

**Market data slow:**
- Normal - fetching real-time data
- First run caches ticker list
- Subsequent runs faster

**Want faster commands:**
Use fenrir_secretary.py instead of main.py - it's optimized for speed.

## Tips

1. **Start your day:** `python fenrir_secretary.py briefing`
2. **Quick risk check:** `python fenrir_secretary.py risk`
3. **See what's moving:** `python main.py scan`
4. **End your day:** `python fenrir_secretary.py eod`
5. **Check after hours:** `python fenrir_secretary.py afterhours`

## What's Different About Fenrir

❌ **NOT** a price tracker (prices available anytime via yfinance)  
❌ **NOT** just alerts (you need opinions, not just notifications)  
✅ **IS** a proactive secretary that tells you what you NEED to know  
✅ **IS** adaptive (bleeding positions checked every 2 minutes)  
✅ **IS** comprehensive (10 secretary features)  
✅ **IS** using your real portfolio (not demo/paper)

## Remember

This is **REAL MONEY**. Every decision matters.

Fenrir tracks your:
- $1,450 portfolio
- 3 day trades/week limit (PDT)
- Position concentration (max 35% per stock)
- After-hours moves (overnight risk)
- Upcoming catalysts (earnings surprises)

Use it. Don't let it collect dust.

---

🐺 **Start with: `python fenrir_secretary.py briefing`**

LLHR - Love, Laughter, Honor, Respect
