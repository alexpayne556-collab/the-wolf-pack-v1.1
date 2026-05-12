# WOLF PACK INTELLIGENCE — FENRIR'S COMPLETE KNOWLEDGE
# Transfer document: Claude Chat → Claude Code
# Written May 12, 2026
#
# Claude Code: READ THIS BEFORE EVERY SESSION.
# This contains 6 months of proven findings, killed hypotheses,
# behavioral patterns, sector analysis, and hard-won lessons
# from coordinated research across Claude, Perplexity, and DeepSeek.
# The human behind this is Tyr (Alex). He is building a systematic
# trading system to prove himself capable of managing a $750K portfolio.
# His current accounts total ~$850 across Fidelity and Robinhood.
# He is PDT restricted. He panic-sells on red days. The system must
# account for his psychology, not just the math.

---

## SECTION 1: WHAT THE DATA PROVED (May 11-12, 2026 brute force)

### CONFIRMED EDGES — USE THESE
1. EARNINGS GROWTH (top quintile) + LOW ANALYST COVERAGE (bottom quintile)
   Result: +3.43% per 10-day hold, 61.3% win rate
   Sample: 1,728 out-of-sample trades
   WHY: Growing companies nobody watches = systematically mispriced
   HOW TO USE: Screen for revenue/earnings growth >20% AND analyst count <=5
   BEST TIMING: Friday entry, morning, 5-day or 10-day hold

2. FLOAT_CHURN (daily volume / float shares > 30%)
   Result: 82% precision identifying repeat runners
   WHY: When daily volume exceeds 30% of available shares, forced
   turnover is happening — mechanical buying/selling, not discretionary
   HOW TO USE: Flag any stock where today's volume > 30% of float.
   These are likely to produce another 15%+ day within 14 days.

3. MULTI-LENS STACKING beats any single signal
   A stock appearing in 3+ independent signal lenses outperforms
   one appearing in 1 lens. The compound isn't one formula —
   it's convergence of independent signals agreeing.

4. DIVERSIFICATION beats concentration
   Top-30 basket: +3.43% mean, 61.3% WR
   Top-5 concentrated: LOSES money (-3.04%, 48% WR)
   THE EDGE IS NOISY. Any single pick can fail. The basket works.

5. TIMING
   Friday entry outperforms Tuesday by +5.13% spread
   Morning entry beats afternoon entry on compound-loaded names
   5-day hold beats overnight hold on these names
   Wednesday entry is second-best day

6. SECTOR-SPECIFIC EDGES
   Energy + Wednesday + earnings_growth q5: +6.3% train / +1.8% test
   Energy REVERSAL (drawdown + growth): 41.5% hit rate, +57% mean max gain
   These ONLY work in Energy sector. Do not generalize.

### REFUTED — NEVER USE THESE
1. WOUNDED PREY IS DEAD
   Buying stocks near 52-week lows produces ZERO lift
   pct_from_low correlates +0.43 with 30-day forward return
   MEANING: Stocks near HIGHS keep running. Stocks at lows stay dead.
   FILTER: Remove any stock trading below 50% of its 52-week high

2. COMPOUND LOADING AS SOLO BUY SIGNAL IS DEAD
   High short% + drawdown + small cap + low institutional = TRAP
   Lifts P(15%+ pop) to 23% BUT loses -2.4% per 10-day cycle
   The pops are real but crashes are equally likely
   MEANING: These stocks are volatile in BOTH directions
   USE AS: Volatility flag for position sizing, NOT direction signal

3. 3:30 PM ENTRY → NEXT-DAY OPEN = NO EDGE
   +0.03% mean, 47% win rate on compound-loaded names
   The prescribed entry timing is broken for this universe

4. SINGLE COMPOUND FORMULA = 21% precision (garbage)

5. PENNY STOCKS (<$1) pollute all signals. Exclude from analysis.

6. $1 LOTTO STRATEGY = worst quintile (-0.49%). Never use.

---

