#!/usr/bin/env python3
"""
🧠 BIOTECH CATALYST ANALYSIS PROMPTS FOR FENRIR
================================================
Pre-built prompts for analyzing biotech setups with Ollama/Fenrir
"""

def get_pdufa_analysis_prompt(ticker: str, catalyst_data: dict, price_data: dict) -> str:
    """Generate prompt for PDUFA runup analysis"""
    
    return f"""You are analyzing a biotech PDUFA play for the Wolf Pack trading system.

TICKER: {ticker}
DRUG: {catalyst_data.get('drug', 'Unknown')}
INDICATION: {catalyst_data.get('indication', 'Unknown')}
PDUFA DATE: {catalyst_data.get('date', 'Unknown')}
DAYS UNTIL: {catalyst_data.get('days_until', 'Unknown')}

CURRENT PRICE: ${price_data.get('price', 0):.2f}
52-WEEK HIGH: ${price_data.get('high_52w', 0):.2f}
% OFF HIGH: {price_data.get('pct_from_high', 0):.1f}%
VOLUME: {price_data.get('rel_volume', 1):.1f}x average

WOLF PACK PDUFA STRATEGY:
- Typical runup: 15-30% in 2 weeks before PDUFA
- Buy window: 7-14 days before
- Exit: 1-2 days before decision (avoid binary risk)
- If approved: +20-50% pop
- If CRL (rejection): -40-80% crash

ANALYZE:
1. FDA Approval Probability (Low/Medium/High) - Consider indication competitiveness
2. Optimal Entry Price - Where to buy
3. Expected Runup % - Based on typical PDUFA patterns
4. Exit Strategy - When to sell
5. Position Size Recommendation (1-5% of portfolio)
6. Similar Past Plays - What stocks had similar setups?

VERDICT: BUY / WATCH / AVOID

Keep response concise and actionable."""


def get_insider_buying_prompt(ticker: str, insider_data: dict, price_data: dict) -> str:
    """Generate prompt for insider buying analysis"""
    
    return f"""You are analyzing insider buying for the Wolf Pack trading system.

TICKER: {ticker}
INSIDER ACTIVITY:
- Recent Buys: {insider_data.get('recent_buys', 0)}
- Buyers: {', '.join(insider_data.get('buyers', []))}
- Total Value: ${insider_data.get('total_value', 0):,}
- Last Purchase: {insider_data.get('last_purchase', 'Unknown')}
- Conviction Score: {insider_data.get('conviction', 0)}/10

CURRENT PRICE: ${price_data.get('price', 0):.2f}
CHANGE TODAY: {price_data.get('change_pct', 0):+.1f}%

WOLF PACK INSIDER RULES:
- Directors buying = Strong signal (they know pipeline)
- Multiple buys = Higher conviction
- Buying near lows = Usually smart
- Buying before catalyst = Very bullish

ANALYZE:
1. Is this routine buying or unusual accumulation?
2. What might they know that market doesn't?
3. Timing - Why now?
4. Trade Setup - Should we follow?
5. Risk/Reward

VERDICT: BUY / WATCH / AVOID"""


def get_catalyst_ranking_prompt(opportunities: dict) -> str:
    """Generate prompt to rank multiple catalyst opportunities"""
    
    pdufa_plays = opportunities.get('pdufa_runup_plays', [])
    insider_plays = opportunities.get('insider_buying_plays', [])
    imminent = opportunities.get('imminent_catalysts', [])
    
    prompt = """You are ranking biotech catalyst opportunities for the Wolf Pack trading system.

OPPORTUNITIES AVAILABLE:

"""
    
    # PDUFA Plays
    if pdufa_plays:
        prompt += "🔥 PDUFA RUNUP PLAYS (7-14 days out):\n"
        for i, play in enumerate(pdufa_plays, 1):
            prompt += f"{i}. {play['ticker']}: {play['drug']} - {play['indication']}\n"
            prompt += f"   Days until: {play['days_until']} | Type: {play['type']}\n"
        prompt += "\n"
    
    # Insider Buying
    if insider_plays:
        prompt += "👔 INSIDER BUYING SIGNALS:\n"
        for i, play in enumerate(insider_plays, 1):
            prompt += f"{i}. {play['ticker']}: {play['recent_buys']} buys, Conviction: {play['conviction']}/10\n"
        prompt += "\n"
    
    # Imminent (risky)
    if imminent:
        prompt += "⚠️  IMMINENT CATALYSTS (0-7 days - HIGH RISK):\n"
        for i, cat in enumerate(imminent, 1):
            prompt += f"{i}. {cat['ticker']}: {cat['days_until']} days to {cat['type']}\n"
        prompt += "\n"
    
    prompt += """
WOLF PACK RANKING CRITERIA:
1. Risk/Reward Ratio (10pts)
2. Catalyst Timing (10pts) - 7-14 days = best, <7 = risky
3. Setup Quality (10pts) - Insider buying + catalyst = best
4. Expected Move % (10pts)
5. Probability of Success (10pts)

RANK each opportunity 1-50 points.

OUTPUT FORMAT:
RANK | TICKER | SCORE | WHY | ACTION

Then pick your TOP 3 for tomorrow."""
    
    return prompt


