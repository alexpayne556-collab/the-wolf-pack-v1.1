"""Earnings tomorrow (May 13) or Thursday (May 14), under $50, with last 2 quarters' beats + insider buys."""
import requests, time, csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf

KEY = 'd5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0'
SESS = requests.Session()
SESS.headers.update({'User-Agent':'wolf-pack-research backtest'})

# 1. Earnings calendar May 13-14
r = SESS.get(f'https://finnhub.io/api/v1/calendar/earnings?from=2026-05-13&to=2026-05-14&token={KEY}', timeout=30).json()
er = r.get('earningsCalendar', [])
tickers = sorted({e['symbol'] for e in er if e.get('symbol')})
emap = {}
for e in er:
    s = e.get('symbol')
    if s: emap.setdefault(s, []).append({'date': e.get('date'), 'hour': e.get('hour')})
print(f'[1] earnings May 13-14: {len(er)} entries / {len(tickers)} unique tickers')

# 2. Prices via yfinance batch (much faster than per-ticker Finnhub)
print(f'[2] yfinance batch quote for {len(tickers)} tickers…')
t0 = time.time()
df = yf.download(' '.join(tickers), period='3d', interval='1d', group_by='ticker',
                 auto_adjust=False, progress=False, threads=True)
import pandas as pd
prices = {}
if isinstance(df.columns, pd.MultiIndex):
    for t in tickers:
        try:
            sub = df[t].dropna(how='all')
            if len(sub) and 'Close' in sub.columns:
                prices[t] = float(sub['Close'].iloc[-1])
        except Exception:
            continue
print(f'    got prices for {len(prices)}/{len(tickers)} in {time.time()-t0:.1f}s')

under50 = [t for t in tickers if prices.get(t) is not None and 0 < prices[t] < 50]
print(f'[3] under $50: {len(under50)}')

# 3. For each ticker under $50, fetch last 2 quarterly earnings + insider buys (Finnhub)
def earnings_history(t):
    try:
        r = SESS.get('https://finnhub.io/api/v1/stock/earnings',
                     params={'symbol': t, 'token': KEY}, timeout=15)
        if r.status_code == 429:
            time.sleep(2); return earnings_history(t)
        if r.status_code != 200: return []
        j = r.json()
        if not isinstance(j, list): return []
        rows = [x for x in j if x.get('symbol') == t]
        if not rows: rows = j
        rows = sorted(rows, key=lambda x: x.get('period') or '', reverse=True)
        return rows[:2]
    except Exception:
        return []

def insider_buys_60d(t):
    try:
        r = SESS.get('https://finnhub.io/api/v1/stock/insider-transactions',
                     params={'symbol': t, 'token': KEY}, timeout=15)
        if r.status_code == 429:
            time.sleep(3); return insider_buys_60d(t)
        if r.status_code != 200: return []
        d = r.json().get('data', [])
        import datetime as dt
        cutoff = (dt.date.today() - dt.timedelta(days=60)).isoformat()
        return [x for x in d if x.get('transactionCode') == 'P' and (x.get('filingDate') or '') >= cutoff]
    except Exception:
        return []

print(f'[4] fetching Finnhub earnings + insider for {len(under50)} tickers (pacing ~1/s)')
results = {}
t0 = time.time()
# Single worker — sustained ~57/min, safely under 60/min cap (2 endpoints per ticker = 2 calls)
for i, t in enumerate(under50, 1):
    deadline = t0 + i * 2.1  # 2 calls per ticker, 1.05s each
    eh = earnings_history(t); ib = insider_buys_60d(t)
    results[t] = {'earnings': eh, 'insider_buys': ib}
    if i % 20 == 0:
        print(f'    {i}/{len(under50)}  elapsed={time.time()-t0:.0f}s', flush=True)
    now = time.time()
    if now < deadline: time.sleep(deadline - now)
print(f'    done in {time.time()-t0:.0f}s')

# 4. Build sorted table
rows = []
for t in under50:
    r = results.get(t, {})
    eh = r.get('earnings', [])
    ib = r.get('insider_buys', [])
    sp1 = eh[0].get('surprisePercent') if len(eh) >= 1 else None
    sp2 = eh[1].get('surprisePercent') if len(eh) >= 2 else None
    beat1 = (sp1 > 0) if sp1 is not None else None
    beat2 = (sp2 > 0) if sp2 is not None else None
    n_buys = len(ib)
    has_buys = n_buys > 0
    both_beat = (beat1 == True) and (beat2 == True)
    rank = (
        1 if (both_beat and has_buys) else 0,    # tier 1
        1 if both_beat else 0,                    # tier 2
        1 if (beat1 == True and has_buys) else 0,  # tier 3
        n_buys,
        (sp1 if sp1 is not None else -1e9),
    )
    rows.append({
        'ticker': t, 'price': prices[t],
        'er_date': emap.get(t, [{}])[0].get('date'),
        'er_hour': emap.get(t, [{}])[0].get('hour'),
        'beat_q': beat1, 'sp_q': sp1,
        'beat_prev_q': beat2, 'sp_prev_q': sp2,
        'insider_buys_60d': n_buys, 'rank': rank,
    })
rows.sort(key=lambda r: r['rank'], reverse=True)

# 5. Print
print('\n=== EARNINGS MAY 13-14, PRICE < $50 ===')
print(f"{'#':>3} {'ticker':<6} {'price':>7}  {'er_date':<10} {'time':<3}  {'beat_Q':>6} {'sp%_Q':>9}  {'beat_PQ':>7} {'sp%_PQ':>9}  {'buys_60d':>8}")
print('-'*99)
for i, r in enumerate(rows, 1):
    bq = '✓' if r['beat_q'] == True else ('✗' if r['beat_q'] == False else '?')
    bp = '✓' if r['beat_prev_q'] == True else ('✗' if r['beat_prev_q'] == False else '?')
    sp1 = f"{r['sp_q']:+.1f}%" if r['sp_q'] is not None else '   —   '
    sp2 = f"{r['sp_prev_q']:+.1f}%" if r['sp_prev_q'] is not None else '   —   '
    print(f"{i:>3} {r['ticker']:<6} ${r['price']:>6.2f}  {r['er_date'] or '':<10} {r['er_hour'] or '':<3}  {bq:>6} {sp1:>9}  {bp:>7} {sp2:>9}  {r['insider_buys_60d']:>8}")

# 6. Save full CSV
with open('data/gamma_analysis/earnings_may13_14.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['rank','ticker','price','er_date','er_hour','beat_last_q','sp_last_q','beat_prev_q','sp_prev_q','insider_buys_60d'])
    for i, r in enumerate(rows, 1):
        w.writerow([i, r['ticker'], r['price'], r['er_date'], r['er_hour'],
                    r['beat_q'], r['sp_q'], r['beat_prev_q'], r['sp_prev_q'], r['insider_buys_60d']])
print(f'\n{len(rows)} rows -> data/gamma_analysis/earnings_may13_14.csv')

tier1 = [r for r in rows if r['rank'][0] == 1]
print(f'\n*** TIER 1: beat BOTH last 2 quarters AND insider buying in last 60 days — {len(tier1)} names ***')
for r in tier1:
    print(f"  {r['ticker']:<6} ${r['price']:>6.2f}  Q-beats: {r['sp_q']:+5.1f}% / {r['sp_prev_q']:+5.1f}%  insider_buys: {r['insider_buys_60d']}  er: {r['er_date']} {r['er_hour']}")
