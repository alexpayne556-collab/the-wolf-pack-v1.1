"""
PROVE-IT-OR-KILL-IT backtest.

Strategy: on each trading day D, for each ticker, evaluate 5 binary signals
using only information available AS OF the close of D-1.  If >= 3 of 5 fire,
"buy" $200 at close of D, exit at close of D+10 trading days.

Signals (evaluated point-in-time, except where flagged):
  S1  Insider open-market PURCHASE (Form 4 code 'P') in the 60 calendar days
      preceding D.
  S2  Most recent reported quarterly earnings BEFORE D had surprisePercent > 0
      (a "beat").
  S3  Short interest as % of float > 20%.  *** LOOKAHEAD WARNING *** This uses
      a current snapshot (FINRA historical archive not accessible from this
      environment); treated as static per ticker.  Reported separately.
  S4  3-day average volume ending D-1 was >= 2.0x trailing 20-day avg volume.
  S5  Close on D-1 was within 5% of the trailing 252-day high (52w).

Also tracks: every stock that had a 30%+ gain in any 10-day window over the
backtest period, and how many of the 5 signals were present at the start of
that window — the forensic half of the test.

Inputs:  ohlcv.pkl, signal1_insider_buys.json, signal2_earnings.json, signal3_short.json
Outputs:
  trades.csv          every simulated trade
  movers_30pct.csv    every 30%/10d window and its signal composition
  summary.json        headline stats
  report.md           human-readable verdict
"""
from __future__ import annotations
import json, pickle
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

OUT = Path(__file__).parent

# --- Tunables -----------------------------------------------------------
HOLD_DAYS = 10
WINDOW_30PCT = 10
THRESH_VOL_SPIKE = 2.0       # S4: 3-day avg vol >= 2x 20-day avg
THRESH_52W_PROX = 0.05       # S5: within 5% of 252-day high
THRESH_SHORT = 0.20          # S3: > 20% short
THRESH_INSIDER_DAYS = 60     # S1: purchase within last 60 calendar days
SIGNAL_MIN = 3               # buy when >= this many signals fire
POSITION_USD = 200.0
BACKTEST_START_OFFSET_DAYS = 252   # need 252 bars of history before first trade

# --- Load ---------------------------------------------------------------
print("[load] OHLCV…")
with open(OUT / "ohlcv.pkl", "rb") as f:
    OHLCV: dict[str, pd.DataFrame] = pickle.load(f)
print(f"  tickers: {len(OHLCV)}")

print("[load] signal files…")
with open(OUT / "signal1_insider_buys.json") as f:
    S1_DATA: dict[str, list[str]] = json.load(f)
with open(OUT / "signal2_earnings.json") as f:
    S2_DATA: dict[str, list[dict]] = json.load(f)
with open(OUT / "signal3_short.json") as f:
    S3_DATA: dict[str, dict] = json.load(f)
print(f"  S1 keys: {len(S1_DATA)}, S2 keys: {len(S2_DATA)}, S3 keys: {len(S3_DATA)}")


def normalize_ohlcv(df: pd.DataFrame) -> pd.DataFrame | None:
    """Return df indexed by tz-naive date with columns Close, Volume.  None if unusable."""
    if df is None or df.empty: return None
    df = df.copy()
    if "Close" not in df.columns: return None
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None) if df.index.tz else df.index
    df.index = pd.to_datetime(df.index).normalize()
    df = df[~df.index.duplicated(keep="first")]
    df = df.dropna(subset=["Close", "Volume"])
    if len(df) < 100: return None
    return df[["Close", "Volume", "High", "Low", "Open"]]


