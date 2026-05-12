"""
M2 — Pattern analysis on movers vs baseline.

For each T-1 feature, compare distribution on (the day before a 15%+ move) vs
(all other ticker-days).  Compute separation metrics (median delta, AUC,
quantile comparison).

Also answers:
  - Gap-and-run vs gap-and-fade: of movers that gap up at open, how many close
    above open vs below?
  - Continuation rate: after a 15%+ move, P(next-day or 5-day-forward 15%+ move)?
  - Day-of-week clustering
  - Price-bucket return distribution

Outputs:
  features_signature.csv       per-feature distribution stats
  continuation_stats.json      continuation rates
  gap_vs_fade.json             gap-and-run analysis
  dow_clustering.csv           DoW analysis
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).parent
MOVE_THRESH = 0.15

print("loading all_panel.parquet...")
df = pd.read_parquet(OUT / "all_panel.parquet")
print(f"  rows: {len(df):,}")

# Apply universe constraint: T-1 close in $1-$200, has all features
df = df.dropna(subset=["pct_chg","rel_vol_20_t1","close_vs_ma20_t1","prox_52w_high_t1","close_t1"])
df = df[(df.close_t1 >= 1) & (df.close_t1 <= 200)]
print(f"  in $1-200 with features: {len(df):,}")

is_mover = df.pct_chg >= MOVE_THRESH
print(f"  movers (>=15% same day): {is_mover.sum():,}  ({is_mover.mean()*100:.3f}% base rate)")

# ---- 1. PER-FEATURE SIGNATURE ----
FEATURES = [
    "rel_vol_20_t1","rel_vol_50_t1","vol_5d_over_20_t1",
    "intraday_range_pct_t1","close_vs_ma20_t1","close_vs_ma50_t1",
    "close_vs_ma200_t1","prox_52w_high_t1","prox_52w_low_t1",
    "ret_3d_t1","ret_5d_t1","ret_10d_t1","ret_20d_t1",
    "atr_5_pct_t1","atr_20_pct_t1","atr_5_over_20_t1",
    "boll_width_t1","consec_up_t1","consec_dn_t1","consol_range_10_t1",
]

def quantile_lift(feature: str) -> dict:
    """Bin feature into quintiles using baseline, measure mover-rate in each bin."""
    s = df[feature].dropna()
    if len(s) < 1000: return {}
    qs = s.quantile([0.0,0.2,0.4,0.6,0.8,1.0]).tolist()
    qs[0] = -np.inf; qs[-1] = np.inf
    out = {}
    for i in range(5):
        lo, hi = qs[i], qs[i+1]
        mask = (df[feature] >= lo) & (df[feature] < hi)
        if mask.sum() == 0: continue
        sub = df[mask]
        out[f"q{i+1}"] = {
            "range": [float(lo) if np.isfinite(lo) else None, float(hi) if np.isfinite(hi) else None],
            "n": int(mask.sum()),
            "mover_rate_pct": float(is_mover[mask].mean() * 100),
        }
    return out

print("\n=== PER-FEATURE SIGNATURE ===")
rows = []
for f in FEATURES:
    s_all = df[f].dropna()
    s_mv  = df.loc[is_mover, f].dropna()
    if len(s_mv) < 30: continue
    baseline_med = float(s_all.median())
    mover_med    = float(s_mv.median())
    mover_p10    = float(s_mv.quantile(0.10))
    mover_p90    = float(s_mv.quantile(0.90))
    base_p10     = float(s_all.quantile(0.10))
    base_p90     = float(s_all.quantile(0.90))
    delta_med    = mover_med - baseline_med

    # Approximate AUC: P(rand_mover > rand_baseline)
    # Use ranks for efficiency
    nm = min(len(s_mv), 5000)  # sample
    nb = min(len(s_all), 50000)
    mv_s = s_mv.sample(nm, random_state=0).values
    ba_s = s_all.sample(nb, random_state=0).values
    auc = float((mv_s.reshape(-1,1) > ba_s.reshape(1,-1)).mean())

    rows.append({
        "feature": f,
        "baseline_median": baseline_med,
        "mover_median": mover_med,
        "delta": delta_med,
        "mover_p10": mover_p10,
        "mover_p90": mover_p90,
        "baseline_p10": base_p10,
        "baseline_p90": base_p90,
        "auc_mover_higher": auc,
    })

sig_df = pd.DataFrame(rows)
sig_df["abs_auc_minus_50"] = (sig_df.auc_mover_higher - 0.5).abs()
sig_df = sig_df.sort_values("abs_auc_minus_50", ascending=False)
sig_df.to_csv(OUT / "features_signature.csv", index=False)
print(sig_df[["feature","baseline_median","mover_median","auc_mover_higher"]].to_string(index=False))
print(f"\nsaved features_signature.csv")

# Detailed quantile lift for top-3 features
print("\n=== QUANTILE LIFT (top-3 by AUC separation) ===")
quantile_results = {}
for f in sig_df.head(5).feature:
    print(f"\n{f}:")
    ql = quantile_lift(f)
    quantile_results[f] = ql
    for q, info in ql.items():
        r0, r1 = info["range"]
        r0s = f"{r0:.3g}" if r0 is not None else "-inf"
        r1s = f"{r1:.3g}" if r1 is not None else "+inf"
        print(f"  {q}: range=[{r0s}, {r1s}]  n={info['n']:,}  mover_rate={info['mover_rate_pct']:.3f}%")
with open(OUT / "quantile_lift.json","w") as f: json.dump(quantile_results, f, indent=2, default=str)

# ---- 2. GAP-AND-RUN vs GAP-AND-FADE on mover days ----
print("\n=== GAP-AND-RUN vs FADE (on the mover day itself) ===")
mv = df[is_mover].copy()
gap_up = mv.gap_pct > 0.02       # gapped up at open by >2%
gap_flat = (mv.gap_pct.abs() <= 0.02)
gap_dn = mv.gap_pct < -0.02
n_gap_up = int(gap_up.sum()); n_gap_flat = int(gap_flat.sum()); n_gap_dn = int(gap_dn.sum())
# Of gap-ups, how many closed above open (run) vs below (fade)?
mv_gu = mv[gap_up]
ran_pct = float((mv_gu.open_to_close > 0).mean() * 100)
faded_pct = float((mv_gu.open_to_close <= 0).mean() * 100)
gap_results = {
    "n_movers": int(len(mv)),
    "gap_up_pct": float(gap_up.mean() * 100),
    "gap_flat_pct": float(gap_flat.mean() * 100),
    "gap_down_pct": float(gap_dn.mean() * 100),
    "of_gap_ups": {
        "n": n_gap_up,
        "ran_after_open_pct": ran_pct,
        "faded_after_open_pct": faded_pct,
    },
    "open_to_close_median_gap_up": float(mv_gu.open_to_close.median() * 100),
    "open_to_close_median_gap_flat": float(mv[gap_flat].open_to_close.median() * 100),
    "open_to_close_median_gap_down": float(mv[gap_dn].open_to_close.median() * 100),
}
print(json.dumps(gap_results, indent=2))
with open(OUT / "gap_vs_fade.json", "w") as f: json.dump(gap_results, f, indent=2)

# ---- 3. CONTINUATION ANALYSIS ----
print("\n=== CONTINUATION: after a 15%+ day ===")
cont = {
    "n_movers": int(len(mv)),
    "t1_close_was_15plus_pct": float((mv.t1_close_pct >= 0.15).mean() * 100),
    "t1_close_was_5plus_pct": float((mv.t1_close_pct >= 0.05).mean() * 100),
    "t1_close_was_negative_pct": float((mv.t1_close_pct < 0).mean() * 100),
    "t1_open_gap_was_positive_pct": float((mv.t1_open_gap_pct > 0).mean() * 100),
    "t1_open_gap_was_5plus_pct": float((mv.t1_open_gap_pct >= 0.05).mean() * 100),
    "median_t1_close_pct": float(mv.t1_close_pct.median() * 100),
    "median_t1_open_gap_pct": float(mv.t1_open_gap_pct.median() * 100),
    "any_15plus_in_next_5_days_pct": float((mv[["t1_close_pct","t2_close_pct","t3_close_pct","t4_close_pct","t5_close_pct"]].max(axis=1) >= 0.15).mean() * 100),
    "any_5plus_in_next_5_days_pct": float((mv[["t1_close_pct","t2_close_pct","t3_close_pct","t4_close_pct","t5_close_pct"]].max(axis=1) >= 0.05).mean() * 100),
    "median_5d_forward_close_pct": float(mv.fwd_5d_close_pct.median() * 100),
    "median_5d_forward_max_pct": float(mv.fwd_5d_max_pct.median() * 100),
}
print(json.dumps(cont, indent=2))
with open(OUT / "continuation_stats.json","w") as f: json.dump(cont, f, indent=2)

# Baseline for comparison: random day's next-day stats
print("\n=== BASELINE (non-mover days) - to compare continuation ===")
base = df[~is_mover]
base_cont = {
    "t1_close_was_15plus_pct": float((base.t1_close_pct >= 0.15).mean() * 100),
    "t1_open_gap_was_5plus_pct": float((base.t1_open_gap_pct >= 0.05).mean() * 100),
    "median_t1_close_pct": float(base.t1_close_pct.median() * 100),
    "median_t1_open_gap_pct": float(base.t1_open_gap_pct.median() * 100),
}
print(json.dumps(base_cont, indent=2))
cont["baseline"] = base_cont
with open(OUT / "continuation_stats.json","w") as f: json.dump(cont, f, indent=2)

# ---- 4. DAY-OF-WEEK clustering ----
print("\n=== DAY-OF-WEEK ===")
dow_names = ["Mon","Tue","Wed","Thu","Fri"]
dow_rows = []
for d in range(5):
    n_total = int((df.dow == d).sum())
    n_mover = int(((df.dow == d) & is_mover).sum())
    rate = n_mover/n_total*100 if n_total else 0
    dow_rows.append({"dow": dow_names[d], "ticker_days": n_total, "mover_days": n_mover, "rate_pct": rate})
dow_df = pd.DataFrame(dow_rows)
print(dow_df.to_string(index=False))
dow_df.to_csv(OUT / "dow_clustering.csv", index=False)

# ---- 5. PRICE BUCKET ----
print("\n=== PRICE BUCKET ===")
pb_rows = []
for pb, grp in df.groupby("price_bucket_t1"):
    if grp.empty: continue
    pb_rows.append({
        "price_bucket": pb,
        "ticker_days": len(grp),
        "mover_days": int((grp.pct_chg >= MOVE_THRESH).sum()),
        "rate_pct": float((grp.pct_chg >= MOVE_THRESH).mean() * 100),
        "median_mover_pct": float(grp[grp.pct_chg >= MOVE_THRESH].pct_chg.median() * 100) if (grp.pct_chg >= MOVE_THRESH).any() else None,
    })
pb_df = pd.DataFrame(pb_rows).sort_values("rate_pct", ascending=False)
print(pb_df.to_string(index=False))
pb_df.to_csv(OUT / "price_bucket_stats.csv", index=False)
print("\ndone.")
