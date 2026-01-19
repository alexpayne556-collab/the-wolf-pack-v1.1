#!/usr/bin/env python3
"""
Smart Secretary - Rule-based logic + Ollama for formatting
The MATH decides, Ollama just explains it nicely
"""

import sys
from typing import Dict, List, Any
from position_health_checker import check_all_positions, HOLDINGS
from thesis_tracker import THESIS_DATABASE

def analyze_portfolio() -> Dict[str, Any]:
    """
    Do the MATH first - no AI, just logic
    """
    print("Analyzing portfolio (pure math, no AI)...")
    
    # Get health scores
    health_results = check_all_positions()
    
    analysis = {
        'dead_money': [],      # score <= -5
        'weak': [],            # score -4 to -3
        'watch': [],           # score -2 to -1
        'healthy': [],         # score 0 to +4
        'running': [],         # score >= +5
        'total_positions': len(HOLDINGS)
    }
    
    for result in health_results:
        ticker = result['ticker']
        score = result['health_score']
        thesis = THESIS_DATABASE.get(ticker)
        thesis_score = thesis.thesis_strength if thesis else 0
        
        position = {
            'ticker': ticker,
            'health_score': score,
            'thesis_score': thesis_score,
            'pnl': result.get('pnl_percent', 0),
            'status': result.get('status', 'UNKNOWN')
        }
        
        # STRICT categorization based on MATH
        if score <= -5:
            analysis['dead_money'].append(position)
        elif score <= -3:
            analysis['weak'].append(position)
        elif score <= -1:
            analysis['watch'].append(position)
        elif score <= 4:
            analysis['healthy'].append(position)
        else:
            analysis['running'].append(position)
    
    return analysis


def format_response(query: str, analysis: Dict[str, Any]) -> str:
    """
    Format the response in plain English based on MATH
    No AI involved - just rules
    """
    response = []
    
    # Dead money check
    if 'dead money' in query.lower() or 'sell' in query.lower() or 'weak' in query.lower():
        if analysis['dead_money']:
            response.append(f"🔴 DEAD MONEY FOUND ({len(analysis['dead_money'])} positions):")
            for pos in analysis['dead_money']:
                response.append(f"  {pos['ticker']}: Score {pos['health_score']}, Thesis {pos['thesis_score']}/10, P/L {pos['pnl']:.1f}%")
                response.append(f"  → CUT IT (score <=-5 threshold)")
        else:
            response.append("✅ NO DEAD MONEY")
            response.append(f"All {analysis['total_positions']} positions > -5 threshold")
        
        # Show weak/watch for context
        if analysis['weak']:
            response.append(f"\n⚠️ WEAK (score -4 to -3): {len(analysis['weak'])} positions")
            for pos in analysis['weak']:
                thesis_note = "STRONG thesis, HOLD" if pos['thesis_score'] >= 8 else "weak thesis, consider exit"
                response.append(f"  {pos['ticker']}: Score {pos['health_score']}, Thesis {pos['thesis_score']}/10 → {thesis_note}")
        
        if analysis['watch']:
            response.append(f"\n🟡 WATCH (score -2 to -1): {len(analysis['watch'])} positions")
            for pos in analysis['watch']:
                thesis_note = "STRONG thesis, HOLD" if pos['thesis_score'] >= 8 else "weak thesis, monitor"
                response.append(f"  {pos['ticker']}: Score {pos['health_score']}, Thesis {pos['thesis_score']}/10 → {thesis_note}")
    
    # Running hot check
    if 'running' in query.lower() or 'hot' in query.lower() or 'strong' in query.lower():
        if analysis['running']:
            response.append(f"🔥 RUNNING HOT ({len(analysis['running'])} positions):")
            for pos in analysis['running']:
                response.append(f"  {pos['ticker']}: Score {pos['health_score']}, Thesis {pos['thesis_score']}/10, P/L {pos['pnl']:.1f}%")
                response.append(f"  → ADD on dips (score >=5)")
        else:
            response.append("No positions running hot (score >=5) right now")
    
    # Summary if no specific query
    if not response or 'summary' in query.lower():
        response.append(f"\n📊 PORTFOLIO SUMMARY:")
        response.append(f"Total positions: {analysis['total_positions']}")
        response.append(f"🔴 Dead money (≤-5): {len(analysis['dead_money'])}")
        response.append(f"⚠️ Weak (-4 to -3): {len(analysis['weak'])}")
        response.append(f"🟡 Watch (-2 to -1): {len(analysis['watch'])}")
        response.append(f"✅ Healthy (0 to +4): {len(analysis['healthy'])}")
        response.append(f"🔥 Running (≥+5): {len(analysis['running'])}")
    
    return "\n".join(response)


def ask_secretary(query: str) -> str:
    """
    Main function - MATH decides, we just format nicely
    """
    print(f"\n💬 You: {query}")
    print("="*60)
    
    # Step 1: Do the MATH (no AI)
    analysis = analyze_portfolio()
    
    # Step 2: Format based on pure logic rules (no AI)
    response = format_response(query, analysis)
    
    print(f"\n🐺 Fenrir (rule-based, 100% accurate):")
    print(response)
    print("="*60)
    
    return response


def interactive_mode():
    """
    Chat with the secretary - but it's rules, not AI
    """
    print("="*60)
    print("🐺 FENRIR SMART SECRETARY (Rule-Based)")
    print("="*60)
    print("This uses MATH, not AI guessing")
    print("Type 'quit' to exit")
    print("="*60)
    
    while True:
        try:
            query = input("\n💬 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n🐺 Later.")
                break
            
            ask_secretary(query)
            
        except KeyboardInterrupt:
            print("\n\n🐺 Interrupted. Later.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI mode
        query = " ".join(sys.argv[1:])
        ask_secretary(query)
    else:
        # Interactive mode
        interactive_mode()
