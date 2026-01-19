# 🐺 Wolf Pack News Tracker

## Purpose

Capture ALL SEC filings, categorize events, track price reactions.
No hardcoded tickers. Events drive discovery.

After 30 days, we'll know what ACTUALLY moves stocks vs what retail ignores.

---

## Setup

1. **Create database**:
```bash
python database_setup.py
```

2. **Collect first batch**:
```bash
python daily_collector.py
```

3. **Wait 1+ days, then update returns**:
```bash
python return_updater.py
```

4. **Analyze patterns** (after 10+ events have returns):
```bash
python pattern_analyzer.py
```

---

## Daily Workflow

**After market close (5 PM ET)**:
```bash
python daily_collector.py
python return_updater.py
```

**Anytime (to see patterns)**:
```bash
python pattern_analyzer.py
```

---

## What It Tracks

### Event Types:
- **contract**: Dollar-denominated agreements, awards
- **partnership**: Collaborations, joint ventures
- **fda**: FDA approvals, clinical trial results
- **earnings**: Quarterly results
- **insider_buy**: Form 4 insider purchases
- **insider_sell**: Form 4 insider sales
- **offering**: Dilution events
- **acquisition**: M&A activity
- **analyst**: Upgrades, downgrades
- **other**: Everything else

### Metrics:
- Price at event
- Volume vs 20-day average
- Market cap
- Returns at 1d, 3d, 5d, 10d

---

## Questions We'll Answer

After 30 days of data:

1. **What event types have highest average return?**
   - Are contracts better than partnerships?
   - Do FDA approvals really move stocks?

2. **Do small caps react more than large caps?**
   - Is there a market cap sweet spot?

3. **Does volume matter?**
   - Do 5x volume events outperform 2x volume?

4. **What's the continuation rate?**
   - If stock is up 1d, what % continue up 5d?

5. **Which sectors react most?**
   - Do biotech FDA approvals outperform defense contracts?

---

## Database Schema

**events table**:
- Stores every SEC filing we track
- Records price, volume, market cap at event time
- Returns calculated after X days pass

**tickers table**:
- Auto-populated from events
- Stores fundamentals (sector, industry, float, short interest)

---

## Output Examples

**By Event Type**:
```
event_type       count  avg_return  win_rate  big_winner_rate
contract         45     +4.2%       58.3%     12.4%
fda              23     +8.7%       65.2%     26.1%
partnership      34     +1.8%       52.9%     5.9%
offering         18     -2.3%       38.9%     0.0%
```

**By Market Cap**:
```
cap_bucket       count  avg_return  win_rate
Micro (<100M)    67     +6.3%       61.2%
Small (100-500M) 89     +3.8%       55.1%
Mid (500M-2B)    45     +2.1%       51.1%
Large (>2B)      23     +0.9%       47.8%
```

---

## Notes

- **Rate limiting**: Sleeps 0.5s between API calls
- **Deduplication**: Same event on same day for same ticker = ignored
- **Missing data**: If yfinance can't fetch ticker, event is skipped
- **Returns update**: Run daily to fill in returns as days pass

---

## Future Enhancements

1. Add float data (track low float movers)
2. Parse 8-K form items (1.01, 2.01, etc.)
3. Track short interest changes
4. Add sentiment analysis on headlines
5. Export to CSV for ML training

---

🐺 LLHR - Let the data reveal the truth
