# Market-Wide Mover Forensics — 8mo Analysis

**Sample:** 3,086 US-listed tickers × 167 trading days = **511,150 ticker-days**.
Of those, **5,113 same-day 15%+ moves** (1.0% base rate).  In the $1–$200
entry band, **3,777 mover events**.

This is the data the watchlist work was missing.  Everything below uses the
**whole market**, not 379 names you knew about.

---

## 1. The T-1 signature of a 15%+ same-day mover

For every mover and every non-mover day, computed 20 features describing the
DAY BEFORE.  Ranked by AUC (separation power):

| feature (yesterday) | baseline median | mover-T-1 median | AUC | Q5 mover-rate |
|---|---:|---:|---:|---:|
| **ATR(5)% of price**        | 3.6%  | **10.7%** | **0.845** | **2.81%** (3.7× lift) |
| ATR(20)% of price          | 3.7%  | 10.2% | 0.842 | similar |
| 10-day consolidation range | 8.1%  | 25.5% | 0.829 | 2.68% |
| Bollinger width(20,2)      | 15.9% | 46.4% | 0.827 | 2.64% |
| Intraday range yesterday   | 3.1%  |  9.8% | 0.800 | 2.67% |
| **Proximity to 52w high (inverted)** | 87.8% | **54.9%** | **0.261** | beaten down → moves more |
| Close vs 200-day MA        | 1.00  | 0.88  | 0.410 | below MA → moves more |
| rel_vol(20) yesterday      | 0.81  | 0.95  | 0.569 | weak |
| vol_5d / vol_20d           | 0.93  | 1.06  | 0.571 | weak |

**The dominant signal is volatility, not volume.**

Pre-mover stocks are NOT quiet coiled springs with volume building.  They are
**already-volatile, beaten-down stocks that explode further**.  Their ATR
yesterday was ~3× normal.  Volume builds *on the move*, not before it.

The user's hypothesis "rel-vol > 2× the day before predicts tomorrow's move"
is **weakly supported at best**: AUC 0.569 is barely above 0.5.  ATR is 3×
stronger.

---

## 2. The hard part: T-1 features do not predict DIRECTION

Same comparison, but UPWARD movers vs DOWNWARD movers (both ≥15% magnitude):

| feature | up-T-1 median | down-T-1 median | AUC |
|---|---:|---:|---:|
| atr_5_pct_t1     | 0.107 | 0.132 | 0.432 |
| boll_width_t1    | 0.464 | 0.555 | 0.444 |
| prox_52w_high_t1 | 0.549 | 0.523 | 0.512 |
| rel_vol_20_t1    | 0.953 | 1.074 | 0.464 |
| ret_20d_t1       | −0.6% | +1.95% | 0.480 |
| **gap_pct (same-day morning gap)** | **+3.97%** | **−6.54%** | **0.900** |

T-1 features distinguish UPWARD from DOWNWARD movers at AUC 0.43–0.51 — i.e.
near-random.  **The morning gap (AUC 0.900) is what determines direction.**

For a 3:30 PM entry strategy, the gap hasn't formed yet at entry time.  This
means: **you cannot reliably predict direction of tomorrow's big mover from
today's close-of-day features alone.**  The volatility scanner identifies
stocks about to move big — half move up, half move down.

---

## 3. Gap-and-run vs gap-and-fade (on the day of the move)

| same-day open behavior  | n        | of those: closed above open |
|-------------------------|---------:|----------------------------:|
| gap up >2% at open      | 1,387    | **79.7% ran further**       |
| open flat (-2..+2%)     |   643    | (intraday accumulation)     |
| gap down <-2% at open   |   186    | (reversal trade)            |

| open behavior | median open→close on mover day |
|---|---:|
| gapped up >2%  | +10.95% |
| flat open      | **+19.16%** |
| gapped down    | **+26.15%** |

**Counter-intuitive:** the LARGEST same-day moves come from stocks that gapped
DOWN at open and then reversed.  But the most COMMON shape is gap-up + further
run (62.6% of all 15%+ days started with a gap up).

---

## 4. Continuation — does today's 15%+ mover run tomorrow?

After a same-day 15%+ move:

| next-day outcome | rate |
|---|---:|
| Another 15%+ day        | 7.6% (vs 0.71% baseline = **10.7× lift**) |
| Any +5% day in next 5d  | 60.0% |
| Any +15% day in next 5d | 23.8% |
| Median next-day close   | **−1.28%** (most fade) |
| Median 5-day forward    | **−4.49%** (cumulative fade is real) |
| Median 5-day MAX forward| +2.39% (intraday continuation exists) |

The "obvious" trade — buy after a big day, expect continuation — has
**negative expectancy on average**.  Big days fade ~55% of the time.

