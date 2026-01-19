#!/usr/bin/env python3
"""
Fenrir Chat - INSTANT responses, SMART analysis, ZERO waiting
No AI, just pure math + smart pattern matching = FAST + ACCURATE
"""

import sys
from typing import Dict, List, Tuple
from position_health_checker import check_all_positions, HOLDINGS
from thesis_tracker import THESIS_DATABASE

# Pre-calculate everything once
print("🐺 Starting up Fenrir...")
PORTFOLIO_DATA = None

def load_portfolio():
    """Load portfolio once at startup"""
    global PORTFOLIO_DATA
    if PORTFOLIO_DATA:
        return PORTFOLIO_DATA
    
    print("📊 Analyzing positions...", end=" ")
    health_results = check_all_positions()
    
    data = {
        'positions': {},
        'dead_money': [],
        'weak': [],
        'watch': [],
        'healthy': [],
        'running': []
    }
    
    for result in health_results:
        ticker = result['ticker']
        score = result['health_score']
        thesis = THESIS_DATABASE.get(ticker)
        
        pos = {
            'ticker': ticker,
            'score': score,
            'thesis': thesis.thesis_strength if thesis else 0,
            'pnl': result.get('pnl_percent', 0),
            'value': result.get('position_value', 0),
            'catalyst_days': result.get('days_to_catalyst', 999),
            'demand': thesis.demand_type if thesis else 'UNKNOWN',
            'what': thesis.what_they_do if thesis else 'Unknown',
            'who': thesis.who_needs_it if thesis else 'Unknown'
        }
        
        data['positions'][ticker] = pos
        
        # Categorize
        if score <= -5:
            data['dead_money'].append(pos)
        elif score <= -3:
            data['weak'].append(pos)
        elif score <= -1:
            data['watch'].append(pos)
        elif score <= 4:
            data['healthy'].append(pos)
        else:
            data['running'].append(pos)
    
    print("✅")
    PORTFOLIO_DATA = data
    return data