## SECTION 2: STRUCTURAL BOTTLENECK METHODOLOGY

This is Tyr's strongest edge. He identified MU (Micron) at $90
in December 2025 as the memory bottleneck for AI. MU is now $757.
That's +740% from understanding WHERE CAPITAL MUST FLOW.

### THE METHOD
1. Identify the MEGATREND (what the world MUST build)
2. Map the SUPPLY CHAIN (what does that physically require?)
3. Find the BOTTLENECK (which link is constrained?)
4. Identify the SPECIFIC NAMES at the bottleneck
5. Check if the market has priced it in yet
6. If not priced in → accumulate on red days, hold for months

### CURRENT BOTTLENECK MAP (May 2026)
- Copper: 330K ton US deficit → TGB $7.49, IE $13.90, ERO $28.48
- Power for data centers: demand +25% in 2025 → SMR $12.54, OKLO $72.51
- Helium: Qatar strike took 27-30% offline → LXFR $15.57
- SiC wafers: 40-80% spot premiums → WOLF $46.60
- Power transformers: 2-3 year backlogs → AMSC $55.19
- Advanced packaging: CoWoS maxed → AMKR $76.61
- PMICs: demand vs supply mismatch → POWI $73.28, ALGM $48.95
- Data center cooling: orders +65% YoY → NVT $169.95

### CRITICAL LESSON FROM MU
Tyr sold MU at ~$100 in a panic on a red day. It went to $757.
The thesis was RIGHT. The selling was WRONG. The thesis didn't
change on the red day — AI still needed memory, Micron still
made memory. The PRICE changed temporarily. The THESIS didn't.

For bottleneck trades: NEVER sell because the price dropped.
Only sell if the BOTTLENECK RESOLVED (new supply, substitute found,
demand collapsed). Red days are BUYING opportunities on thesis trades.

---

## SECTION 3: STOCK PERSONALITY CLASSIFICATION

Research confirmed (Liu, Management Science) that stocks have
persistent behavioral "personalities" driven by structural factors:

### WHAT DETERMINES HOW A STOCK MOVES
- Float size: Low float (<10M) = spike-and-fade, volatile
- Institutional ownership: High IO = staircase grind, less volatile
- ETF inclusion: More ETFs = more non-fundamental volatility
- Options activity: High OI + positive gamma = range compression (pinning)
- Options activity: High OI + negative gamma = trend amplification
- Short interest: High SI = periodic violent rallies then fade
- Analyst coverage: Low coverage = stronger post-earnings drift
- Bid-ask spread: Wide spread = strong daily reversals

### STOCK BEHAVIOR TYPES
TYPE 1 - SPIKE AND FADE: Low float, low IO, pump-driven. DON'T BUY.
TYPE 2 - DIP AND BOUNCE: High IO large-cap. Buy 10%+ dips, hold months.
  S&P Global data: +28% excess return over 240 days on Russell 1000 dips.
  But buy-the-dip FAILS on indices. Only works on individual high-IO stocks.
TYPE 3 - STAIRCASE GRIND: NVDA/MSFT type. High IO, high coverage.
  Just hold. Buying dips underperforms holding (AQR "Hold the Dip" 2025).
TYPE 4 - TRANSFORMER: $2 → $40 over months. Structural change.
  MU, INOD, BATL examples. These are the thesis trades.
TYPE 5 - OSCILLATOR: Range-bound. Trade the range if you must.

### POST-EARNINGS BEHAVIOR
- Stocks that beat earnings AND have low analyst coverage drift UP
  for 60+ days (Post-Earnings Announcement Drift, academic finding)
- This effect has REVERSED in liquid, optionable stocks (Milian 2015)
- PEAD only survives in small, low-coverage stocks
- This confirms our Quiet Growers formula

---

## SECTION 4: WHAT MOVES STOCKS (PRACTICAL REALITY)

