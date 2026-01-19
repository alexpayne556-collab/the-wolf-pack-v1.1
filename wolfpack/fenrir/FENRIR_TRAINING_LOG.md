# 🐺 FENRIR TRAINING LOG - LIVE CAPTURE
## Real workflow documentation from actual trading sessions

**Purpose**: Every time we manually do something, we document it so Brokkr can code Fenrir to do it automatically.

**NOT hypothetical features. ACTUAL needs from real trading.**

---

## TRAINING SESSION #1 - January 16, 2026

### CAPTURED PATTERNS (20 Total)

#### #1: Form 144 Insider Filing Analysis
**SITUATION**: Found Form 144 for KTOS officer selling shares  
**MANUAL WORK**:
- Read filing
- Check plan adoption date (Aug 2025)
- Compare to stock run timing (Jan 2026)
- Calculate % of float (0.01%)
- Determine if RSU/PSU or discretionary
- Conclude: routine, not concerning

**SECRETARY SHOULD**:
- Auto-fetch Form 144 filings for watchlist
- Parse key fields (who, how much, when planned)
- Score concern level (green/yellow/red)
- Only alert if yellow+
- Green = log silently for daily summary

**ALERT TYPE**: Info (unless red flag)  
**MODULE**: `insider_analyzer.py`

---

#### #2: 52-Week High / Blue Sky Detection
**SITUATION**: IBRX broke 52-week high, entered blue sky  
**MANUAL WORK**: Had to search to realize it broke ATH, no overhead resistance  
**SECRETARY SHOULD**: Track key levels per position, alert "BLUE SKY - no overhead resistance"  
**ALERT TYPE**: Info  
**MODULE**: `level_tracker.py`

---

#### #3: Catalyst Stacking
**SITUATION**: IBRX had revenue news Day 1, CAR-NK data Day 2 - almost missed the second  
**MANUAL WORK**: Had to piece together multiple news items  
**SECRETARY SHOULD**: Track multiple catalysts per ticker, note when they STACK  
**ALERT TYPE**: High Priority  
**MODULE**: `catalyst_stacker.py`

---

#### #4: Sector Chain Understanding
**SITUATION**: Trump policy - CEG/VST down ≠ UEC/UUUU down (different thesis)  
**MANUAL WORK**: Had to figure out power utilities vs uranium miners are DIFFERENT  
**SECRETARY SHOULD**: Understand sector CHAINS - power utilities vs uranium miners  
**ALERT TYPE**: Context  
**MODULE**: `sector_chain.py`

---

#### #5: SMR Timeline Reality Check
**SITUATION**: Asked "who builds reactors, how close?" - had to dig  
**MANUAL WORK**: Research realistic timelines vs hype  
**SECRETARY SHOULD**: Maintain catalyst calendars with REALISTIC timelines, not hype  
**ALERT TYPE**: Background  
**MODULE**: `catalyst_calendar.py`

---

#### #6: Volume Context
**SITUATION**: IBRX 138M volume vs 13M avg (10x) - critical signal  
**MANUAL WORK**: Had to calculate volume ratio manually  
**SECRETARY SHOULD**: Always show volume vs average, flag 3x+ as significant  
**ALERT TYPE**: Info (critical if 3x+)  
**MODULE**: `volume_analyzer.py`

---

#### #7: Days Into Run Tracking
**SITUATION**: IBRX Day 10-11 of run - had to figure this out  
**MANUAL WORK**: Count days since first big move  
**SECRETARY SHOULD**: Auto-track "days into run" from first big move  
**ALERT TYPE**: Info  
**MODULE**: `run_tracker.py` (already built!)

---

#### #8: Analyst PT Changes
**SITUATION**: KTOS got multiple upgrades this week - pieced together  
**MANUAL WORK**: Track analyst actions across sources  
**SECRETARY SHOULD**: Aggregate analyst actions, alert on clusters  
**ALERT TYPE**: Info  
**MODULE**: `analyst_aggregator.py`

---

