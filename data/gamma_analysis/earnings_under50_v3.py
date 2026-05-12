"""V3: Finnhub earnings phase with proper rolling-window rate limiter.

Tracks last-60s call timestamps; sleeps just enough to stay under 60/min.
Reuses SEC insider scan from v2 (cached output if present).
"""
import json, re, time, csv, requests
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
import datetime as dt
from xml.etree import ElementTree as ET
from pathlib import Path

OUT = Path('data/gamma_analysis')
KEY = 'd5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0'
HDRS = {'User-Agent': 'wolf-pack-research backtest@example.com'}
FN = requests.Session(); FN.headers.update(HDRS)
SEC = requests.Session(); SEC.headers.update(HDRS)

# Rolling rate limiter
class RateLimiter:
    def __init__(self, max_calls=55, window=60):
        self.max = max_calls; self.window = window; self.calls = deque()
    def wait(self):
        now = time.time()
        while self.calls and now - self.calls[0] > self.window:
            self.calls.popleft()
        if len(self.calls) >= self.max:
            sleep_for = self.window - (now - self.calls[0]) + 0.1
            time.sleep(max(0, sleep_for))
            now = time.time()
            while self.calls and now - self.calls[0] > self.window:
                self.calls.popleft()
        self.calls.append(time.time())

FN_LIMIT = RateLimiter(max_calls=55, window=60)

# --- 1. Earnings calendar (with retry-on-429) ---
for attempt in range(8):
    FN_LIMIT.wait()
    resp = FN.get(f'https://finnhub.io/api/v1/calendar/earnings?from=2026-05-13&to=2026-05-14&token={KEY}', timeout=30)
    if resp.status_code == 200:
        r = resp.json(); break
    print(f'    calendar attempt {attempt+1}: status={resp.status_code}; sleeping', flush=True)
    time.sleep(5 + attempt * 3)
else:
    raise RuntimeError('cannot fetch calendar')
er = r.get('earningsCalendar', [])
tickers = sorted({e['symbol'] for e in er if e.get('symbol')})
if not tickers:
    raise RuntimeError(f'calendar returned 0 tickers; full response keys: {list(r.keys())}')
emap = {}
for e in er:
    s = e.get('symbol')
    if s: emap.setdefault(s, []).append({'date': e.get('date'), 'hour': e.get('hour')})
print(f'[1] earnings May 13-14: {len(tickers)} unique tickers', flush=True)

# --- 2. Prices ---
print(f'[2] yfinance batch quote…', flush=True)
t0 = time.time()
df = yf.download(' '.join(tickers), period='3d', interval='1d', group_by='ticker',
                 auto_adjust=False, progress=False, threads=True)
prices = {}
if isinstance(df.columns, pd.MultiIndex):
    for t in tickers:
        try:
            sub = df[t].dropna(how='all')
            if len(sub) and 'Close' in sub.columns:
                prices[t] = float(sub['Close'].iloc[-1])
        except Exception:
            continue
print(f'    {len(prices)}/{len(tickers)} priced in {time.time()-t0:.0f}s', flush=True)
under50 = sorted([t for t in tickers if prices.get(t) is not None and 0 < prices[t] < 50])
print(f'[3] under $50: {len(under50)}', flush=True)

# --- 4a. SEC insider buys (with local CIK cache) ---
_CACHE = OUT / 'sec_company_tickers.json'
if _CACHE.exists() and _CACHE.stat().st_size > 100000:
    sec_map = json.loads(_CACHE.read_text())
    print(f'[4a] loaded SEC ticker map from cache: {len(sec_map)} entries', flush=True)
else:
    raise RuntimeError(f'no SEC cache at {_CACHE}; run prefetch first')
t2cik = {row['ticker'].upper(): str(row['cik_str']).zfill(10) for row in sec_map.values()}
cutoff_60 = (dt.date(2026, 5, 12) - dt.timedelta(days=60)).isoformat()

def list_form4_in_60d(cik):
    try:
        r = SEC.get(f'https://data.sec.gov/submissions/CIK{cik}.json', timeout=15)
        if r.status_code != 200: return []
        recent = r.json().get('filings', {}).get('recent', {})
        forms = recent.get('form', []); dates = recent.get('filingDate', []); accs = recent.get('accessionNumber', [])
        return [(dates[i], accs[i]) for i, f in enumerate(forms) if f == '4' and dates[i] >= cutoff_60]
    except Exception:
        return []

def is_purchase(cik, acc):
    acc_clean = acc.replace('-', '')
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}"
    try:
        idx = SEC.get(base + '/', timeout=15)
        if idx.status_code != 200: return False
        m = re.search(r'href="([^"]+\.xml)"', idx.text, re.IGNORECASE)
        if not m: return False
        xml_url = m.group(1)
        if not xml_url.startswith('http'):
            xml_url = ('https://www.sec.gov' + xml_url) if xml_url.startswith('/') else f"{base}/{xml_url}"
        r = SEC.get(xml_url, timeout=15)
        if r.status_code != 200: return False
        if '<transactionCode>P</transactionCode>' not in r.text: return False
        try: root = ET.fromstring(r.text)
        except ET.ParseError: return False
        for tx in root.iter('nonDerivativeTransaction'):
            for code in tx.iter('transactionCode'):
                if (code.text or '').strip() == 'P': return True
        return False
    except Exception:
        return False

