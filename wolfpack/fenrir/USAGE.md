# 🐺 FENRIR V2 - USAGE GUIDE

## Quick Start

**EASIEST WAY:** Just double-click `fenrir.bat` to start chat mode!

Or from command line:
```bash
cd c:\Users\alexp\Desktop\brokkr\wolfpack\fenrir
python main.py chat
```

Then type naturally:
- "how's ibrx doing"
- "show my positions"
- "what's moving today"
- "should i buy ktos"
- "what do i need to know"
- "any catalysts coming up"

## Secretary Features

### Morning Routine (6 AM)
```bash
python main.py briefing
```
Shows: Pre-market gaps, overnight news, today's catalysts, risk status, day trades available

### Market Open (9:30 AM)
```bash
python main.py scan
```
Finds big movers and volume spikes

### Midday Checks
```bash
python main.py holdings  # Check P/L
python main.py risk      # PDT usage, concentration
python main.py levels    # Support/resistance alerts
```

### Market Close (4:15 PM)
```bash
python main.py eod
```
Today's P/L, what moved and why, character changes, AH preview

### After Hours (5-8 PM)
```bash
python main.py afterhours
```
AH moves >3%, news dropped after 4 PM

### Anytime
```bash
python main.py catalysts      # Upcoming earnings/events
python main.py correlation TICKER  # Sympathy plays
python main.py analyze TICKER # Deep dive on ticker
python main.py missed        # Analyze missed opportunities
```

## Natural Language Examples

The chat mode understands:

**Check positions:**
- "show my positions"
- "how's my portfolio"
- "holdings"

**Check specific ticker:**
- "how's ibrx doing"
- "check ktos"
- "what about mu"

**Market scanning:**
- "what's moving today"
- "scan the market"
- "any big movers"

**Buy/sell decisions:**
- "should i buy ktos"
- "should i sell ibrx"
- "buy mu?"

**Risk management:**
- "risk check"
- "how many day trades"
- "am i too concentrated"

**Pre-market:**
- "any gaps"
- "premarket scan"
- "check premarket"

**After hours:**
- "after hours"
- "anything moving ah"
- "check afterhours"

**Daily info:**
- "what do i need to know"
- "morning briefing"
- "give me summary"

**Catalysts:**
- "any earnings coming"
- "catalysts this week"
- "what events coming up"

**Technical levels:**
- "show levels"
- "levels for ibrx"
- "support and resistance"

**End of day:**
- "eod report"
- "today summary"
- "how'd we do today"

**Correlations:**
- "sympathy plays"
- "what moves with mu"
- "correlation for ktos"

**General questions:**
Just ask normally! Fenrir will answer:
- "what's your read on the market"
- "thoughts on nuclear stocks"
- "what do you think about tech"

## Workflow Tips

1. **Start your day:** `python main.py briefing`
2. **During market:** Keep chat mode open, type naturally
3. **End your day:** `python main.py eod`
4. **Check after hours:** `python main.py afterhours`

## Notifications

Fenrir will send desktop notifications for:
- URGENT (with sound): Positions bleeding >5%
- WARNING: News on holdings, AH moves >3%
- INFO: Volume spikes, level approaches

(Requires win10toast - already installed)

## Database

All data stored in `data/fenrir.db`:
- alerts - All alerts generated
- trades - Trade log
- patterns - Pattern learning
- catalysts - Catalyst events
- stock_state - Adaptive tracking state
- intraday_ticks - Within-day price action
- daily_summary - EOD snapshots

## Tips for Typing

Since you mentioned typing issues - chat mode is very forgiving:
- No need for exact commands
- Partial words work ("pos" = positions)
- Tickers anywhere in sentence
- Case doesn't matter
- Misspellings often work

Examples that all work:
- "shw poisions" → shows holdings
- "hws ibrx" → analyzes IBRX
- "buy ktos?" → buy check on KTOS
- "whats mvoing" → scans movers

Just type naturally and Fenrir will figure it out!

## Future Enhancements

Coming soon:
- SMS alerts via Twilio for critical events
- Auto-run briefing at 6 AM (scheduled task)
- Auto-run EOD at 4:15 PM
- Voice commands (speech recognition)
- Mobile app integration
