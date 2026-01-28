# 🐺 FENRIR V2 - OLLAMA BRAIN
# The core AI query engine with RAG context injection
# NOW CONNECTED TO WOLFPACK DATABASE (99 stocks daily history)

import requests
import json
import sqlite3
import os
from typing import Optional, Dict, List
from config import OLLAMA_URL, OLLAMA_MODEL, HOLDINGS, WATCHLIST
from market_data import get_stock_data, get_sector_performance
from news_fetcher import get_company_news, format_news_for_context
from services.br0kkr_service import get_8k_filings, format_filings_for_context

# WolfPack database path
WOLFPACK_DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'wolfpack.db')


def check_ollama_running() -> bool:
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def list_models() -> List[str]:
    """List available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = response.json()
        return [m['name'] for m in data.get('models', [])]
    except:
        return []


def build_holdings_context() -> str:
    """Build context string for current holdings"""
    lines = ["YOUR CURRENT HOLDINGS:"]
    
    total_value = 0
    for ticker, info in HOLDINGS.items():
        data = get_stock_data(ticker)
        if data:
            value = info['shares'] * data['price']
            total_value += value
            pnl = ((data['price'] - info['avg_cost']) / info['avg_cost']) * 100
            lines.append(
                f"  {ticker}: {info['shares']} shares @ ${info['avg_cost']:.2f} "
                f"(now ${data['price']:.2f}, {data['change_pct']:+.2f}% today, {pnl:+.2f}% total) "
                f"[{info.get('thesis', '')}]"
            )
    
    lines.append(f"\nTotal portfolio value: ~${total_value:,.2f}")
    return "\n".join(lines)


def build_ticker_context(ticker: str) -> str:
    """Build context for a specific ticker"""
    lines = [f"\n{ticker} ANALYSIS:"]
    
    # Price data
    data = get_stock_data(ticker)
    if data:
        lines.append(f"  Price: ${data['price']:.2f}")
        lines.append(f"  Today: {data['change_pct']:+.2f}%")
        lines.append(f"  Volume: {data['volume_ratio']:.1f}x average")
        lines.append(f"  52wk High: ${data['high_52w']:.2f} ({data['from_high']:+.1f}%)")
        lines.append(f"  52wk Low: ${data['low_52w']:.2f} ({data['from_low']:+.1f}%)")
    
    # News
    news = get_company_news(ticker, days=7)
    if news:
        lines.append(f"\n  RECENT NEWS:")
        for item in news[:3]:
            lines.append(f"    [{item['datetime']}] {item['headline'][:80]}")
    
    # SEC filings
    filings = get_8k_filings(ticker, count=3)
    if filings:
        lines.append(f"\n  SEC FILINGS:")
        for f in filings:
            lines.append(f"    [{f.get('date')}] {f.get('title', '')[:60]}")
    
    # Check if it's a holding
    if ticker in HOLDINGS:
        info = HOLDINGS[ticker]
        lines.append(f"\n  YOU OWN THIS: {info['shares']} shares @ ${info['avg_cost']:.2f}")
        lines.append(f"  Thesis: {info.get('thesis', 'N/A')}")
    
    return "\n".join(lines)


def build_sector_context() -> str:
    """Build sector performance context"""
    perf = get_sector_performance(WATCHLIST)
    
    lines = ["\nSECTOR PERFORMANCE TODAY:"]
    for sector, change in perf.items():
        emoji = "🟢" if change > 0 else "🔴"
        lines.append(f"  {emoji} {sector}: {change:+.2f}%")
    
    return "\n".join(lines)


def build_wolfpack_context(ticker: str = None) -> str:
    """Build context from WolfPack database (historical patterns)"""
    if not os.path.exists(WOLFPACK_DB):
        return "\n[WolfPack database not initialized - no historical data available]"
    
    try:
        conn = sqlite3.connect(WOLFPACK_DB)
        cursor = conn.cursor()
        
        lines = ["\nWOLFPACK DATABASE (Historical Intelligence):"]
        
        # Total records
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT ticker) FROM daily_records")
        total_records, total_tickers = cursor.fetchone()
        lines.append(f"  {total_records} records across {total_tickers} tickers")
        
        # If specific ticker requested
        if ticker:
            cursor.execute('''
                SELECT COUNT(*), MIN(date), MAX(date)
                FROM daily_records
                WHERE ticker = ?
            ''', (ticker,))
            result = cursor.fetchone()
            if result and result[0] > 0:
                count, first_date, last_date = result
                lines.append(f"\n  {ticker} HISTORY:")
                lines.append(f"    {count} days tracked ({first_date} to {last_date})")
                
                # Get recent pattern
                cursor.execute('''
                    SELECT date, daily_return_pct, volume_ratio, 
                           dist_52w_high_pct, return_60d
                    FROM daily_records
                    WHERE ticker = ?
                    ORDER BY date DESC
                    LIMIT 5
                ''', (ticker,))
                recent = cursor.fetchall()
                lines.append(f"    Recent pattern:")
                for row in recent:
                    lines.append(f"      {row[0]}: {row[1]:+.1f}% ({row[2]:.1f}x vol), "
                               f"{row[3]:+.1f}% from high, 60d: {row[4]:+.1f}%")
        
        # Recent big moves across all stocks
        cursor.execute('''
            SELECT ticker, date, daily_return_pct, volume_ratio, sector
            FROM daily_records
            WHERE ABS(daily_return_pct) > 5
            ORDER BY date DESC
            LIMIT 5
        ''')
        big_moves = cursor.fetchall()
        if big_moves:
            lines.append(f"\n  RECENT BIG MOVES:")
            for row in big_moves:
                lines.append(f"    {row[0]} ({row[4]}): {row[2]:+.1f}% on {row[3]:.1f}x vol | {row[1]}")
        
        # Wounded prey patterns
        cursor.execute('''
            SELECT ticker, date, daily_return_pct, dist_52w_high_pct
            FROM daily_records
            WHERE dist_52w_high_pct < -30 AND daily_return_pct > 3
            ORDER BY date DESC
            LIMIT 3
        ''')
        wounded = cursor.fetchall()
        if wounded:
            lines.append(f"\n  WOUNDED PREY BOUNCES:")
            for row in wounded:
                lines.append(f"    {row[0]}: +{row[2]:.1f}% from {row[3]:.1f}% below highs | {row[1]}")
        
        conn.close()
        return "\n".join(lines)
        
    except Exception as e:
        return f"\n[WolfPack database error: {e}]"


def build_full_context(ticker: str = None, include_sectors: bool = False,
                       include_wolfpack: bool = True) -> str:
    """Build complete context for Fenrir"""
    parts = []
    
    # Always include holdings
    parts.append(build_holdings_context())
    
    # Specific ticker if requested
    if ticker:
        parts.append(build_ticker_context(ticker))
    
    # Sector overview if requested
    if include_sectors:
        parts.append(build_sector_context())
    
    # WolfPack historical data (NEW)
    if include_wolfpack:
        parts.append(build_wolfpack_context(ticker=ticker))
    
    return "\n".join(parts)


def ask_fenrir(question: str, ticker: str = None, 
               include_context: bool = True,
               include_sectors: bool = False,
               include_wolfpack: bool = True) -> str:
    """
    Ask Fenrir a question with optional real-time context
    
    Args:
        question: Your question
        ticker: Specific ticker to analyze (adds detailed context)
        include_context: Whether to include holdings context
        include_sectors: Whether to include sector performance
        include_wolfpack: Whether to include WolfPack database patterns (NEW)
    
    Returns:
        Fenrir's response
    """
    
    # Check if Ollama is running
    if not check_ollama_running():
        return "❌ Ollama is not running. Start it with: ollama serve"
    
    # Check if Fenrir model exists
    models = list_models()
    if OLLAMA_MODEL not in models and f"{OLLAMA_MODEL}:latest" not in models:
        return f"❌ Model '{OLLAMA_MODEL}' not found. Create it with: ollama create fenrir -f Modelfile"
    
    # Build the prompt
    if include_context:
        context = build_full_context(ticker=ticker, include_sectors=include_sectors,
                                    include_wolfpack=include_wolfpack)
        full_prompt = f"""