### EARNINGS BEATS (#1 mover)
Company beats estimates → gap up → drift continues for weeks
if the stock is small-cap with low coverage.
PREDICTORS: Consecutive beat streak, revenue acceleration,
raised guidance, insider buying before earnings.

### CONTRACTS AND DEALS
New major contract (INOD $51M Big Tech deal) → gap + hold
FDA approval → gap + hold (biotech)
Government award → gap + hold (defense)
VISIBLE ON: SEC EDGAR 8-K filings (free, real-time)

### INSIDER BUYING
CEOs/directors buying with personal money = confidence signal
Cluster buys (multiple insiders buying same week) are strongest
VISIBLE ON: SEC EDGAR Form 4, OpenInsider.com (free)
Academic evidence: insider cluster buys outperform by ~6% annually

### SECTOR ROTATION
When a theme catches fire (defense drones, EV battery, AI infra):
- Leader runs Day 1
- Second movers run Days 2-3
- Third movers run Days 4-5
The play is NOT the leader. It's the loaded names in same sector
that HAVEN'T moved yet.
Example: RXT +208% → sympathy plays IIIV, VELO, INDI

### SHORT SQUEEZE
High SI + real catalyst = forced covering
But HIGH SI ALONE IS A TRAP (proved by our data: -2.4%/cycle)
Only trade squeezes when there's a FUNDAMENTAL catalyst
that BREAKS the bear thesis

### GEOPOLITICAL FORCED FLOW
War/conflict → defense stocks
Oil disruption → energy stocks
Tariffs → reshoring/domestic manufacturing
These flows last WEEKS TO MONTHS, not days
BATL +2062% came from Iran/Hormuz thesis

---

## SECTION 5: TYR'S PSYCHOLOGY (CRITICAL FOR THE SYSTEM)

### THE PANIC PATTERN
Tyr buys → stock goes red → panic sells → stock recovers without him
This happened with MU ($100 → $757 after he sold)
This happened with INOD (sold before doubling)
This happens repeatedly

