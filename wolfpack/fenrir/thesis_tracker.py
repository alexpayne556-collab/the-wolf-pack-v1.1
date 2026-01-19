#!/usr/bin/env python3
"""
🐺 FENRIR V2 - THESIS TRACKER
Validates every position has a real thesis:
- What they DO
- Who NEEDS it
- What's the CATALYST
- Is demand REAL or SPECULATIVE

Training Note #22: Portfolio evolved from random tickers to real theses.
Every position should answer: Why will this continue?
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import re


# ============================================
# DATA STRUCTURES
# ============================================

@dataclass
class Thesis:
    ticker: str
    what_they_do: str
    who_needs_it: str
    catalyst: str
    catalyst_date: Optional[str]
    demand_type: str  # "REAL", "SPECULATIVE", "UNKNOWN"
    demand_timeline: str  # "NOW", "1-2_YEARS", "5+_YEARS"
    thesis_strength: int  # 1-10
    last_validated: str
    validation_notes: str
    
    # Thesis factors
    has_revenue: bool
    has_contracts: bool
    analyst_support: bool
    sector_tailwind: bool


# ============================================
# THESIS DATABASE - YOUR CURRENT HOLDINGS
# ============================================

THESIS_DATABASE = {
    'IBRX': Thesis(
        ticker='IBRX',
        what_they_do='CAR-NK cancer immunotherapy - turns immune cells into cancer killers using natural killer cells',
        who_needs_it='Cancer patients, hospitals, oncology centers worldwide',
        catalyst='Q4 revenue +700% YoY ($113M), CAR-NK showing 100% disease control in trials',
        catalyst_date='2026-01-15',
        demand_type='REAL',
        demand_timeline='NOW',
        thesis_strength=9,
        last_validated='2026-01-17',
        validation_notes='DUAL CATALYST FIRING: Revenue beat Day 1, CAR-NK data Day 2. Blue sky breakout - no overhead resistance. Saudi FDA approvals expanding market.',
        has_revenue=True,
        has_contracts=True,
        analyst_support=True,
        sector_tailwind=True
    ),
    
    'MU': Thesis(
        ticker='MU',
        what_they_do='Memory chips (DRAM, HBM, NAND) - the memory that powers AI training and inference',
        who_needs_it='NVIDIA (HBM for GPUs), AMD, data centers, hyperscalers building AI infrastructure',
        catalyst='AI memory supercycle - HBM demand exceeds supply, Reuters confirmed backlog',
        catalyst_date='2026-03-20',
        demand_type='REAL',
        demand_timeline='NOW',
        thesis_strength=8,
        last_validated='2026-01-17',
        validation_notes='AI infrastructure needs memory NOW. Every GPU needs HBM. Real revenue, real backlog, not speculative. Part of AI Fuel Chain thesis.',
        has_revenue=True,
        has_contracts=True,
        analyst_support=True,
        sector_tailwind=True
    ),
    
    'KTOS': Thesis(
        ticker='KTOS',
        what_they_do='Military drones (Valkyrie, XQ-58), loyal wingman systems, defense tech',
        who_needs_it='US Military, Marine Corps, Air Force - drone warfare is the future',
        catalyst='$231M Marine Corps MUX TACAIR contract (Jan 8), Trump $1.5T defense budget proposal',
        catalyst_date='2026-01-08',
        demand_type='REAL',
        demand_timeline='NOW',
        thesis_strength=8,
        last_validated='2026-01-17',
        validation_notes='SIGNED CONTRACTS - not speculation. +45-50% week of Jan 5-9. Multiple analyst upgrades. Drone warfare proven in Ukraine. Trump defense tailwind.',
        has_revenue=True,
        has_contracts=True,
        analyst_support=True,
        sector_tailwind=True
    ),
    
    'UUUU': Thesis(
        ticker='UUUU',
        what_they_do='Mine uranium and rare earth elements - domestic fuel supply for nuclear',
        who_needs_it='US nuclear reactors (93 operating), need fuel continuously, Russia banned',
        catalyst='Reactor restarts (Palisades 2026, TMI 2027-28), Russia uranium import ban',
        catalyst_date='2026-02-27',
        demand_type='REAL',
        demand_timeline='NOW',
        thesis_strength=8,
        last_validated='2026-01-17',
        validation_notes='Trump power plant news BULLISH for uranium miners (not utilities). 93 reactors need fuel NOW. Russia ban forces domestic buying. Lowest cost US producer.',
        has_revenue=True,
        has_contracts=True,
        analyst_support=True,
        sector_tailwind=True
    ),
    
    'UEC': Thesis(
        ticker='UEC',
        what_they_do='Uranium mining - only US company with both uranium mining and UF6 processing',
        who_needs_it='US nuclear utilities needing domestic supply, government strategic reserves',
        catalyst='$47/lb margin at spot uranium $81/lb, Russia ban, $698M cash zero debt',
        catalyst_date='2026-02-10',
        demand_type='REAL',
        demand_timeline='NOW',
        thesis_strength=8,
        last_validated='2026-01-17',
        validation_notes='100% unhedged uranium exposure. Massive margin at current spot. Most liquid US uranium play. Same thesis as UUUU but different value chain position.',
        has_revenue=True,
        has_contracts=True,
        analyst_support=True,
        sector_tailwind=True
    ),
}


# ============================================
# THESIS SCORING LOGIC
# ============================================

def calculate_thesis_strength(thesis_data: Dict) -> int:
    """Calculate thesis strength score 1-10"""
    score = 0
    
    # Clear product (+2)
    if thesis_data.get('what_they_do'):
        score += 2
    
    # Identifiable customers (+2)
    if thesis_data.get('who_needs_it'):
        score += 2
    
    # Near-term catalyst (+1 to +2)
    if thesis_data.get('catalyst'):
        score += 1
        catalyst_date = thesis_data.get('catalyst_date')
        if catalyst_date:
            try:
                days = (datetime.strptime(catalyst_date, '%Y-%m-%d') - datetime.now()).days
                if days < 30:
                    score += 1
            except:
                pass
    
    # Real demand (+2) vs speculative (+0)
    if thesis_data.get('demand_type') == 'REAL':
        score += 2
    
    # Has revenue/contracts (+1 each)
    if thesis_data.get('has_revenue'):
        score += 1
    if thesis_data.get('has_contracts'):
        score += 1
    
    # Analyst support (+1) or penalty (-2 for downgrade)
    if thesis_data.get('analyst_support'):
        score += 1
    elif thesis_data.get('analyst_support') == False:  # Explicit False = downgrade
        score -= 2  # Stronger penalty for downgrade
    else:
        score -= 0  # None/unknown = neutral
    
    return min(10, max(1, score))


def get_thesis_status(score: int) -> str:
    """Convert score to emoji status"""
    if score >= 8:
        return "💪 STRONG"
    elif score >= 5:
        return "🟡 MODERATE"
    else:
        return "🔴 WEAK"


# ============================================
# VALIDATION FUNCTIONS
# ============================================

def validate_thesis(ticker: str, thesis: Thesis) -> Dict:
    """Validate a thesis and return analysis"""
    
    # Recalculate strength with current data
    strength = calculate_thesis_strength({
        'what_they_do': thesis.what_they_do,
        'who_needs_it': thesis.who_needs_it,
        'catalyst': thesis.catalyst,
        'catalyst_date': thesis.catalyst_date,
        'demand_type': thesis.demand_type,
        'has_revenue': thesis.has_revenue,
        'has_contracts': thesis.has_contracts,
        'analyst_support': thesis.analyst_support
    })
    
    status = get_thesis_status(strength)
    
    # Generate warnings
    warnings = []
    if thesis.demand_type == 'SPECULATIVE':
        warnings.append("⚠️ Demand is SPECULATIVE, not proven")
    if thesis.demand_timeline in ['1-2_YEARS', '5+_YEARS']:
        warnings.append(f"⚠️ Demand timeline: {thesis.demand_timeline}")
    if not thesis.analyst_support:
        warnings.append("⚠️ No analyst support or DOWNGRADED")
    if not thesis.has_contracts:
        warnings.append("⚠️ No major contracts announced")
    
    # Calculate days to catalyst
    days_to_catalyst = None
    if thesis.catalyst_date:
        try:
            catalyst_dt = datetime.strptime(thesis.catalyst_date, '%Y-%m-%d')
            days_to_catalyst = (catalyst_dt - datetime.now()).days
        except:
            pass
    
    return {
        'ticker': ticker,
        'thesis_strength': strength,
        'status': status,
        'what_they_do': thesis.what_they_do,
        'who_needs_it': thesis.who_needs_it,
        'catalyst': thesis.catalyst,
        'catalyst_date': thesis.catalyst_date,
        'days_to_catalyst': days_to_catalyst,
        'demand_type': thesis.demand_type,
        'demand_timeline': thesis.demand_timeline,
        'warnings': warnings,
        'notes': thesis.validation_notes,
        'recommendation': 'HOLD' if strength >= 5 else 'REVIEW - Consider exit'
    }


# ============================================
# REPORTING FUNCTIONS
# ============================================

def thesis_health_check() -> str:
    """Run thesis check on all holdings"""
    
    output = []
    output.append("\n" + "=" * 60)
    output.append("📊 FENRIR V2 - THESIS HEALTH CHECK")
    output.append("=" * 60)
    output.append("\nThe question isn't 'what's moving?' - it's 'WHY and will it CONTINUE?'")
    
    strong = []
    moderate = []
    weak = []
    
    for ticker, thesis in THESIS_DATABASE.items():
        result = validate_thesis(ticker, thesis)
        
        if result['thesis_strength'] >= 8:
            strong.append(result)
        elif result['thesis_strength'] >= 5:
            moderate.append(result)
        else:
            weak.append(result)
    
    if strong:
        output.append("\n" + "-" * 60)
        output.append("💪 STRONG THESIS (8+) - These have REAL reasons to continue")
        output.append("-" * 60)
        for r in sorted(strong, key=lambda x: x['thesis_strength'], reverse=True):
            output.append(f"\n   {r['ticker']}: {r['thesis_strength']}/10 {r['status']}")
            output.append(f"   📌 What: {r['what_they_do'][:60]}...")
            output.append(f"   👥 Who: {r['who_needs_it'][:60]}...")
            output.append(f"   ⚡ Catalyst: {r['catalyst'][:50]}...")
            output.append(f"   📊 Demand: {r['demand_type']} | Timeline: {r['demand_timeline']}")
    
    if moderate:
        output.append("\n" + "-" * 60)
        output.append("🟡 MODERATE THESIS (5-7) - Watch for changes")
        output.append("-" * 60)
        for r in moderate:
            output.append(f"\n   {r['ticker']}: {r['thesis_strength']}/10 {r['status']}")
            output.append(f"   📌 What: {r['what_they_do'][:60]}...")
            if r['warnings']:
                for w in r['warnings']:
                    output.append(f"   {w}")
    
    if weak:
        output.append("\n" + "=" * 60)
        output.append("🔴 WEAK THESIS (<5) - ACTION REQUIRED")
        output.append("=" * 60)
        for r in weak:
            output.append(f"\n   {r['ticker']}: {r['thesis_strength']}/10 {r['status']}")
            output.append(f"   📌 What: {r['what_they_do'][:60]}...")
            output.append(f"   👥 Who: {r['who_needs_it'][:50]}...")
            output.append(f"   ⚡ Catalyst: {r['catalyst'][:50]}...")
            output.append(f"   📊 Demand: {r['demand_type']} | Timeline: {r['demand_timeline']}")
            if r['days_to_catalyst']:
                output.append(f"   ⏰ Days to catalyst: {r['days_to_catalyst']}")
            output.append(f"\n   📝 Notes: {r['notes'][:80]}...")
            for w in r['warnings']:
                output.append(f"   {w}")
            output.append(f"\n   → ACTION: {r['recommendation']}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


def explain_thesis(ticker: str) -> str:
    """Explain the thesis for a single ticker in detail"""
    
    if ticker not in THESIS_DATABASE:
        return f"\n❌ No thesis on file for {ticker}. Add it to THESIS_DATABASE."
    
    thesis = THESIS_DATABASE[ticker]
    result = validate_thesis(ticker, thesis)
    
    output = []
    output.append(f"\n{'=' * 60}")
    output.append(f"📋 THESIS DEEP DIVE: {ticker}")
    output.append(f"{'=' * 60}")
    
    output.append(f"\n🎯 STRENGTH: {result['thesis_strength']}/10 {result['status']}")
    
    output.append(f"\n{'─' * 40}")
    output.append(f"📌 WHAT THEY DO:")
    output.append(f"   {thesis.what_they_do}")
    
    output.append(f"\n{'─' * 40}")
    output.append(f"👥 WHO NEEDS IT (RIGHT NOW):")
    output.append(f"   {thesis.who_needs_it}")
    
    output.append(f"\n{'─' * 40}")
    output.append(f"⚡ CATALYST:")
    output.append(f"   {thesis.catalyst}")
    if result['days_to_catalyst'] is not None:
        if result['days_to_catalyst'] < 0:
            output.append(f"   (Catalyst already passed - {abs(result['days_to_catalyst'])} days ago)")
        else:
            output.append(f"   (In {result['days_to_catalyst']} days - {thesis.catalyst_date})")
    
    output.append(f"\n{'─' * 40}")
    output.append(f"📊 DEMAND ANALYSIS:")
    output.append(f"   Type: {thesis.demand_type}")
    output.append(f"   Timeline: {thesis.demand_timeline}")
    output.append(f"   Has Revenue: {'✅' if thesis.has_revenue else '❌'}")
    output.append(f"   Has Contracts: {'✅' if thesis.has_contracts else '❌'}")
    output.append(f"   Analyst Support: {'✅' if thesis.analyst_support else '❌ DOWNGRADED'}")
    output.append(f"   Sector Tailwind: {'✅' if thesis.sector_tailwind else '❌'}")
    
    if result['warnings']:
        output.append(f"\n{'─' * 40}")
        output.append(f"⚠️ WARNINGS:")
        for w in result['warnings']:
            output.append(f"   {w}")
    
    output.append(f"\n{'─' * 40}")
    output.append(f"📝 VALIDATION NOTES:")
    output.append(f"   {thesis.validation_notes}")
    
    output.append(f"\n   Last validated: {thesis.last_validated}")
    
    output.append(f"\n{'─' * 40}")
    output.append(f"📢 RECOMMENDATION: {result['recommendation']}")
    
    output.append(f"\n{'=' * 60}")
    
    return "\n".join(output)


def portfolio_thesis_summary() -> str:
    """Quick summary of portfolio thesis alignment"""
    
    output = []
    output.append("\n" + "=" * 60)
    output.append("📈 PORTFOLIO THESIS ALIGNMENT")
    output.append("=" * 60)
    
    total = len(THESIS_DATABASE)
    strong = sum(1 for t, th in THESIS_DATABASE.items() if validate_thesis(t, th)['thesis_strength'] >= 8)
    moderate = sum(1 for t, th in THESIS_DATABASE.items() if 5 <= validate_thesis(t, th)['thesis_strength'] < 8)
    weak = sum(1 for t, th in THESIS_DATABASE.items() if validate_thesis(t, th)['thesis_strength'] < 5)
    
    output.append(f"\n   Total Positions: {total}")
    output.append(f"   💪 Strong (8+): {strong} ({strong/total*100:.0f}%)")
    output.append(f"   🟡 Moderate (5-7): {moderate} ({moderate/total*100:.0f}%)")
    output.append(f"   🔴 Weak (<5): {weak} ({weak/total*100:.0f}%)")
    
    # Demand breakdown
    real = sum(1 for th in THESIS_DATABASE.values() if th.demand_type == 'REAL')
    spec = sum(1 for th in THESIS_DATABASE.values() if th.demand_type == 'SPECULATIVE')
    
    output.append(f"\n   REAL Demand: {real}/{total}")
    output.append(f"   SPECULATIVE: {spec}/{total}")
    
    if weak > 0:
        output.append(f"\n   ⚠️ {weak} position(s) need review!")
        weak_tickers = [t for t, th in THESIS_DATABASE.items() if validate_thesis(t, th)['thesis_strength'] < 5]
        output.append(f"   Tickers: {', '.join(weak_tickers)}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


# ============================================
# NATURAL LANGUAGE INTERFACE
# ============================================

def parse_thesis_query(query: str) -> Dict:
    """Parse natural language queries about theses"""
    query_lower = query.lower()
    
    # Extract ticker if mentioned
    ticker = None
    for t in THESIS_DATABASE.keys():
        if t.lower() in query_lower:
            ticker = t
            break
    
    # Determine intent
    intent = None
    if any(word in query_lower for word in ['weak', 'bad', 'failing', 'broken']):
        intent = 'weak_thesis'
    elif any(word in query_lower for word in ['strong', 'good', 'solid', 'best']):
        intent = 'strong_thesis'
    elif any(word in query_lower for word in ['why', 'explain', 'thesis', 'case for', 'tell me about']):
        if ticker:
            intent = 'explain_single'
        else:
            intent = 'full_check'
    elif any(word in query_lower for word in ['summary', 'overview', 'portfolio']):
        intent = 'summary'
    elif ticker:
        intent = 'explain_single'
    else:
        intent = 'full_check'
    
    return {'ticker': ticker, 'intent': intent}


def answer_thesis_query(query: str) -> str:
    """Answer natural language questions about theses"""
    parsed = parse_thesis_query(query)
    intent = parsed['intent']
    ticker = parsed['ticker']
    
    if intent == 'weak_thesis':
        weak = []
        for t, th in THESIS_DATABASE.items():
            result = validate_thesis(t, th)
            if result['thesis_strength'] < 5:
                weak.append(result)
        
        if not weak:
            return "✅ No weak theses. All positions have solid backing."
        
        output = [f"🔴 Found {len(weak)} weak thesis(es):\n"]
        for r in weak:
            output.append(f"  {r['ticker']}: {r['thesis_strength']}/10")
            output.append(f"  Problem: {r['warnings'][0] if r['warnings'] else 'Multiple issues'}")
            output.append(f"  → {r['recommendation']}\n")
        return "\n".join(output)
    
    elif intent == 'strong_thesis':
        strong = []
        for t, th in THESIS_DATABASE.items():
            result = validate_thesis(t, th)
            if result['thesis_strength'] >= 8:
                strong.append(result)
        
        if not strong:
            return "⚠️ No positions have strong (8+) theses right now."
        
        output = [f"💪 {len(strong)} strong thesis(es):\n"]
        for r in sorted(strong, key=lambda x: x['thesis_strength'], reverse=True):
            output.append(f"  {r['ticker']}: {r['thesis_strength']}/10")
            output.append(f"  What: {r['what_they_do'][:50]}...")
            output.append(f"  Demand: {r['demand_type']} | Timeline: {r['demand_timeline']}\n")
        return "\n".join(output)
    
    elif intent == 'explain_single' and ticker:
        return explain_thesis(ticker)
    
    elif intent == 'summary':
        return portfolio_thesis_summary()
    
    else:  # full_check
        return thesis_health_check()


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("\n" + "🐺" * 30)
    print("   FENRIR V2 - THESIS TRACKER")
    print("🐺" * 30)
    
    # Portfolio summary
    summary = portfolio_thesis_summary()
    print(summary)
    
    # Full thesis check
    report = thesis_health_check()
    print(report)
    
    # Deep dive on weak positions
    print("\n" + "🔍" * 30)
    print("   DEEP DIVE: WEAK THESIS")
    print("🔍" * 30)
    
    for ticker, thesis in THESIS_DATABASE.items():
        result = validate_thesis(ticker, thesis)
        if result['thesis_strength'] < 5:
            print(explain_thesis(ticker))
    
    print("\n🐺 LLHR - Random movement = gambling. Thesis-backed movement = trading!")
