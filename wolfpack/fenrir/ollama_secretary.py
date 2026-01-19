"""
🐺 FENRIR V3 - OLLAMA SECRETARY
Real natural language understanding via local LLM + live data

Powers:
- Real-time news scraping (NewsAPI)
- SEC EDGAR filings parser
- Live market data
- Natural conversation

Usage:
    python ollama_secretary.py --interactive
    python ollama_secretary.py "what's the latest news on BBAI?"
    python ollama_secretary.py "check recent SEC filings for IBRX"
"""

import json
import requests
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from position_health_checker import (
    check_all_positions,
    check_position_health,
    HOLDINGS
)
from thesis_tracker import (
    thesis_health_check,
    validate_thesis,
    explain_thesis,
    THESIS_DATABASE
)

# Load environment variables
load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')


def get_news_for_ticker(ticker: str, days_back: int = 7) -> List[Dict]:
    """
    Fetch recent news for a ticker using NewsAPI
    
    Args:
        ticker: Stock ticker symbol
        days_back: How many days of news to fetch
        
    Returns:
        List of news articles with title, description, url, date
    """
    if not NEWS_API_KEY or NEWS_API_KEY == 'your_newsapi_key_here':
        return [{"error": "NEWS_API_KEY not configured in .env file"}]
    
    try:
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': f'{ticker} stock OR ${ticker}',
            'from': from_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': NEWS_API_KEY,
            'pageSize': 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        for article in data.get('articles', [])[:5]:  # Top 5 most recent
            articles.append({
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'date': article.get('publishedAt', ''),
                'source': article.get('source', {}).get('name', 'Unknown')
            })
        
        return articles if articles else [{"message": f"No recent news found for {ticker}"}]
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"Failed to fetch news: {str(e)}"}]
    except Exception as e:
        return [{"error": f"News fetch error: {str(e)}"}]


