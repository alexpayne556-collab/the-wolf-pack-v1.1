#!/usr/bin/env python3
"""
🐺 WOLF PACK PRE-POP SCANNER (INTEGRATED VERSION)
==================================================
Scores stocks on pre-explosion characteristics and integrates with autonomous brain

IMPROVEMENTS FROM ORIGINAL:
- Uses existing biotech_catalyst_scanner.py (no duplication)
- Integrates with autonomous_brain.py database
- Uses configured APIs (Finnhub, SEC, etc.)
- Stores results for learning
- Works with strategy coordinator

Author: Wolf Pack Trading System
"""

import yfinance as yf
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from modules.biotech_catalyst_scanner import BiotechCatalystScanner
except ImportError:
    print("⚠️  biotech_catalyst_scanner not found, using fallback")
    BiotechCatalystScanner = None


class PrePopScorer:
    """Scores stocks on 6 pre-explosion factors"""
    
    def __init__(self, db_path: str = "../../data/wolf_brain/autonomous_memory.db"):
        self.db_path = db_path
        self.biotech_scanner = BiotechCatalystScanner() if BiotechCatalystScanner else None
    
    def score_stock(self, ticker: str) -> Dict:
        """
        Score a stock on all 6 factors:
        1. Float/Liquidity (amplification potential)
        2. Catalyst Timing (when is the event?)
        3. Uncertainty Discount (beaten down = upside)
        4. Technical Compression (coiled spring)
        5. Insider Buying (smart money)
        6. Short Squeeze (additional fuel)
        """
        print(f"🔍 Scoring {ticker}...")
        
        # Get stock data
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="3mo")
            
            if hist.empty:
                return {"ticker": ticker, "error": "No data"}
            
            current_price = hist['Close'].iloc[-1]
            
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}
        
        # Calculate each factor
        scores = {
            "ticker": ticker,
            "price": round(current_price, 2),
            "scan_time": datetime.now().isoformat(),
        }
        
        # 1. Float/Liquidity
        float_score = self._score_float(info, hist)
        scores["float"] = float_score
        
        # 2. Catalyst Timing
        catalyst_score = self._score_catalyst(ticker)
        scores["catalyst"] = catalyst_score
        
        # 3. Uncertainty Discount
        uncertainty_score = self._score_uncertainty(info, stock, current_price)
        scores["uncertainty"] = uncertainty_score
        
        # 4. Technical Compression
        compression_score = self._score_compression(hist)
        scores["compression"] = compression_score
        
        # 5. Insider Buying (placeholder - would integrate with SEC Edgar)
        insider_score = self._score_insider(ticker)
        scores["insider"] = insider_score
        
        # 6. Short Squeeze
        squeeze_score = self._score_squeeze(info)
        scores["squeeze"] = squeeze_score
        
        # Calculate weighted total
        weights = {
            "catalyst": 2.0,      # Most important
            "float": 1.5,
            "uncertainty": 1.5,
            "compression": 1.0,
            "insider": 1.5,
            "squeeze": 1.0
        }
        
        weighted_sum = sum(scores[k]["score"] * weights[k] for k in weights.keys())
        max_possible = sum(10 * w for w in weights.values())
        total_score = round((weighted_sum / max_possible) * 100, 1)
        
        scores["total_score"] = total_score
        scores["grade"] = self._get_grade(total_score)
        
        return scores
    
    def _score_float(self, info: Dict, hist: any) -> Dict:
        """Low float = amplified moves"""
        float_shares = info.get("floatShares", info.get("sharesOutstanding", 0) * 0.8)
        avg_volume = int(hist['Volume'].mean())
        
        if float_shares < 10_000_000:
            score = 10
            desc = "EXPLOSIVE (<10M)"
        elif float_shares < 20_000_000:
            score = 8
            desc = "HIGH (10-20M)"
        elif float_shares < 50_000_000:
            score = 6
            desc = "MODERATE (20-50M)"
        else:
            score = 4
            desc = "LOW (>50M)"
        
        return {
            "score": score,
            "float_shares": float_shares,
            "avg_volume": avg_volume,
            "description": desc
        }
    
    def _score_catalyst(self, ticker: str) -> Dict:
        """Binary catalyst timing"""
        if self.biotech_scanner:
            catalysts = self.biotech_scanner.get_upcoming_catalysts(days_ahead=90)
            ticker_catalyst = next((c for c in catalysts if c["ticker"] == ticker), None)
            
            if ticker_catalyst:
                days_until = ticker_catalyst["days_until"]
                
                if days_until <= 7:
                    score = 10
                    timing = "IMMINENT (1-7 days)"
                elif days_until <= 14:
                    score = 9
                    timing = "SWEET SPOT (8-14 days)"
                elif days_until <= 30:
                    score = 7
                    timing = "GOOD (15-30 days)"
                elif days_until <= 60:
                    score = 5
                    timing = "EARLY (31-60 days)"
                else:
                    score = 3
                    timing = "TOO EARLY (60+ days)"
                
                return {
                    "score": score,
                    "catalyst": f"{ticker_catalyst['type']}: {ticker_catalyst['drug']}",
                    "date": ticker_catalyst["date"],
                    "days_until": days_until,
                    "timing": timing
                }
        
        return {
            "score": 1,
            "catalyst": None,
            "timing": "NO KNOWN CATALYST"
        }
    
    def _score_uncertainty(self, info: Dict, stock: any, current_price: float) -> Dict:
        """High uncertainty = big discount = big upside"""
        market_cap = info.get("marketCap", 0)
        revenue = info.get("totalRevenue", 0)
        
        # Revenue ratio
        rev_ratio = revenue / market_cap if market_cap > 0 and revenue else 0
        
        # Distance from 52-week high
        year_hist = stock.history(period="1y")
        if not year_hist.empty:
            high_52w = year_hist['High'].max()
            pct_from_high = ((current_price - high_52w) / high_52w) * 100
        else:
            pct_from_high = 0
        
        # Score
        if rev_ratio < 0.01:
            score = 9
            desc = "PRE-REVENUE"
        elif rev_ratio < 0.1:
            score = 7
            desc = "MINIMAL REVENUE"
        else:
            score = 5
            desc = "ESTABLISHED"
        
        # Bonus for beaten down
        if pct_from_high < -50:
            score = min(10, score + 2)
            desc += " + HEAVILY BEATEN"
        
        return {
            "score": score,
            "revenue_ratio": round(rev_ratio, 4),
            "pct_from_high": round(pct_from_high, 2),
            "description": desc
        }
    
    def _score_compression(self, hist: any) -> Dict:
        """Technical compression = coiled spring"""
        if len(hist) < 20:
            return {"score": 5, "description": "INSUFFICIENT DATA"}
        
        recent_20 = hist.tail(20)
        high_20 = recent_20['High'].max()
        low_20 = recent_20['Low'].min()
        range_20 = ((high_20 - low_20) / low_20) * 100 if low_20 > 0 else 0
        
        if range_20 < 15:
            score = 10
            desc = "TIGHT COIL (<15%)"
        elif range_20 < 25:
            score = 7
            desc = "MODERATE (15-25%)"
        elif range_20 < 40:
            score = 4
            desc = "LOOSE (25-40%)"
        else:
            score = 2
            desc = "VOLATILE (>40%)"
        
        return {
            "score": score,
            "range_20d": round(range_20, 2),
            "description": desc
        }
    
    def _score_insider(self, ticker: str) -> Dict:
        """Smart money accumulation (placeholder - integrate with SEC Edgar)"""
        # Known insider buying from manual research
        known_buys = {
            "PALI": {"buys": 3, "score": 10},
            "ONCY": {"buys": 1, "score": 4}
        }
        
        if ticker in known_buys:
            return {
                "score": known_buys[ticker]["score"],
                "buys": known_buys[ticker]["buys"],
                "description": f"{known_buys[ticker]['buys']} recent buys"
            }
        
        return {
            "score": 1,
            "buys": 0,
            "description": "NO DATA"
        }
    
    def _score_squeeze(self, info: Dict) -> Dict:
        """Short squeeze potential"""
        short_pct = info.get("shortPercentOfFloat", 0)
        
        if short_pct > 0.30:
            score = 10
            desc = f"EXTREME ({short_pct*100:.1f}%)"
        elif short_pct > 0.20:
            score = 8
            desc = f"HIGH ({short_pct*100:.1f}%)"
        elif short_pct > 0.10:
            score = 5
            desc = f"MODERATE ({short_pct*100:.1f}%)"
        else:
            score = 2
            desc = f"LOW ({short_pct*100:.1f}%)"
        
        return {
            "score": score,
            "short_percent": round(short_pct * 100, 2),
            "description": desc
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 80:
            return "🔥 A+ (PRIME SETUP)"
        elif score >= 70:
            return "🎯 A (STRONG)"
        elif score >= 60:
            return "✅ B (GOOD)"
        elif score >= 50:
            return "⚡ C (WATCH)"
        else:
            return "❌ D (PASS)"
    
    def scan_universe(self, tickers: List[str]) -> List[Dict]:
        """Scan multiple tickers and rank"""
        print(f"\n{'🐺'*20}")
        print(f"PRE-POP SCANNER - Scanning {len(tickers)} tickers")
        print(f"{'🐺'*20}\n")
        
        results = []
        for ticker in tickers:
            try:
                result = self.score_stock(ticker)
                if "error" not in result:
                    results.append(result)
                    self._store_result(result)
            except Exception as e:
                print(f"  ❌ {ticker}: {e}")
        
        # Sort by score
        results.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        
        return results
    
    def _store_result(self, result: Dict):
        """Store scan result in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''CREATE TABLE IF NOT EXISTS prepop_scans (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                ticker TEXT,
                price REAL,
                total_score REAL,
                catalyst_score REAL,
                float_score REAL,
                uncertainty_score REAL,
                compression_score REAL,
                insider_score REAL,
                squeeze_score REAL,
                catalyst_details TEXT,
                grade TEXT
            )''')
            
            c.execute("""INSERT INTO prepop_scans VALUES (
                NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )""", (
                result["scan_time"],
                result["ticker"],
                result["price"],
                result["total_score"],
                result["catalyst"]["score"],
                result["float"]["score"],
                result["uncertainty"]["score"],
                result["compression"]["score"],
                result["insider"]["score"],
                result["squeeze"]["score"],
                json.dumps(result["catalyst"]),
                result["grade"]
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"  ⚠️  Could not store result: {e}")
    
    def print_results(self, results: List[Dict], top_n: int = 10):
        """Print formatted results"""
        print(f"\n{'='*80}")
        print(f"🎯 TOP {top_n} PRE-POP CANDIDATES")
        print(f"{'='*80}\n")
        
        print(f"{'RANK':<5} {'TICKER':<8} {'PRICE':<8} {'SCORE':<8} {'GRADE':<20}")
        print("-" * 80)
        
        for i, r in enumerate(results[:top_n], 1):
            print(f"{i:<5} {r['ticker']:<8} ${r['price']:<7.2f} {r['total_score']:<8.1f} {r['grade']:<20}")
        
        print(f"\n{'='*80}")
        print("DETAILED BREAKDOWN - TOP 3")
        print(f"{'='*80}\n")
        
        for r in results[:3]:
            self._print_detailed(r)
    
    def _print_detailed(self, result: Dict):
        """Print detailed breakdown"""
        print(f"\n{'─'*60}")
        print(f"📊 {result['ticker']} - Score: {result['total_score']}/100 {result['grade']}")
        print(f"   Price: ${result['price']}")
        print(f"{'─'*60}")
        
        print(f"\n  📅 CATALYST: {result['catalyst']['score']}/10")
        print(f"     {result['catalyst'].get('catalyst', 'None')}")
        print(f"     {result['catalyst'].get('timing', 'Unknown')}")
        
        print(f"\n  📉 FLOAT: {result['float']['score']}/10 - {result['float']['description']}")
        print(f"\n  ❓ UNCERTAINTY: {result['uncertainty']['score']}/10 - {result['uncertainty']['description']}")
        print(f"\n  📈 COMPRESSION: {result['compression']['score']}/10 - {result['compression']['description']}")
        print(f"\n  👔 INSIDER: {result['insider']['score']}/10 - {result['insider']['description']}")
        print(f"\n  🩳 SQUEEZE: {result['squeeze']['score']}/10 - {result['squeeze']['description']}")


def main():
    """CLI interface"""
    import sys
    
    # Default universe
    BIOTECH_UNIVERSE = [
        "PALI", "ONCY", "RCAT", "AQST", "OCUL", "VNDA", "ASND",
        "ZURA", "LXRX", "NVAX", "IBRX", "MNMD", "XENE",
        "NTLA", "CRSP", "BEAM", "EDIT", "SRPT", "RARE",
        "MRNA", "BNTX", "ALNY", "IONS", "ARWR"
    ]
    
    scanner = PrePopScorer()
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "check":
        # Check specific ticker
        if len(sys.argv) > 2:
            ticker = sys.argv[2].upper()
            result = scanner.score_stock(ticker)
            scanner._print_detailed(result)
    else:
        # Full scan
        results = scanner.scan_universe(BIOTECH_UNIVERSE)
        scanner.print_results(results)
        
        # Show timing-based recommendations
        print(f"\n{'🕐'*30}")
        print("CATALYST TIMING BREAKDOWN")
        print(f"{'🕐'*30}\n")
        
        buy_now = [r for r in results if r['catalyst'].get('days_until', 999) <= 14 and r['catalyst'].get('days_until', 999) >= 7]
        watch_close = [r for r in results if r['catalyst'].get('days_until', 999) < 7]
        
        print("🚨 BUY NOW (7-14 days to catalyst):")
        for r in buy_now[:5]:
            cat = r['catalyst']
            print(f"  • {r['ticker']} @ ${r['price']} - {cat.get('days_until')} days - Score: {r['total_score']}")
        
        print("\n⚠️ WATCH CLOSE (< 7 days - risky):")
        for r in watch_close[:5]:
            cat = r['catalyst']
            print(f"  • {r['ticker']} @ ${r['price']} - {cat.get('days_until')} days - Score: {r['total_score']}")


if __name__ == "__main__":
    main()
