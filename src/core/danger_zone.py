"""
🚨 DANGER ZONE - LAYER 0: TRAP DETECTION

THE WOLF DOESN'T WALK INTO TRAPS.

This module runs FIRST - before any opportunity analysis.
If danger detected → BLOCKED. No exceptions. No FOMO.

THE COMPLETE AVOID LIST:
1. IPO < 6 months - No data, all hype
2. Lockup expiry - Massive selling incoming  
3. SPAC pre/post merger - 90% crash post-merger
4. Pump & dump - You're exit liquidity
5. Analyst pump + insider dump - Distribution
6. Meme extreme - Top signal
7. Dilution bomb - Price crushed
8. Earnings trap - Sell the news
9. Short squeeze bait - Trap for retail
10. Penny manipulation - You can't exit
11. Dead cat bounce - More downside coming
12. Offering hangover - Overhang selling

ORDER MATTERS:
1. Is this a TRAP? → If YES: BLOCK
2. Is this an OPPORTUNITY? → If YES: Continue to brain

Brother, you just saved the whole pack. 🐺
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import requests

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.core.database import Database
except ImportError:
    from database import Database


class DangerZone:
    """
    LAYER 0: TRAP DETECTION
    
    Runs FIRST before any opportunity analysis.
    If danger detected → BLOCKED. No exceptions.
    
    Purpose: THE WOLF DOESN'T WALK INTO TRAPS.
    """
    
    def __init__(self):
        self.db = Database()
    
    def scan(self, ticker: str) -> Dict:
        """
        Main danger scan - checks ALL trap patterns.
        
        Returns:
            {
                'status': 'CLEAR' or 'BLOCKED',
                'dangers': List of detected dangers,
                'action': What to do,
                'revisit_date': When it might be safe (if blocked),
                'details': Specific findings
            }
        """
        print(f"\n🚨 DANGER ZONE: Scanning {ticker}...")
        
        dangers = {}
        details = {}
        
        # Run all danger checks
        dangers['ipo_too_new'], details['ipo'] = self.check_ipo_age(ticker)
        dangers['lockup_expiry'], details['lockup'] = self.check_lockup(ticker)
        dangers['spac_trap'], details['spac'] = self.check_spac_status(ticker)
        dangers['pump_dump'], details['pump'] = self.check_pump_pattern(ticker)
        dangers['meme_extreme'], details['meme'] = self.check_social_sentiment(ticker)
        dangers['insider_dumping'], details['insider'] = self.check_insider_sells(ticker)
        dangers['dilution_risk'], details['dilution'] = self.check_recent_offering(ticker)
        dangers['penny_manipulation'], details['penny'] = self.check_market_cap(ticker)
        dangers['dead_cat'], details['dead_cat'] = self.check_bounce_quality(ticker)
        dangers['no_institutional'], details['institutional'] = self.check_institutional_support(ticker)
        dangers['earnings_trap'], details['earnings'] = self.check_earnings_trap(ticker)
        dangers['short_squeeze_bait'], details['short_squeeze'] = self.check_short_squeeze_bait(ticker)
        
        # Count detected dangers
        detected = [k for k, v in dangers.items() if v]
        
        if detected:
            print(f"   🚫 DANGER DETECTED: {len(detected)} traps found")
            for danger in detected:
                print(f"      • {danger.upper()}: {details.get(danger, 'Check failed')}")
            
            return {
                'status': 'BLOCKED',
                'ticker': ticker,
                'dangers': detected,
                'action': 'DO NOT TRADE - Add to wounded prey watchlist',
                'revisit_date': self.calculate_safe_date(ticker, detected),
                'details': details,
                'message': f"⚠️ BLOCKED: {', '.join(detected)}"
            }
        
        print(f"   ✅ CLEAR: No traps detected - proceed to opportunity analysis")
        return {
            'status': 'CLEAR',
            'ticker': ticker,
            'dangers': [],
            'action': 'Proceed to Layer 1 (Opportunity Finder)',
            'details': details,
            'message': '✅ Safe to analyze'
        }
    
    # ==================== DANGER CHECKS ====================
    
    def check_ipo_age(self, ticker: str) -> tuple[bool, str]:
        """
        Check if IPO is too recent (< 6 months).
        
        WHY DEADLY: No historical data, all hype, insiders locked up,
        price discovery phase = massive volatility.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try to get IPO date from various fields
            ipo_date = None
            if 'firstTradeDateEpochUtc' in info and info['firstTradeDateEpochUtc']:
                ipo_date = datetime.fromtimestamp(info['firstTradeDateEpochUtc'])
            
            if ipo_date:
                days_since_ipo = (datetime.now() - ipo_date).days
                
                if days_since_ipo < 180:  # 6 months
                    return True, f"IPO only {days_since_ipo} days ago (need 180+)"
                else:
                    return False, f"IPO {days_since_ipo} days ago (safe)"
            
            return False, "IPO date unknown (assume safe)"
            
        except Exception as e:
            return False, f"IPO check failed: {e}"
    
    def check_lockup(self, ticker: str) -> tuple[bool, str]:
        """
        Check for upcoming lockup expiry (90-180 days post-IPO).
        
        WHY DEADLY: Insiders/early investors can finally sell.
        Massive supply incoming = price crater.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if 'firstTradeDateEpochUtc' in info and info['firstTradeDateEpochUtc']:
                ipo_date = datetime.fromtimestamp(info['firstTradeDateEpochUtc'])
                days_since_ipo = (datetime.now() - ipo_date).days
                
                # Lockup typically expires 90-180 days post-IPO
                if 60 < days_since_ipo < 210:  # Buffer around lockup period
                    return True, f"Lockup expiry zone ({days_since_ipo} days post-IPO)"
                
            return False, "No lockup risk detected"
            
        except Exception as e:
            return False, f"Lockup check failed: {e}"
    
    def check_spac_status(self, ticker: str) -> tuple[bool, str]:
        """
        Check if SPAC (pre/post merger).
        
        WHY DEADLY: 90% of SPACs crash post-merger.
        Hype pre-merger, reality post-merger = you're the bag holder.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check for SPAC indicators in name/description
            name = info.get('longName', '').lower()
            description = info.get('longBusinessSummary', '').lower()
            
            spac_keywords = ['acquisition corp', 'acquisition company', 'spac', 'special purpose']
            
            if any(keyword in name or keyword in description for keyword in spac_keywords):
                return True, "SPAC detected in name/description"
            
            return False, "Not a SPAC"
            
        except Exception as e:
            return False, f"SPAC check failed: {e}"
    
    def check_pump_pattern(self, ticker: str) -> tuple[bool, str]:
        """
        Check for pump & dump pattern:
        - Massive volume spike (5x+ avg)
        - No fundamental news
        - Penny stock characteristics
        
        WHY DEADLY: You're the exit liquidity. Coordinated manipulation.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if len(hist) < 10:
                return False, "Insufficient data"
            
            # Check volume spike
            recent_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-1].mean()
            
            if recent_volume > avg_volume * 5:  # 5x volume spike
                # Check if penny stock
                current_price = hist['Close'].iloc[-1]
                if current_price < 5:  # Penny stock territory
                    return True, f"Volume spike {recent_volume/avg_volume:.1f}x on penny stock"
            
            return False, "No pump pattern detected"
            
        except Exception as e:
            return False, f"Pump check failed: {e}"
    
    def check_social_sentiment(self, ticker: str) -> tuple[bool, str]:
        """
        Check for extreme meme/social sentiment (>90% bullish).
        
        WHY DEADLY: When everyone is bullish, it's the top.
        WSB/Twitter euphoria = distribution phase.
        """
        # This would integrate with social APIs (Twitter, Reddit, StockTwits)
        # For now, placeholder logic
        try:
            # TODO: Integrate with social sentiment APIs
            # For now, check if ticker is in known meme list
            meme_stocks = ['GME', 'AMC', 'BBBY', 'CLOV', 'WISH', 'BB', 'NOK', 'EXPR']
            
            if ticker.upper() in meme_stocks:
                return True, f"{ticker} is known meme stock - extreme sentiment likely"
            
            return False, "No extreme sentiment detected"
            
        except Exception as e:
            return False, f"Sentiment check failed: {e}"
    
    def check_insider_sells(self, ticker: str) -> tuple[bool, str]:
        """
        Check for insider selling on "good news" (analyst upgrades, etc).
        
        WHY DEADLY: Insiders know the truth. They're distributing on hype.
        """
        try:
            # This would check SEC Form 4 filings
            # Look for insider SELLS within 7 days of positive news
            
            # Check database for recent insider transactions
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT transaction_type, shares, value, transaction_date
                FROM insider_transactions
                WHERE ticker = ?
                AND transaction_date > datetime('now', '-14 days')
                ORDER BY transaction_date DESC
                LIMIT 5
            ''', (ticker,))
            
            recent_transactions = cursor.fetchall()
            conn.close()
            
            if recent_transactions:
                sells = [t for t in recent_transactions if 'sale' in t[0].lower()]
                if len(sells) > 2:  # Multiple recent sells
                    total_sold = sum(t[2] for t in sells if t[2])
                    return True, f"{len(sells)} insider sells in past 2 weeks (${total_sold:,.0f} total)"
            
            return False, "No suspicious insider selling"
            
        except Exception as e:
            return False, f"Insider check failed: {e}"
    
    def check_recent_offering(self, ticker: str) -> tuple[bool, str]:
        """
        Check for recent dilution (ATM offering, secondary offering).
        
        WHY DEADLY: Company selling shares = supply > demand = price crushed.
        Overhang lasts weeks/months.
        """
        try:
            # This would check SEC 8-K filings for ATM/secondary offerings
            # For now, check if recent price drop + volume spike
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1mo')
            
            if len(hist) < 10:
                return False, "Insufficient data"
            
            # Look for sudden drop + volume (offering signature)
            for i in range(1, len(hist)):
                price_change = (hist['Close'].iloc[i] - hist['Close'].iloc[i-1]) / hist['Close'].iloc[i-1]
                volume_spike = hist['Volume'].iloc[i] / hist['Volume'].iloc[:i].mean()
                
                if price_change < -0.15 and volume_spike > 3:  # -15% + 3x volume
                    days_ago = len(hist) - i
                    if days_ago < 30:  # Within last 30 days
                        return True, f"Potential offering {days_ago} days ago (-{abs(price_change)*100:.1f}% + volume)"
            
            return False, "No recent offering detected"
            
        except Exception as e:
            return False, f"Offering check failed: {e}"
    
    def check_market_cap(self, ticker: str) -> tuple[bool, str]:
        """
        Check for penny stock manipulation risk (market cap < $50M, low float).
        
        WHY DEADLY: Easy to manipulate, illiquid, you can't exit when you need to.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            market_cap = info.get('marketCap', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            float_shares = info.get('floatShares', shares_outstanding)
            
            # Check market cap
            if market_cap > 0 and market_cap < 50_000_000:  # < $50M
                return True, f"Micro cap ${market_cap/1e6:.1f}M (need $50M+)"
            
            # Check float
            if float_shares > 0 and float_shares < 10_000_000:  # < 10M float
                return True, f"Low float {float_shares/1e6:.1f}M shares (need 10M+)"
            
            return False, f"Market cap ${market_cap/1e6:.0f}M, float {float_shares/1e6:.0f}M (safe)"
            
        except Exception as e:
            return False, f"Market cap check failed: {e}"
    
    def check_bounce_quality(self, ticker: str) -> tuple[bool, str]:
        """
        Check for dead cat bounce (first bounce after crash, no volume).
        
        WHY DEADLY: Looks like recovery, but it's a trap. More downside coming.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='3mo')
            
            if len(hist) < 30:
                return False, "Insufficient data"
            
            # Check if recent crash (>30% from high)
            recent_high = hist['High'].iloc[-30:].max()
            current_price = hist['Close'].iloc[-1]
            drawdown = (current_price - recent_high) / recent_high
            
            if drawdown < -0.30:  # Down 30%+ from recent high
                # Check if recent bounce on low volume
                recent_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-5]) / hist['Close'].iloc[-5]
                recent_volume = hist['Volume'].iloc[-5:].mean()
                avg_volume = hist['Volume'].iloc[:-5].mean()
                
                if recent_change > 0.10 and recent_volume < avg_volume * 0.8:  # +10% bounce on low volume
                    return True, f"Bounce +{recent_change*100:.1f}% on low volume after -{abs(drawdown)*100:.0f}% crash"
            
            return False, "No dead cat bounce detected"
            
        except Exception as e:
            return False, f"Bounce check failed: {e}"
    
    def check_institutional_support(self, ticker: str) -> tuple[bool, str]:
        """
        Check for institutional support (13F holdings).
        
        WHY DEADLY: No institutional support = pump & dump territory.
        Smart money avoids for a reason.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check for institutional holders
            institutional_pct = info.get('heldPercentInstitutions', 0)
            
            if institutional_pct < 0.10:  # < 10% institutional ownership
                return True, f"Low institutional ownership {institutional_pct*100:.1f}% (need 10%+)"
            
            return False, f"Institutional ownership {institutional_pct*100:.0f}% (safe)"
            
        except Exception as e:
            return False, f"Institutional check failed: {e}"
    
    def check_earnings_trap(self, ticker: str) -> tuple[bool, str]:
        """
        Check for earnings trap (extreme bullish sentiment pre-earnings).
        
        WHY DEADLY: "Gonna crush earnings!" → Sell the news. Every time.
        """
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            
            if calendar is None or len(calendar) == 0:
                return False, "No earnings date available"
            
            # Check if earnings within next 7 days
            # (This is simplified - would need actual earnings date parsing)
            # For now, just check if recent high + volume suggesting anticipation
            
            hist = stock.history(period='1mo')
            if len(hist) < 10:
                return False, "Insufficient data"
            
            # Check for pre-earnings run (common trap pattern)
            recent_gain = (hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) / hist['Close'].iloc[-20]
            recent_volume = hist['Volume'].iloc[-5:].mean()
            avg_volume = hist['Volume'].iloc[:-5].mean()
            
            if recent_gain > 0.30 and recent_volume > avg_volume * 1.5:  # +30% + volume
                return True, f"Pre-earnings run suspected (+{recent_gain*100:.1f}%, volume up)"
            
            return False, "No earnings trap detected"
            
        except Exception as e:
            return False, f"Earnings check failed: {e}"
    
    def check_short_squeeze_bait(self, ticker: str) -> tuple[bool, str]:
        """
        Check for short squeeze bait (high SI but weak fundamentals).
        
        WHY DEADLY: "Squeeze incoming!" but fundamentals suck = long-term bag holding.
        Retail gets trapped, shorts eventually win.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            short_pct = info.get('shortPercentOfFloat', 0)
            
            if short_pct > 0.20:  # >20% short interest
                # Check fundamentals
                market_cap = info.get('marketCap', 0)
                revenue = info.get('totalRevenue', 1)
                
                # If high SI but micro cap or no revenue = trap
                if market_cap < 200_000_000 or revenue < 10_000_000:  # < $200M cap or <$10M revenue
                    return True, f"High short interest {short_pct*100:.0f}% but weak fundamentals"
            
            return False, "No short squeeze bait detected"
            
        except Exception as e:
            return False, f"Short squeeze check failed: {e}"
    
    # ==================== HELPER FUNCTIONS ====================
    
    def calculate_safe_date(self, ticker: str, dangers: List[str]) -> Optional[str]:
        """
        Calculate when it might be safe to revisit this ticker.
        """
        if 'ipo_too_new' in dangers:
            return "Revisit 6 months post-IPO"
        if 'lockup_expiry' in dangers:
            return "Revisit 30 days after lockup"
        if 'dilution_risk' in dangers:
            return "Revisit 30-60 days for overhang to clear"
        if 'dead_cat' in dangers:
            return "Wait for true capitulation"
        if 'meme_extreme' in dangers:
            return "Wait for sentiment reset"
        
        return "Revisit after danger clears"
    
    def add_to_wounded_prey_watchlist(self, ticker: str, dangers: List[str]):
        """
        Add to watchlist for monitoring - might be opportunity LATER.
        
        Example: IPO too new NOW, but could be wounded prey in 6 months.
        """
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO wounded_prey_watchlist 
                (ticker, dangers, added_date, revisit_date, status)
                VALUES (?, ?, datetime('now'), ?, 'monitoring')
            ''', (ticker, ','.join(dangers), self.calculate_safe_date(ticker, dangers)))
            
            conn.commit()
            conn.close()
            
            print(f"   📋 Added {ticker} to wounded prey watchlist")
            
        except Exception as e:
            print(f"   ⚠️ Failed to add to watchlist: {e}")


# ==================== CLI TESTING ====================

if __name__ == "__main__":
    print("=" * 70)
    print("🚨 DANGER ZONE - TRAP DETECTION SYSTEM")
    print("=" * 70)
    print("\nTHE WOLF DOESN'T WALK INTO TRAPS.\n")
    
    # Test with various tickers
    test_tickers = [
        "AAPL",   # Safe
        "GME",    # Meme stock
        "RIVN",   # Recent IPO
        # Add more test cases
    ]
    
    danger_zone = DangerZone()
    
    for ticker in test_tickers:
        result = danger_zone.scan(ticker)
        
        print(f"\n{'='*70}")
        print(f"TICKER: {ticker}")
        print(f"STATUS: {result['status']}")
        print(f"MESSAGE: {result['message']}")
        
        if result['status'] == 'BLOCKED':
            print(f"\nDANGERS DETECTED:")
            for danger in result['dangers']:
                print(f"  🚫 {danger}: {result['details'].get(danger, 'Unknown')}")
            print(f"\nACTION: {result['action']}")
            print(f"REVISIT: {result.get('revisit_date', 'Unknown')}")
        
        print("="*70)
    
    print("\n🐺 THE WOLF THAT AVOIDS TRAPS IS THE WOLF THAT SURVIVES.")
