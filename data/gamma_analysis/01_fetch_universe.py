"""
Fetch a defensible universe of US-listed equities and 6 months of daily OHLCV.

Universe source: SEC company_tickers.json (all SEC-registered tickers).
Price filter: $0.50 - $200 average close, last 6 months.
Output: data/gamma_analysis/ohlcv.pkl  (dict: ticker -> DataFrame)
"""
from __future__ import annotations
import json, os, pickle, sys, time
from pathlib import Path
import requests
import pandas as pd
import yfinance as yf

OUT = Path(__file__).parent
HDRS = {"User-Agent": "wolf-pack-research backtest@example.com"}

def get_sec_tickers() -> list[str]:
    r = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HDRS, timeout=20)
    r.raise_for_status()
    data = r.json()
    tickers = sorted({row["ticker"].upper() for row in data.values()})
    # Drop obviously broken / class-share suffixes that yfinance handles poorly via dot
    cleaned = []
    for t in tickers:
        if len(t) > 5: continue
        if any(c in t for c in ".$/^"): continue
        cleaned.append(t)
    return cleaned

def fetch_ohlcv(tickers: list[str], batch: int = 100) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    n = len(tickers)
    for i in range(0, n, batch):
        chunk = tickers[i:i+batch]
        try:
            df = yf.download(
                tickers=" ".join(chunk),
                period="8mo",
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                progress=False,
                threads=True,
            )
        except Exception as e:
            print(f"  batch {i}: error {e}", file=sys.stderr)
            continue
        if df is None or len(df) == 0:
            continue
        if isinstance(df.columns, pd.MultiIndex):
            for t in chunk:
                if t in df.columns.get_level_values(0):
                    sub = df[t].dropna(how="all")
                    if len(sub) >= 100 and "Close" in sub.columns:
                        out[t] = sub
        else:
            # Single ticker case
            if len(chunk) == 1 and len(df) >= 100:
                out[chunk[0]] = df
        print(f"  batch {i}-{i+len(chunk)-1}: kept {sum(1 for t in chunk if t in out)}/{len(chunk)} (total {len(out)})")
    return out

def main():
    print("[1] Fetching SEC ticker universe...")
    tickers = get_sec_tickers()
    print(f"    SEC tickers cleaned: {len(tickers)}")
    if (OUT / "universe.txt").exists():
        existing = (OUT / "universe.txt").read_text().split()
        if existing == tickers:
            pass
    (OUT / "universe.txt").write_text("\n".join(tickers))

    print(f"[2] Downloading 8mo daily OHLCV in batches of 100...")
    t0 = time.time()
    data = fetch_ohlcv(tickers, batch=100)
    print(f"    fetched {len(data)} tickers in {time.time()-t0:.1f}s")

    print("[3] Filtering by avg close $0.50 - $200...")
    keep = {}
    for t, df in data.items():
        try:
            avg = float(df["Close"].dropna().mean())
            if 0.5 <= avg <= 200:
                keep[t] = df
        except Exception:
            continue
    print(f"    in price band: {len(keep)} / {len(data)}")

    with open(OUT / "ohlcv.pkl", "wb") as f:
        pickle.dump(keep, f)
    print(f"[4] Saved {OUT/'ohlcv.pkl'}  ({os.path.getsize(OUT/'ohlcv.pkl')/1e6:.1f} MB)")

if __name__ == "__main__":
    main()