def insider_count_for(t):
    cik = t2cik.get(t)
    if not cik: return 0
    filings = list_form4_in_60d(cik)
    return sum(1 for fd, acc in filings if is_purchase(cik, acc))

print(f'[4a] SEC scan for {len(under50)} tickers, 8 workers', flush=True)
insider_counts = {}
t0 = time.time(); last = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(insider_count_for, t): t for t in under50}
    for i, fut in enumerate(as_completed(futs), 1):
        insider_counts[futs[fut]] = fut.result()
        if time.time() - last > 5:
            print(f'    SEC: {i}/{len(under50)} ({i/(time.time()-t0):.1f}/s)', flush=True); last = time.time()
print(f'    SEC done in {time.time()-t0:.0f}s — names with buys: {sum(1 for v in insider_counts.values() if v>0)}', flush=True)

# --- 4b. Finnhub earnings with rolling rate limiter ---
print(f'[4b] Finnhub earnings for {len(under50)} tickers, rolling 55/min', flush=True)
earnings_h = {}
t0 = time.time()
for i, t in enumerate(under50, 1):
    FN_LIMIT.wait()
    try:
        r = FN.get('https://finnhub.io/api/v1/stock/earnings',
                   params={'symbol': t, 'token': KEY}, timeout=15)
        if r.status_code == 200:
            j = r.json()
            if isinstance(j, list):
                rows = [x for x in j if x.get('symbol') == t] or j
                rows = sorted(rows, key=lambda x: x.get('period') or '', reverse=True)
                earnings_h[t] = rows[:2]
            else: earnings_h[t] = []
        elif r.status_code == 429:
            time.sleep(15)
            earnings_h[t] = []
        else:
            earnings_h[t] = []
    except Exception:
        earnings_h[t] = []
    if i % 25 == 0:
        print(f'    Finnhub: {i}/{len(under50)} ({time.time()-t0:.0f}s)', flush=True)
print(f'    Finnhub done in {time.time()-t0:.0f}s', flush=True)

# --- 5. Build + rank + emit ---
rows = []
for t in under50:
    eh = earnings_h.get(t, [])
    sp1 = eh[0].get('surprisePercent') if len(eh) >= 1 else None
    sp2 = eh[1].get('surprisePercent') if len(eh) >= 2 else None
    beat1 = (sp1 > 0) if sp1 is not None else None
    beat2 = (sp2 > 0) if sp2 is not None else None
    n_buys = insider_counts.get(t, 0)
    has_buys = n_buys > 0
    both_beat = (beat1 is True) and (beat2 is True)
    rank = (
        1 if (both_beat and has_buys) else 0,
        1 if both_beat else 0,
        1 if (beat1 is True and has_buys) else 0,
        n_buys,
        (sp1 if sp1 is not None else -1e9),
    )
    rows.append({
        'ticker': t, 'price': prices[t],
        'er_date': emap.get(t, [{}])[0].get('date'),
        'er_hour': emap.get(t, [{}])[0].get('hour'),
        'beat_q': beat1, 'sp_q': sp1, 'beat_prev_q': beat2, 'sp_prev_q': sp2,
        'insider_buys_60d': n_buys, 'rank': rank,
    })
rows.sort(key=lambda r: r['rank'], reverse=True)

# Save CSV first (so the data is preserved even if printing crashes)
with open(OUT / 'earnings_may13_14.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['rank','ticker','price','er_date','er_hour','beat_last_q','sp_last_q','beat_prev_q','sp_prev_q','insider_buys_60d'])
    for i, r in enumerate(rows, 1):
        w.writerow([i, r['ticker'], r['price'], r['er_date'], r['er_hour'],
                    r['beat_q'], r['sp_q'], r['beat_prev_q'], r['sp_prev_q'], r['insider_buys_60d']])
print(f'\n{len(rows)} rows -> data/gamma_analysis/earnings_may13_14.csv', flush=True)

# Tier 1 first
tier1 = [r for r in rows if r['rank'][0] == 1]
print(f'\n*** TIER 1: beat BOTH last 2 quarters AND insider buying in last 60d — {len(tier1)} names ***')
for r in tier1:
    print(f"  {r['ticker']:<6} ${r['price']:>6.2f}  Q-beats: {r['sp_q']:+5.1f}% / {r['sp_prev_q']:+5.1f}%  buys: {r['insider_buys_60d']}  er: {r['er_date']} {r['er_hour']}")

# Print full table (header first)
print()
print(f"{'#':>3} {'ticker':<6} {'price':>7}  {'er_date':<10} {'time':<3}  {'beat_Q':>6} {'sp%_Q':>9}  {'beat_PQ':>7} {'sp%_PQ':>9}  {'buys_60d':>8}")
print('-' * 99)
for i, r in enumerate(rows, 1):
    bq = '✓' if r['beat_q'] is True else ('✗' if r['beat_q'] is False else '?')
    bp = '✓' if r['beat_prev_q'] is True else ('✗' if r['beat_prev_q'] is False else '?')
    sp1s = f"{r['sp_q']:+.1f}%" if r['sp_q'] is not None else '   —   '
    sp2s = f"{r['sp_prev_q']:+.1f}%" if r['sp_prev_q'] is not None else '   —   '
    print(f"{i:>3} {r['ticker']:<6} ${r['price']:>6.2f}  {r['er_date'] or '':<10} {r['er_hour'] or '':<3}  {bq:>6} {sp1s:>9}  {bp:>7} {sp2s:>9}  {r['insider_buys_60d']:>8}")