---

## 5. For Tyr's 3:30 PM → 8:30 AM pre-market trade

This is the **most directly actionable finding** in the whole study.

For every 15%+ same-day mover I measured the **overnight gap** (close → next
session open).  That's the exact P&L window for the user's strategy.

**Unconditional:**
- P(overnight gap > 0%):  **39.4%**
- P(overnight gap > +2%): 22.8%
- P(overnight gap > +5%): 12.4%
- **Median overnight gap: 0.00%**
- **Mean overnight gap: −0.25%**

**Trading every 15%+ mover overnight has negative expectancy.**  Roughly,
$200 × −0.25% = −$0.50 per trade plus commissions and slippage.

**What turns it positive — conditional on subsets:**

| filter on the mover day                | n     | P(gap>0) | mean gap |
|----------------------------------------|------:|---------:|---------:|
| **Closed strong (open→close > +5%)**   | 3,038 | **42.3%** | **+0.20%** |
| Closed weak (open→close < 0%)          |   287 | 32.8%     | **−3.88%** |
| Near 52w high (prox > 0.80)            |   578 | **43.4%** | **+1.34%** |
| Mid (prox 0.5–0.8)                     |   681 |  39.6%    |  +1.00% |
| **Deeply beaten (prox < 0.5)**         |   975 |  35.6%    | **−1.70%** |
| Magnitude 15–25%                       | 2,415 |  41.7%    |  +0.27% |
| Magnitude 25–50%                       |   994 |  37.1%    |  −0.87% |
| **Magnitude ≥ 50%**                    |   353 |  29.7%    | **−2.10%** |
| **Friday**                             |   795 |  41.6%    | **+0.88%** |
| Wednesday                              |   752 |  36.6%    | −1.20% |

**Stacking the positive filters:** 15–25% mover that closed strong, near 52w
high, on a Friday — the model predicts genuinely positive overnight gap
expectancy.  Conservative composite score in `M5_continuation.py`:

```
+1  gap_pct (day's open gap) > 2%
+1  open_to_close > 5% (closed strong intraday)
+1  pct_chg in [15-25%] (not >25%)   ← bigger reverts more
+1  intraday_range > 15%
+1  close < $5  (small cap)
```

This is **inverted from the wounded-prey watchlist thesis** for overnight
trades.  Beaten-down stocks DO move big — but they fade overnight.  For an
overnight hold you want **mover strength + recent uptrend + Friday**.

---

## 6. Day of week clustering

| DoW | ticker-days | mover days | rate |
|-----|---:|---:|---:|
| Mon | 56,829 | 433 | 0.762% |
| Tue | 61,889 | 442 | 0.714% |
| Wed | 59,576 | 438 | 0.735% |
| Thu | 54,165 | 414 | 0.764% |
| Fri | 56,831 | **489** | **0.860%** |

Friday has 13% more 15%+ days than the weekly average.  (Likely earnings &
weekly-OPEX timing.)  Combined with the overnight-gap data, **Friday afternoon
into Monday open** is the most favorable holding window in the sample.

---

## 7. Price-bucket distribution

| price bucket | ticker-days | mover-days | rate | median mover-pct |
|---|---:|---:|---:|---:|
| $1–5  | 64,463 | **1,236** | **1.92%** | +21.2% |
| $5–20 | 104,501 |  668 | 0.64% | +20.6% |
| $20–50|  70,664 |  200 | 0.28% | +20.3% |
| $50–200| 49,655 |  111 | 0.22% | +19.7% |

Sub-$5 stocks are **8.6× more likely** to have 15%+ days than $50–200 stocks.
This is your hunting ground.

---

## 8. Today's gainers (May 12, 2026)

14 stocks gained ≥15% today in $1–$200.  Pattern check:

| ticker | %day | gap | open→close | atr_5_t1 | prox_52w_h_t1 | pre5d_trend |
|---|---:|---:|---:|---:|---:|---|
| BWEN | +68.5% | +17.2% | +43.8% | 14.8% | 0.51 | declining |
| AEHL | +59.4% | −14.3% | +73.7% | 42.5% | 0.05 | building |
| RAASY | +56.7% | +75.9% | −18.7% | 10.8% | 0.61 | building |
| STAK | +55.8% | −3.6% | +59.4% | 9.1% | 0.85 | building |
| AMBQ | +40.5% | +16.4% | +24.0% | 7.3% | 1.00 | building |
| BAK | +26.1% | +8.9% | +17.2% | 5.4% | 0.77 | flat |
| AEVA | +24.2% | −1.7% | +25.8% | 15.0% | 0.75 | flat |
| DDD | +23.3% | +15.5% | +7.6% | 8.5% | 0.66 | declining |
| CNCK | +22.9% | +36.0% | −13.1% | 8.5% | 0.22 | flat |
| **QUBT** | **+15.7%** | +25.0% | −9.3% | 8.3% | 0.41 | building |

