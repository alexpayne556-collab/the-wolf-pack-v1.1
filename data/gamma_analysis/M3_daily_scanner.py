"""
M3 — Daily pre-mover scanner.

Uses the empirical signature from M2: pre-mover days are characterized by
HIGH volatility (ATR, range, Bollinger width, 10-day consolidation range) and
beaten-down price (below 60% of 52w high, below 200d MA).  Volume contributes
weakly.

Composite score combines the strongest features (ranked by AUC):
  atr_5_pct       (AUC 0.845)  -- 30% weight
  consol_range_10 (AUC 0.829)  -- 25%
  boll_width      (AUC 0.827)  -- 25%
  intraday_range  (AUC 0.800)  -- 10%
  prox_52w_high   (AUC 0.261 inverted) -- 5%  (beaten down)
  rel_vol_20      (AUC 0.569)  --  5%  (small but real)

Each feature is converted to a 0-1 percentile, the inverted ones flipped, then
weighted-summed.  Output ranks tickers from most to least mover-resembling.

Usage:
  python3 M3_daily_scanner.py           # rank tickers as of latest cached close
  python3 M3_daily_scanner.py --date YYYY-MM-DD  # rank as of given day
"""
from __future__ import annotations
import argparse, json, pickle
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).parent

WEIGHTS = {
    "atr_5_pct_t1":         0.30,
    "consol_range_10_t1":   0.25,
    "boll_width_t1":        0.25,
    "intraday_range_pct_t1":0.10,
    "prox_52w_high_t1":     -0.05,  # negative because LOW value predicts mover
    "rel_vol_20_t1":        0.05,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="Date to evaluate (YYYY-MM-DD).  Default: latest in cache.")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--price-min", type=float, default=1.0)
    ap.add_argument("--price-max", type=float, default=200.0)
    args = ap.parse_args()

    print("[load] all_panel.parquet…")
    df = pd.read_parquet(OUT / "all_panel.parquet")
    df = df.dropna(subset=list(WEIGHTS.keys()) + ["close_t1"])
    df = df[(df.close_t1 >= args.price_min) & (df.close_t1 <= args.price_max)]
    df["date"] = pd.to_datetime(df["date"])
    if args.date:
        target = pd.to_datetime(args.date)
    else:
        target = df["date"].max()
    print(f"  evaluating as of close of {target.date()}")

    # We want the snapshot evaluated USING T-1 features looking at day = target.
    # The "T-1 features" on row `target` describe yesterday's data.  So we use
    # rows where date == target.
    snap = df[df["date"] == target].copy()
    if len(snap) == 0:
        print(f"  no data for {target.date()}")
        return

    # Compute baseline percentiles ACROSS ALL HISTORICAL ticker-days (so the
    # percentile reflects "how unusual is this value compared to all days").
    baseline = df  # entire history
    for feat in WEIGHTS:
        s = baseline[feat].dropna()
        # Percentile rank for each snap[feat] value within baseline distribution
        # Use simple searchsorted on sorted baseline values
        sorted_vals = np.sort(s.values)
        ranks = np.searchsorted(sorted_vals, snap[feat].values) / len(sorted_vals)
        snap[f"pct_{feat}"] = ranks

    # Score: weighted sum.  For prox_52w_high (negative weight), we use (1 - percentile)
    # ... i.e. a low value (beaten down) gets a HIGH pct(1-pct) score.
    score = np.zeros(len(snap))
    for feat, w in WEIGHTS.items():
        p = snap[f"pct_{feat}"].values
        if w < 0:
            score += abs(w) * (1 - p)
        else:
            score += w * p
    snap["score"] = score

    snap = snap.sort_values("score", ascending=False)

    # Sanity: also show whether the picks have made a big move recently
    snap["pct_chg_today"] = snap["pct_chg"]

    cols = ["ticker","score","close_t1","close","pct_chg","atr_5_pct_t1","boll_width_t1",
            "consol_range_10_t1","intraday_range_pct_t1","prox_52w_high_t1","rel_vol_20_t1",
            "ret_20d_t1","price_bucket_t1"]
    show = snap[cols].head(args.top).copy()
    show["score"]=show["score"].round(3)
    for c in ["close_t1","close","atr_5_pct_t1","boll_width_t1","consol_range_10_t1",
              "intraday_range_pct_t1","prox_52w_high_t1","rel_vol_20_t1","ret_20d_t1"]:
        show[c] = show[c].astype(float).round(4)
    show["pct_chg"] = (show["pct_chg"]*100).round(2)
    print(f"\n=== TOP {args.top} PRE-MOVER SCORE on {target.date()} (universe: $1-200, n={len(snap)}) ===")
    print(show.to_string(index=False))

    # Save
    out_path = OUT / f"scanner_{target.date()}.csv"
    snap.to_csv(out_path, index=False)
    print(f"\nsaved {out_path}")

    # Backtest sanity: how did the top-20 from yesterday actually perform?
    if args.date is None:
        ydate = df["date"].sort_values().unique()[-2]
        ysnap = df[df["date"] == ydate].copy()
        for feat in WEIGHTS:
            s = baseline[feat].dropna()
            sorted_vals = np.sort(s.values)
            ranks = np.searchsorted(sorted_vals, ysnap[feat].values) / len(sorted_vals)
            ysnap[f"pct_{feat}"] = ranks
        ys = np.zeros(len(ysnap))
        for feat, w in WEIGHTS.items():
            p = ysnap[f"pct_{feat}"].values
            if w < 0:  ys += abs(w) * (1 - p)
            else:      ys += w * p
        ysnap["score"] = ys
        ysnap = ysnap.sort_values("score", ascending=False).head(20)
        # ysnap.pct_chg is yesterday's same-day pct_chg.  But the prediction is for TODAY.
        # The prediction "T-1 features predict day-T move" — so for ysnap (date=yesterday)
        # the next-day move is t1_close_pct on that row.
        ysnap["next_day_pct"] = (ysnap["t1_close_pct"] * 100).round(2)
        print(f"\n=== SANITY: yesterday's ({ydate.date()}) top-20 scorers - what they did next day ===")
        sc = ["ticker","score","close_t1","close","next_day_pct","atr_5_pct_t1","prox_52w_high_t1"]
        sc = [c for c in sc if c in ysnap.columns]
        print(ysnap[sc].to_string(index=False))
        wins = (ysnap["t1_close_pct"] > 0).sum()
        big = (ysnap["t1_close_pct"] >= 0.05).sum()
        moved = (ysnap["t1_close_pct"] >= 0.15).sum()
        print(f"\n  of those 20: positive next day {wins}/20 = {wins/20*100:.0f}%, "
              f"+5%+ {big}/20 ({big/20*100:.0f}%), +15%+ {moved}/20 ({moved/20*100:.0f}%)")
        print(f"  median next-day return: {ysnap['t1_close_pct'].median()*100:.2f}%")
        print(f"  mean next-day return: {ysnap['t1_close_pct'].mean()*100:.2f}%")


if __name__ == "__main__":
    main()
