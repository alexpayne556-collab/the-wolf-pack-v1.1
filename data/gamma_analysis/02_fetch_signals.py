"""
Fetch the three external-data signals for every ticker (point-in-time correct).

Signal 1: Form 4 'P' purchases — using filingDate (public-info date), not transactionDate
Signal 2: Earnings surprise — using yfinance earnings_dates which has actual announcement
          date+time (not just quarter-end period).
Signal 3: Current short interest snapshot (NO history available from free tier — flagged).

Outputs:
  signal1_insider_buys.json    ticker -> [filing_date strings of P transactions]
  signal2_earnings.json        ticker -> [{date, surprisePercent}]   actual announcement
  signal3_short.json           ticker -> {shortPercentOfFloat, sharesShort, floatShares}
"""
from __future__ import annotations
import json, os, pickle, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import yfinance as yf
import pandas as pd

OUT = Path(__file__).parent
KEY = os.getenv("FINNHUB_API_KEY", "d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0")
SESS = requests.Session()
SESS.headers.update({"User-Agent": "wolf-pack-research backtest@example.com"})


def load_universe() -> list[str]:
    with open(OUT / "ohlcv.pkl", "rb") as f:
        d = pickle.load(f)
    return sorted(d.keys())


def fetch_insider_buys(ticker: str) -> list[str]:
    """Return list of YYYY-MM-DD FILING dates for open-market purchases."""
    try:
        r = SESS.get(
            "https://finnhub.io/api/v1/stock/insider-transactions",
            params={"symbol": ticker, "token": KEY}, timeout=15,
        )
        if r.status_code == 429:
            time.sleep(3); return fetch_insider_buys(ticker)
        if r.status_code != 200: return []
        data = r.json().get("data", [])
        # Use filingDate — when information became public.  TransactionDate may
        # precede filingDate by up to 2 business days; filingDate is correct
        # for point-in-time backtests.
        dates = sorted({
            x.get("filingDate") for x in data
            if x.get("transactionCode") == "P" and x.get("filingDate")
        })
        return dates
    except Exception:
        return []


def fetch_earnings(ticker: str) -> list[dict]:
    """Return list of {date, surprisePercent} using actual announcement date+time."""
    try:
        t = yf.Ticker(ticker)
        ed = t.earnings_dates
        if ed is None or len(ed) == 0: return []
        rows = []
        for idx, row in ed.iterrows():
            sp = row.get("Surprise(%)")
            if pd.isna(sp): continue
            # idx is timestamp (with tz); take the calendar date.  An announcement
            # at 4pm ET on day D should be tradeable starting D+1 (we use this in backtest).
            ts = pd.Timestamp(idx)
            try:
                ts_naive = ts.tz_convert(None) if ts.tzinfo else ts
            except Exception:
                ts_naive = ts.tz_localize(None) if ts.tzinfo else ts
            rows.append({
                "announce_dt": ts_naive.isoformat(),
                "surprisePercent": float(sp),
            })
        return rows
    except Exception:
        return []


def fetch_short(ticker: str) -> dict:
    """Current snapshot of short interest — LOOKAHEAD, flagged."""
    try:
        info = yf.Ticker(ticker).info
        sho = info.get("sharesShort")
        flt = info.get("floatShares") or info.get("sharesOutstanding")
        pct = info.get("shortPercentOfFloat")
        if pct is None and sho and flt:
            try: pct = float(sho) / float(flt)
            except Exception: pct = None
        return {
            "shortPercentOfFloat": pct,
            "sharesShort": sho,
            "floatShares": flt,
        }
    except Exception:
        return {"shortPercentOfFloat": None, "sharesShort": None, "floatShares": None}


def run_parallel(label: str, tickers: list[str], fn, max_workers: int) -> dict:
    out: dict = {}
    t0 = time.time()
    last_print = 0
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(fn, t): t for t in tickers}
        for i, fut in enumerate(as_completed(futures), 1):
            t = futures[fut]
            try:
                out[t] = fut.result()
            except Exception:
                out[t] = None
            now = time.time()
            if now - last_print > 5:
                rate = i / (now - t0) if (now - t0) > 0 else 0
                eta = (len(tickers) - i) / rate if rate > 0 else 0
                print(f"  {label}: {i}/{len(tickers)} ({rate:.1f}/s, ETA {eta/60:.1f}m)", flush=True)
                last_print = now
    print(f"  {label}: done {len(tickers)} tickers in {time.time()-t0:.1f}s", flush=True)
    return out


def main():
    tickers = load_universe()
    print(f"[universe] {len(tickers)} tickers")

    print("\n[signal 1] Finnhub insider purchases (filingDate, code P)")
    s1 = run_parallel("S1", tickers, fetch_insider_buys, max_workers=10)
    with open(OUT / "signal1_insider_buys.json", "w") as f:
        json.dump(s1, f)
    n_with = sum(1 for v in s1.values() if v)
    print(f"  tickers with >=1 purchase: {n_with}  ({n_with/len(tickers)*100:.1f}%)")

    print("\n[signal 2] yfinance earnings_dates (announcement date+time)")
    s2 = run_parallel("S2", tickers, fetch_earnings, max_workers=8)
    with open(OUT / "signal2_earnings.json", "w") as f:
        json.dump(s2, f)
    n_with = sum(1 for v in s2.values() if v)
    print(f"  tickers with earnings data: {n_with}  ({n_with/len(tickers)*100:.1f}%)")

    print("\n[signal 3] yfinance short interest snapshot (LOOKAHEAD)")
    s3 = run_parallel("S3", tickers, fetch_short, max_workers=8)
    with open(OUT / "signal3_short.json", "w") as f:
        json.dump(s3, f)
    have_pct = sum(1 for v in s3.values() if v and v.get("shortPercentOfFloat") is not None)
    over_20 = sum(1 for v in s3.values() if v and (v.get("shortPercentOfFloat") or 0) > 0.20)
    print(f"  tickers with short-pct: {have_pct}  >20%: {over_20}")


if __name__ == "__main__":
    main()
