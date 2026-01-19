#!/usr/bin/env python3
"""
🐺 FENRIR V2 - SECRETARY INTEGRATION
Natural language interface for position health and thesis tracking

USAGE:
  python secretary_talk.py "any dead money?"
  python secretary_talk.py "check BBAI health"  
  python secretary_talk.py "whats the thesis on UUUU"
  python secretary_talk.py "which ones are strong"
  python secretary_talk.py "show me everything"

Or run interactively:
  python secretary_talk.py
"""

import sys
import argparse
from position_health_checker import answer_natural_query as answer_health
from thesis_tracker import answer_thesis_query as answer_thesis


# ============================================
# QUERY ROUTER - Decides which module to use
# ============================================

def route_query(query: str) -> dict:
    """
    Route query to correct module based on intent
    Returns: {'module': 'health'|'thesis'|'both', 'query': str}
    """
    query_lower = query.lower()
    
    # Thesis-specific keywords
    thesis_keywords = [
        'thesis', 'why', 'case for', 'conviction', 
        'demand', 'catalyst', 'speculative', 'real demand',
        'what do they do', 'who needs', 'revenue', 'contracts'
    ]
    
    # Health-specific keywords
    health_keywords = [
        'dead money', 'dying', 'sick', 'health', 'score',
        'analyst', 'price target', 'pt', 'downgrade',
        'peer', 'vs peers', 'outperform', 'reallocate'
    ]
    
    # Check for explicit module request
    if any(keyword in query_lower for keyword in thesis_keywords):
        return {'module': 'thesis', 'query': query}
    
    if any(keyword in query_lower for keyword in health_keywords):
        return {'module': 'health', 'query': query}
    
    # Ambiguous queries that could be either
    ambiguous_keywords = ['weak', 'strong', 'good', 'bad', 'show', 'check']
    if any(keyword in query_lower for keyword in ambiguous_keywords):
        # Default to health for ambiguous queries
        return {'module': 'health', 'query': query}
    
    # If mentions specific ticker, show both
    tickers = ['IBRX', 'MU', 'KTOS', 'UUUU', 'UEC', 'BBAI']
    if any(ticker.lower() in query_lower for ticker in tickers):
        return {'module': 'both', 'query': query}
    
    # Default to full health check
    return {'module': 'both', 'query': query}


# ============================================
# MAIN QUERY HANDLER
# ============================================

def ask_secretary(query: str, verbose: bool = False):
    """
    Main function - routes query and returns answer
    """
    if not query or not query.strip():
        return "❓ What would you like to know? Try 'help' for examples."
    
    # Route the query
    route = route_query(query)
    module = route['module']
    
    if verbose:
        print(f"\n🔍 Routing to: {module.upper()}\n")
    
    # Execute query
    if module == 'health':
        return answer_health(query)
    
    elif module == 'thesis':
        return answer_thesis(query)
    
    elif module == 'both':
        # Show both health and thesis
        health_result = answer_health(query)
        thesis_result = answer_thesis(query)
        
        return f"{health_result}\n\n{'─'*60}\n\n{thesis_result}"
    
    else:
        return "❌ Something went wrong routing your query."


# ============================================
# INTERACTIVE MODE
# ============================================

def interactive_mode():
    """
    Interactive conversation with the secretary
    """
    print("\n" + "🐺" * 30)
    print("   FENRIR V2 - SECRETARY MODE")
    print("🐺" * 30)
    print("\nAsk me about your positions in natural language!")
    print("Examples:")
    print("  - 'any dead money?'")
    print("  - 'check BBAI health'")
    print("  - 'why are we holding UUUU?'")
    print("  - 'which ones are strong?'")
    print("  - 'show me everything'")
    print("\nType 'quit' or 'exit' to leave.\n")
    
    while True:
        try:
            query = input("💬 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q', 'bye']:
                print("\n🐺 LLHR - See you next time!")
                break
            
            if query.lower() == 'help':
                print("\nAvailable queries:")
                print("  HEALTH: 'dead money?', 'check BBAI', 'what's healthy?', 'what to sell?'")
                print("  THESIS: 'why UUUU?', 'thesis on MU?', 'weak theses?', 'what's the case for IBRX?'")
                print("  BOTH: Mention a ticker by name, or ask 'show everything'")
                continue
            
            # Get answer
            response = ask_secretary(query, verbose=False)
            print(f"\n🐺 Fenrir:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n🐺 LLHR - See you next time!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


# ============================================
# CLI MODE
# ============================================

def cli_mode(query: str, verbose: bool = False):
    """
    Single query mode for command line
    """
    response = ask_secretary(query, verbose=verbose)
    print(response)


# ============================================
# EXAMPLE QUERIES (for testing/demo)
# ============================================

def show_examples():
    """Show example queries and responses"""
    print("\n" + "="*60)
    print("📚 EXAMPLE QUERIES")
    print("="*60)
    
    examples = [
        ("any dead money?", "Checks for positions losing money with no catalyst"),
        ("check BBAI health", "Full health report on BBAI"),
        ("why are we holding UUUU?", "Explains the thesis for UUUU"),
        ("which ones are strong?", "Shows positions with strong health scores"),
        ("weak theses?", "Shows positions with weak investment theses"),
        ("what should i sell?", "Reallocation recommendations"),
        ("explain the case for IBRX", "Deep dive on IBRX thesis"),
        ("show me everything", "Full portfolio health + thesis check"),
    ]
    
    for query, description in examples:
        print(f"\n💬 '{query}'")
        print(f"   → {description}")
    
    print("\n" + "="*60)


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🐺 Fenrir V2 Secretary - Natural language portfolio analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python secretary_talk.py "any dead money?"
  python secretary_talk.py "check BBAI health"
  python secretary_talk.py "why UUUU?"
  python secretary_talk.py --interactive
  python secretary_talk.py --examples
        """
    )
    
    parser.add_argument('query', nargs='*', help='Your question in natural language')
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='Start interactive conversation mode')
    parser.add_argument('-e', '--examples', action='store_true',
                       help='Show example queries')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show routing information')
    
    args = parser.parse_args()
    
    # Show examples
    if args.examples:
        show_examples()
        sys.exit(0)
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        sys.exit(0)
    
    # CLI mode with query
    if args.query:
        query = ' '.join(args.query)
        cli_mode(query, verbose=args.verbose)
    else:
        # No arguments = show help
        parser.print_help()
        print("\n💡 Tip: Run with --interactive for conversation mode")
        print("💡 Tip: Run with --examples to see sample queries")
