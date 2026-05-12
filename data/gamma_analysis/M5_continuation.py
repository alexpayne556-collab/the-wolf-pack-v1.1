"""
M5 — Continuation analysis tailored to Tyr's overnight-swing strategy.

The user buys at ~3:30 PM ET and exits at ~8:30 AM ET pre-market.
What they need predicted is the OVERNIGHT GAP: close[t] → open[t+1].

Question: among 15%+ same-day movers, what subset has a POSITIVE overnight gap?

Strategy: for each 15%+ mover, look at:
  - gap_pct_today (was it gap-and-run or steady-build?)
  - open_to_close (closed strong or faded?)
  - rel_vol_20_today (extreme volume?)
  - vs ATR (how big relative to its normal range?)
  - day-of-week
  - price bucket

Compute P(overnight gap > 0 | each feature), find the subset with positive
expected gap.  Output a "continuation candidate" ranking.

Also: M5b — given TODAY's 15%+ gainers, rank by predicted continuation
probability using these features.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).parent

print("[load] all_panel.parquet…")
df = pd.read_parquet(OUT / "all_panel.parquet")
df = df.dropna(subset=["pct_chg","t1_open_gap_pct","close_t1"])
df = df[(df.close_t1 >= 1) & (df.close_t1 <= 200)]

mv = df[df.pct_chg >= 0.15].copy()
print(f"  15%+ movers: {len(mv):,}")
print(f"  base rate: P(overnight gap > 0) = {(mv.t1_open_gap_pct > 0).mean()*100:.1f}%")
print(f"  base rate: P(overnight gap > 2%) = {(mv.t1_open_gap_pct > 0.02).mean()*100:.1f}%")
print(f"  base rate: P(overnight gap > 5%) = {(mv.t1_open_gap_pct > 0.05).mean()*100:.1f}%")
print(f"  median overnight gap: {mv.t1_open_gap_pct.median()*100:.2f}%")
print(f"  mean overnight gap:   {mv.t1_open_gap_pct.mean()*100:.2f}%")

print("\n=== CONDITIONAL OVERNIGHT-GAP STATS ===")
def cond(name, mask):
    sub = mv[mask]
    if len(sub) < 30: return
    p_pos = (sub.t1_open_gap_pct > 0).mean() * 100
    p_2 = (sub.t1_open_gap_pct > 0.02).mean() * 100
    med = sub.t1_open_gap_pct.median() * 100
    mean = sub.t1_open_gap_pct.mean() * 100
    print(f"  {name:<40}n={len(sub):>5,}  P(gap>0)={p_pos:5.1f}%  P(>2%)={p_2:5.1f}%  median={med:+6.2f}%  mean={mean:+6.2f}%")

# Splits
print("By price bucket:")
for pb, grp in mv.groupby("price_bucket_t1"):
    cond(f"  {pb}", mv.price_bucket_t1 == pb)
print("\nBy gap behavior on the move day:")
cond("gap up >2% (gap-and-run)", mv.gap_pct > 0.02)
cond("gap flat (-2..+2%)", (mv.gap_pct >= -0.02) & (mv.gap_pct <= 0.02))
cond("gap down (intraday rally)", mv.gap_pct < -0.02)
print("\nBy close strength:")
cond("closed strong (open->close > 5%)", mv.open_to_close > 0.05)
cond("closed weak  (open->close < 0%)", mv.open_to_close < 0)
print("\nBy magnitude:")
cond("15-25%", (mv.pct_chg >= 0.15) & (mv.pct_chg < 0.25))
cond("25-50%", (mv.pct_chg >= 0.25) & (mv.pct_chg < 0.50))
cond(">=50%", mv.pct_chg >= 0.50)
print("\nBy intraday range size:")
cond("intraday range > 15%", mv.intraday_range_pct > 0.15)
cond("intraday range < 10%", mv.intraday_range_pct < 0.10)
print("\nBy volume:")
mv["rel_vol_today"] = mv.volume / (mv.volume.rolling(20).mean())  # approx
cond("price below $5", mv.close_t1 < 5)
cond("price $5-20", (mv.close_t1 >= 5) & (mv.close_t1 < 20))
cond("price > $20", mv.close_t1 >= 20)
print("\nBy day of week:")
dow_names = ["Mon","Tue","Wed","Thu","Fri"]
for d in range(5):
    cond(f"  {dow_names[d]}", mv.dow == d)
print("\nBy beaten-down status (T-1 prox to 52w high):")
cond("prox_52w_high < 0.5 (deeply beaten)", mv.prox_52w_high_t1 < 0.5)
cond("prox_52w_high 0.5-0.8", (mv.prox_52w_high_t1 >= 0.5) & (mv.prox_52w_high_t1 < 0.8))
cond("prox_52w_high >= 0.8 (near high)", mv.prox_52w_high_t1 >= 0.8)

# ---- BUILD CONTINUATION SCORER ----
# For TODAY's 15%+ movers, score by predicted P(positive overnight gap)
# using the features that DO show a directional edge above.

print("\n\n=== TODAY's 15%+ MOVERS - CONTINUATION CANDIDATES ===")
latest = df["date"].max()
print(f"  date: {pd.to_datetime(latest).date()}")
today = mv[mv["date"] == latest].copy()
if len(today) == 0:
    print("  no >=15% movers today.")
else:
    # Simple scoring rules drawn from the conditional stats above:
    def score_row(r):
        s = 0
        if r["gap_pct"] > 0.02: s += 1            # gap-up on day (gap-and-run)
        if r["open_to_close"] > 0.05: s += 1      # closed strong intraday
        if r["pct_chg"] >= 0.25: s += 1           # bigger movers continue more
        if r["intraday_range_pct"] > 0.15: s += 1 # wide range (high participation)
        if r["close_t1"] < 5: s += 1              # cheap stocks gap more
        return s
    today["cont_score"] = today.apply(score_row, axis=1)
    today = today.sort_values("cont_score", ascending=False)
    cols = ["ticker","pct_chg","close","close_t1","gap_pct","open_to_close",
            "intraday_range_pct","cont_score","price_bucket_t1"]
    show = today[cols].copy()
    show["pct_chg"] = (show["pct_chg"]*100).round(2)
    show["gap_pct"] = (show["gap_pct"]*100).round(2)
    show["open_to_close"] = (show["open_to_close"]*100).round(2)
    show["intraday_range_pct"] = (show["intraday_range_pct"]*100).round(2)
    print(show.to_string(index=False))
    today.to_csv(OUT / f"continuation_candidates_{pd.to_datetime(latest).date()}.csv", index=False)
    print(f"\nsaved continuation_candidates_{pd.to_datetime(latest).date()}.csv")