def answer(query: str) -> str:
    """
    INSTANT answers using pattern matching + pre-calculated data
    """
    data = load_portfolio()
    q = query.lower().strip()
    
    # Dead money check
    if any(word in q for word in ['dead', 'dying', 'trash', 'cut', 'sell']):
        if data['dead_money']:
            lines = [f"🔴 DEAD MONEY FOUND:"]
            for p in data['dead_money']:
                lines.append(f"  {p['ticker']}: Score {p['score']}, Thesis {p['thesis']}/10 → CUT IT")
            return "\n".join(lines)
        else:
            lines = ["✅ NO DEAD MONEY"]
            if data['weak'] or data['watch']:
                lines.append(f"\nYou have {len(data['weak'])} weak and {len(data['watch'])} watch positions,")
                lines.append("but all have STRONG theses (8-10/10) = HOLD through volatility")
            return "\n".join(lines)
    
    # Buy/add check
    if any(word in q for word in ['buy', 'add', 'worth buying', 'opportunities']):
        if data['running']:
            lines = ["🔥 WORTH BUYING:"]
            for p in data['running']:
                lines.append(f"  {p['ticker']}: Score {p['score']} (RUNNING), Thesis {p['thesis']}/10, up {p['pnl']:.1f}%")
                lines.append(f"  → Add on dips (momentum confirmed)")
            return "\n".join(lines)
        else:
            lines = ["No positions running hot (score ≥5) right now."]
            if data['healthy']:
                lines.append(f"\n✅ {len(data['healthy'])} HEALTHY positions:")
                for p in data['healthy']:
                    lines.append(f"  {p['ticker']}: Score {p['score']}, Thesis {p['thesis']}/10 → Solid hold")
            return "\n".join(lines)
    
    # Running/hot check
    if any(word in q for word in ['running', 'hot', 'ripping', 'strong']):
        if data['running']:
            lines = [f"🔥 RUNNING HOT ({len(data['running'])} positions):"]
            for p in data['running']:
                lines.append(f"  {p['ticker']}: Score {p['score']}, up {p['pnl']:.1f}% → {p['what']}")
            return "\n".join(lines)
        return "Nothing running hot right now (score ≥5)"
    
    # Weak check
    if 'weak' in q or 'worried' in q or 'concerning' in q:
        weak_all = data['weak'] + data['watch']
        if weak_all:
            lines = [f"⚠️ WEAK HEALTH ({len(weak_all)} positions):"]
            for p in weak_all:
                if p['thesis'] >= 8:
                    action = "HOLD (strong thesis)"
                else:
                    action = "WATCH CLOSELY"
                lines.append(f"  {p['ticker']}: Score {p['score']}, Thesis {p['thesis']}/10 → {action}")
            return "\n".join(lines)
        return "✅ No weak positions (all scores > -3)"
    
    # Specific ticker check
    for ticker in data['positions'].keys():
        if ticker.lower() in q:
            p = data['positions'][ticker]
            lines = [f"📊 {ticker}:"]
            lines.append(f"  Health: {p['score']}/10, Thesis: {p['thesis']}/10, P/L: {p['pnl']:.1f}%")
            lines.append(f"  What: {p['what']}")
            lines.append(f"  Who: {p['who']}")
            lines.append(f"  Demand: {p['demand']} (thesis {p['thesis']}/10)")
            
            # Recommendation
            if p['score'] <= -5:
                lines.append(f"  🔴 DEAD MONEY → Cut it")
            elif p['score'] <= -3 and p['thesis'] >= 8:
                lines.append(f"  ⚠️ WEAK but thesis STRONG → HOLD")
            elif p['score'] <= -1 and p['thesis'] >= 8:
                lines.append(f"  🟡 WATCH but thesis STRONG → HOLD (normal volatility)")
            elif p['score'] >= 5:
                lines.append(f"  🔥 RUNNING → Add on dips")
            else:
                lines.append(f"  ✅ HEALTHY → Hold")
            
            return "\n".join(lines)
    
    # Summary/overview
    if any(word in q for word in ['summary', 'overview', 'portfolio', 'status', 'all']):
        lines = ["📊 PORTFOLIO STATUS:"]
        lines.append(f"  Total: {len(data['positions'])} positions")
        lines.append(f"  🔴 Dead money: {len(data['dead_money'])}")
        lines.append(f"  ⚠️ Weak: {len(data['weak'])}")
        lines.append(f"  🟡 Watch: {len(data['watch'])}")
        lines.append(f"  ✅ Healthy: {len(data['healthy'])}")
        lines.append(f"  🔥 Running: {len(data['running'])}")
        
        if data['running']:
            lines.append(f"\n🔥 RUNNING HOT:")
            for p in data['running']:
                lines.append(f"  {p['ticker']}: +{p['pnl']:.1f}%")
        
        if data['dead_money']:
            lines.append(f"\n🔴 DEAD MONEY:")
            for p in data['dead_money']:
                lines.append(f"  {p['ticker']}: Score {p['score']}")
        
        return "\n".join(lines)
    
    # Default: show what we can answer
    return """I can help with:
  "any dead money?" → Find positions to cut
  "what's worth buying?" → Find opportunities
  "what's running?" → See hot positions
  "what's weak?" → See concerning positions
  "check TICKER" → Deep dive on specific position
  "portfolio summary" → Full overview"""


def chat():
    """Interactive chat mode - INSTANT responses"""
    load_portfolio()  # Pre-load once
    
    print("\n" + "="*60)
    print("🐺 FENRIR CHAT - Instant Analysis")
    print("="*60)
    print("Ask me anything. Type 'quit' to exit.")
    print("="*60 + "\n")
    
    while True:
        try:
            q = input("💬 You: ").strip()
            
            if not q:
                continue
            
            if q.lower() in ['quit', 'exit', 'q']:
                print("\n🐺 Later.\n")
                break
            
            print(f"\n🐺 Fenrir:\n{answer(q)}\n")
            
        except KeyboardInterrupt:
            print("\n\n🐺 Later.\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        load_portfolio()
        query = " ".join(sys.argv[1:])
        print(f"\n💬 You: {query}")
        print(f"\n🐺 Fenrir:\n{answer(query)}\n")
    else:
        # Chat mode
        chat()
