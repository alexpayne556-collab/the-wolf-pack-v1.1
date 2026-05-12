"""Signal 2: yfinance earnings_dates with surprise% — actual announcement date+time."""
import json, pickle, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd

OUT = Path(__file__).parent

def fetch(t: str) -> list[dict]:
    try:
        ed = yf.Ticker(t).earnings_dates
        if ed is None or len(ed) == 0: return []
        rows = []
        for idx, row in ed.iterrows():
            sp = row.get("Surprise(%)")
            if pd.isna(sp): continue
            ts = pd.Timestamp(idx)
            try:
                ts_naive = ts.tz_convert(None) if ts.tzinfo else ts
            except Exception:
                ts_naive = ts.tz_localize(None) if ts.tzinfo else ts
            rows.append({"announce_dt": ts_naive.isoformat(), "surprisePercent": float(sp)})
        return rows
    except Exception:
        return []

with open(OUT / "ohlcv.pkl", "rb") as f:
    tickers = sorted(pickle.load(f).keys())
print(f"[S2] {len(tickers)} tickers — 8 workers", flush=True)

out: dict = {}
t0 = time.time(); last = 0
out_path = OUT / "signal2_earnings.json"
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(fetch, t): t for t in tickers}
    for i, f in enumerate(as_completed(futures), 1):
        out[futures[f]] = f.result()
        if time.time() - last > 5:
            n_with = sum(1 for v in out.values() if v)
            rate = i / (time.time() - t0)
            eta = (len(tickers) - i) / rate / 60 if rate else 0
            print(f"  S2: {i}/{len(tickers)}  with-data={n_with}  rate={rate:.1f}/s  ETA={eta:.1f}m", flush=True)
            with open(out_path, "w") as fh:
                json.dump(out, fh)
            last = time.time()
with open(out_path, "w") as fh:
    json.dump(out, fh)
n_with = sum(1 for v in out.values() if v)
print(f"[S2] done in {(time.time()-t0)/60:.1f}m — tickers with data: {n_with}", flush=True)