def signals_for_ticker(ticker: str, df: pd.DataFrame) -> pd.DataFrame:
    """Return df indexed by date with bool columns s1..s5 evaluated as-of close of that date.
    A trade entry on day D uses signals from D-1 (handled in main loop by shift)."""
    out = pd.DataFrame(index=df.index)
    close = df["Close"]; vol = df["Volume"]

    # S4: vol spike — 3-day avg / 20-day avg >= 2x
    vol3 = vol.rolling(3).mean()
    vol20 = vol.rolling(20).mean()
    out["s4"] = (vol3 / vol20) >= THRESH_VOL_SPIKE

    # S5: within 5% of trailing 252-day high
    high252 = close.rolling(252, min_periods=60).max()
    out["s5"] = (close / high252) >= (1.0 - THRESH_52W_PROX)

    # S1: any insider purchase in prior 60 calendar days
    raw = S1_DATA.get(ticker) or []
    p_dates = pd.to_datetime(raw, errors="coerce").dropna()
    p_dates = pd.Series(1, index=p_dates).sort_index()
    if len(p_dates):
        # For each calendar day, count purchases in last 60 days.
        # Resample to daily, then rolling sum 60 days.
        daily = p_dates.resample("D").sum().fillna(0)
        roll = daily.rolling("60D").sum()
        s1 = roll.reindex(df.index, method="ffill").fillna(0)
        out["s1"] = (s1 > 0).values
    else:
        out["s1"] = False

    # S2: most recent ANNOUNCED earnings strictly before date D had surprisePercent > 0.
    # Use yfinance's actual announcement datetime — earnings reported at 4pm
    # of day E are first tradeable on D=E+1, so we require announce_dt < D.
    er = S2_DATA.get(ticker) or []
    if er:
        rows = []
        for e in er:
            ad = e.get("announce_dt"); sp = e.get("surprisePercent")
            if not ad or sp is None: continue
            try:
                ts = pd.to_datetime(ad).normalize()
            except Exception:
                continue
            rows.append((ts, float(sp)))
        if rows:
            rows.sort()
            er_dates = pd.DatetimeIndex([r[0] for r in rows])
            er_beats = [r[1] > 0 for r in rows]
            s2 = []
            for d in df.index:
                idx = er_dates.searchsorted(d, side="left") - 1
                s2.append(er_beats[idx] if idx >= 0 else False)
            out["s2"] = s2
        else:
            out["s2"] = False
    else:
        out["s2"] = False

    # S3: current short interest > 20% (STATIC, lookahead-flagged)
    s3v = (S3_DATA.get(ticker) or {}).get("shortPercentOfFloat")
    out["s3"] = bool(s3v and s3v > THRESH_SHORT)

    return out


# --- Build per-ticker signal panels + run backtest ----------------------
print("\n[panel] building daily signal panels…")
trades = []
movers = []
panel_counts = {"tickers_processed": 0, "tickers_skipped": 0}
signal_fire_counts = np.zeros(6, dtype=int)  # index = count of signals that fired (0..5)

for ticker, raw in OHLCV.items():
    df = normalize_ohlcv(raw)
    if df is None:
        panel_counts["tickers_skipped"] += 1
        continue
    panel_counts["tickers_processed"] += 1

    sig = signals_for_ticker(ticker, df)
    # Shift signals: entering on D uses information from close of D-1 (no peek at D)
    sig_lag = sig.shift(1).fillna(False).astype(bool)
    sig_count = sig_lag.sum(axis=1)

    # --- forensic: every 30%+ 10d-window mover ---
    close = df["Close"].values
    dates = df.index
    # window_start has gain = close[start+10]/close[start] - 1
    if len(close) > WINDOW_30PCT + 1:
        ratios = close[WINDOW_30PCT:] / close[:-WINDOW_30PCT] - 1
        for i, g in enumerate(ratios):
            if g >= 0.30:
                start_idx = i
                end_idx = i + WINDOW_30PCT
                # signals as of start_idx (using lagged sig = D-1 info on day start)
                if start_idx < len(sig_lag):
                    row = sig_lag.iloc[start_idx]
                    movers.append({
                        "ticker": ticker,
                        "start_date": dates[start_idx].date().isoformat(),
                        "end_date": dates[end_idx].date().isoformat() if end_idx < len(dates) else None,
                        "start_close": float(close[start_idx]),
                        "end_close": float(close[end_idx]) if end_idx < len(close) else None,
                        "gain_pct": float(g * 100),
                        "s1": bool(row.get("s1", False)),
                        "s2": bool(row.get("s2", False)),
                        "s3": bool(row.get("s3", False)),
                        "s4": bool(row.get("s4", False)),
                        "s5": bool(row.get("s5", False)),
                        "n_signals": int(row.sum()),
                    })

    # --- strategy: buy when >=3 signals fire ---
    # Skip first 60 bars to give signals time to populate. Use per-ticker cooldown so
    # consecutive triggers on the same ticker don't open overlapping positions —
    # next entry allowed only after the prior 10-day hold completes.
    start = 60
    next_allowed_i = start
    for i in range(start, len(df) - HOLD_DAYS):
        n = int(sig_count.iloc[i])
        signal_fire_counts[min(n, 5)] += 1
        if n < SIGNAL_MIN: continue
        if i < next_allowed_i: continue
        entry_price = float(close[i])
        if entry_price <= 0 or entry_price < 0.50 or entry_price > 200.0:
            continue
        exit_price = float(close[i + HOLD_DAYS])
        pnl_pct = (exit_price / entry_price - 1) * 100
        shares = POSITION_USD / entry_price
        pnl_usd = shares * (exit_price - entry_price)
        row = sig_lag.iloc[i]
        trades.append({
            "ticker": ticker,
            "entry_date": dates[i].date().isoformat(),
            "exit_date": dates[i + HOLD_DAYS].date().isoformat(),
            "entry_price": round(entry_price, 4),
            "exit_price": round(exit_price, 4),
            "pnl_pct": round(pnl_pct, 4),
            "pnl_usd": round(pnl_usd, 4),
            "n_signals": n,
            "s1": bool(row.get("s1", False)),
            "s2": bool(row.get("s2", False)),
            "s3": bool(row.get("s3", False)),
            "s4": bool(row.get("s4", False)),
            "s5": bool(row.get("s5", False)),
        })
        next_allowed_i = i + HOLD_DAYS  # no overlapping positions in same name

