# Winner Profile + Watchlist Scan — 2026-05-12

## Method

Pulled 12 months of OHLCV, yfinance `.info`, yfinance `earnings_dates`, and SEC
EDGAR Form 4 purchases (transactionCode `P`) for nine named winners:

> MU, INOD, BATL, RKLB, RXT, FLNC, QUBT, NNE, AEVA

For each, defined **run-start** as the lowest close in the 60 trading days
before the 12-month high, then measured what was visible **at run-start**:
30-day prior trend, 52-week-high proximity, volume ratios, last earnings
surprise, insider purchase count.  Fundamentals (sector, market cap, short
interest) are **current snapshots** — not historical-at-run-start (Yahoo
doesn't expose history).

---

## What the 9 winners actually share

| feature                                | result                    | strong signal? |
|----------------------------------------|---------------------------|----------------|
| Below 70% of 52w high at run-start     | **7/9**                   | yes — wounded prey, not coiled springs |
| Pre-run trend was DECLINING (vs flat/building) | **6/9**           | yes — they fell *into* the move |
| Earnings BEAT in quarter before run    | **6/9**                   | moderate       |
| Currently >15% short interest          | **7/9** (median 20.8%)    | suggestive, but POST-run measurement |
| Currently >25% short interest          | **5/9**                   | suggestive, contaminated |
| Mid-cap ($300M–$10B)                   | **5/9** (plus 2 micro, 2 large) | concentrated mid-cap, with outliers |
| Sector ∈ {Tech, Industrials, Energy, Utilities} | **9/9**          | yes — clean cluster |
| Low analyst coverage (3–20)            | **8/9** (median 6)        | yes — under-followed |
| Revenue growth > 5%                    | **8/9**                   | yes |

## What the 9 winners DON'T share (theses that broke)

| feature                                | result          | implication |
|----------------------------------------|-----------------|-------------|
| Volume building (5d/30d ≥ 2.0x) before move | **0/9** (median 1.01) | volume builds **on** the move, not before. The "coiled spring with rising volume" template is wrong for this sample. |
| Form 4 insider purchases in 60d before run-start | **0/9 had any** (AEVA had 2) | Insider buying does NOT precede the move in this sample.  Looking for insider P transactions as a pre-run signal is unsupported. |

> Two of the framework's headline pre-run signals — volume buildup and
> insider buying — are not present in the winners we picked.  Either the
> sample is biased (we picked specific runners) or those signals don't
> actually fire before these kinds of moves.

---

## The profile that emerges

**Wounded mid-cap growth, deeply shorted, under-followed, with a recent
earnings beat that the market hadn't yet priced in.**

It looks like this:

- Price down 30–80% from its 52w high
- Already declining or flat in the 30 days before the move
- Mid-cap ($1–4B common, $300M–$10B range)
- Tech / Industrials / Energy / Utilities sector
- 3–20 analysts covering it (often single digits)
- Revenue growing meaningfully (often >50% YoY)
- Short interest already heavy (15–40%+)
- A recent earnings beat the chart didn't recover from

The catalyst that fires the move isn't necessarily new information — it's
the moment when shorts give up.  Volume only confirms after the price moves.

---

## Watchlist scan — top 20 matches

7-point matches (everything fits the profile):

| ticker | price | %52w-high | 30d trend | sector | mcap | short% | rev gr | analysts |
|--------|------:|----------:|----------:|--------|-----:|-------:|-------:|---------:|
| **SOUN** | $8.06  | 38% | +17% | Tech | $3.4B | 40% | +52%   | 8 |
| **BTDR** | $12.83 | 50% | +48% | Tech | $3.1B | 35% | +226%  | 11 |
| **ONDS** | $9.04  | 65% |  0%  | Tech | $4.5B | 34% | +629%  | 8 |
| **EOSE** | $8.10  | 42% | +63% | Industrials | $2.7B | 30% | +700% | 7 |
| **QUBT** | $11.78 | 48% | +72% | Tech | $2.7B | 30% | +94x  | 6 |
| **PATH** | $10.00 | 52% | −10% | Tech | $5.2B | 30% | +14%  | 16 |
| **RCAT** | $11.03 | 64% | −16% | Industrials | $1.4B | 27% | +849% | 4 |

6-point matches:

VG, GO, TMDX, LCID, UPST, SYM, TEM, FIG, AEVA, QLYS, RDW, QBTS, RGTI

(Full table in `watchlist_scored.csv`.)

---

## Your current holdings — graded against the profile

| ticker | shares | broker     | P/L  | score | what the profile says |
|--------|-------:|------------|-----:|------:|-----------------------|
| **QUBT** | 4   | Fidelity   |  —   | 7/7   | Best match in your book. Currently 48% of 52w high, +72% in last 30 days, 30% short, 94x rev growth. The setup is intact. |
| **VG**   | 5   | Robinhood  | +19% | 6/7   | 94% short interest is unusually deep. You're on the right side. |
| **FIG**  | 100 | Fidelity   | −35% | 6/7   | At 16% of 52w high — extremely beaten. Profile says it could run; reality says it's been broken since IPO. Hold/sell is a judgment call; the score doesn't override "why hasn't it caught a bid yet?" |
| **BATL** | 200 | Fidelity   | −85% | 4/7   | This is what happens after the +2,400% run. Now at 10% of 52w high, revenue declining, no analyst coverage. The move is over. You're holding the post-mania wreckage. |
| **TPET** | 100 | Fidelity   | −74% | 4/7   | $13M market cap. At 20% of 52w high. Down 43% in last 30 days alone. Same pattern as BATL. |
| **TMDE** | 500 | Fidelity   | −46% | 2/7   | $24M micro, doesn't match the profile at all. |
| **INTC** | 3   | Fidelity   |  —   | 2/7   | Already at 93% of 52w high (+173% in 30d). It's NOT the early setup — it's the late move you usually fade. |
| **BSX**  | 3   | Robinhood  |  —   | 2/7   | Mega-cap healthcare. Won't behave like winners in this sample. |

**The pattern in your book:** two of your positions (QUBT, VG) match the winner
profile cleanly.  Three (BATL, TPET, TMDE) are the SAME profile after the move
has already played out and rolled over — the trade was the run, and the run is
done.  The remainder are normal stocks, not profile candidates.

---

## Important caveats — read before doing anything

1. **N = 9.** This is not statistics, it's pattern observation.  The
   "profile" is a hypothesis worth testing, not a strategy.

2. **Survivorship bias.** We picked nine stocks because they ran.  We did
   not look at nine stocks with the SAME pre-run profile that *didn't* run.
   Without that, we can't measure precision — only describe what these
   particular survivors looked like.

3. **Current snapshot ≠ historical snapshot.** Short interest, revenue
   growth, and analyst count are TODAY's numbers, not what they were at
   run-start.  Some of these stocks attracted shorts AFTER they ran.
   Treat the short-interest match as a soft signal.

4. **Match score predicts resemblance, not return.**  A 7/7 means the
   stock looks like the winners' setup did.  It does not say the move
   will happen, or when.  Some stocks have looked like this for years.

5. **The next step that would make this real:** scan the same profile
   across the universe of stocks 6 months ago, hold for 30 days, measure
   what fraction of "7/7 matches" actually delivered ≥50% returns.  Until
   that's done, this is a hypothesis.

---

## Files

- `winners_profile.csv` — the 9 winners' run-start snapshots
- `winners_raw.json`    — same with insider-buy dates and 30d-prior trend detail
- `watchlist_parsed.json` — 379-ticker deduplicated watchlist
- `watchlist_scored.csv` — every ticker's score + components
- `watchlist_scored.json` — same with full match-component breakdown
- `W1_study_winners.py`, `W2_parse_watchlist.py`, `W3_scan_watchlist.py` — runnable scripts