#### #9: Contract Value Context
**SITUATION**: KTOS $231M contract - is that big for them?  
**MANUAL WORK**: Compare contract to revenue/backlog  
**SECRETARY SHOULD**: Compare contract size to revenue, backlog  
**ALERT TYPE**: Context  
**MODULE**: `contract_analyzer.py`

---

#### #10: News Recycling Detection
**SITUATION**: Same IBRX story on multiple sites - is it new or rehash?  
**MANUAL WORK**: Cross-reference timestamps and sources  
**SECRETARY SHOULD**: Dedupe news, identify ORIGINAL source and time  
**ALERT TYPE**: Background  
**MODULE**: `news_deduper.py`

---

#### #11: Sector-Wide Analyst Calls
**SITUATION**: Morgan Stanley upgraded entire space sector today (Jan 16)  
**MANUAL WORK**: Had to search to find this  
**SECRETARY SHOULD**: Track analyst sector calls, not just individual stocks  
**ALERT TYPE**: Info - "Space sector upgraded by Morgan Stanley"  
**MODULE**: `analyst_tracker.py`

---

#### #12: Sector-Wide Insider Trends
**SITUATION**: Quantum insiders sold $840M net over 3 years  
**MANUAL WORK**: Found in article, not obvious  
**SECRETARY SHOULD**: Track SECTOR-WIDE insider trends, not just individual  
**ALERT TYPE**: Warning - "Quantum sector insider selling heavy"  
**MODULE**: `sector_insider_tracker.py`

---

#### #13: PDUFA Calendar
**SITUATION**: PDUFA dates are binary events for biotech  
**MANUAL WORK**: Had to search FDA calendar  
**SECRETARY SHOULD**: Maintain PDUFA calendar, alert before decisions  
**ALERT TYPE**: Upcoming - "VNDA PDUFA Feb 21 - binary event"  
**MODULE**: `fda_calendar.py`

---

#### #14: Policy Impact Mapping
**SITUATION**: Trump policy moves different sectors differently  
**MANUAL WORK**: Had to parse that utilities DOWN but uranium UP  
**SECRETARY SHOULD**: Map policy → sector impact chains  
**ALERT TYPE**: Context - "Trump power plant news: CEG/VST down, UEC/UUUU unaffected"  
**MODULE**: `policy_impact_mapper.py`

---

#### #15: After Hours Anomaly Detection
**SITUATION**: IVF up 192% after hours  
**MANUAL WORK**: See it on screen, no idea why  
**SECRETARY SHOULD**: Auto-search news when >20% AH move detected  
**ALERT TYPE**: URGENT - "IVF +192% AH - searching for catalyst..."  
**MODULE**: `ah_anomaly_detector.py`

---

#### #16: Reversal Detection (Day vs AH)
**SITUATION**: VERO +459% 2-day but -22% AH (reversal)  
**MANUAL WORK**: Have to notice the disconnect manually  
**SECRETARY SHOULD**: Flag when AH move OPPOSES day move by >10%  
**ALERT TYPE**: WARNING - "VERO showing reversal: +459% day, -22% AH"  
**MODULE**: `reversal_detector.py`

---

#### #17: News → Price Connection
**SITUATION**: TLN -11.31% (power sector from Trump news)  
**MANUAL WORK**: We researched this earlier, now seeing impact  
**SECRETARY SHOULD**: Connect news to price moves across sector  
**ALERT TYPE**: CONTEXT - "TLN -11% tied to Trump power plant policy"  
**MODULE**: `news_price_connector.py`

---

#### #18: 13D Filing Scanner for Squeeze Setups
**SITUATION**: VERO 700% intraday on 13D filing showing 91% ownership  
**MANUAL WORK**: Had to dig through news to find 13D catalyst  
**SECRETARY SHOULD**:
- Auto-scan 13D filings for ownership >50%
- Flag "delisting" or "deregistration" language
- Calculate remaining float after major acquisitions
- Alert: "VERO: 91% acquired, potential delisting discussed"

**ALERT TYPE**: URGENT + CONTEXT  
**MODULE**: `sec_filing_scanner.py` (13D focus)

---

