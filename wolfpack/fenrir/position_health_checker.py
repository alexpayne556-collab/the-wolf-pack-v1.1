#!/usr/bin/env python3
"""
🐺 FENRIR V2 - POSITION HEALTH CHECKER
Detects dead money positions and suggests reallocations

Training Note #21: BBAI was -5.8%, at analyst PT, 7 weeks to catalyst
while UUUU was ripping +5.31%. We should catch this automatically.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import re

# ============================================
# CONFIGURATION - UPDATE WITH YOUR HOLDINGS
# ============================================

HOLDINGS = {
    'IBRX': {'shares': 37.08, 'avg_cost': 4.69, 'broker': 'robinhood'},
    'MU': {'shares': 1.268, 'avg_cost': 335.00, 'broker': 'both'},
    'KTOS': {'shares': 2.72, 'avg_cost': 117.83, 'broker': 'robinhood'},
    'UUUU': {'shares': 3.0, 'avg_cost': 22.09, 'broker': 'robinhood'},
    'UEC': {'shares': 2.0, 'avg_cost': 17.29, 'broker': 'fidelity'},
}

# Sector mapping for peer comparison
SECTOR_PEERS = {
    'IBRX': ['MRNA', 'BNTX', 'NVAX'],
    'MU': ['NVDA', 'AMD', 'INTC'],
    'KTOS': ['RCAT', 'AVAV', 'LMT'],
    'UUUU': ['UEC', 'DNN', 'CCJ'],
    'UEC': ['UUUU', 'DNN', 'CCJ'],
}

# Known upcoming catalysts
CATALYST_CALENDAR = {
    'IBRX': {'event': 'Earnings + CAR-NK updates', 'date': '2026-02-15'},
    'MU': {'event': 'Q2 Earnings', 'date': '2026-03-20'},
    'KTOS': {'event': 'Q4 Earnings', 'date': '2026-02-25'},
    'UUUU': {'event': 'Q4 Earnings', 'date': '2026-02-27'},
    'UEC': {'event': 'Q1 Earnings', 'date': '2026-02-10'},
}


# ============================================
# DATA FETCHING FUNCTIONS
# ============================================

def get_analyst_data(ticker: str) -> Dict:
    """Pull analyst PT and recommendations from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'target_mean': info.get('targetMeanPrice'),
            'target_high': info.get('targetHighPrice'),
            'target_low': info.get('targetLowPrice'),
            'recommendation': info.get('recommendationKey', 'none'),
            'num_analysts': info.get('numberOfAnalystOpinions', 0)
        }
    except Exception as e:
        print(f"  ⚠️ Error getting analyst data for {ticker}: {e}")
        return {}


