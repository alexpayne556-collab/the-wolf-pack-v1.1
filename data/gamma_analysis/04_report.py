"""
Render the pass-or-fail verdict from summary.json + trades.csv.

Decision rule (user-specified):
  win rate >= 60% AND total P&L > 0  -> PASS  (buy paid data, go live)
  win rate <= 50%                    -> FAIL  (signals don't work, try different)
  in between                         -> AMBIGUOUS  (more data / refinement)
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

OUT = Path(__file__).parent
summary = json.loads((OUT / "summary.json").read_text())
trades = pd.read_csv(OUT / "trades.csv") if (OUT / "trades.csv").exists() else pd.DataFrame()
movers = pd.read_csv(OUT / "movers_30pct.csv") if (OUT / "movers_30pct.csv").exists() else pd.DataFrame()

s = summary.get("all_trades", {})
n = s.get("n_trades", 0)
wr = s.get("win_rate", 0) or 0
total = s.get("total_pnl_usd", 0) or 0
avg = s.get("avg_return_pct", 0) or 0

def verdict():
    if n == 0:
        return "INCONCLUSIVE", "No trades fired. Signals never reached 3+ together — strategy is unusable as written."
    if wr >= 0.60 and total > 0:
        return "PASS", f"Win rate {wr:.1%} >= 60% AND total P&L ${total:,.2f} > 0. Buy the paid data, go live."
    if wr <= 0.50:
        return "FAIL", f"Win rate {wr:.1%} <= 50%. Signals don't work as a combined filter. Try different signals."
    return "AMBIGUOUS", f"Win rate {wr:.1%} between 50% and 60%. Not a clear pass — refine signals or test more data before risking real money."

label, rationale = verdict()

lines = []
lines.append(f"# PROVE-OR-KILL BACKTEST — {label}")
lines.append("")
lines.append(f"**Rationale:** {rationale}")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Strategy")
lines.append("Buy $200 when >= 3 of 5 signals fire (point-in-time, no lookahead except S3); hold 10 trading days; close-to-close.")
lines.append("")
lines.append("**Signals**")
lines.append("- S1: Form 4 insider open-market purchase (code P) in past 60 days (filingDate)")
lines.append("- S2: Most recent ANNOUNCED earnings before entry day had surprisePercent > 0")
lines.append("- S3: Current short interest > 20% of float  ⚠️ LOOKAHEAD — snapshot only, no historical archive accessible")
lines.append("- S4: 3-day avg volume ending D-1 >= 2.0x trailing 20-day avg")
lines.append("- S5: Close on D-1 within 5% of trailing 252-day high")
lines.append("")
lines.append("## Headline")
lines.append(f"- Trades: **{n:,}**")
lines.append(f"- Win rate: **{wr:.2%}**")
lines.append(f"- Avg return per trade: **{avg:+.2f}%**")
lines.append(f"- Total P&L on $200/trade: **${total:+,.2f}**")
lines.append(f"- Avg win: **{(s.get('avg_win_pct') or 0):+.2f}%**, avg loss: **{(s.get('avg_loss_pct') or 0):+.2f}%**")
lines.append(f"- Best trade: **{(s.get('best_trade_pct') or 0):+.2f}%**, worst: **{(s.get('worst_trade_pct') or 0):+.2f}%**")
lines.append("")
by_month = summary.get("by_month") or {}
if by_month:
    lines.append("## By month")
    lines.append("| month | n | win rate | avg pct | total P&L |")
    lines.append("|------:|--:|---------:|--------:|----------:|")
    for m, row in sorted(by_month.items()):
        lines.append(f"| {m} | {int(row['n'])} | {row['win_rate']:.1%} | {row['avg_pct']:+.2f}% | ${row['total_pnl']:+,.2f} |")
    lines.append("")
    months = list(by_month.items())
    best = max(months, key=lambda x: x[1]["total_pnl"])
    worst = min(months, key=lambda x: x[1]["total_pnl"])
    lines.append(f"- **Best month:** {best[0]} (${best[1]['total_pnl']:+,.2f})")
    lines.append(f"- **Worst month:** {worst[0]} (${worst[1]['total_pnl']:+,.2f})")
    lines.append("")

bsc = summary.get("by_signal_count") or {}
if bsc:
    lines.append("## By signal count")
    lines.append("| n_signals | trades | win rate | avg pct | total P&L |")
    lines.append("|----------:|-------:|---------:|--------:|----------:|")
    for k in sorted(bsc.keys(), key=int):
        st = bsc[k]
        lines.append(f"| {k} | {st['n_trades']} | {(st.get('win_rate') or 0):.1%} | {(st.get('avg_return_pct') or 0):+.2f}% | ${(st.get('total_pnl_usd') or 0):+,.2f} |")
    lines.append("")

s3on = summary.get("s3_on_only", {})
s3off = summary.get("s3_off_only", {})
if s3on.get("n_trades") or s3off.get("n_trades"):
    lines.append("## S3 isolation (does the lookahead signal carry the strategy?)")
    lines.append("| variant | trades | win rate | avg pct | total P&L |")
    lines.append("|---------|-------:|---------:|--------:|----------:|")
    for label_, st in (("s3 ON", s3on), ("s3 OFF", s3off)):
        if st.get("n_trades"):
            lines.append(f"| {label_} | {st['n_trades']} | {(st.get('win_rate') or 0):.1%} | {(st.get('avg_return_pct') or 0):+.2f}% | ${(st.get('total_pnl_usd') or 0):+,.2f} |")
    lines.append("")
    lines.append("> If S3=ON dominates the P&L, the headline number is partially driven by lookahead.")
    lines.append("")

m = summary.get("movers_30pct", {})
if m:
    lines.append("## 30%+/10d mover forensics")
    lines.append(f"- 10-day windows with 30%+ gain (overlapping allowed): **{m.get('n_windows',0):,}**")
    lines.append(f"- Windows in $0.50-$200 entry band: **{m.get('n_windows_in_price_band',0):,}**")
    lines.append(f"- Unique tickers in band: **{m.get('n_unique_tickers_in_band',0):,}**")
    lines.append(f"- Fraction of those that had 3+ signals at window start: **{(m.get('frac_with_ge3_signals_in_band') or 0):.1%}**")
    sd = m.get("signal_count_dist_in_band") or {}
    if sd:
        lines.append(f"- Signal-count distribution: {dict(sorted(sd.items(), key=lambda x: int(x[0])))}")
    lines.append("")

br = summary.get("base_rate", {})
pl = summary.get("predictive_lift", {})
if br and pl:
    p_uncond = br.get("P_30pct_gain_unconditional") or 0
    p_cond = pl.get("P_30pct_gain_given_3plus_signals") or 0
    lift = (p_cond / p_uncond) if p_uncond else None
    lines.append("## Predictive lift")
    lines.append(f"- Unconditional P(30%+ gain in next 10 days) over universe: **{p_uncond*100:.3f}%**")
    lines.append(f"- Conditional P(30%+ gain | 3+ signals): **{p_cond*100:.2f}%**")
    if lift is not None:
        lines.append(f"- Lift: **{lift:.1f}x**  (1.0 = no edge, < 1.0 = anti-signal)")
    lines.append("")

# Top winners / losers
if len(trades):
    lines.append("## Top 10 winners")
    top = trades.nlargest(10, "pnl_pct")[["entry_date","ticker","entry_price","exit_price","pnl_pct","pnl_usd","n_signals","s1","s2","s3","s4","s5"]]
    lines.append(top.to_markdown(index=False))
    lines.append("")
    lines.append("## Top 10 losers")
    bot = trades.nsmallest(10, "pnl_pct")[["entry_date","ticker","entry_price","exit_price","pnl_pct","pnl_usd","n_signals","s1","s2","s3","s4","s5"]]
    lines.append(bot.to_markdown(index=False))
    lines.append("")

lines.append("## Caveats")
lines.append("- **Universe:** 3,086 US-listed tickers from SEC company_tickers.json with valid 8-month yfinance history and avg close in $0.50-$200. Not the full 4,841 you assumed cached — those DBs were empty.")
lines.append("- **S3 lookahead:** historical biweekly short-interest archive isn't accessible from this environment (FINRA paywalled the public CSV; NASDAQ API returned 503). S3 uses today's snapshot statically. The 's3 ON vs OFF' table above shows how much of the result this contaminates.")
lines.append("- **Execution model:** close-to-close fills. Real fills include slippage, partial fills, halted tickers; backtest is an upper bound.")
lines.append("- **Survivorship:** SEC tickers list as of today omits delisted names. Strategy P&L on small caps is biased upward by ~3-5% typically.")
lines.append("- **Borrow / hard-to-borrow:** not modeled. Real shorts of high-SI names cost.")
lines.append("- **Earnings drift / pre-announcement runs:** S2 uses actual announcement date+time. No quarter-end lookahead.")
lines.append("")
lines.append("## What this tells you")
if label == "PASS":
    lines.append("- The combined 3+ signal filter has positive expectancy on this data over this window. NEXT STEP: re-run on a different 6-month window (e.g., 2024 H2) for out-of-sample. If it holds, the signals are real. If it falls apart, the 6-month window we tested was a regime-specific gift.")
elif label == "FAIL":
    lines.append("- The signal combo as defined does not produce profitable 10-day trades on this universe. The hypothesis is dead. Stop refining the SAME signals — they were chosen for narrative fit, not predictive power. Consider: trend persistence (post-breakout follow-through), liquidity-adjusted volume z-scores, or sector momentum. Throw out the 'compound mechanics' framework as currently specified.")
else:
    lines.append("- Between pass and fail. Don't go live yet — refine, then re-test. Likely candidates: tighten the volume signal (3-day avg vs 60-day median z-score), or replace the short-interest signal with something point-in-time (FTD list).")
lines.append("")

out_md = OUT / "report.md"
out_md.write_text("\n".join(lines))
print(f"wrote {out_md}")
print(f"\nVERDICT: {label}")
print(rationale)