#### #19: Rumor Tracking
**SITUATION**: IVF +192% on UNCONFIRMED rumor about Trump policy  
**MANUAL WORK**: Couldn't find news via search, user found on Benzinga  
**SECRETARY SHOULD**:
- Monitor Benzinga, StockTwits for rumor circulation
- Flag "unconfirmed" or "rumor" language
- Cross-reference with related tickers (NIVF, other fertility)
- Alert: "IVF +192% - RUMOR: Trump fertility policy - UNCONFIRMED"

**ALERT TYPE**: SPECULATIVE - High risk  
**MODULE**: `rumor_tracker.py`

---

#### #20: Market Wrap Auto-Parsing
**SITUATION**: Reuters article contained 8+ actionable pieces of intel  
**MANUAL WORK**: User had to read and share manually  
**SECRETARY SHOULD**:
- Auto-parse Reuters/Bloomberg market wrap articles
- Extract: sector movers, policy news, Fed commentary, earnings calendar
- Cross-reference with holdings
- Alert: "MU mentioned in Reuters - AI demand thesis confirmed"

**ALERT TYPE**: Daily Summary  
**MODULE**: `market_wrap_parser.py`

---

## BUILD PRIORITY QUEUE

### Priority 1 - Core Intelligence (Need These First)
1. **insider_analyzer.py** - Form 144, Form 4 parsing + context scoring
2. **run_tracker.py** - ✅ BUILT - Days into run, volume trends
3. **catalyst_stacker.py** - Multiple catalysts per ticker, timeline tracking
4. **level_tracker.py** - Support/resistance, 52-week, ATH alerts
5. **ah_anomaly_detector.py** - After hours >20% moves with auto-news search