def get_compression_breakout_prompt(ticker: str, compression_data: dict, catalyst_data: dict) -> str:
    """Analyze compression + catalyst setup"""
    
    return f"""You are analyzing a COMPRESSION BREAKOUT setup for the Wolf Pack.

TICKER: {ticker}

COMPRESSION DATA:
- Days Flat: {compression_data.get('flat_days', 0)}
- Price Range: {compression_data.get('range_pct', 0):.1f}%
- Volume Profile: {compression_data.get('avg_volume', 0):,.0f} avg
- Compression Score: {compression_data.get('score', 0)}/100

CATALYST:
- Type: {catalyst_data.get('type', 'Unknown')}
- Date: {catalyst_data.get('date', 'Unknown')}
- Drug: {catalyst_data.get('drug', 'Unknown')}

WOLF PACK COMPRESSION EDGE:
"Find stocks sleeping (flat + low volume), wait for catalyst to wake them up, ride the boom."

Entry Rule: First pullback to VWAP after initial spike, NOT on the spike itself.

ANALYZE:
1. Is compression quality HIGH? (flat >10 days, range <15%)
2. Is catalyst REAL? (FDA, partnership, data - not just news)
3. What's expected move on catalyst?
4. Entry price on pullback
5. Stop loss
6. Target

VERDICT: EXPLOSIVE / GOOD / WEAK / AVOID"""


def get_daily_mover_analysis_prompt(movers: list) -> str:
    """Analyze today's movers to find patterns"""
    
    prompt = """You are analyzing today's biotech movers to find patterns for FUTURE trades.

TODAY'S MOVERS:

"""
    
    for mover in movers[:10]:
        prompt += f"• {mover['ticker']}: {mover['gap_pct']:+.1f}% | Vol: {mover['volume_ratio']:.1f}x | Float: {mover['float']/1e6:.0f}M\n"
    
    prompt += """

WOLF PACK PATTERN RECOGNITION:
1. WHY did each stock move? (Scrape news)
2. What's the common thread? (FDA? Partnership? Data?)
3. Which moves are DONE vs JUST STARTING?
4. What stocks HAVEN'T moved yet but have similar catalysts?

OUTPUT:
- Pattern identified
- Stocks to watch that fit the pattern
- Entry strategy for the pattern"""
    
    return prompt


def get_trade_thesis_prompt(ticker: str, all_data: dict) -> str:
    """Generate complete trade thesis"""
    
    return f"""Generate a COMPLETE TRADE THESIS for {ticker}.

ALL DATA:
{all_data}

WOLF PACK THESIS FORMAT:

1. CATALYST: What's happening?
2. TIMING: When?
3. PROBABILITY: Approval/success chance (Low/Med/High)
4. EXPECTED MOVE:
   - On positive news: +X%
   - On negative news: -X%
5. ENTRY: Exact price to buy
6. STOP LOSS: Exact price to cut
7. TARGET 1: First take-profit (50% position)
8. TARGET 2: Final exit (remaining 50%)
9. POSITION SIZE: X% of portfolio (max 5% for biotech binary events)
10. RISK/REWARD: X:1

11. WOLF PACK RULES APPLIED:
    - 2% Test Trade Rule? (YES/NO)
    - Compression Breakout? (YES/NO)
    - PDUFA Runup? (YES/NO)
    - Insider Following? (YES/NO)

FINAL VERDICT: BUY NOW / WAIT FOR PULLBACK / AVOID

One sentence summary of the trade."""
    
    return prompt
