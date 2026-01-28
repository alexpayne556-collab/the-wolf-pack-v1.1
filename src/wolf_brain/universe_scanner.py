"""
🔍 UNIVERSE SCANNER - 100+ TICKERS, TWO HUNTING MODES
Built: January 20, 2026

Scans a universe of 100+ tickers looking for:
1. STEADY HUNTER setups (5-20% gains, higher win rate)
2. HEAD HUNTER setups (50-500%+ gains, explosive)

The scanner runs continuously and feeds opportunities to the brain.

Usage:
    from wolf_brain.universe_scanner import UniverseScanner
    
    scanner = UniverseScanner()
    
    # Get top opportunities
    setups = scanner.scan_for_opportunities()
    
    # Scan specific tickers
    results = scanner.scan_tickers(['GLSI', 'BTAI', 'ONCY'])
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Add wolfpack to path for shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'wolfpack'))
from utils.indicators import calculate_rsi, calculate_sma, calculate_volume_ratio

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False
    print("⚠️  yfinance not installed. Run: pip install yfinance")


class UniverseManager:
    """
    Manages the 100+ ticker universe
    """
    
    def __init__(self):
        """Initialize universe with core tickers"""
        self.static_universe = self._build_static_universe()
        self.dynamic_universe = {}
        self.blacklist = []
        self.hot_list = []
        
        print(f"📊 Universe Manager: {len(self.get_full_universe())} tickers loaded")
    
    def _build_static_universe(self) -> Dict[str, List[str]]:
        """Build the static universe of tickers by sector"""
        return {
            'biotech_clinical': [
                'ONCY', 'BTAI', 'EDSA', 'SNGX', 'TNXP', 'IBRX', 'OCGN', 'MNMD',
                'KROS', 'KYTX', 'CELC', 'VNDA', 'DNLI', 'NUVL', 'CGTX', 'ALLO',
                'FDMT', 'ADVM', 'PHGE', 'IOVA', 'GLSI', 'PMCB', 'HGEN', 'TGTX'
            ],
            
            'nuclear_energy': [
                'SMR', 'OKLO', 'NNE', 'BWXT', 'LEU', 'UEC', 'UUUU', 'DNN',
                'CCJ', 'NXE', 'URG', 'LTBR'
            ],
            
            'defense_space': [
                'KTOS', 'RKLB', 'LUNR', 'ASTS', 'RDW', 'ASTR', 'SPCE', 'VORB',
                'PL', 'IRDM', 'GILT', 'PLTR', 'LMT', 'RTX', 'NOC', 'GD'
            ],
            
            'quantum_ai': [
                'QBTS', 'IONQ', 'RGTI', 'QUBT', 'ARQQ', 'BBAI', 'SOUN', 'PATH',
                'AI', 'UPST', 'PLTR', 'PALX', 'SNOW', 'DDOG'
            ],
            
            'semiconductors': [
                'MU', 'INTC', 'AMD', 'NVDA', 'MRVL', 'KLAC', 'AMAT', 'LRCX',
                'TSM', 'ASML', 'AVGO', 'QCOM'
            ],
            
            'small_cap_momentum': [
                'CIFR', 'HIMS', 'RXRX', 'TALK', 'GEVO', 'PLUG', 'FCEL', 'BE',
                'NKLA', 'LCID', 'RIVN', 'FSR', 'FFIE', 'MULN'
            ],
            
            'crypto_fintech': [
                'COIN', 'MSTR', 'RIOT', 'MARA', 'HIVE', 'HUT', 'BITF', 'CLSK',
                'SQ', 'PYPL', 'SOFI', 'HOOD', 'AFRM'
            ],
            
            'healthcare_pharma': [
                'MRNA', 'BNTX', 'PFE', 'JNJ', 'LLY', 'NVO', 'ABBV', 'BMY',
                'GILD', 'REGN', 'VRTX', 'BIIB'
            ],
            
            'growth_tech': [
                'SHOP', 'NET', 'CRWD', 'ZS', 'OKTA', 'TWLO', 'MDB', 'DOCN',
                'GTLB', 'APP', 'BILL', 'TTD'
            ]
        }
    
    def get_full_universe(self) -> List[str]:
        """Get all tickers in the universe"""
        all_tickers = set()
        
        # Add static universe
        for sector, tickers in self.static_universe.items():
            all_tickers.update(tickers)
        
        # Add dynamic universe
        for category, tickers in self.dynamic_universe.items():
            all_tickers.update(tickers)
        
        # Remove blacklisted
        all_tickers -= set(self.blacklist)
        
        return list(all_tickers)
    
    def get_sector_tickers(self, sector: str) -> List[str]:
        """Get tickers for a specific sector"""
        return self.static_universe.get(sector, [])
    
    def get_sectors(self) -> List[str]:
        """Get list of all sectors"""
        return list(self.static_universe.keys())
    
    def add_to_hot_list(self, ticker: str):
        """Add ticker to priority monitoring"""
        if ticker not in self.hot_list:
            self.hot_list.append(ticker)
    
    def add_to_blacklist(self, ticker: str, reason: str = ""):
        """Add ticker to blacklist"""
        if ticker not in self.blacklist:
            self.blacklist.append(ticker)
            print(f"⛔ {ticker} blacklisted: {reason}")
    
    def add_dynamic_tickers(self, category: str, tickers: List[str]):
        """Add tickers to dynamic universe"""
        self.dynamic_universe[category] = tickers


class TickerDataFetcher:
    """
    Fetches ticker data using yfinance
    """
    
    def __init__(self, cache_duration_minutes: int = 5):
        """Initialize with optional caching"""
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def get_ticker_data(self, ticker: str, use_cache: bool = True) -> Dict:
        """
        Get comprehensive data for a ticker
        """
        # Check cache
        if use_cache and ticker in self.cache:
            cached_time, cached_data = self.cache[ticker]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        if not YF_AVAILABLE:
            return self._get_mock_data(ticker)
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get price history
            hist = stock.history(period='3mo')
            
            if hist.empty:
                return self._get_mock_data(ticker)
            
            current_price = hist['Close'].iloc[-1]
            high_52w = info.get('fiftyTwoWeekHigh', hist['High'].max())
            low_52w = info.get('fiftyTwoWeekLow', hist['Low'].min())
            
            # Calculate metrics
            drawdown = (high_52w - current_price) / high_52w if high_52w > 0 else 0
            
            # Volume analysis
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            relative_volume = calculate_volume_ratio(current_volume, avg_volume)
            
            # Price change
            day_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] if len(hist) > 1 else 0
            week_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5] if len(hist) > 5 else 0
            month_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20] if len(hist) > 20 else 0
            
            # Technical indicators - using unified indicators
            ma_50 = calculate_sma(hist['Close'], 50)
            above_50ma = current_price > ma_50 if ma_50 else False
            
            # RSI calculation (14-day) - using unified indicators
            rsi = calculate_rsi(hist['Close'])
            
            # Chart health classification
            chart_health = self._classify_chart_health(hist)
            
            data = {
                'ticker': ticker,
                'current_price': float(current_price),
                'high_52w': float(high_52w),
                'low_52w': float(low_52w),
                'drawdown_from_high': float(drawdown),
                'float': info.get('floatShares', 0),
                'market_cap': info.get('marketCap', 0),
                'avg_volume': float(avg_volume),
                'current_volume': float(current_volume),
                'relative_volume': float(relative_volume),
                'day_change_pct': float(day_change * 100),
                'week_change_pct': float(week_change * 100),
                'month_change_pct': float(month_change * 100),
                'rsi': float(rsi) if not pd.isna(rsi) else 50,
                'above_50ma': above_50ma,
                'ma_50': float(ma_50),
                'chart_health': chart_health,
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'short_interest_pct': info.get('shortPercentOfFloat', 0) * 100 if info.get('shortPercentOfFloat') else 0,
                'fetched_at': datetime.now().isoformat()
            }
            
            # Cache the data
            self.cache[ticker] = (datetime.now(), data)
            
            return data
            
        except Exception as e:
            print(f"⚠️  Error fetching {ticker}: {e}")
            return self._get_mock_data(ticker)
    
    def _classify_chart_health(self, hist) -> str:
        """
        Classify chart as HEALTHY (IBRX-style) or UNHEALTHY (IVF-style)
        """
        if len(hist) < 20:
            return 'UNCERTAIN'
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        # Check for spike and crash (unhealthy)
        max_single_day_gain = returns.max()
        max_single_day_loss = returns.min()
        
        if max_single_day_gain > 0.30:  # 30%+ single day spike
            # Check if followed by crash
            spike_idx = returns.idxmax()
            if spike_idx in hist.index:
                post_spike = hist.loc[spike_idx:]['Close']
                if len(post_spike) > 1:
                    post_spike_return = (post_spike.iloc[-1] - post_spike.iloc[0]) / post_spike.iloc[0]
                    if post_spike_return < -0.20:  # 20%+ crash after spike
                        return 'UNHEALTHY'
        
        # Check for stair-step pattern (healthy)
        # Look for higher lows
        lows = hist['Low'].rolling(5).min()
        higher_lows = (lows.diff() > 0).sum() / len(lows) > 0.4
        
        # Look for controlled pullbacks
        pullbacks = []
        high = hist['High'].iloc[0]
        for i, row in hist.iterrows():
            if row['High'] > high:
                high = row['High']
            pullback = (high - row['Low']) / high
            pullbacks.append(pullback)
        
        max_pullback = max(pullbacks)
        avg_pullback = sum(pullbacks) / len(pullbacks)
        
        if max_pullback < 0.25 and avg_pullback < 0.10 and higher_lows:
            return 'HEALTHY'
        elif max_pullback > 0.40:
            return 'UNHEALTHY'
        else:
            return 'UNCERTAIN'
    
    def _get_mock_data(self, ticker: str) -> Dict:
        """Return mock data for testing"""
        return {
            'ticker': ticker,
            'current_price': 10.00,
            'high_52w': 15.00,
            'low_52w': 5.00,
            'drawdown_from_high': 0.33,
            'float': 10_000_000,
            'market_cap': 100_000_000,
            'avg_volume': 500_000,
            'current_volume': 750_000,
            'relative_volume': 1.5,
            'day_change_pct': 2.5,
            'week_change_pct': 5.0,
            'month_change_pct': -10.0,
            'rsi': 55,
            'above_50ma': True,
            'ma_50': 9.50,
            'chart_health': 'UNCERTAIN',
            'sector': 'Healthcare',
            'industry': 'Biotechnology',
            'short_interest_pct': 15.0,
            'fetched_at': datetime.now().isoformat()
        }
    
    def fetch_multiple(self, tickers: List[str], max_workers: int = 10) -> Dict[str, Dict]:
        """
        Fetch data for multiple tickers in parallel
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(self.get_ticker_data, ticker): ticker
                for ticker in tickers
            }
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    data = future.result()
                    results[ticker] = data
                except Exception as e:
                    print(f"⚠️  Error fetching {ticker}: {e}")
                    results[ticker] = self._get_mock_data(ticker)
        
        return results


