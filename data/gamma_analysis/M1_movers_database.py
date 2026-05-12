"""
M1 — Build the movers database.

Scans the cached OHLCV (3,086 tickers × ~167 bars = ~480K ticker-days).
For every day where close-to-close return >= threshold, records:

  Same-day:
    pct_chg, open_to_close_pct, gap_pct, intraday_range_pct, volume, rel_vol_20

  T-1 (the day BEFORE the move - the predictive snapshot):
    rel_vol_20_t1, rel_vol_50_t1, vol_5d_avg_over_20d, range_pct_t1,
    close_vs_20ma, close_vs_50ma, close_vs_200ma,
    proximity_52w_high, proximity_52w_low,
    return_3d, return_5d, return_10d, return_20d,
    atr_5_pct, atr_20_pct, atr_5_over_20, bollinger_width_20,
    consec_up_days, consec_down_days,
    consolidation_range_10d (high-low)/close,
    price_bucket ($1-5, $5-20, $20-50, $50-200, >200)

  Forward (continuation):
    t1_close_pct, t1_open_gap_pct, t5_close_pct,
    t1_was_big_mover (>=10%), t2_was_big_mover, t3, t4, t5

Output: data/gamma_analysis/movers_database.parquet (or .csv)
         data/gamma_analysis/baseline_features.parquet (T-1 features for ALL ticker-days as comparison)
"""
from __future__ import annotations
import json, pickle, time
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).parent

MOVE_THRESH = 0.15   # primary threshold (15% single-day close-to-close)
SECONDARY = [0.05, 0.10, 0.15, 0.20, 0.30]  # for distribution

def price_bucket(p: float) -> str:
    if p < 1: return "$0.50-1"
    if p < 5: return "$1-5"
    if p < 20: return "$5-20"
    if p < 50: return "$20-50"
    if p < 200: return "$50-200"
    return ">$200"

def compute_panel(ticker: str, df: pd.DataFrame) -> pd.DataFrame | None:
    """Compute per-day features.  T-1 cols are the value on day t-1 (yesterday)."""
    if df is None or len(df) < 60: return None
    df = df.copy()
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index = pd.to_datetime(df.index).normalize()
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df = df.dropna(subset=["Close","Open","High","Low","Volume"])
    if len(df) < 60: return None

    close = df["Close"]; openp = df["Open"]; high = df["High"]; low = df["Low"]; vol = df["Volume"]
    prev_close = close.shift(1)

    # daily return (close-to-close)
    pct_chg = close.pct_change()
    open_to_close = (close - openp) / openp
    gap = (openp - prev_close) / prev_close
    intraday_range = (high - low) / prev_close

    # Volume metrics
    vol_ma20 = vol.rolling(20).mean()
    vol_ma50 = vol.rolling(50).mean()
    rel_vol_20 = vol / vol_ma20
    rel_vol_50 = vol / vol_ma50
    vol_5d_avg = vol.rolling(5).mean()
    vol_5d_over_20 = vol_5d_avg / vol_ma20

    # Moving averages
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200, min_periods=60).mean()
    close_vs_ma20 = close / ma20
    close_vs_ma50 = close / ma50
    close_vs_ma200 = close / ma200

    # 52w extremes
    high_252 = close.rolling(252, min_periods=60).max()
    low_252  = close.rolling(252, min_periods=60).min()
    prox_high_52w = close / high_252
    prox_low_52w  = close / low_252

    # Trailing returns
    ret_3 = close.pct_change(3)
    ret_5 = close.pct_change(5)
    ret_10 = close.pct_change(10)
    ret_20 = close.pct_change(20)

    # ATR
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr_5 = tr.rolling(5).mean()
    atr_20 = tr.rolling(20).mean()
    atr_5_pct = atr_5 / close
    atr_20_pct = atr_20 / close
    atr_5_over_20 = atr_5 / atr_20

    # Bollinger width
    std20 = close.rolling(20).std()
    boll_width = (4 * std20) / ma20  # 2-std up + 2-std down

    # Consecutive up/down days
    up = (pct_chg > 0).astype(int)
    dn = (pct_chg < 0).astype(int)
    # cumulative-since-last-reset: hack
    def consec(s):
        out = np.zeros(len(s), dtype=int)
        cur = 0
        for i, v in enumerate(s):
            cur = cur + 1 if v else 0
            out[i] = cur
        return out
    consec_up = pd.Series(consec(up.values), index=close.index)
    consec_dn = pd.Series(consec(dn.values), index=close.index)

    # Consolidation range last 10 days
    consol_range_10 = (close.rolling(10).max() - close.rolling(10).min()) / close

    # Forward returns (continuation)
    t1_close = close.shift(-1) / close - 1
    t1_open  = openp.shift(-1) / close - 1   # overnight gap (next-day open vs today's close)
    t5_close = close.shift(-5) / close - 1
    fwd_max_5d = close.rolling(5).max().shift(-5) / close - 1

    pct_chg_next = pct_chg.shift(-1)
    pct_chg_n2 = pct_chg.shift(-2)
    pct_chg_n3 = pct_chg.shift(-3)
    pct_chg_n4 = pct_chg.shift(-4)
    pct_chg_n5 = pct_chg.shift(-5)

    panel = pd.DataFrame({
        "ticker": ticker,
        "date": close.index,
        "close": close.values,
        "open": openp.values,
        "high": high.values,
        "low": low.values,
        "volume": vol.values,
        "pct_chg": pct_chg.values,
        "open_to_close": open_to_close.values,
        "gap_pct": gap.values,
        "intraday_range_pct": intraday_range.values,
        # T-1 (yesterday) features
        "rel_vol_20_t1": rel_vol_20.shift(1).values,
        "rel_vol_50_t1": rel_vol_50.shift(1).values,
        "vol_5d_over_20_t1": vol_5d_over_20.shift(1).values,
        "intraday_range_pct_t1": intraday_range.shift(1).values,
        "close_vs_ma20_t1": close_vs_ma20.shift(1).values,
        "close_vs_ma50_t1": close_vs_ma50.shift(1).values,
        "close_vs_ma200_t1": close_vs_ma200.shift(1).values,
        "prox_52w_high_t1": prox_high_52w.shift(1).values,
        "prox_52w_low_t1": prox_low_52w.shift(1).values,
        "ret_3d_t1": ret_3.shift(1).values,
        "ret_5d_t1": ret_5.shift(1).values,
        "ret_10d_t1": ret_10.shift(1).values,
        "ret_20d_t1": ret_20.shift(1).values,
        "atr_5_pct_t1": atr_5_pct.shift(1).values,
        "atr_20_pct_t1": atr_20_pct.shift(1).values,
        "atr_5_over_20_t1": atr_5_over_20.shift(1).values,
        "boll_width_t1": boll_width.shift(1).values,
        "consec_up_t1": consec_up.shift(1).values,
        "consec_dn_t1": consec_dn.shift(1).values,
        "consol_range_10_t1": consol_range_10.shift(1).values,
        "close_t1": close.shift(1).values,
        "price_bucket_t1": [price_bucket(c) if pd.notna(c) else None for c in close.shift(1).values],
        # Forward
        "t1_close_pct": pct_chg_next.values,
        "t1_open_gap_pct": t1_open.values,
        "t2_close_pct": pct_chg_n2.values,
        "t3_close_pct": pct_chg_n3.values,
        "t4_close_pct": pct_chg_n4.values,
        "t5_close_pct": pct_chg_n5.values,
        "fwd_5d_close_pct": t5_close.values,
        "fwd_5d_max_pct": fwd_max_5d.values,
        "dow": close.index.dayofweek,
    })
    return panel