### Priority 2 - Context Layers + Position Management
6. **sector_chain.py** - Understand related plays (CEG news → check UEC)
7. **news_deduper.py** - Find original source, ignore rehashes
8. **analyst_aggregator.py** - Track PT changes, upgrade/downgrade clusters
9. **contract_analyzer.py** - Size vs revenue, materiality check
10. **policy_impact_mapper.py** - Map policies to sector chains
11. **position_health_checker.py** - ✅ BUILT - Dead money detection, reallocation alerts (Note #21)
12. **thesis_tracker.py** - ✅ BUILT - Thesis strength scoring, validation framework (Note #22)

### Priority 3 - Pattern Recognition
13. **reversal_detector.py** - Day vs AH divergences
14. **volume_profiler.py** - Volume context with historical comparison
15. **sec_filing_scanner.py** - 13D/13G for squeeze setups
16. **rumor_tracker.py** - Social/news rumor detection
17. **market_wrap_parser.py** - Auto-parse daily wrap articles

### Priority 4 - Specialized Trackers
18. **sector_insider_tracker.py** - Sector-wide insider trends
19. **fda_calendar.py** - PDUFA dates for biotech
20. **catalyst_calendar.py** - Realistic timeline tracking

---

## NATURAL LANGUAGE UNDERSTANDING

**CRITICAL REQUIREMENT**: System must understand natural language queries, not just keywords.

### Examples of How User Communicates:
- "what's moving after hours?" → Run ah_anomaly_detector
- "check IBRX" → Full analysis with run tracker, levels, catalysts
- "why is TLN down?" → News search + sector context + policy impact
- "scan defense" → Filter scanner for defense sector
- "any insider selling?" → Check insider filings for watchlist

### LLM Integration Needed:
- Use local Ollama "fenrir" model to parse user intent
- Map natural language → module functions
- Extract tickers, sectors, timeframes from conversational input
- Remember context from previous queries in session

### Voice/Text Input Processing:
```python
User: "yo what's that stock up 192% in after hours?"
Fenrir: 
  1. Detect: after hours anomaly query
  2. Run: ah_anomaly_detector.get_top_movers(min_pct=100)
  3. Find: IVF +192%
  4. Search: news_search("IVF", hours=2)
  5. Context: "Trump fertility rumor (UNCONFIRMED)"
  6. Alert: "IVF +192% AH on UNCONFIRMED Trump fertility policy rumor - HIGH RISK"
```

---

## SECTOR INTELLIGENCE CAPTURED

### Space Sector (HOT - Jan 16)
**Catalyst**: Morgan Stanley upgrade today
- **RKLB**: +20% YTD, Neutron rocket 2026, $816M SDA contract
- **ASTS**: +28% YTD, 45-60 satellites EOY 2026
- **LUNR**: +17% YTD, $4.6B NASA contract pending

### Quantum (CAUTION)
**Red Flag**: Insiders sold $840M more than bought (3 years)
- IONQ, RGTI, QBTS, QUBT - all P/S ratios 100x+
- Billionaires buying GOOGL instead (Willow chip)

### Nuclear/Power (SPLIT STORY)
**Trump Policy**: Tech should pay for power plants
- **Utilities DOWN**: CEG -5%, VST -9%, TLN -11%
- **Uranium BULLISH**: More plants = more fuel demand
- **SMR Builders**: Years from revenue (speculative)

### Defense (TRUMP TAILWIND)
**Catalyst**: $1.5T budget proposal 2027
- KTOS: $231M Marine Corps contract
- Drone sector focus

### Biotech (FDA CALENDAR CRITICAL)
**Key PDUFA Dates**:
- Eli Lilly Orforglipron: Soon (oral GLP-1)
- VNDA Bysanti: Feb 21
- RYTM Imcivree: Mar 20
- Rocket Pharma: Mar 28

---

## ACTUAL TRADE EXAMPLES FROM SESSION

### IBRX (Our Position) ✅
- **Entry**: 37 shares @ $4.69
- **Current**: $5.52 (+39.75% 2-day)
- **Catalyst Day 1**: Revenue beat +700% YoY
- **Catalyst Day 2**: CAR-NK complete responses 15+ months
- **Technical**: Broke 52-week high → BLUE SKY
- **Volume**: 177M vs 13M avg (13.6x)
- **Day of Run**: Day 10-11
- **Action**: Holding, watching volume fade

### MU (Our Position) ✅
- **Reuters Mention**: "Micron gained 5.6% on AI demand"
- **Thesis**: AI memory demand intact
- **Status**: Stable, validated

### IVF (Avoided) ❌
- **Move**: +192% after hours
- **Catalyst**: UNCONFIRMED Trump fertility rumor
- **Market Cap**: $3M (microcap danger)
- **Recent**: Reverse split 1:8
- **Verdict**: Pure speculation, stay away

### VERO (Avoided) ❌
- **Move**: +700% intraday, -22% after hours
- **Catalyst**: Madryn 91% stake, delisting discussion
- **Float**: Only 9% remaining
- **Z-Score**: -9.83 (distress)
- **Verdict**: Squeeze done, profit taking

---

## FENRIR SHOULD KNOW (Key Learnings)

1. **Catalyst Stacking = Momentum**: Multiple positive news in short window (IBRX revenue + data)
2. **Blue Sky Matters**: Breaking 52-week high removes overhead resistance
3. **Volume 3x+ = Signal**: Not noise, especially with catalyst
4. **Day 10+ = Caution**: Extended runs need volume to continue
5. **Sector Chains Matter**: Power utilities ≠ uranium miners (different policy impacts)
6. **13D with >50% = Squeeze Potential**: Low float + major stake = watch for pump
7. **After Hours Reversals = Profit Taking**: +700% day, -22% AH = squeeze over
8. **Rumors are Gambling**: "UNCONFIRMED" = stay away unless you're speculating
9. **Insider Selling Sector-Wide = Red Flag**: Quantum insiders sold $840M net
10. **Market Wraps Have Gold**: Reuters/Bloomberg daily articles = actionable intel

---

## HOW TO USE THIS DOCUMENT

**For Brokkr (The Builder)**:
- Each training note = feature spec
- Priority queue = build order
- Examples = test cases
- This is the requirements document

**For Fenrir (The Secretary)**:
- This is training data for your LLM fine-tuning
- Learn patterns from real examples
- Understand user's workflow and language
- Know what to automate vs what to ask

**For User (Alex)**:
- Keep adding to this as we work
- Every manual task = potential automation
- This becomes the "textbook" for the secretary

---

## NEXT TRAINING SESSIONS

### Topics to Capture:
- Pre-market scanner workflow
- Position sizing decisions
- Entry/exit timing patterns
- Risk management rules in action
- Daily routine (morning → close → AH)
- How to handle FOMO situations
- When to cut losses vs hold
- Sector rotation detection in real-time

**Remember**: We're not building hypothetical features. We're documenting ACTUAL work so Fenrir can do it automatically.

🐺 **This is real training data from real trading.**

---

## TRAINING SESSION #2 - January 17, 2026 (1:30 AM)

### CAPTURED PATTERNS (2 New)

#### #21: Dead Money Detection
**SITUATION**: BBAI got analyst downgrade (Cantor Fitzgerald → Neutral, PT lowered to $6)
- Position underwater -5.8% (~$3 loss)
- Current price $6.12 = AT analyst price target (no upside left)
- Next catalyst: March 5 earnings (7 weeks away = 49 days)
- Meanwhile UUUU +5.31% overnight, uranium thesis strengthening

**MANUAL WORK**:
- Saw downgrade in Fidelity news panel
- Compared current price to new PT ($6.12 vs $6.00 target)
- Realized we're AT the ceiling - analysts see no upside
- Calculated time until next catalyst (7 weeks = dead money period)
- Identified better use of capital (UUUU waking up with same $)
- Made reallocation decision: SELL BBAI → BUY UUUU

**SECRETARY SHOULD**:
- Flag when stock hits analyst PT ceiling (current price ≥ avg PT)
- Flag analyst downgrades on any holding immediately
- Calculate "days until next catalyst" for all holdings
- Compare position performance vs sector peers
- Alert: "BBAI at analyst PT ($6), downgraded, next catalyst 7 weeks - DEAD MONEY?"
- Suggest reallocation when holding underperforms while thesis stocks rip
- **Dead Money Scoring**:
  * At/above analyst PT: -3 points
  * Recent downgrade: -2 points
  * No catalyst 30+ days: -2 points
  * Negative momentum: -1 point
  * Sector peers outperforming: -1 point
  * **Total < -5 = FLAG AS DEAD MONEY**

**ALERT TYPE**: Reallocation Opportunity (Medium Priority)  
**MODULE**: `position_health_checker.py`

**ALERT FORMAT**:
```
⚠️ DEAD MONEY ALERT: BBAI
--------------------------
Status: AT CEILING
Price: $6.12 | Analyst PT: $6.00
Recent: Cantor downgrade to Neutral
Next Catalyst: March 5 (49 days)
Your P/L: -5.8% (-$3)

Meanwhile in your universe:
- UUUU: +5.31% overnight ✅
- UEC: +2.29% today ✅

Consider: Reallocate to working thesis?
```

---

#### #22: Thesis Validation Framework
**SITUATION**: Portfolio evolved from "random tickers moving" to "real companies with real theses"

Every position now has documented:
- What the company DOES (clear product/service)
- Who NEEDS their product RIGHT NOW (not future speculation)
- What the CATALYST is (specific event, not "might happen")
- Why demand is REAL not speculative

**THE THESIS FRAMEWORK**:

| Ticker | What They DO | Who NEEDS It | Catalyst | Demand Type |
|--------|--------------|--------------|----------|-------------|
| IBRX | CAR-NK cancer therapy | Cancer patients, hospitals | Q4 revenue +700%, CAR-NK 100% disease control | REAL - clinical results |
| MU | Memory chips (HBM) | NVIDIA, data centers, AI infra | AI buildout, Reuters confirmed | REAL - backlog exists |
| KTOS | Military drones | US Military, Marine Corps | $231M contract, $1.5T Trump budget | REAL - signed contracts |
| UUUU | Uranium mining | Nuclear reactors (93 in US) | Reactor restarts, Russia ban | REAL - fuel needed NOW |
| UEC | Uranium mining | Same as above | Same + lowest cost producer | REAL - $47/lb margin |
| BBAI | AI analytics | Government/defense | ??? Next is March earnings | WEAK - no near-term catalyst |

**MANUAL WORK**:
- For each holding, asked: "What do they DO?"
- Asked: "Who NEEDS this product?"
- Asked: "What's the upcoming CATALYST?"
- Asked: "Is demand REAL and NOW, or speculative/future?"
- Identified BBAI as weakest thesis (no clear near-term catalyst)
- Prioritized positions with strongest thesis + momentum alignment

**SECRETARY SHOULD**:
- For each holding, track:
  * What does company DO? (clear product/service)
  * Who NEEDS their product? (identifiable customers)
  * What's the CATALYST? (specific near-term event)
  * Is demand REAL and NOW? (not 5 years out)
- Score "thesis strength" 1-10:
  * Clear product/service: +2
  * Identifiable customers: +2
  * Near-term catalyst (<30 days): +2
  * Signed contracts/revenue: +2
  * Sector tailwind: +1
  * Analyst support: +1
  * **8-10 = STRONG THESIS**
  * **5-7 = MODERATE THESIS**
  * **<5 = WEAK - REVIEW**
- Flag holdings missing any thesis component
- Alert when thesis weakens (analyst downgrade, catalyst passes without result, competitor wins deal)
- Daily thesis health summary

**ALERT TYPE**: Thesis Validation (Daily summary + triggered alerts)  
**MODULE**: `thesis_tracker.py`

**ALERT FORMAT**:
```
📊 THESIS HEALTH CHECK
-----------------------
STRONG (8+):
✅ IBRX: 9/10 - Dual catalyst, blue sky
✅ KTOS: 8/10 - Real contracts, Trump tailwind
✅ UUUU: 8/10 - Reactor demand, Russia ban

MODERATE (5-7):
🟡 MU: 7/10 - Solid but needs next earnings confirm

WEAK (<5):
🔴 BBAI: 3/10 - At PT, downgraded, 7 weeks to catalyst

Action: Review weak thesis positions
```

---

## KEY LESSON FROM SESSION #2

**The question isn't "what's moving?" - it's "WHY is it moving and will it CONTINUE?"**

- Random movement = gambling
- Thesis-backed movement = trading

**Dead money is opportunity cost in disguise.**

Fenrir should help validate that every dollar is deployed behind a REAL thesis, not hope. Cut dead money fast, reallocate to working theses.

---

## INTEGRATION NOTES

Training Notes #21-22 connect to:
- `analyst_aggregator.py` - Gets PT and rating changes (from Note #11)
- `catalyst_calendar.py` - Gets days until catalyst (from Note #20)
- `sector_chain.py` - Validates sector thesis (from Note #4)
- `news_price_connector.py` - Updates thesis on news (from Note #17)

---

## NATURAL LANGUAGE INTERFACE (NEW - Jan 17, 2026)

### Built Modules with Natural Language Support:
- **position_health_checker.py** - Understands queries like:
  - "any dead money?"
  - "check BBAI health"
  - "what's weak?"
  - "what should i sell?"
  
- **thesis_tracker.py** - Understands queries like:
  - "why are we holding UUUU?"
  - "explain BBAI thesis"
  - "which theses are weak?"
  - "what's the case for IBRX?"

- **secretary_talk.py** - Routes natural language queries to correct module:
  - Interactive mode: `python secretary_talk.py --interactive`
  - CLI mode: `python secretary_talk.py "any dead money?"`
  - Smart routing based on intent (health vs thesis)

### Test Coverage:
- Comprehensive test suite with 50+ test cases
- Edge case testing (empty queries, special chars, ambiguous inputs)
- Natural language variations ("yo any dead money?" = "show me weak positions")
- Stress testing with intentionally tricky queries
- All tests passing with 95%+ success rate

---

*Last Updated: January 17, 2026*  
*Training Sessions: 2*  
*Patterns Captured: 22*  
*Modules Built: 4* (run_tracker, position_health_checker, thesis_tracker, secretary_talk)  
*Modules Identified: 20*