# Need pandas for RSI calculation
try:
    import pandas as pd
except ImportError:
    print("⚠️  pandas not installed")


class UniverseScanner:
    """
    Scans the universe for trading opportunities
    """
    
    def __init__(self):
        """Initialize scanner"""
        self.universe = UniverseManager()
        self.fetcher = TickerDataFetcher()
        
        print(f"🔍 Universe Scanner initialized")
        print(f"   Total tickers: {len(self.universe.get_full_universe())}")
    
    def scan_for_opportunities(self, limit: int = 20) -> Dict[str, List[Dict]]:
        """
        Scan entire universe for opportunities
        
        Returns:
            {
                'steady_setups': [...],
                'head_hunter_setups': [...]
            }
        """
        print("\n🔍 SCANNING UNIVERSE FOR OPPORTUNITIES...")
        start_time = time.time()
        
        # Get all tickers
        all_tickers = self.universe.get_full_universe()
        print(f"   Scanning {len(all_tickers)} tickers...")
        
        # Fetch data in parallel
        all_data = self.fetcher.fetch_multiple(all_tickers)
        
        # Classify setups
        steady_setups = []
        head_hunter_setups = []
        
        for ticker, data in all_data.items():
            # Check for Steady Hunter setup
            steady_score, steady_reasons = self._score_steady_setup(data)
            if steady_score >= 40:
                steady_setups.append({
                    'ticker': ticker,
                    'strategy': 'STEADY_HUNTER',
                    'score': steady_score,
                    'reasons': steady_reasons,
                    'data': data
                })
            
            # Check for Head Hunter setup
            head_score, head_reasons = self._score_head_hunter_setup(data)
            if head_score >= 50:
                head_hunter_setups.append({
                    'ticker': ticker,
                    'strategy': 'HEAD_HUNTER',
                    'score': head_score,
                    'reasons': head_reasons,
                    'data': data
                })
        
        # Sort by score
        steady_setups = sorted(steady_setups, key=lambda x: x['score'], reverse=True)[:limit]
        head_hunter_setups = sorted(head_hunter_setups, key=lambda x: x['score'], reverse=True)[:limit]
        
        elapsed = time.time() - start_time
        print(f"   Scan complete in {elapsed:.1f}s")
        print(f"   Found {len(steady_setups)} STEADY setups, {len(head_hunter_setups)} HEAD HUNTER setups")
        
        return {
            'steady_setups': steady_setups,
            'head_hunter_setups': head_hunter_setups,
            'scan_time': elapsed,
            'tickers_scanned': len(all_tickers)
        }
    
    def scan_tickers(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        Scan specific tickers
        """
        results = {}
        data = self.fetcher.fetch_multiple(tickers)
        
        for ticker, ticker_data in data.items():
            steady_score, steady_reasons = self._score_steady_setup(ticker_data)
            head_score, head_reasons = self._score_head_hunter_setup(ticker_data)
            
            results[ticker] = {
                'data': ticker_data,
                'steady_hunter': {
                    'score': steady_score,
                    'reasons': steady_reasons,
                    'signal': 'BUY' if steady_score >= 40 else 'PASS'
                },
                'head_hunter': {
                    'score': head_score,
                    'reasons': head_reasons,
                    'signal': 'BUY' if head_score >= 50 else 'PASS'
                }
            }
        
        return results
    
    def scan_sector(self, sector: str) -> List[Dict]:
        """Scan a specific sector"""
        tickers = self.universe.get_sector_tickers(sector)
        return self.scan_tickers(tickers)
    
    def _score_steady_setup(self, data: Dict) -> Tuple[int, List[str]]:
        """
        Score a setup for Steady Hunter strategy
        Target: 5-20% gains, higher win rate
        """
        score = 0
        reasons = []
        
        # Wounded prey (20-40% off highs)
        drawdown = data.get('drawdown_from_high', 0)
        if 0.20 <= drawdown <= 0.40:
            score += 25
            reasons.append(f"Wounded {drawdown:.0%} from highs")
        elif 0.10 <= drawdown <= 0.20:
            score += 10
            reasons.append(f"Pullback {drawdown:.0%}")
        
        # Near support / above 50 MA
        if data.get('above_50ma'):
            score += 15
            reasons.append("Above 50-day MA")
        
        # Healthy chart
        if data.get('chart_health') == 'HEALTHY':
            score += 20
            reasons.append("Healthy chart pattern")
        elif data.get('chart_health') == 'UNHEALTHY':
            score -= 20
            reasons.append("⚠️ Unhealthy chart")
        
        # Volume confirmation
        rel_vol = data.get('relative_volume', 1.0)
        if rel_vol >= 1.5:
            score += 10
            reasons.append(f"Volume surge {rel_vol:.1f}x")
        
        # RSI not overbought
        rsi = data.get('rsi', 50)
        if 30 <= rsi <= 60:
            score += 10
            reasons.append(f"RSI healthy ({rsi:.0f})")
        elif rsi > 70:
            score -= 10
            reasons.append(f"⚠️ RSI overbought ({rsi:.0f})")
        
        # Quality filter - market cap
        market_cap = data.get('market_cap', 0)
        if market_cap >= 100_000_000:  # $100M+
            score += 10
            reasons.append("Quality market cap")
        
        return score, reasons
    
    def _score_head_hunter_setup(self, data: Dict) -> Tuple[int, List[str]]:
        """
        Score a setup for Head Hunter strategy
        Target: 50-500%+ gains, explosive moves
        """
        score = 0
        reasons = []
        
        # Low float (REQUIRED for explosions)
        float_shares = data.get('float', float('inf'))
        if float_shares < 10_000_000:
            score += 30
            reasons.append(f"Ultra-low float: {float_shares/1e6:.1f}M")
        elif float_shares < 20_000_000:
            score += 20
            reasons.append(f"Low float: {float_shares/1e6:.1f}M")
        elif float_shares < 50_000_000:
            score += 10
            reasons.append(f"Moderate float: {float_shares/1e6:.1f}M")
        else:
            return 0, ["Float too high for head hunter"]  # Disqualify
        
        # Price range ($0.50 - $10 ideal)
        price = data.get('current_price', 0)
        if 0.50 <= price <= 5.00:
            score += 20
            reasons.append(f"Prime price: ${price:.2f}")
        elif 5.00 < price <= 10.00:
            score += 10
            reasons.append(f"Good price: ${price:.2f}")
        elif price > 20:
            score -= 10
            reasons.append(f"Price high for moonshot: ${price:.2f}")
        
        # High short interest (squeeze fuel)
        short_pct = data.get('short_interest_pct', 0)
        if short_pct > 20:
            score += 15
            reasons.append(f"High short: {short_pct:.0f}%")
        elif short_pct > 10:
            score += 10
            reasons.append(f"Short interest: {short_pct:.0f}%")
        
        # Chart compression (coiled spring)
        if data.get('chart_health') == 'HEALTHY':
            score += 10
            reasons.append("Healthy base pattern")
        
        # Recent momentum building
        week_change = data.get('week_change_pct', 0)
        if 5 <= week_change <= 20:
            score += 10
            reasons.append(f"Building momentum: +{week_change:.0f}% week")
        
        # Biotech/high-beta sector bonus
        sector = data.get('sector', '').lower()
        if 'health' in sector or 'biotech' in sector:
            score += 10
            reasons.append("Biotech sector (binary events)")
        
        return score, reasons
    
    def get_top_opportunities(self, n: int = 10) -> List[Dict]:
        """
        Get top N opportunities across both strategies
        """
        results = self.scan_for_opportunities(limit=n)
        
        all_setups = results['steady_setups'] + results['head_hunter_setups']
        
        # Sort by score
        all_setups = sorted(all_setups, key=lambda x: x['score'], reverse=True)
        
        return all_setups[:n]
    
    def get_premarket_movers(self) -> List[Dict]:
        """
        Get premarket movers (placeholder - would need real premarket data)
        """
        # Would integrate with premarket data source
        return []
    
    def get_after_hours_movers(self) -> List[Dict]:
        """
        Get after hours movers (placeholder - would need real AH data)
        """
        # Would integrate with after-hours data source
        return []


# ============ TESTING ============

def test_scanner():
    """Test the universe scanner"""
    print("\n" + "="*80)
    print("🔍 TESTING UNIVERSE SCANNER")
    print("="*80)
    
    scanner = UniverseScanner()
    
    # Test specific tickers
    print("\n📝 Testing: Scan specific tickers")
    test_tickers = ['IBRX', 'GLSI', 'ONCY', 'MU', 'KTOS']
    results = scanner.scan_tickers(test_tickers)
    
    for ticker, result in results.items():
        print(f"\n{ticker}:")
        print(f"   Price: ${result['data']['current_price']:.2f}")
        print(f"   Steady Score: {result['steady_hunter']['score']} ({result['steady_hunter']['signal']})")
        print(f"   Head Hunter Score: {result['head_hunter']['score']} ({result['head_hunter']['signal']})")
    
    # Test full scan (comment out if taking too long)
    # print("\n📝 Testing: Full universe scan")
    # opportunities = scanner.scan_for_opportunities(limit=5)
    # print(f"   Found {len(opportunities['steady_setups'])} steady setups")
    # print(f"   Found {len(opportunities['head_hunter_setups'])} head hunter setups")
    
    print("\n✅ Scanner tests complete!")


if __name__ == "__main__":
    test_scanner()