def get_price_history(ticker: str) -> Dict:
    """Get price changes over multiple timeframes"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        
        if len(hist) < 2:
            return {}
        
        current = hist['Close'].iloc[-1]
        
        # 1-day change
        prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else current
        change_1d = ((current - prev_close) / prev_close) * 100
        
        # 7-day change
        week_ago = hist['Close'].iloc[-7] if len(hist) >= 7 else hist['Close'].iloc[0]
        change_7d = ((current - week_ago) / week_ago) * 100
        
        # 30-day change
        month_ago = hist['Close'].iloc[0]
        change_30d = ((current - month_ago) / month_ago) * 100
        
        return {
            'current_price': current,
            'change_1d': change_1d,
            'change_7d': change_7d,
            'change_30d': change_30d
        }
    except Exception as e:
        print(f"  ⚠️ Error getting price history for {ticker}: {e}")
        return {}


# ============================================
# HEALTH SCORING LOGIC
# ============================================

def calculate_health_score(
    pnl_percent: float,
    at_analyst_ceiling: bool,
    recent_downgrade: bool,
    days_to_catalyst: Optional[int],
    peer_outperformance: float
) -> int:
    """
    Calculate health score from -10 to +10
    Negative = dead money, Positive = healthy
    """
    score = 0
    
    # P/L impact (-3 to +3)
    if pnl_percent > 20:
        score += 3
    elif pnl_percent > 5:
        score += 2
    elif pnl_percent > 0:
        score += 1
    elif pnl_percent > -5:
        score -= 1
    elif pnl_percent > -15:
        score -= 2
    else:
        score -= 3
    
    # Analyst ceiling (-3 to 0)
    if at_analyst_ceiling:
        score -= 3
    
    # Recent downgrade (-2)
    if recent_downgrade:
        score -= 2
    
    # Catalyst proximity (-2 to +2)
    if days_to_catalyst is None or days_to_catalyst > 60:
        score -= 2
    elif days_to_catalyst > 30:
        score -= 1
    elif days_to_catalyst < 14:
        score += 2
    elif days_to_catalyst < 30:
        score += 1
    
    # Peer comparison (-2 to +2)
    if peer_outperformance > 15:
        score += 2
    elif peer_outperformance > 5:
        score += 1
    elif peer_outperformance > -5:
        score -= 0  # Neutral zone
    elif peer_outperformance > -10:
        score -= 1
    else:
        score -= 2
    
    return max(-10, min(10, score))


def get_health_status(score: int) -> str:
    """Convert score to emoji status"""
    if score >= 5:
        return "🔥 RUNNING"
    elif score >= 2:
        return "✅ HEALTHY"
    elif score >= -2:
        return "🟡 WATCH"
    elif score >= -5:
        return "⚠️ WEAK"
    else:
        return "🔴 DEAD MONEY"


# ============================================
# MAIN HEALTH CHECK FUNCTION
# ============================================

def check_position_health(ticker: str, holding: Dict) -> Dict:
    """Full health check on a single position"""
    
    price_data = get_price_history(ticker)
    analyst_data = get_analyst_data(ticker)
    
    if not price_data:
        return {'ticker': ticker, 'error': f'Could not get data for {ticker}'}
    
    current_price = price_data['current_price']
    shares = holding['shares']
    avg_cost = holding['avg_cost']
    
    # Calculate P/L
    pnl_dollars = (current_price - avg_cost) * shares
    pnl_percent = ((current_price - avg_cost) / avg_cost) * 100
    
    # Check analyst ceiling (within 5% of PT)
    analyst_pt = analyst_data.get('target_mean')
    at_ceiling = False
    if analyst_pt and current_price >= analyst_pt * 0.95:
        at_ceiling = True
    
    # Check catalyst
    catalyst_info = CATALYST_CALENDAR.get(ticker, {})
    next_catalyst = catalyst_info.get('event')
    catalyst_date = catalyst_info.get('date')
    days_to_catalyst = None
    if catalyst_date:
        catalyst_dt = datetime.strptime(catalyst_date, '%Y-%m-%d')
        days_to_catalyst = (catalyst_dt - datetime.now()).days
    
    # Get peer performance
    peers = SECTOR_PEERS.get(ticker, [])
    peer_returns = []
    for peer in peers[:2]:  # Top 2 peers to speed up
        peer_data = get_price_history(peer)
        if peer_data:
            peer_returns.append(peer_data.get('change_7d', 0))
    
    peer_avg = sum(peer_returns) / len(peer_returns) if peer_returns else 0
    peer_outperformance = price_data['change_7d'] - peer_avg
    
    # BBAI specific: Mark as downgraded (we know this from session)
    recent_downgrade = ticker == 'BBAI'  # Cantor downgrade
    
    # Calculate health score
    health_score = calculate_health_score(
        pnl_percent=pnl_percent,
        at_analyst_ceiling=at_ceiling,
        recent_downgrade=recent_downgrade,
        days_to_catalyst=days_to_catalyst,
        peer_outperformance=peer_outperformance
    )
    
    status = get_health_status(health_score)
    
    # Generate recommendation
    if health_score <= -5:
        recommendation = f"🚨 CONSIDER REALLOCATING - Dead money until {catalyst_date or 'unknown'}"
    elif health_score <= -2:
        recommendation = "⚠️ WATCH CLOSELY - Thesis weakening"
    elif at_ceiling:
        recommendation = "📊 AT ANALYST CEILING - Limited upside per analysts"
    else:
        recommendation = "✅ HOLD - Thesis intact"
    
    return {
        'ticker': ticker,
        'current_price': round(current_price, 2),
        'avg_cost': avg_cost,
        'shares': shares,
        'position_value': round(current_price * shares, 2),
        'pnl_dollars': round(pnl_dollars, 2),
        'pnl_percent': round(pnl_percent, 2),
        'analyst_pt': round(analyst_pt, 2) if analyst_pt else None,
        'at_ceiling': at_ceiling,
        'analyst_rating': analyst_data.get('recommendation', 'N/A'),
        'next_catalyst': next_catalyst,
        'catalyst_date': catalyst_date,
        'days_to_catalyst': days_to_catalyst,
        'change_1d': round(price_data['change_1d'], 2),
        'change_7d': round(price_data['change_7d'], 2),
        'change_30d': round(price_data['change_30d'], 2),
        'peer_avg_7d': round(peer_avg, 2),
        'vs_peers': round(peer_outperformance, 2),
        'health_score': health_score,
        'status': status,
        'recommendation': recommendation
    }


def check_all_positions() -> List[Dict]:
    """Check health of all holdings"""
    results = []
    
    print("🐺 Fetching market data...\n")
    
    for ticker, holding in HOLDINGS.items():
        print(f"  Checking {ticker}...")
        result = check_position_health(ticker, holding)
        results.append(result)
    
    # Sort by health score (worst first for action)
    results.sort(key=lambda x: x.get('health_score', 0))
    
    return results


# ============================================
# REPORTING FUNCTIONS
# ============================================

def format_health_report(results: List[Dict]) -> str:
    """Format results for display"""
    
    output = []
    output.append("\n" + "=" * 60)
    output.append("🐺 FENRIR V2 - POSITION HEALTH CHECK")
    output.append("=" * 60)
    
    # Calculate totals
    total_value = sum(r.get('position_value', 0) for r in results if 'error' not in r)
    total_pnl = sum(r.get('pnl_dollars', 0) for r in results if 'error' not in r)
    
    output.append(f"\n💰 Portfolio Value: ${total_value:,.2f} | P/L: ${total_pnl:+,.2f}")
    
    dead_money = []
    weak = []
    watch = []
    healthy = []
    running = []
    
    for r in results:
        if 'error' in r:
            continue
        
        score = r.get('health_score', 0)
        if score <= -5:
            dead_money.append(r)
        elif score <= -2:
            weak.append(r)
        elif score < 2:
            watch.append(r)
        elif score >= 5:
            running.append(r)
        else:
            healthy.append(r)
    
    if running:
        output.append("\n🔥 RUNNING:")
        for r in running:
            output.append(f"   {r['ticker']}: ${r['current_price']} | {r['pnl_percent']:+.1f}% (${r['pnl_dollars']:+.2f}) | Score: {r['health_score']}")
            output.append(f"      7d: {r['change_7d']:+.1f}% | vs Peers: {r['vs_peers']:+.1f}%")
    
    if healthy:
        output.append("\n✅ HEALTHY:")
        for r in healthy:
            output.append(f"   {r['ticker']}: ${r['current_price']} | {r['pnl_percent']:+.1f}% (${r['pnl_dollars']:+.2f}) | Score: {r['health_score']}")
    
    if watch:
        output.append("\n🟡 WATCH:")
        for r in watch:
            output.append(f"   {r['ticker']}: ${r['current_price']} | {r['pnl_percent']:+.1f}% | Score: {r['health_score']}")
            output.append(f"      Catalyst: {r['next_catalyst']} in {r['days_to_catalyst']} days")
    
    if weak:
        output.append("\n⚠️ WEAK:")
        for r in weak:
            output.append(f"   {r['ticker']}: ${r['current_price']} | {r['pnl_percent']:+.1f}% | Score: {r['health_score']}")
            output.append(f"      → {r['recommendation']}")
    
    if dead_money:
        output.append("\n" + "=" * 60)
        output.append("🔴 DEAD MONEY DETECTED:")
        output.append("=" * 60)
        for r in dead_money:
            output.append(f"\n   {r['ticker']}: ${r['current_price']} | {r['pnl_percent']:+.1f}% (${r['pnl_dollars']:+.2f})")
            output.append(f"      Position Value: ${r['position_value']:.2f}")
            output.append(f"      Analyst PT: ${r['analyst_pt']} | At Ceiling: {'YES ❌' if r['at_ceiling'] else 'No'}")
            output.append(f"      Rating: {r['analyst_rating']}")
            output.append(f"      Next Catalyst: {r['next_catalyst']}")
            output.append(f"      Days to Catalyst: {r['days_to_catalyst']} days")
            output.append(f"      7d Change: {r['change_7d']:+.1f}% | vs Peers: {r['vs_peers']:+.1f}%")
            output.append(f"      Health Score: {r['health_score']}")
            output.append(f"      → {r['recommendation']}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


def find_reallocation_opportunities(results: List[Dict]) -> str:
    """Suggest where to move dead money"""
    
    dead = [r for r in results if r.get('health_score', 0) <= -5 and 'error' not in r]
    strong = [r for r in results if r.get('health_score', 0) >= 2 and 'error' not in r]
    
    if not dead:
        return "\n✅ No dead money positions found. Portfolio is healthy!"
    
    output = []
    output.append("\n" + "=" * 60)
    output.append("💡 REALLOCATION OPPORTUNITIES")
    output.append("=" * 60)
    
    for d in dead:
        value = d['position_value']
        output.append(f"\n🔻 SELL {d['ticker']} (~${value:.2f}):")
        output.append(f"   Reason: {d['recommendation']}")
        output.append(f"   Current P/L: {d['pnl_percent']:+.1f}% (${d['pnl_dollars']:+.2f})")
        
        if strong:
            output.append(f"\n   📈 Consider adding to:")
            for s in sorted(strong, key=lambda x: x['health_score'], reverse=True)[:3]:
                output.append(f"      → {s['ticker']} (Score: {s['health_score']}, 7d: {s['change_7d']:+.1f}%)")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


# ============================================
# NATURAL LANGUAGE INTERFACE
# ============================================

def parse_natural_query(query: str) -> Dict:
    """Parse natural language queries about position health"""
    query_lower = query.lower()
    
    # Extract ticker if mentioned
    ticker = None
    for t in HOLDINGS.keys():
        if t.lower() in query_lower:
            ticker = t
            break
    
    # Determine intent
    intent = None
    if any(word in query_lower for word in ['dead', 'dying', 'weak', 'sick', 'bad']):
        intent = 'dead_money'
    elif any(word in query_lower for word in ['healthy', 'good', 'strong', 'best', 'running', 'hot', 'ripping']):
        intent = 'healthy'
    elif any(word in query_lower for word in ['sell', 'dump', 'exit', 'cut']):
        intent = 'sell_recommendations'
    elif any(word in query_lower for word in ['buy', 'add', 'increase', 'double down']):
        intent = 'buy_recommendations'
    elif 'all' in query_lower or 'everything' in query_lower or 'portfolio' in query_lower:
        intent = 'full_check'
    elif ticker:
        intent = 'single_check'
    else:
        intent = 'full_check'
    
    return {'ticker': ticker, 'intent': intent}


def answer_natural_query(query: str) -> str:
    """Answer natural language questions about position health"""
    parsed = parse_natural_query(query)
    intent = parsed['intent']
    ticker = parsed['ticker']
    
    # Run health check
    results = check_all_positions()
    
    if intent == 'dead_money':
        dead = [r for r in results if r.get('health_score', 0) <= -5 and 'error' not in r]
        if not dead:
            return "✅ No dead money positions right now. All positions are working."
        
        output = [f"🔴 Found {len(dead)} dead money position(s):\n"]
        for r in dead:
            output.append(f"  {r['ticker']}: {r['pnl_percent']:+.1f}% | Score: {r['health_score']}")
            output.append(f"  → {r['recommendation']}\n")
        return "\n".join(output)
    
    elif intent == 'healthy':
        healthy = [r for r in results if r.get('health_score', 0) >= 5 and 'error' not in r]
        if not healthy:
            return "⚠️ No positions are currently 'running hot'. Portfolio needs attention."
        
        output = [f"🔥 {len(healthy)} position(s) running strong:\n"]
        for r in sorted(healthy, key=lambda x: x['health_score'], reverse=True):
            output.append(f"  {r['ticker']}: {r['pnl_percent']:+.1f}% | Score: {r['health_score']} | 7d: {r['change_7d']:+.1f}%")
        return "\n".join(output)
    
    elif intent == 'sell_recommendations':
        return find_reallocation_opportunities(results)
    
    elif intent == 'buy_recommendations':
        strong = [r for r in results if r.get('health_score', 0) >= 3 and 'error' not in r]
        if not strong:
            return "⚠️ No positions are strong enough to add to right now."
        
        output = ["📈 Strong positions to consider adding:\n"]
        for r in sorted(strong, key=lambda x: x['health_score'], reverse=True)[:3]:
            output.append(f"  {r['ticker']}: Score {r['health_score']} | {r['change_7d']:+.1f}% (7d) | {r['status']}")
        return "\n".join(output)
    
    elif intent == 'single_check' and ticker:
        # Find the specific ticker
        ticker_result = next((r for r in results if r['ticker'] == ticker), None)
        if not ticker_result or 'error' in ticker_result:
            return f"❌ Couldn't get data for {ticker}"
        
        r = ticker_result
        output = [f"\n📊 {r['ticker']} Health Check:"]
        output.append(f"  Status: {r['status']}")
        output.append(f"  Health Score: {r['health_score']}/10")
        output.append(f"  Price: ${r['current_price']} (avg cost ${r['avg_cost']})")
        output.append(f"  P/L: {r['pnl_percent']:+.1f}% (${r['pnl_dollars']:+.2f})")
        output.append(f"  7-day: {r['change_7d']:+.1f}% | vs Peers: {r['vs_peers']:+.1f}%")
        if r['analyst_pt']:
            output.append(f"  Analyst PT: ${r['analyst_pt']} {'❌ AT CEILING' if r['at_ceiling'] else ''}")
        if r['next_catalyst']:
            output.append(f"  Next Catalyst: {r['next_catalyst']} ({r['days_to_catalyst']} days)")
        output.append(f"\n  → {r['recommendation']}")
        return "\n".join(output)
    
    else:  # full_check
        return format_health_report(results)


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("\n" + "🐺" * 30)
    print("   FENRIR V2 - POSITION HEALTH CHECKER")
    print("🐺" * 30)
    
    results = check_all_positions()
    
    report = format_health_report(results)
    print(report)
    
    realloc = find_reallocation_opportunities(results)
    print(realloc)
    
    print("\n🐺 LLHR - Cut dead money fast!")