REAL-TIME MARKET DATA:
{context}

---

USER QUESTION:
{question}

---

Respond as Fenrir. Be direct, give your opinion, no disclaimers. If the data shows something, say it. If you need more info, ask for it specifically.
"""
    else:
        full_prompt = question
    
    # Query Ollama
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
        }
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}", 
            json=payload,
            timeout=120  # LLMs can be slow
        )
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', 'No response from Fenrir')
        
    except requests.exceptions.Timeout:
        return "❌ Fenrir timed out. The model might be loading or the question is too complex."
    except requests.exceptions.RequestException as e:
        return f"❌ Error talking to Fenrir: {e}"


def quick_opinion(ticker: str) -> str:
    """Get a quick opinion on a ticker"""
    data = get_stock_data(ticker)
    if not data:
        return f"Couldn't fetch data for {ticker}"
    
    question = f"{ticker} is at ${data['price']:.2f}, {data['change_pct']:+.2f}% today with {data['volume_ratio']:.1f}x volume. What's your read?"
    
    return ask_fenrir(question, ticker=ticker)


def analyze_mover(ticker: str, change_pct: float) -> str:
    """Analyze why something is moving"""
    question = f"{ticker} is moving {change_pct:+.2f}% today. What's the catalyst? Should I care?"
    return ask_fenrir(question, ticker=ticker)


def should_i_buy(ticker: str) -> str:
    """Get buy/don't buy opinion"""
    question = f"Should I buy {ticker} right now? Give me your honest take."
    return ask_fenrir(question, ticker=ticker)


def should_i_sell(ticker: str) -> str:
    """Get sell/hold opinion on a position"""
    if ticker not in HOLDINGS:
        return f"You don't own {ticker}."
    
    info = HOLDINGS[ticker]
    data = get_stock_data(ticker)
    
    if data:
        pnl = ((data['price'] - info['avg_cost']) / info['avg_cost']) * 100
        question = f"I own {info['shares']} shares of {ticker} at ${info['avg_cost']:.2f}. It's now ${data['price']:.2f} ({pnl:+.2f}%). Should I sell, hold, or add?"
    else:
        question = f"Should I sell my {ticker} position?"
    
    return ask_fenrir(question, ticker=ticker)


# =============================================================================
# TEST
# =============================================================================
if __name__ == "__main__":
    print("🐺 Testing Fenrir Brain...\n")
    
    # Check Ollama
    if check_ollama_running():
        print("✅ Ollama is running")
        print(f"   Available models: {list_models()}")
    else:
        print("❌ Ollama not running. Start with: ollama serve")
        exit(1)
    
    # Test basic question
    print("\n--- Testing Basic Question ---")
    response = ask_fenrir("What's your current read on the market?", include_sectors=True)
    print(response)
    
    # Test ticker analysis
    print("\n--- Testing Ticker Analysis ---")
    response = quick_opinion("IBRX")
    print(response)
