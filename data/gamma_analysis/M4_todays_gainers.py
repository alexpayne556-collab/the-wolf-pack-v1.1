"""
M4 — Today's gainers + 5-day pre-move context.

Find every ticker that gained >= 15% TODAY (close-to-close) in $1-$200, then
pull the 5 days BEFORE today and describe what was visible:

  - close trend over last 5 days (up / flat / down + %)
  - relative volume on T-1 (yesterday vs 20-day average)
  - 5-day average vol / 20-day average vol  (volume building?)
  - intraday range trend (was it already volatile?)
  - 52w high proximity
  - market cap, float (from yfinance .info if available)

This is the "yesterday's biggest movers — what did they look like Friday?" report
that you can stare at every morning and pattern-match by eye.
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np

OUT = Path(__file__).parent

print("[load] all_panel.parquet…")
df = pd.read_parquet(OUT / "all_panel.parquet")
df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ticker","date"])

latest = df["date"].max()
print(f"  latest date in cache: {latest.date()}")

# Today's 15%+ gainers in $1-200
today = df[df["date"] == latest].copy()
today = today.dropna(subset=["pct_chg","close_t1"])
today = today[(today.close_t1 >= 1) & (today.close_t1 <= 200)]
gainers = today[today["pct_chg"] >= 0.15].sort_values("pct_chg", ascending=False)
print(f"  today's >=15% gainers ($1-200): {len(gainers)}")

# For each gainer, build the 5-day pre-move context
rows = []
for _, g in gainers.iterrows():
    t = g["ticker"]
    hist = df[df["ticker"] == t].sort_values("date")
    today_idx = hist[hist["date"] == latest].index
    if len(today_idx) == 0: continue
    pos = hist.index.get_loc(today_idx[0])
    pre = hist.iloc[max(0,pos-5):pos]
    if len(pre) < 3: continue
    pre_close_first = float(pre["close"].iloc[0])
    pre_close_last  = float(pre["close"].iloc[-1])
    pre5_pct = (pre_close_last / pre_close_first - 1) * 100
    if pre5_pct < -3:   pre5_trend = "declining"
    elif pre5_pct > 3:  pre5_trend = "building"
    else:               pre5_trend = "flat"
    rows.append({
        "ticker": t,
        "pct_chg_today": round(g["pct_chg"] * 100, 2),
        "close_today": round(g["close"], 4),
        "close_yesterday": round(g["close_t1"], 4),
        "gap_pct_today": round(g["gap_pct"] * 100, 2),
        "open_to_close_today": round(g["open_to_close"] * 100, 2),
        "intraday_range_today": round(g["intraday_range_pct"] * 100, 2),
        "vol_today": int(g["volume"]),
        "rel_vol_20_t1": round(g["rel_vol_20_t1"], 2) if pd.notna(g["rel_vol_20_t1"]) else None,
        "vol_5d_over_20_t1": round(g["vol_5d_over_20_t1"], 2) if pd.notna(g["vol_5d_over_20_t1"]) else None,
        "intraday_range_t1": round(g["intraday_range_pct_t1"] * 100, 2) if pd.notna(g["intraday_range_pct_t1"]) else None,
        "atr_5_pct_t1": round(g["atr_5_pct_t1"] * 100, 2) if pd.notna(g["atr_5_pct_t1"]) else None,
        "boll_width_t1": round(g["boll_width_t1"], 2) if pd.notna(g["boll_width_t1"]) else None,
        "prox_52w_high_t1": round(g["prox_52w_high_t1"], 3) if pd.notna(g["prox_52w_high_t1"]) else None,
        "ret_5d_t1": round(g["ret_5d_t1"] * 100, 2) if pd.notna(g["ret_5d_t1"]) else None,
        "pre5_trend": pre5_trend,
        "pre5_pct": round(pre5_pct, 2),
        "price_bucket": g["price_bucket_t1"],
    })

out = pd.DataFrame(rows)
out.to_csv(OUT / f"todays_gainers_{latest.date()}.csv", index=False)
print(f"saved todays_gainers_{latest.date()}.csv")

print(f"\n=== TODAY'S {len(out)} GAINERS (>=15%, $1-200) ===")
show_cols = ["ticker","pct_chg_today","close_today","close_yesterday","gap_pct_today",
             "rel_vol_20_t1","vol_5d_over_20_t1","atr_5_pct_t1","prox_52w_high_t1",
             "pre5_trend","pre5_pct","price_bucket"]
print(out[show_cols].to_string(index=False))

# Aggregate the patterns of TODAY's gainers
print(f"\n=== AGGREGATE PATTERNS OF TODAY'S GAINERS ===")
print(f"gap up at open:    {(out.gap_pct_today >  2).sum()}/{len(out)}  ({(out.gap_pct_today >  2).mean()*100:.0f}%)")
print(f"gap down at open:  {(out.gap_pct_today < -2).sum()}/{len(out)}  ({(out.gap_pct_today < -2).mean()*100:.0f}%)")
print(f"gap flat (-2..+2): {((out.gap_pct_today >= -2)&(out.gap_pct_today <= 2)).sum()}/{len(out)}")
print()
print(f"price bucket:")
print(out.price_bucket.value_counts().to_string())
print()
print(f"pre-5d trend:")
print(out.pre5_trend.value_counts().to_string())
print()
print(f"rel_vol_20 yesterday > 2x:  {(out.rel_vol_20_t1 > 2.0).sum()}/{len(out)}  ({(out.rel_vol_20_t1 > 2.0).mean()*100:.0f}%)")
print(f"atr_5_pct yesterday > 5%:  {(out.atr_5_pct_t1 > 5).sum()}/{len(out)}")
print(f"prox_52w_high yesterday < 0.6:  {(out.prox_52w_high_t1 < 0.6).sum()}/{len(out)}")
