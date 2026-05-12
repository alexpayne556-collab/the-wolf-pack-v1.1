"""Earnings May 13-14, under $50: split workload across SEC EDGAR (insider) + Finnhub (earnings).

Insider buys via SEC EDGAR (no shared rate limit with Finnhub):
  ticker -> CIK -> submissions JSON -> Form 4 filings in last 60d -> XML parse for transactionCode=P

Earnings beat history via Finnhub /stock/earnings (60/min cap, 1 worker @ 1.1s pacing).
"""
import json, re, time, csv, requests
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

# --- 1. Earnings calendar May 13-14 ---
r = FN.get(f'https://finnhub.io/api/v1/calendar/earnings?from=2026-05-13&to=2026-05-14&token={KEY}', timeout=30).json()
er = r.get('earningsCalendar', [])
tickers = sorted({e['symbol'] for e in er if e.get('symbol')})
emap = {}
for e in er:
    s = e.get('symbol')
    if s: emap.setdefault(s, []).append({'date': e.get('date'), 'hour': e.get('hour')})
print(f'[1] earnings May 13-14: {len(tickers)} unique tickers', flush=True)

# --- 2. Prices (yfinance batch) ---
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

# --- 4a. SEC EDGAR insider buys (last 60 days) ---
print(f'[4a] SEC ticker->CIK map', flush=True)
_CIK_CACHE = OUT / 'sec_company_tickers.json'
if _CIK_CACHE.exists() and _CIK_CACHE.stat().st_size > 100000:
    sec_map = json.loads(_CIK_CACHE.read_text())
else:
    for attempt in range(5):
        try:
            r = SEC.get('https://www.sec.gov/files/company_tickers.json', timeout=20)
            sec_map = r.json()
            _CIK_CACHE.write_text(r.text)
            break
        except Exception as e:
            print(f'    sec map fetch attempt {attempt+1} failed: {e}', flush=True)
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError('cannot load SEC company_tickers.json')
t2cik = {row['ticker'].upper(): str(row['cik_str']).zfill(10) for row in sec_map.values()}
cutoff_60 = (dt.date(2026, 5, 12) - dt.timedelta(days=60)).isoformat()
print(f'    insider-buys cutoff: {cutoff_60}', flush=True)

def list_form4_in_60d(cik):
    try:
        r = SEC.get(f'https://data.sec.gov/submissions/CIK{cik}.json', timeout=15)
        if r.status_code != 200: return []
        recent = r.json().get('filings', {}).get('recent', {})
        forms = recent.get('form', [])
        dates = recent.get('filingDate', [])
        accs = recent.get('accessionNumber', [])
        out = []
        for i, f in enumerate(forms):
            if f == '4' and dates[i] >= cutoff_60:
                out.append((dates[i], accs[i]))
        return out
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
                if (code.text or '').strip() == 'P':
                    return True
        return False
    except Exception:
        return False

def insider_count_for(t):
    cik = t2cik.get(t)
    if not cik: return 0
    filings = list_form4_in_60d(cik)
    count = 0
    for fd, acc in filings:
        if is_purchase(cik, acc): count += 1
    return count

print(f'[4a] SEC scan for {len(under50)} tickers, 8 workers', flush=True)
insider_counts = {}
t0 = time.time(); last = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(insider_count_for, t): t for t in under50}
    for i, fut in enumerate(as_completed(futs), 1):
        insider_counts[futs[fut]] = fut.result()
        if time.time() - last > 5:
            print(f'    SEC: {i}/{len(under50)} ({i/(time.time()-t0):.1f}/s)', flush=True)
            last = time.time()
print(f'    SEC done in {time.time()-t0:.0f}s — names with buys: {sum(1 for v in insider_counts.values() if v>0)}', flush=True)