def main():
    with open(OUT / "ohlcv.pkl", "rb") as f:
        OHLCV = pickle.load(f)
    print(f"loaded {len(OHLCV)} tickers")

    panels = []
    t0 = time.time()
    for i, (t, df) in enumerate(OHLCV.items(), 1):
        try:
            p = compute_panel(t, df)
            if p is not None:
                panels.append(p)
        except Exception as e:
            print(f"  {t}: {e}")
        if i % 500 == 0:
            print(f"  {i}/{len(OHLCV)}  elapsed={time.time()-t0:.1f}s")
    print(f"  panels: {len(panels)}, elapsed={time.time()-t0:.1f}s")

    all_panel = pd.concat(panels, ignore_index=True)
    print(f"all_panel rows: {len(all_panel):,}")

    # Distribution of pct_chg
    print("\n=== pct_chg distribution ===")
    pc = all_panel.pct_chg.dropna()
    for th in [0.05, 0.10, 0.15, 0.20, 0.30, 0.50]:
        n = int((pc >= th).sum())
        pct = n / len(pc) * 100
        print(f"  >= {th*100:>4.0f}%: {n:>7,} ({pct:6.3f}% of {len(pc):,} ticker-days)")

    # Save full panel (only essential columns to keep size manageable)
    save_cols = list(all_panel.columns)
    all_panel.to_parquet(OUT / "all_panel.parquet", index=False)
    print(f"saved all_panel.parquet ({(OUT/'all_panel.parquet').stat().st_size/1e6:.1f} MB)")

    # Save movers (15%+ subset) for quick analysis
    movers = all_panel[all_panel.pct_chg >= MOVE_THRESH].copy()
    movers = movers.sort_values("date").reset_index(drop=True)
    movers.to_csv(OUT / "movers_15pct.csv", index=False)
    print(f"saved movers_15pct.csv  ({len(movers):,} mover events)")

    # By price bucket - only in $1-200 range (user's constraint)
    in_band = movers[(movers.close_t1 >= 1) & (movers.close_t1 <= 200)]
    print(f"\nin $1-$200 price band: {len(in_band):,} mover events")
    print("\nby price bucket:")
    print(in_band.price_bucket_t1.value_counts().to_string())


if __name__ == "__main__":
    main()
