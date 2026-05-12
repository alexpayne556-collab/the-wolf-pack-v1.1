"""
Scan the 379-ticker watchlist against the winner profile.

Profile features observed across the 9 winners:
  - Beaten down: price < 70% of 52w high            (7/9)
  - High short interest: shortPct > 15%             (7/9)
  - Deep short interest: shortPct > 25%             (5/9, scored as bonus point)
  - Revenue growth > 5%                              (8/9)
  - 3-20 analyst coverage (under-covered to moderate) (8/9)
  - Mid-cap: $300M to $10B                            (6/9)
  - Sector in {Technology, Industrials, Energy, Utilities} (9/9)

Each ticker gets 0-7.  Sort desc.  Top-20 = focus list.
"""
from __future__ import annotations
import json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import yfinance as yf

OUT = Path(__file__).parent

WINNING_SECTORS = {"Technology", "Industrials", "Energy", "Utilities"}

def get_features(t: str) -> dict:
    feat = {"ticker": t, "ok": False}
    try:
        tk = yf.Ticker(t)
        info = dict(tk.info or {})
        if not info:
            return feat
        hist = tk.history(period="1y", interval="1d", auto_adjust=False)
        if hist is None or len(hist) < 30:
            return feat
        if hist.index.tz is not None:
            hist.index = hist.index.tz_convert(None)
        last_close = float(hist["Close"].iloc[-1])
        high_52w = float(hist["Close"].max())
        low_52w = float(hist["Close"].min())
        prox_high = last_close / high_52w if high_52w > 0 else None
        prox_low = last_close / low_52w if low_52w > 0 else None
        # recent trend: last 30 days
        if len(hist) >= 30:
            c30 = float(hist["Close"].iloc[-30])
            trend_30d_pct = (last_close / c30 - 1) * 100
        else:
            trend_30d_pct = None
        # volume ratio
        if len(hist) >= 30:
            v30 = float(hist["Volume"].iloc[-30:].mean())
            v5  = float(hist["Volume"].iloc[-5:].mean())
            vol_ratio = v5 / v30 if v30 > 0 else None
        else:
            vol_ratio = None
        feat.update({
            "ok": True,
            "currentPrice": last_close,
            "high_52w": high_52w,
            "low_52w": low_52w,
            "proximity_52w_high": round(prox_high, 3) if prox_high else None,
            "proximity_52w_low":  round(prox_low, 3) if prox_low else None,
            "trend_30d_pct": round(trend_30d_pct, 2) if trend_30d_pct is not None else None,
            "vol_ratio_5_over_30": round(vol_ratio, 2) if vol_ratio else None,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": info.get("marketCap"),
            "floatShares": info.get("floatShares"),
            "sharesOutstanding": info.get("sharesOutstanding"),
            "shortPercentOfFloat": info.get("shortPercentOfFloat"),
            "shortRatio": info.get("shortRatio"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
        })
    except Exception as e:
        feat["error"] = str(e)[:120]
    return feat


def score(row: dict) -> tuple[int, dict]:
    """Return (score, components dict).  Max 7 points."""
    c = {}
    s = 0
    prox = row.get("proximity_52w_high")
    c["beaten_down"] = bool(prox is not None and prox < 0.70)
    if c["beaten_down"]: s += 1

    sp = row.get("shortPercentOfFloat")
    c["high_short"] = bool(sp is not None and sp > 0.15)
    if c["high_short"]: s += 1
    c["deep_short"] = bool(sp is not None and sp > 0.25)
    if c["deep_short"]: s += 1

    rg = row.get("revenueGrowth")
    c["rev_growth"] = bool(rg is not None and rg > 0.05)
    if c["rev_growth"]: s += 1

    n = row.get("numberOfAnalystOpinions")
    c["mid_coverage"] = bool(n is not None and 3 <= n <= 20)
    if c["mid_coverage"]: s += 1

    mc = row.get("marketCap")
    c["mid_cap"] = bool(mc is not None and 300_000_000 <= mc <= 10_000_000_000)
    if c["mid_cap"]: s += 1

    sec = row.get("sector") or ""
    c["sector_match"] = sec in WINNING_SECTORS
    if c["sector_match"]: s += 1

    return s, c


def main():
    parsed = json.loads((OUT / "watchlist_parsed.json").read_text())
    tickers = [r["ticker"] for r in parsed]
    cat_map = {r["ticker"]: r.get("categories", []) for r in parsed}
    hold_map = {r["ticker"]: r.get("holding") for r in parsed if r.get("holding")}
    print(f"scanning {len(tickers)} tickers — 8 workers")

    rows = []
    t0 = time.time(); last = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(get_features, t): t for t in tickers}
        for i, f in enumerate(as_completed(futures), 1):
            r = f.result()
            rows.append(r)
            if time.time() - last > 5:
                ok = sum(1 for r in rows if r.get("ok"))
                rate = i / (time.time() - t0)
                eta = (len(tickers) - i) / rate / 60 if rate else 0
                print(f"  {i}/{len(tickers)}  ok={ok}  rate={rate:.1f}/s  ETA={eta:.1f}m", flush=True)
                last = time.time()

    # Score
    for r in rows:
        if r.get("ok"):
            s, comps = score(r)
            r["score"] = s
            r["match_components"] = comps
        else:
            r["score"] = None
            r["match_components"] = None
        r["categories"] = cat_map.get(r["ticker"], [])
        r["holding"] = hold_map.get(r["ticker"])

    df = pd.DataFrame(rows)
    df = df.sort_values(["score","shortPercentOfFloat"], ascending=[False, False])

    # save CSV
    csv_cols = ["ticker","score","currentPrice","proximity_52w_high","trend_30d_pct",
                "vol_ratio_5_over_30","sector","industry","marketCap","floatShares",
                "shortPercentOfFloat","revenueGrowth","numberOfAnalystOpinions",
                "categories","holding","ok"]
    have = [c for c in csv_cols if c in df.columns]
    df[have].to_csv(OUT / "watchlist_scored.csv", index=False)

    # detail with components
    with open(OUT / "watchlist_scored.json", "w") as f:
        json.dump(rows, f, indent=2, default=str)

    print(f"\n=== TOP 20 ===")
    top = df[df.score.notna()].nlargest(20, ["score"])
    show_cols = ["ticker","score","currentPrice","proximity_52w_high","trend_30d_pct",
                 "sector","marketCap","shortPercentOfFloat","revenueGrowth","numberOfAnalystOpinions"]
    show_cols = [c for c in show_cols if c in top.columns]
    print(top[show_cols].to_string(index=False))
    print(f"\nSaved: watchlist_scored.csv and watchlist_scored.json")

    print(f"\n=== CURRENT HOLDINGS — score against profile ===")
    hold_rows = df[df.holding.notna()] if "holding" in df.columns else pd.DataFrame()
    if len(hold_rows):
        show = hold_rows[show_cols + ["holding"]].copy()
        print(show.to_string(index=False))


if __name__ == "__main__":
    main()