print(f"  processed: {panel_counts['tickers_processed']}, skipped: {panel_counts['tickers_skipped']}")
print(f"  signal-count distribution across (ticker,day) pairs:")
for k in range(6):
    print(f"    {k} signals firing: {signal_fire_counts[k]:>10,}")

# --- save -----------------------------------------------------------------
trades_df = pd.DataFrame(trades)
movers_df = pd.DataFrame(movers)
trades_df.to_csv(OUT / "trades.csv", index=False)
movers_df.to_csv(OUT / "movers_30pct.csv", index=False)
print(f"\n  trades: {len(trades_df)} -> trades.csv")
print(f"  movers (30%+ in 10d): {len(movers_df)} -> movers_30pct.csv")

# --- aggregate ------------------------------------------------------------
def stats(df: pd.DataFrame) -> dict:
    if len(df) == 0:
        return {"n": 0}
    wins = df[df.pnl_pct > 0]
    losses = df[df.pnl_pct <= 0]
    out = {
        "n_trades": len(df),
        "win_rate": float((df.pnl_pct > 0).mean()),
        "avg_return_pct": float(df.pnl_pct.mean()),
        "median_return_pct": float(df.pnl_pct.median()),
        "avg_win_pct": float(wins.pnl_pct.mean()) if len(wins) else None,
        "avg_loss_pct": float(losses.pnl_pct.mean()) if len(losses) else None,
        "total_pnl_usd": float(df.pnl_usd.sum()),
        "best_trade_pct": float(df.pnl_pct.max()),
        "worst_trade_pct": float(df.pnl_pct.min()),
    }
    return out

summary = {"all_trades": stats(trades_df)}

if len(trades_df):
    trades_df["entry_month"] = pd.to_datetime(trades_df.entry_date).dt.to_period("M").astype(str)
    by_month = trades_df.groupby("entry_month").apply(
        lambda g: pd.Series({
            "n": len(g),
            "win_rate": (g.pnl_pct > 0).mean(),
            "avg_pct": g.pnl_pct.mean(),
            "total_pnl": g.pnl_usd.sum(),
        })
    )
    summary["by_month"] = by_month.to_dict(orient="index")

    # Stratify by n_signals
    summary["by_signal_count"] = {
        int(n): stats(trades_df[trades_df.n_signals == n])
        for n in sorted(trades_df.n_signals.unique())
    }

    # Signals s3 (lookahead) on vs off — see if it's load-bearing
    summary["s3_on_only"] = stats(trades_df[trades_df.s3])
    summary["s3_off_only"] = stats(trades_df[~trades_df.s3])

# Forensic stats on 30% movers
if len(movers_df):
    in_band = movers_df[(movers_df.start_close >= 0.50) & (movers_df.start_close <= 200.0)]
    summary["movers_30pct"] = {
        "n_windows": len(movers_df),
        "n_windows_in_price_band": len(in_band),
        "n_unique_tickers_in_band": int(in_band.ticker.nunique()),
        "signal_count_dist_in_band": in_band.n_signals.value_counts().sort_index().to_dict(),
        "frac_with_ge3_signals_in_band": float((in_band.n_signals >= 3).mean()) if len(in_band) else None,
        "avg_gain_pct_in_band": float(in_band.gain_pct.mean()) if len(in_band) else None,
    }

# Predictive lift: P(big gain | 3+ signals) vs P(big gain | <3 signals)
if len(trades_df):
    big = (trades_df.pnl_pct >= 30.0)  # did the 10-day return hit the 30% threshold?
    summary["predictive_lift"] = {
        "P_30pct_gain_given_3plus_signals": float(big.mean()),
        "n_3plus_signal_trades": int(len(trades_df)),
        "n_3plus_signal_30pct_winners": int(big.sum()),
    }
    # Compare to base rate computed from signal_fire_counts (trades NOT in trades_df because n<3)
    # Base rate of 30%+ 10d moves in the universe (denominator below) is approximated via
    # the movers_30pct count vs total (ticker,day) pairs evaluated:
    total_ticker_days = int(signal_fire_counts.sum())
    total_30pct_windows = int(len(movers_df))
    summary["base_rate"] = {
        "total_ticker_days_evaluated": total_ticker_days,
        "total_30pct_10d_windows": total_30pct_windows,
        "P_30pct_gain_unconditional": float(total_30pct_windows / total_ticker_days) if total_ticker_days else None,
    }

with open(OUT / "summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n=== HEADLINE STATS (all trades, 3+ signals required) ===")
s = summary["all_trades"]
print(json.dumps(s, indent=2))
if "movers_30pct" in summary:
    print("\n=== 30%+/10d MOVER FORENSICS ===")
    print(json.dumps(summary["movers_30pct"], indent=2))
