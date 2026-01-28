"""
WOLF PACK - LIGHTWEIGHT RESEARCH SYSTEM
========================================

THIS VERSION: Research and scanning ONLY (no trading, no Ollama, minimal RAM)

Purpose: Find wounded prey opportunities and export data for manual review
No trading execution - just intelligence gathering
Can run on low-RAM machines or cloud instances

Author: Wolf Pack Team
Date: January 27, 2026
"""

import os
import sys
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add wolfpack to path for shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'wolfpack'))
from utils.indicators import calculate_rsi, calculate_volume_ratio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# API Keys (optional - system works without them, just fewer features)
FINNHUB_KEY = os.environ.get('FINNHUB_API_KEY', '')
NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY', '')

# Import optional dependencies
try:
    import finnhub
    FINNHUB_AVAILABLE = bool(FINNHUB_KEY)
except ImportError:
    FINNHUB_AVAILABLE = False
    log.warning("⚠️  Finnhub not installed. Run: pip install finnhub-python")

try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = bool(NEWSAPI_KEY)
except ImportError:
    NEWSAPI_AVAILABLE = False
    log.warning("⚠️  NewsAPI not installed. Run: pip install newsapi-python")


class LightweightResearcher:
    """
    Lightweight research-only scanner
    
    Features:
    - Scans for wounded prey patterns
    - Analyzes technical signals
    - Grades opportunities (0-100 score)
    - Exports data to JSON/CSV
    - NO trading execution
    - NO heavy AI models
    - Minimal RAM usage
    """
    
    def __init__(self, universe_file: str = None):
        """
        Initialize the researcher
        
        Args:
            universe_file: Path to JSON file with stock symbols (optional)
        """
        self.universe_file = universe_file or "data/research_universe.json"
        self.results_dir = "research_output"
        
        # Create output directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialize API clients (if available)
        self.finnhub_client = None
        self.news_client = None
        
        if FINNHUB_AVAILABLE:
            self.finnhub_client = finnhub.Client(api_key=FINNHUB_KEY)
            log.info("✅ Finnhub connected")
        
        if NEWSAPI_AVAILABLE:
            self.news_client = NewsApiClient(api_key=NEWSAPI_KEY)
            log.info("✅ NewsAPI connected")
        
        log.info("🐺 Lightweight Researcher initialized")
    
    def load_universe(self) -> List[str]:
        """Load stock universe from file or use defaults"""
        try:
            with open(self.universe_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'symbols' in data:
                    return data['symbols']
                else:
                    log.warning("⚠️  Invalid universe format, using defaults")
                    return self._default_universe()
        except FileNotFoundError:
            log.info("📋 No universe file found, using defaults")
            return self._default_universe()
    
    def _default_universe(self) -> List[str]:
        """Default small-cap biotech/tech universe"""
        return [
            # Biotech small caps
            'IBRX', 'RXRX', 'RNAZ', 'SAVA', 'ABCL', 'FATE', 'BEAM', 'CRSP',
            'NTLA', 'BLUE', 'SGMO', 'EDIT', 'IONS', 'MRNA', 'BNTX',
            # Tech small caps
            'PLTR', 'SNOW', 'NET', 'DDOG', 'ZS', 'CRWD', 'S', 'ESTC',
            # Volatile momentum
            'TSLA', 'GME', 'AMC', 'BBBY', 'LCID', 'RIVN'
        ]
    
    def analyze_wounded_prey(self, symbol: str) -> Optional[Dict]:
        """
        Analyze a single symbol for wounded prey pattern
        
        Returns dict with:
        - convergence_score (0-100)
        - signals (dict of individual signal scores)
        - recommendation (BUY/HOLD/PASS)
        - data (price, volume, etc)
        """
        try:
            log.info(f"🔍 Analyzing {symbol}...")
            
            # Get historical data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period='3mo', interval='1d')
            
            if len(df) < 30:
                log.warning(f"⚠️  {symbol}: Insufficient data")
                return None
            
            # Calculate signals
            signals = {}
            
            # 1. Volume Spike (0-20 points) - using unified indicators
            avg_volume = df['Volume'].tail(20).mean()
            recent_volume = df['Volume'].tail(5).mean()
            volume_ratio = calculate_volume_ratio(recent_volume, avg_volume)
            signals['volume_spike'] = min(20, volume_ratio * 10)
            
            # 2. Price Decline (wounded prey - 0-20 points)
            high_52w = df['High'].tail(252).max()
            current_price = df['Close'].iloc[-1]
            decline_pct = ((high_52w - current_price) / high_52w) * 100
            signals['decline'] = min(20, decline_pct / 3)  # More decline = more points
            
            # 3. RSI Oversold (0-20 points) - using unified indicators
            rsi = calculate_rsi(df['Close'])
            if rsi < 30:
                signals['rsi_oversold'] = 20
            elif rsi < 40:
                signals['rsi_oversold'] = 10
            else:
                signals['rsi_oversold'] = 0
            
            # 4. Recent Reversal (0-20 points)
            last_3_days = df['Close'].tail(3).pct_change()
            if len(last_3_days) >= 2 and last_3_days.iloc[-1] > 0 and last_3_days.iloc[-2] < 0:
                signals['reversal'] = 20
            elif last_3_days.iloc[-1] > 0:
                signals['reversal'] = 10
            else:
                signals['reversal'] = 0
            
            # 5. News Sentiment (0-20 points) - if available
            if self.news_client:
                sentiment_score = self._get_news_sentiment(symbol)
                signals['news_sentiment'] = sentiment_score
            else:
                signals['news_sentiment'] = 0
            
            # Calculate total convergence score
            convergence_score = sum(signals.values())
            
            # Recommendation
            if convergence_score >= 70:
                recommendation = "🟢 STRONG BUY"
            elif convergence_score >= 50:
                recommendation = "🟡 BUY"
            elif convergence_score >= 30:
                recommendation = "⚪ WATCH"
            else:
                recommendation = "🔴 PASS"
            
            # Build result
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'convergence_score': round(convergence_score, 1),
                'recommendation': recommendation,
                'signals': signals,
                'data': {
                    'current_price': round(current_price, 2),
                    'high_52w': round(high_52w, 2),
                    'decline_from_high': round(decline_pct, 1),
                    'volume_ratio': round(volume_ratio, 2),
                    'rsi': round(rsi, 1),
                    'avg_volume': int(avg_volume),
                    'recent_volume': int(recent_volume)
                }
            }
            
            log.info(f"✅ {symbol}: {convergence_score:.1f}/100 - {recommendation}")
            return result
            
        except Exception as e:
            log.error(f"❌ {symbol}: Error - {e}")
            return None
    
    def _get_news_sentiment(self, symbol: str) -> float:
        """Get news sentiment score (0-20 points)"""
        try:
            yesterday = datetime.now() - timedelta(days=7)
            articles = self.news_client.get_everything(
                q=symbol,
                from_param=yesterday.strftime('%Y-%m-%d'),
                language='en',
                sort_by='relevancy',
                page_size=10
            )
            
            if not articles['articles']:
                return 0
            
            # Simple sentiment: count positive vs negative keywords
            positive_words = ['surge', 'jump', 'rally', 'gain', 'beat', 'breakthrough', 'approval']
            negative_words = ['crash', 'plunge', 'drop', 'miss', 'decline', 'lawsuit', 'warning']
            
            pos_count = 0
            neg_count = 0
            
            for article in articles['articles'][:5]:
                text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                pos_count += sum(word in text for word in positive_words)
                neg_count += sum(word in text for word in negative_words)
            
            if pos_count > neg_count:
                return 20
            elif pos_count == neg_count:
                return 10
            else:
                return 0
                
        except Exception as e:
            log.warning(f"⚠️  News sentiment failed: {e}")
            return 0
    
    def scan_universe(self, top_n: int = 10) -> List[Dict]:
        """
        Scan entire universe and return top opportunities
        
        Args:
            top_n: Number of top results to return
            
        Returns:
            List of opportunity dicts sorted by convergence score
        """
        log.info("🐺 Starting universe scan...")
        universe = self.load_universe()
        log.info(f"📋 Scanning {len(universe)} symbols...")
        
        results = []
        for symbol in universe:
            result = self.analyze_wounded_prey(symbol)
            if result:
                results.append(result)
        
        # Sort by convergence score
        results.sort(key=lambda x: x['convergence_score'], reverse=True)
        
        log.info(f"✅ Scan complete: {len(results)} analyzed, top {top_n} returned")
        return results[:top_n]
    
    def export_results(self, results: List[Dict], format: str = 'both'):
        """
        Export results to file
        
        Args:
            results: List of opportunity dicts
            format: 'json', 'csv', or 'both'
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export JSON
        if format in ['json', 'both']:
            json_path = os.path.join(self.results_dir, f'scan_{timestamp}.json')
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            log.info(f"💾 JSON saved: {json_path}")
        
        # Export CSV
        if format in ['csv', 'both']:
            # Flatten data for CSV
            flat_data = []
            for r in results:
                flat = {
                    'symbol': r['symbol'],
                    'score': r['convergence_score'],
                    'recommendation': r['recommendation'],
                    'price': r['data']['current_price'],
                    'decline_pct': r['data']['decline_from_high'],
                    'volume_ratio': r['data']['volume_ratio'],
                    'rsi': r['data']['rsi'],
                    'timestamp': r['timestamp']
                }
                flat_data.append(flat)
            
            df = pd.DataFrame(flat_data)
            csv_path = os.path.join(self.results_dir, f'scan_{timestamp}.csv')
            df.to_csv(csv_path, index=False)
            log.info(f"💾 CSV saved: {csv_path}")
    
    def run_scan(self, top_n: int = 10, export: bool = True):
        """
        Main entry point: scan universe and export results
        
        Args:
            top_n: Number of top opportunities to return
            export: Whether to export results to files
        """
        log.info("=" * 50)
        log.info("🐺 WOLF PACK LIGHTWEIGHT RESEARCH SCAN")
        log.info("=" * 50)
        
        # Scan
        results = self.scan_universe(top_n=top_n)
        
        # Print top results
        log.info("\n📊 TOP OPPORTUNITIES:")
        log.info("-" * 50)
        for i, r in enumerate(results[:10], 1):
            log.info(f"{i}. {r['symbol']:6s} - {r['convergence_score']:5.1f}/100 - {r['recommendation']}")
            log.info(f"   Price: ${r['data']['current_price']:.2f} | "
                    f"Down {r['data']['decline_from_high']:.1f}% from high | "
                    f"RSI: {r['data']['rsi']:.1f}")
        
        # Export
        if export:
            self.export_results(results)
        
        log.info("\n✅ Scan complete!")
        return results


if __name__ == "__main__":
    # Run the scanner
    researcher = LightweightResearcher()
    results = researcher.run_scan(top_n=15)