# --- 4b. Finnhub earnings history (last 2 quarters) ---
print(f'[4b] Finnhub earnings for {len(under50)} tickers, 1 worker @ 1.1s pacing', flush=True)
earnings_h = {}
t0 = time.time()
for i, t in enumerate(under50, 1):
    deadline = t0 + i * 1.1
    try:
        r = FN.get('https://finnhub.io/api/v1/stock/earnings',
                   params={'symbol': t, 'token': KEY}, timeout=15)
        if r.status_code == 429:
            time.sleep(5)
            r = FN.get('https://finnhub.io/api/v1/stock/earnings',
                       params={'symbol': t, 'token': KEY}, timeout=15)
        if r.status_code == 200:
            j = r.json()
            if isinstance(j, list):
                rows = [x for x in j if x.get('symbol') == t] or j
                rows = sorted(rows, key=lambda x: x.get('period') or '', reverse=True)
                earnings_h[t] = rows[:2]
            else:
                earnings_h[t] = []
        else:
            earnings_h[t] = []
    except Exception:
        earnings_h[t] = []
    if i % 50 == 0:
        print(f'    Finnhub: {i}/{len(under50)} ({time.time()-t0:.0f}s)', flush=True)
    now = time.time()
    if now < deadline:
        time.sleep(deadline - now)
print(f'    Finnhub done in {time.time()-t0:.0f}s', flush=True)

# --- 5. Build, rank, print ---
rows = []
for t in under50:
    eh = earnings_h.get(t, [])
    sp1 = eh[0].get('surprisePercent') if len(eh) >= 1 else None
    sp2 = eh[1].get('surprisePercent') if len(eh) >= 2 else None
    beat1 = (sp1 > 0) if sp1 is not None else None
    beat2 = (sp2 > 0) if sp2 is not None else None
    n_buys = insider_counts.get(t, 0)
    has_buys = n_buys > 0
    both_beat = (beat1 == True) and (beat2 == True)
    rank = (
        1 if (both_beat and has_buys) else 0,
        1 if both_beat else 0,
        1 if (beat1 == True and has_buys) else 0,
        n_buys,
        (sp1 if sp1 is not None else -1e9),
    )
    rows.append({
        'ticker': t, 'price': prices[t],
        'er_date': emap.get(t, [{}])[0].get('date'),
        'er_hour': emap.get(t, [{}])[0].get('hour'),
        'beat_q': beat1, 'sp_q': sp1,
        'beat_prev_q': beat2, 'sp_prev_q': sp2,
        'insider_buys_60d': n_buys,
        'rank': rank,
    })
rows.sort(key=lambda r: r['rank'], reverse=True)

print()
print('=== EARNINGS MAY 13-14 (price < $50) — sorted: both-beats+insider top ===')
print(f"{'#':>3} {'ticker':<6} {'price':>7}  {'er_date':<10} {'time':<3}  {'beat_Q':>6} {'sp%_Q':>9}  {'beat_PQ':>7} {'sp%_PQ':>9}  {'buys_60d':>8}")
print('-' * 99)
for i, r in enumerate(rows, 1):
    bq = '✓' if r['beat_q'] is True else ('✗' if r['beat_q'] is False else '?')
    bp = '✓' if r['beat_prev_q'] is True else ('✗' if r['beat_prev_q'] is False else '?')
    sp1s = f"{r['sp_q']:+.1f}%" if r['sp_q'] is not None else '   —   '
    sp2s = f"{r['sp_prev_q']:+.1f}%" if r['sp_prev_q'] is not None else '   —   '
    print(f"{i:>3} {r['ticker']:<6} ${r['price']:>6.2f}  {r['er_date'] or '':<10} {r['er_hour'] or '':<3}  {bq:>6} {sp1s:>9}  {bp:>7} {sp2s:>9}  {r['insider_buys_60d']:>8}")

with open(OUT / 'earnings_may13_14.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['rank', 'ticker', 'price', 'er_date', 'er_hour', 'beat_last_q', 'sp_last_q', 'beat_prev_q', 'sp_prev_q', 'insider_buys_60d'])
    for i, r in enumerate(rows, 1):
        w.writerow([i, r['ticker'], r['price'], r['er_date'], r['er_hour'],
                    r['beat_q'], r['sp_q'], r['beat_prev_q'], r['sp_prev_q'], r['insider_buys_60d']])
print(f'\n{len(rows)} rows -> data/gamma_analysis/earnings_may13_14.csv')

tier1 = [r for r in rows if r['rank'][0] == 1]
print(f'\n*** TIER 1: beat BOTH last 2 quarters AND insider buying in last 60d — {len(tier1)} names ***')
for r in tier1:
    print(f"  {r['ticker']:<6} ${r['price']:>6.2f}  Q-beats: {r['sp_q']:+5.1f}% / {r['sp_prev_q']:+5.1f}%  buys: {r['insider_buys_60d']}  er: {r['er_date']} {r['er_hour']}")
