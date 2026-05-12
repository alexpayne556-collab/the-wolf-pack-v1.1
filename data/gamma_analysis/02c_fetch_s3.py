"""Signal 3: yfinance current short-interest snapshot (LOOKAHEAD, no historical archive accessible)."""
import json, pickle, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf

OUT = Path(__file__).parent

def fetch(t: str) -> dict:
    try:
        info = yf.Ticker(t).info
        sho = info.get("sharesShort")
        flt = info.get("floatShares") or info.get("sharesOutstanding")
        pct = info.get("shortPercentOfFloat")
        if pct is None and sho and flt:
            try: pct = float(sho) / float(flt)
            except Exception: pct = None
        return {"shortPercentOfFloat": pct, "sharesShort": sho, "floatShares": flt}
    except Exception:
        return {"shortPercentOfFloat": None, "sharesShort": None, "floatShares": None}

with open(OUT / "ohlcv.pkl", "rb") as f:
    tickers = sorted(pickle.load(f).keys())
print(f"[S3] {len(tickers)} tickers — 8 workers", flush=True)

out: dict = {}
t0 = time.time(); last = 0
out_path = OUT / "signal3_short.json"
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(fetch, t): t for t in tickers}
    for i, f in enumerate(as_completed(futures), 1):
        out[futures[f]] = f.result()
        if time.time() - last > 5:
            have = sum(1 for v in out.values() if v and v.get("shortPercentOfFloat") is not None)
            rate = i / (time.time() - t0)
            eta = (len(tickers) - i) / rate / 60 if rate else 0
            print(f"  S3: {i}/{len(tickers)}  have-pct={have}  rate={rate:.1f}/s  ETA={eta:.1f}m", flush=True)
            with open(out_path, "w") as fh:
                json.dump(out, fh)
            last = time.time()
with open(out_path, "w") as fh:
    json.dump(out, fh)
have = sum(1 for v in out.values() if v and v.get("shortPercentOfFloat") is not None)
over20 = sum(1 for v in out.values() if v and (v.get("shortPercentOfFloat") or 0) > 0.20)
print(f"[S3] done in {(time.time()-t0)/60:.1f}m — have-pct={have} over-20%={over20}", flush=True)
