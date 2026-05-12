"""Signal 1: Finnhub insider purchases (filingDate, code 'P'). 1 worker, 1/s pacing."""
import json, os, pickle, time
from pathlib import Path
import requests

OUT = Path(__file__).parent
KEY = os.getenv("FINNHUB_API_KEY", "d5jddu1r01qh37ujsqrgd5jddu1r01qh37ujsqs0")
SESS = requests.Session()
SESS.headers.update({"User-Agent": "wolf-pack-research backtest@example.com"})

with open(OUT / "ohlcv.pkl", "rb") as f:
    OHLCV = pickle.load(f)
tickers = sorted(OHLCV.keys())
print(f"[S1] {len(tickers)} tickers — 1 worker @ 60/min", flush=True)

out: dict = {}
out_path = OUT / "signal1_insider_buys.json"
t0 = time.time()
for i, t in enumerate(tickers, 1):
    # Pace: 1.02s/call ~ 58/min (under the 60/min limit)
    deadline = t0 + i * 1.05
    try:
        r = SESS.get(
            "https://finnhub.io/api/v1/stock/insider-transactions",
            params={"symbol": t, "token": KEY}, timeout=15,
        )
        if r.status_code == 429:
            wait = float(r.headers.get("Retry-After") or 3)
            print(f"  429 at {t}; sleeping {wait}s", flush=True)
            time.sleep(wait)
            r = SESS.get(
                "https://finnhub.io/api/v1/stock/insider-transactions",
                params={"symbol": t, "token": KEY}, timeout=15,
            )
        if r.status_code == 200:
            data = r.json().get("data", [])
            out[t] = sorted({
                x.get("filingDate") for x in data
                if x.get("transactionCode") == "P" and x.get("filingDate")
            })
        else:
            out[t] = []
    except Exception:
        out[t] = []
    if i % 50 == 0:
        n_with = sum(1 for v in out.values() if v)
        elapsed = time.time() - t0
        eta = (len(tickers) - i) * elapsed / i / 60
        print(f"  S1: {i}/{len(tickers)}  with-buys={n_with}  elapsed={elapsed/60:.1f}m  ETA={eta:.1f}m", flush=True)
        with open(out_path, "w") as f:
            json.dump(out, f)
    now = time.time()
    if now < deadline:
        time.sleep(deadline - now)

with open(out_path, "w") as f:
    json.dump(out, f)
n_with = sum(1 for v in out.values() if v)
print(f"[S1] done in {(time.time()-t0)/60:.1f}m — tickers with >=1 purchase: {n_with}", flush=True)
