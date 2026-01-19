#!/usr/bin/env python3
"""
NEWS INTELLIGENCE SERVICE
Context Layer for Scanner Signals

Fetches recent news for tickers and provides context:
- Why is it wounded? (accounting probe, CEO resignation, product failure)
- Is the narrative improving or worsening?
- Sentiment analysis (bullish/bearish/neutral)
- Catalyst discovery (mentions of FDA approval dates, earnings, etc.)

Data Source: NewsAPI (100 requests/day free tier)
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')
NEWSAPI_BASE_URL = "https://newsapi.org/v2"


# =============================================================================
# DATA MODELS
# =============================================================================

class Sentiment(Enum):
    """News sentiment"""
    VERY_BEARISH = -2
    BEARISH = -1
    NEUTRAL = 0
    BULLISH = 1
    VERY_BULLISH = 2


@dataclass
class NewsArticle:
    """Individual news article"""
    title: str
    description: str
    url: str
    source: str
    published_at: str
    sentiment: Sentiment
    keywords: List[str]


@dataclass
class NewsSignal:
    """News intelligence signal for convergence"""
    ticker: str
    score: int  # 0-100 (sentiment + recency + volume)
    sentiment: Sentiment
    recent_articles: List[NewsArticle]
    narrative: str  # Summary of what's happening
    red_flags: List[str]  # Warning signs (probe, resignation, lawsuit, etc.)
    catalysts_mentioned: List[str]  # Upcoming events mentioned in news
    reasoning: str


# =============================================================================
# SENTIMENT ANALYSIS (Simple Keyword-Based)
# =============================================================================

BEARISH_KEYWORDS = [
    'probe', 'investigation', 'fraud', 'resign', 'lawsuit', 'loss', 'missed',
    'downgrade', 'warning', 'concern', 'weak', 'decline', 'plunge', 'crash',
    'bankruptcy', 'restructuring', 'layoff', 'close', 'shut', 'fail',
    'short seller', 'accounting', 'sec investigation', 'doj probe'
]

BULLISH_KEYWORDS = [
    'beat', 'exceed', 'strong', 'growth', 'upgrade', 'buy rating', 'approval',
    'breakthrough', 'partnership', 'contract', 'award', 'positive', 'surge',
    'rally', 'bullish', 'optimistic', 'expansion', 'innovation', 'record',
    'acquisition', 'merger', 'catalyst', 'insider buying'
]

RED_FLAG_KEYWORDS = [
    'sec investigation', 'doj probe', 'fraud', 'accounting irregularities',
    'cfo resigns', 'ceo resigns', 'class action', 'short seller report',
    'bankruptcy', 'going concern', 'restatement', 'whistleblower'
]


def analyze_sentiment(text: str) -> Sentiment:
    """
    Simple keyword-based sentiment analysis
    More sophisticated: use TextBlob or transformers later
    """
    text_lower = text.lower()
    
    bearish_count = sum(1 for keyword in BEARISH_KEYWORDS if keyword in text_lower)
    bullish_count = sum(1 for keyword in BULLISH_KEYWORDS if keyword in text_lower)
    
    # Score from -2 to +2
    if bearish_count >= bullish_count + 3:
        return Sentiment.VERY_BEARISH
    elif bearish_count > bullish_count:
        return Sentiment.BEARISH
    elif bullish_count >= bearish_count + 3:
        return Sentiment.VERY_BULLISH
    elif bullish_count > bearish_count:
        return Sentiment.BULLISH
    else:
        return Sentiment.NEUTRAL


def extract_red_flags(text: str) -> List[str]:
    """Extract red flag keywords from text"""
    text_lower = text.lower()
    return [flag for flag in RED_FLAG_KEYWORDS if flag in text_lower]


# =============================================================================
# NEWS SERVICE
# =============================================================================

class NewsService:
    """Fetch and analyze news for tickers"""
    
    def __init__(self, api_key: str = NEWSAPI_KEY):
        if not api_key:
            raise ValueError("NewsAPI key required. Set NEWSAPI_KEY in .env file")
        
        self.api_key = api_key
        self.base_url = NEWSAPI_BASE_URL
    
    def fetch_news(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        days_back: int = 7
    ) -> List[NewsArticle]:
        """
        Fetch recent news articles for a ticker
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name for better search (optional)
            days_back: How many days back to search
        
        Returns:
            List of NewsArticle objects
        """
        # Search query
        if company_name:
            query = f'"{ticker}" OR "{company_name}"'
        else:
            query = f'"{ticker}"'
        
        # Date range
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        # API request
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', [])[:20]:  # Limit to 20 most recent
                title = article.get('title', '')
                description = article.get('description', '')
                
                # Analyze sentiment
                combined_text = f"{title} {description}"
                sentiment = analyze_sentiment(combined_text)
                keywords = extract_red_flags(combined_text)
                
                articles.append(NewsArticle(
                    title=title,
                    description=description or '',
                    url=article.get('url', ''),
                    source=article.get('source', {}).get('name', 'Unknown'),
                    published_at=article.get('publishedAt', ''),
                    sentiment=sentiment,
                    keywords=keywords
                ))
            
            return articles
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for {ticker}: {e}")
            return []
    
    def get_news_signal_for_convergence(
        self,
        ticker: str,
        company_name: Optional[str] = None,
        days_back: int = 7
    ) -> Optional[Dict]:
        """
        Get news signal formatted for convergence engine
        
        Returns:
            Dict with score (0-100), reasoning, and signal data
        """
        articles = self.fetch_news(ticker, company_name, days_back)
        
        if not articles:
            return None
        
        # Calculate aggregate sentiment
        sentiment_values = [art.sentiment.value for art in articles]
        avg_sentiment = sum(sentiment_values) / len(sentiment_values)
        
        # Extract red flags
        all_red_flags = []
        for article in articles:
            all_red_flags.extend(article.keywords)
        red_flags = list(set(all_red_flags))  # Deduplicate
        
        # Calculate score (0-100)
        # Base score from sentiment: -2 to +2 → 0 to 100
        sentiment_score = int(((avg_sentiment + 2) / 4) * 100)
        
        # Penalties for red flags
        red_flag_penalty = min(len(red_flags) * 15, 50)  # Up to -50 points
        
        # Bonus for recent positive news
        recent_bullish = sum(
            1 for art in articles[:3]  # Last 3 articles
            if art.sentiment.value >= 1
        )
        recency_bonus = recent_bullish * 10
        
        final_score = max(0, min(100, sentiment_score - red_flag_penalty + recency_bonus))
        
        # Determine sentiment enum
        if avg_sentiment >= 1.5:
            overall_sentiment = Sentiment.VERY_BULLISH
        elif avg_sentiment >= 0.5:
            overall_sentiment = Sentiment.BULLISH
        elif avg_sentiment <= -1.5:
            overall_sentiment = Sentiment.VERY_BEARISH
        elif avg_sentiment <= -0.5:
            overall_sentiment = Sentiment.BEARISH
        else:
            overall_sentiment = Sentiment.NEUTRAL
        
        # Generate narrative
        narrative = self._generate_narrative(articles, overall_sentiment, red_flags)
        
        # Build reasoning
        reasoning = f"{ticker} news: {len(articles)} articles (7d), sentiment {overall_sentiment.name}"
        if red_flags:
            reasoning += f", RED FLAGS: {', '.join(red_flags[:2])}"
        
        return {
            'score': final_score,
            'reasoning': reasoning,
            'data': {
                'sentiment': overall_sentiment.name,
                'article_count': len(articles),
                'red_flags': red_flags,
                'narrative': narrative,
                'recent_headlines': [art.title for art in articles[:5]]
            }
        }
    
    def _generate_narrative(
        self,
        articles: List[NewsArticle],
        sentiment: Sentiment,
        red_flags: List[str]
    ) -> str:
        """Generate a narrative summary from news articles"""
        if not articles:
            return "No recent news"
        
        # Check for major themes
        if red_flags:
            return f"⚠️ CAUTION: {', '.join(red_flags[:2])} mentioned in recent news"
        
        if sentiment == Sentiment.VERY_BULLISH:
            return "📈 Strong positive momentum - multiple bullish catalysts"
        elif sentiment == Sentiment.BULLISH:
            return "📊 Positive news flow - sentiment improving"
        elif sentiment == Sentiment.VERY_BEARISH:
            return "📉 Heavy negative pressure - avoid until sentiment stabilizes"
        elif sentiment == Sentiment.BEARISH:
            return "⚠️ Negative news flow - wait for improvement"
        else:
            return "📰 Mixed/neutral news - no clear narrative"


# =============================================================================
# FORMATTING
# =============================================================================

def format_news_report(signal: Optional[Dict], ticker: str) -> str:
    """Format news signal for terminal display"""
    if not signal:
        return f"📰 {ticker}: No recent news"
    
    data = signal['data']
    score = signal['score']
    
    # Emoji based on score
    if score >= 70:
        emoji = "📈"
    elif score >= 50:
        emoji = "📊"
    elif score >= 30:
        emoji = "⚠️"
    else:
        emoji = "🚨"
    
    report = f"""
{emoji} {ticker} NEWS ({score}/100)
Sentiment: {data['sentiment']}
Articles: {data['article_count']} in last 7 days
Narrative: {data['narrative']}
"""
    
    if data['red_flags']:
        report += f"\n🚨 RED FLAGS: {', '.join(data['red_flags'])}\n"
    
    if data['recent_headlines']:
        report += "\nRecent Headlines:\n"
        for headline in data['recent_headlines'][:3]:
            report += f"  • {headline}\n"
    
    return report


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("📰 NEWS SERVICE TEST\n")
    
    news_service = NewsService()
    
    # Test tickers with different news profiles
    test_tickers = [
        ("SMCI", "Super Micro Computer"),  # Recent accounting concerns
        ("MU", "Micron Technology"),        # Earnings coming up
        ("NVDA", "NVIDIA"),                 # Generally bullish
    ]
    
    for ticker, company_name in test_tickers:
        print("=" * 60)
        print(f"Testing: {ticker}")
        print("=" * 60)
        
        signal = news_service.get_news_signal_for_convergence(ticker, company_name)
        print(format_news_report(signal, ticker))
    
    print("\n✅ NEWS SERVICE TEST COMPLETE")