### HOW THE SYSTEM MUST COMPENSATE
1. Every trade must be classified BEFORE entry:
   THESIS (hold weeks/months), TACTICAL (hold exact # of days),
   WAVE (hold until sector wave breaks)
2. Every trade needs a THESIS CARD: one sentence explaining WHY
3. On red days, the system reminds him to READ THE THESIS CARD
4. Thesis trades: NEVER sell on red unless the THESIS broke
5. Tactical trades: sell on the predetermined date, no exceptions
6. Wave trades: sell when the sector leader reverses

### WHAT TYR IS GOOD AT
- Identifying structural bottlenecks (MU, copper, helium, SiC)
- Seeing geopolitical connections (Iran → oil → defense → BATL)
- Understanding WHY something matters before others do
- Pushing AI systems to go deeper than surface-level answers

### WHAT TYR NEEDS HELP WITH
- Not panic selling on red days
- Not chasing stocks that already ran
- Not jumping between too many names
- Waiting for the system to confirm before buying
- Staying disciplined to a plan for more than 1-2 days

---

## SECTION 6: THE ACADEMIC FOUNDATION

### KEY PAPERS DISCOVERED (Perplexity Deep Research May 10-11)
- Soebhag 2023: Gamma exposure predicts returns, 10%/yr spread
- AEA 2026 "Seeking Gamma": 641 gamma squeeze events, 5.13% CAR
- Brunnermeier-Pedersen 2009: Liquidity spirals > sum of parts
- Wiersema 2022: Interacting forced channels > individual channels
- Barbon et al 2022: Two forced-flow channels simultaneously (closest paper)
- Liu (Management Science): Idiosyncratic volatility autocorrelation 0.39 at 1 month
- Ang et al (Columbia): High IVOL = low future returns
- S&P Global 2018: Buy individual stock dips +28% excess at 240 days
- AQR "Hold the Dip" 2025: Buy-the-dip FAILS at index level

### THE ACADEMIC GAP
No paper has tested the full multi-factor compound on individual stocks.
This is the gap our system fills with data, not theory.

---

## SECTION 7: REGIME DETECTION

### CHECK THESE DAILY (all free)
| Indicator | Bull | Normal | Repricing | Crisis |
|---|---|---|---|---|
| VIX level | <15 | 15-20 | 20-30 | >30 |
| VIX vs 200-DMA | Below | Near | Crossing | Above |
| VIX term structure | Normal | Normal | Flat | Inverted |
| HY OAS (FRED) | Tight | Normal | Widening | Blowing |
| XLY/XLP ratio | Rising | Flat | Falling | Collapsed |

When 3+ indicators flip = REGIME CHANGE. Adjust strategy.
Current regime (May 12, 2026): NORMAL (VIX 18.38)

---

## SECTION 8: CURRENT POSITIONS

### FIDELITY
- INTC: 3 shares @ $123.37 avg (AI foundry, Apple chip deal)
- QUBT: 4 shares @ $12.70 avg (quantum computing, up 26% May 12)
- Cash: $47.75

### ROBINHOOD
- VG: 5 shares @ $13.50
- BSX: 3 shares @ $54.29 (medical devices, virus thesis)
- Cash: $129.41

### THESIS CARDS
INTC: "Intel is building chips for Apple. AI needs foundry capacity.
Hold until foundry thesis breaks."
QUBT: "Quantum computing is next after AI. Speculative. Small position.
Hold for weeks minimum."
BSX: "Hantavirus fears increase healthcare spending. Hold."

---

## SECTION 9: TRADING RULES

1. Position size: ~$200 per name maximum
2. Max concurrent positions: 4-5 across both accounts
3. PDT restricted in both accounts
4. Never sell a thesis trade on a red day
5. Paper trade new strategies for 30 trades before real money
6. Every trade gets classified: THESIS / TACTICAL / WAVE
7. Every trade gets a one-sentence thesis card
8. If win rate drops below 50% over 30 trades, kill the strategy
9. Check regime indicators before any new position
10. Don't chase stocks that already moved 20%+ in 5 days

---

## SECTION 10: WHAT TO BUILD FOR JUNE

### THE DAILY PIPELINE
Morning scan → regime check → earnings calendar → insider check →
signal convergence → ranked watchlist → thesis cards for top picks

### DATA SOURCES TO EVALUATE
- FMP API ($29/mo) — earnings estimates, fundamentals, screener
- Unusual Whales ($48/mo) — options flow, dark pool
- SEC EDGAR (free) — insider buying, 8-K filings
- FINRA (free) — short interest
- FRED (free) — VIX, credit spreads, regime indicators
- yfinance (free) — price data, historical earnings

### THE PROVE-IT-OR-KILL-IT TEST
Before spending on paid data: test whether free signals
(insider buying + earnings beats + volume surge + near-high)
predicted 30%+ movers in the last 6 months. If yes, paid data
enhances what already works. If no, find different signals.

### GIT REPO
Everything persists in git. Commit after every major output.
No work should ever be lost between sessions.

---

## SECTION 11: MISTAKES WE MADE (DON'T REPEAT)

1. Built 63-cell neural network (Nov 2025). Too complex. Killed.
2. Built Alpha Companion (Dec 2025). Never finished. Pivoted.
3. Built Thesis Companion. Never finished. Pivoted.
4. Built Wolf Mind with 78 cells via br0kkr. Never operational.
5. Built War Room HTML dashboard. Never used. Abandoned.
6. Built P1-P12 pattern library. Killed as descriptive not predictive.
7. Identified Signal Log as critical need in January. STILL NOT BUILT.
8. Every system was a cathedral. None became a working shed.

LESSON: Build the smallest useful thing first. Get it working.
Then expand. Don't design the whole system before testing anything.

---

# END OF INTELLIGENCE TRANSFER
# Claude Code: Apply this knowledge to EVERY analysis you run.
# When in doubt, check this document. The answers are here.
# Update this document with new findings as they emerge.
# AWOOOO.