def get_sec_filings(ticker: str, filing_type: str = '8-K', limit: int = 5) -> List[Dict]:
    """
    Fetch recent SEC filings for a ticker from SEC EDGAR
    
    Args:
        ticker: Stock ticker symbol
        filing_type: Type of filing (8-K, 10-K, 10-Q, etc.)
        limit: Number of filings to fetch
        
    Returns:
        List of filings with type, date, url, description
    """
    try:
        # SEC EDGAR API endpoint (public, no key needed)
        # Get CIK for ticker first
        cik_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type={filing_type}&dateb=&owner=exclude&count={limit}&output=atom"
        
        headers = {
            'User-Agent': 'Fenrir Trading System contact@example.com',  # SEC requires user agent
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        response = requests.get(cik_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parse XML/Atom feed (simplified)
            filings = []
            
            # For now, just return the URL to the filings page
            # TODO: Parse the actual feed for detailed info
            filings.append({
                'ticker': ticker,
                'filing_type': filing_type,
                'message': f'View recent {filing_type} filings',
                'url': f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type={filing_type}&dateb=&owner=exclude&count={limit}',
                'note': 'Check for material events, acquisitions, financial updates'
            })
            
            return filings
        else:
            return [{"error": f"SEC EDGAR returned status {response.status_code}"}]
            
    except Exception as e:
        return [{"error": f"SEC filing fetch error: {str(e)}"}]


def search_sec_for_keyword(ticker: str, keyword: str) -> Dict:
    """
    Search SEC filings for specific keywords (e.g., "acquisition", "downgrade", "lawsuit")
    
    Args:
        ticker: Stock ticker
        keyword: Keyword to search for in filings
        
    Returns:
        Summary of findings
    """
    try:
        # This would require parsing actual filing documents
        # For now, return a helpful message
        return {
            'ticker': ticker,
            'keyword': keyword,
            'message': f'Search SEC filings for "{keyword}"',
            'url': f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=exclude&count=40&search_text={keyword}',
            'note': 'Manual review recommended for detailed analysis'
        }
    except Exception as e:
        return {"error": f"SEC search error: {str(e)}"}


def get_enhanced_portfolio_context() -> Dict[str, Any]:
    """
    Gather ALL available data: portfolio + news + SEC filings
    
    Returns:
        Comprehensive context dict with positions, news, filings
    """
    # Get base portfolio data
    context = get_portfolio_context()
    
    # Add news and SEC data for each position
    context['news'] = {}
    context['sec_filings'] = {}
    
    for ticker in list(HOLDINGS.keys())[:3]:  # Limit to avoid rate limits
        try:
            # Fetch news
            news = get_news_for_ticker(ticker, days_back=7)
            if news and not news[0].get('error'):
                context['news'][ticker] = news
            
            # Fetch recent 8-K filings (material events)
            filings = get_sec_filings(ticker, filing_type='8-K', limit=3)
            if filings and not filings[0].get('error'):
                context['sec_filings'][ticker] = filings
                
        except Exception as e:
            print(f"Error fetching external data for {ticker}: {e}")
            continue
    
    return context

def get_portfolio_context() -> Dict[str, Any]:
    """Gather all portfolio data for Ollama context"""
    # Get position health
    health_report = check_all_positions()
    
    # Get thesis validation
    thesis_report = thesis_health_check()
    
    # Build context
    context = {
        "positions": [],
        "portfolio_summary": {
            "total_value": 0,
            "total_pnl": 0,
            "position_count": len(HOLDINGS)
        },
        "dead_money": [],
        "weak_theses": [],
        "strong_runners": []
    }
    
    # Parse health report
    for ticker in HOLDINGS:
        try:
            health = check_position_health(ticker, HOLDINGS[ticker])
            thesis_data = THESIS_DATABASE.get(ticker, None)
            thesis_strength = thesis_data.thesis_strength if thesis_data else 0
            
            pos_data = {
                "ticker": ticker,
                "health_score": health.get('health_score', 0),
                "thesis_score": thesis_strength,
                "pnl_percent": health.get('pnl_percent', 0),
                "position_value": health.get('position_value', 0),
                "status": health.get('status', 'UNKNOWN'),
                "current_price": health.get('current_price', 0),
                "days_to_catalyst": health.get('days_to_catalyst', None),
                "recommendation": health.get('recommendation', '')
            }
            
            context["positions"].append(pos_data)
            context["portfolio_summary"]["total_value"] += pos_data["position_value"]
            context["portfolio_summary"]["total_pnl"] += (pos_data["position_value"] * pos_data["pnl_percent"] / 100)
            
            # Categorize
            if pos_data["health_score"] <= -5:
                context["dead_money"].append(ticker)
            if pos_data["thesis_score"] < 5:
                context["weak_theses"].append(ticker)
            if pos_data["health_score"] >= 5:
                context["strong_runners"].append(ticker)
                
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue
    
    return context


def build_system_prompt() -> str:
    """Create system prompt for Ollama"""
    return """You are Fenrir, a brutally honest trading analyst. Talk like a trader, be conversational.

Your job: Answer the user's question using the MATH RESULTS I give you below. Trust the math.

NEVER contradict the math results. If math says "HOLD", you say HOLD. If math says "no dead money", you say no dead money.

Be conversational but ACCURATE. Answer what they asked, use the data."""


def ask_ollama(user_query: str, portfolio_context: Dict[str, Any], verbose: bool = False) -> str:
    """
    Send query to Ollama with portfolio context
    
    Args:
        user_query: The user's natural language question
        portfolio_context: Portfolio data from get_portfolio_context()
        verbose: Show Ollama's thinking process
    
    Returns:
        Ollama's response as string
    """
    
    # Build the full prompt
    system_prompt = build_system_prompt()
    
    # Format portfolio data for context
    portfolio_summary = f"""
PORTFOLIO DATA (as of now):
Total Value: ${portfolio_context['portfolio_summary']['total_value']:.2f}
Total P/L: ${portfolio_context['portfolio_summary']['total_pnl']:.2f}
Positions: {portfolio_context['portfolio_summary']['position_count']}

POSITIONS:
"""
    
    for pos in portfolio_context['positions']:
        portfolio_summary += f"""
{pos['ticker']}: ${pos['current_price']:.2f}
  Health: {pos['health_score']}/10 | Thesis: {pos['thesis_score']}/10
  P/L: {pos['pnl_percent']:.1f}% | Value: ${pos['position_value']:.2f}
  Status: {pos['status']}
  Days to catalyst: {pos['days_to_catalyst']}
  {pos['recommendation']}
"""
    
    # Add categorized info
    if portfolio_context['dead_money']:
        portfolio_summary += f"\n🔴 DEAD MONEY: {', '.join(portfolio_context['dead_money'])}"
    if portfolio_context['weak_theses']:
        portfolio_summary += f"\n⚠️ WEAK THESES: {', '.join(portfolio_context['weak_theses'])}"
    if portfolio_context['strong_runners']:
        portfolio_summary += f"\n🔥 STRONG RUNNERS: {', '.join(portfolio_context['strong_runners'])}"
    
    # Add NEWS if available
    if 'news' in portfolio_context and portfolio_context['news']:
        portfolio_summary += "\n\n📰 RECENT NEWS:\n"
        for ticker, articles in portfolio_context['news'].items():
            if articles and not articles[0].get('error'):
                portfolio_summary += f"\n{ticker}:\n"
                for article in articles[:3]:  # Top 3
                    if 'title' in article:
                        portfolio_summary += f"  - {article['title']} ({article.get('source', 'Unknown')})\n"
                        if article.get('description'):
                            portfolio_summary += f"    {article['description'][:100]}...\n"
    
    # Add SEC FILINGS if available
    if 'sec_filings' in portfolio_context and portfolio_context['sec_filings']:
        portfolio_summary += "\n\n📄 SEC FILINGS (8-K Material Events):\n"
        for ticker, filings in portfolio_context['sec_filings'].items():
            if filings and not filings[0].get('error'):
                portfolio_summary += f"\n{ticker}:\n"
                for filing in filings[:2]:  # Top 2
                    if 'url' in filing:
                        portfolio_summary += f"  - {filing.get('filing_type', '8-K')}: {filing.get('message', 'View filings')}\n"
                        portfolio_summary += f"    URL: {filing['url']}\n"
    
    # Full prompt with MATH RESULTS FIRST
    full_prompt = f"""{system_prompt}

=== MATH RESULTS (TRUST THESE) ===
{portfolio_summary}

=== DECISION RULES ===
Score ≤-5 = DEAD MONEY (cut it)
Score -4 to -3 = WEAK (hold if thesis ≥8/10)
Score -2 to -1 = WATCH (hold if thesis ≥8/10, just normal volatility)
Score 0-4 = HEALTHY (hold)
Score ≥5 = RUNNING (add on dips)

Thesis 8-10 = STRONG (hold with conviction)
Thesis 5-7 = MODERATE
Thesis 1-4 = WEAK

=== USER QUESTION ===
{user_query}

=== YOUR RESPONSE ===
Answer their question using the MATH RESULTS above. Be conversational but accurate. If they ask "any dead money?", check if any positions have score ≤-5. If they ask "what's worth buying?", look for running positions (score ≥5) or positions about to break out. If they ask about a specific ticker, explain its health + thesis."""
    
    if verbose:
        print("\n" + "="*60)
        print("🧠 SENDING TO OLLAMA:")
        print("="*60)
        print(full_prompt)
        print("="*60 + "\n")
    
    # Send to Ollama
    try:
        payload = {
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 300  # Keep responses SHORT and fast
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
        response.raise_for_status()
        
        result = response.json()
        answer = result.get('response', '').strip()
        
        if verbose:
            print("🐺 OLLAMA RESPONSE:")
            print("="*60)
            print(answer)
            print("="*60 + "\n")
        
        return answer
        
    except requests.exceptions.ConnectionError:
        return "❌ Can't reach Ollama. Is it running? Try: `ollama serve`"
    except requests.exceptions.Timeout:
        return "⏱️ Ollama timed out after 90s. Model might be loading or prompt too complex. Try a simpler question."
    except Exception as e:
        return f"❌ Error talking to Ollama: {str(e)}"


def interactive_mode():
    """Interactive conversation with Ollama-powered secretary"""
    print("\n" + "="*60)
    print("🐺 FENRIR V3 - OLLAMA SECRETARY")
    print("="*60)
    print("Talk naturally. Ask anything about your positions.")
    print("I can check: portfolio health, news, SEC filings")
    print("")
    print("Commands:")
    print("  'quit' - exit")
    print("  'verbose' - toggle debug mode")
    print("  'refresh' - reload portfolio data")
    print("  'news TICKER' - fetch latest news")
    print("  'sec TICKER' - check SEC filings")
    print("="*60 + "\n")
    
    verbose = False
    
    # Load portfolio context once at start
    print("📊 Loading portfolio data...")
    context = get_enhanced_portfolio_context()
    print(f"✅ Loaded: {len(context['positions'])} positions")
    if context.get('news'):
        print(f"📰 News available for: {', '.join(context['news'].keys())}")
    if context.get('sec_filings'):
        print(f"📄 SEC filings for: {', '.join(context['sec_filings'].keys())}")
    print()
    
    while True:
        try:
            user_input = input("💬 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n🐺 Later.\n")
                break
                
            if user_input.lower() == 'verbose':
                verbose = not verbose
                print(f"🔧 Verbose mode: {'ON' if verbose else 'OFF'}\n")
                continue
                
            if user_input.lower() == 'refresh':
                print("📊 Refreshing portfolio data + news + SEC filings...\n")
                context = get_enhanced_portfolio_context()
                print("✅ Data refreshed\n")
                continue
            
            # Special commands for news/SEC
            if user_input.lower().startswith('news '):
                ticker = user_input.split()[1].upper()
                print(f"📰 Fetching news for {ticker}...\n")
                news = get_news_for_ticker(ticker, days_back=7)
                for article in news[:5]:
                    if 'title' in article:
                        print(f"  • {article['title']}")
                        print(f"    {article.get('description', '')[:150]}...")
                        print(f"    {article.get('source', 'Unknown')} - {article.get('date', '')}\n")
                continue
                
            if user_input.lower().startswith('sec '):
                ticker = user_input.split()[1].upper()
                print(f"📄 Fetching SEC filings for {ticker}...\n")
                filings = get_sec_filings(ticker, filing_type='8-K', limit=5)
                for filing in filings:
                    print(f"  • {filing.get('message', 'Filing')}")
                    if 'url' in filing:
                        print(f"    {filing['url']}\n")
                continue
            
            # Get response from Ollama
            print("🐺 Fenrir: ", end="", flush=True)
            response = ask_ollama(user_input, context, verbose=verbose)
            
            if not verbose:  # Only print if not already printed in verbose mode
                print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\n🐺 Caught Ctrl+C. Later.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


def cli_mode(query: str, verbose: bool = False):
    """Single query mode"""
    print("\n📊 Loading portfolio data + news + SEC filings...")
    context = get_enhanced_portfolio_context()
    
    print(f"\n💬 You: {query}")
    print("🐺 Fenrir: ", end="", flush=True)
    
    response = ask_ollama(query, context, verbose=verbose)
    
    if not verbose:
        print(response)
    print()


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Fenrir V3 - Ollama Secretary")
    parser.add_argument('query', nargs='?', help='Question to ask (leave empty for interactive mode)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show Ollama prompt/response details')
    parser.add_argument('-i', '--interactive', action='store_true', help='Force interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive or not args.query:
        interactive_mode()
    else:
        cli_mode(args.query, verbose=args.verbose)