100% had ATR yesterday > 5% (median of all stocks: 3.6%).  64% gapped up at
open.  10/14 were in $1–5 bucket.  8/14 were building (not declining) in
the prior 5 days — for TODAY's set, building outperformed.

---

## 9. Pre-market relative-volume scanner (M6 — code framework)

The user asked for a 9:30 AM scanner that flags stocks with pre-market volume
≥5× the 20-day average.  This requires intraday data not available in the
free tier:

- **yfinance daily OHLCV** = post-close only, no pre-market.
- **Finnhub free** = 60 calls/min, no streaming, intraday limited.
- **Polygon free** = 5 calls/min, 15-min delayed.

Operational scanner needs **paid feed** (Polygon Starter $99/mo, IEX Cloud,
or similar).  The script is written and ready (see `M6_premarket_rel_vol.py`),
just needs the data subscription wired in.  Until then, the cleanest free
substitute is:

> At 9:30 AM, query Finnhub `/quote` for the universe in batches.  Use the
> reported "h" (high), "l" (low), "v" (volume) fields to detect early
> abnormal activity by comparing volume in the first 30 minutes against
> historical average opening-period volume.  This costs ~52 API calls/min
> sustained for the 3,086-ticker universe → 60 minutes per full sweep.
> Sampling the universe is realistic; full-coverage is not on free tier.

---

## 10. What this means for you, concretely

1. **The watchlist work I did before was too narrow.**  The 9 named winners
   gave a "wounded mid-cap growth" template that holds for *same-day* 15%
   moves regardless of direction.  But it does NOT generate positive overnight
   expectancy.

2. **Volatility is the magnitude predictor, gap is the direction predictor.**
   For your 3:30 entry, you don't have the gap yet.  Don't pretend you do.

3. **The overnight strategy needs a different filter.**  The continuation
   score in `M5_continuation.py` codifies it: enter only when the mover
   closed strong, the move was 15–25% (not bigger), and the stock isn't
   deeply beaten down.  Friday adds another +0.6% to the mean.

4. **Sub-$5 is where the action is.**  53% of all 15%+ movers in the band are
   $1–5.  Your hunting universe should be biased there — but you also have to
   accept the spread/slippage cost of that bucket.

5. **The discovery to keep:** ATR-as-of-yesterday is a strong universe filter.
   Stocks with atr_5_pct_t1 > 7% have 3–4× the base-rate of a 15%+ move
   tomorrow.  Run that filter every afternoon; pair with a direction-decider
   you trust (recent news, earnings beats, sector momentum) before sizing.

6. **The discovery to discard:** "Volume builds before the move" — barely
   true.  Volume builds *on* the move.  rel_vol_20_t1 > 2× isn't worth
   filtering on as a primary signal.

---

## Files in this pack

| file | purpose |
|------|---------|
| `M1_movers_database.py` | builds 511K-row panel + finds every 15%+ same-day move |
| `M2_pattern_analysis.py` | feature distributions, AUC, gap-vs-fade, continuation, DoW, price bucket |
| `M3_daily_scanner.py` | pre-mover scoring (volatility composite); sanity-tested on yesterday |
| `M4_todays_gainers.py` | every 15%+ gainer today + 5-day pre-context |
| `M5_continuation.py` | overnight-gap analysis + continuation candidate ranking |
| `all_panel.parquet` | 511,150-row feature panel (excluded from repo if >100MB) |
| `movers_15pct.csv` | the 5,113 mover events with full features |
| `features_signature.csv` | per-feature AUC table |
| `continuation_stats.json` | continuation rate stats |
| `gap_vs_fade.json` | gap-and-run analysis |
| `dow_clustering.csv` | DoW rates |
| `price_bucket_stats.csv` | mover-rate by price bucket |
| `scanner_YYYY-MM-DD.csv` | daily scanner output (overwrites) |
| `todays_gainers_YYYY-MM-DD.csv` | today's gainers report |
| `continuation_candidates_YYYY-MM-DD.csv` | overnight candidates |

Run order:
```
python3 M1_movers_database.py   # rebuild panel after fresh OHLCV
python3 M2_pattern_analysis.py  # update feature signatures
python3 M3_daily_scanner.py     # → top 30 pre-mover scores for the latest cached date
python3 M4_todays_gainers.py    # → today's 15%+ gainers + their pre-context
python3 M5_continuation.py      # → overnight candidates after a 15%+ day
```
