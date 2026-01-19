# 🐺 FENRIR V2 - KEY LEVELS TRACKER
# Track support/resistance and alert on approaches

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import database
import config

class KeyLevelsTracker:
    """Track and alert on key price levels"""
    
    def __init__(self):
        self.levels = {}  # ticker -> {'support': [], 'resistance': []}
    
    def calculate_levels(self, ticker: str, days_back: int = 30) -> Dict:
        """Auto-calculate support/resistance from recent price action"""
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f'{days_back}d')
            
            if hist.empty:
                return {'support': [], 'resistance': []}
            
            # Get highs and lows
            high = hist['High'].max()
            low = hist['Low'].min()
            current = hist['Close'].iloc[-1]
            
            # Recent resistance = recent highs
            recent_highs = hist['High'].nlargest(5).tolist()
            resistance = [float(h) for h in recent_highs if h > current]
            
            # Recent support = recent lows
            recent_lows = hist['Low'].nsmallest(5).tolist()
            support = [float(l) for l in recent_lows if l < current]
            
            # Deduplicate (within 2% of each other)
            resistance = self._dedupe_levels(resistance, pct=2.0)
            support = self._dedupe_levels(support, pct=2.0)
            
            # Sort
            resistance.sort()
            support.sort(reverse=True)
            
            return {
                'support': support[:3],     # Top 3 support levels
                'resistance': resistance[:3],  # Top 3 resistance levels
                'current': float(current),
                'high_52w': float(high),
                'low_52w': float(low),
            }
            
        except Exception as e:
            print(f"Error calculating levels for {ticker}: {e}")
            return {'support': [], 'resistance': []}
    
    def _dedupe_levels(self, levels: List[float], pct: float = 2.0) -> List[float]:
        """Remove levels within pct% of each other"""
        
        if not levels:
            return []
        
        deduped = [levels[0]]
        
        for level in levels[1:]:
            # Check if too close to existing
            too_close = False
            for existing in deduped:
                if abs((level - existing) / existing) * 100 < pct:
                    too_close = True
                    break
            
            if not too_close:
                deduped.append(level)
        
        return deduped
    
    def check_near_level(self, ticker: str, current_price: float, 
                        threshold_pct: float = 1.0) -> Optional[Dict]:
        """Check if price is near a key level"""
        
        if ticker not in self.levels:
            self.levels[ticker] = self.calculate_levels(ticker)
        
        levels = self.levels[ticker]
        
        # Check resistance
        for r in levels.get('resistance', []):
            distance = ((r - current_price) / current_price) * 100
            if 0 < distance <= threshold_pct:
                return {
                    'ticker': ticker,
                    'type': 'RESISTANCE',
                    'level': r,
                    'current': current_price,
                    'distance_pct': distance,
                    'action': 'APPROACHING RESISTANCE',
                }
            elif abs(distance) < 0.5:  # Within 0.5%
                return {
                    'ticker': ticker,
                    'type': 'RESISTANCE',
                    'level': r,
                    'current': current_price,
                    'distance_pct': distance,
                    'action': 'AT RESISTANCE',
                }
        
        # Check support
        for s in levels.get('support', []):
            distance = ((current_price - s) / current_price) * 100
            if 0 < distance <= threshold_pct:
                return {
                    'ticker': ticker,
                    'type': 'SUPPORT',
                    'level': s,
                    'current': current_price,
                    'distance_pct': distance,
                    'action': 'APPROACHING SUPPORT',
                }
            elif abs(distance) < 0.5:
                return {
                    'ticker': ticker,
                    'type': 'SUPPORT',
                    'level': s,
                    'current': current_price,
                    'distance_pct': distance,
                    'action': 'AT SUPPORT',
                }
        
        return None
    
    def format_levels_report(self, ticker: str) -> str:
        """Format key levels for display"""
        
        levels = self.calculate_levels(ticker)
        
        output = "\n" + "=" * 60 + "\n"
        output += f"🐺 KEY LEVELS - {ticker}\n"
        output += "=" * 60 + "\n\n"
        
        output += f"Current: ${levels['current']:.2f}\n\n"
        
        # Resistance
        if levels['resistance']:
            output += "🔴 RESISTANCE:\n"
            for r in levels['resistance']:
                distance = ((r - levels['current']) / levels['current']) * 100
                output += f"  ${r:.2f} (+{distance:.1f}%)\n"
            output += "\n"
        
        # Support
        if levels['support']:
            output += "🟢 SUPPORT:\n"
            for s in levels['support']:
                distance = ((levels['current'] - s) / levels['current']) * 100
                output += f"  ${s:.2f} (-{distance:.1f}%)\n"
            output += "\n"
        
        # 52-week range
        output += "📊 52-WEEK RANGE:\n"
        output += f"  High: ${levels.get('high_52w', 0):.2f}\n"
        output += f"  Low: ${levels.get('low_52w', 0):.2f}\n"
        
        output += "\n" + "=" * 60 + "\n"
        
        return output
    
    def scan_all_positions(self) -> str:
        """Scan all positions for level approaches"""
        
        output = "\n🐺 CHECKING KEY LEVELS ON POSITIONS\n\n"
        
        alerts = []
        
        for ticker in config.HOLDINGS.keys():
            try:
                stock = yf.Ticker(ticker)
                current = stock.info.get('regularMarketPrice') or stock.info.get('currentPrice')
                
                if current:
                    alert = self.check_near_level(ticker, current)
                    if alert:
                        alerts.append(alert)
            except:
                pass
        
        if alerts:
            for alert in alerts:
                emoji = "🔴" if alert['type'] == 'RESISTANCE' else "🟢"
                output += f"{emoji} {alert['ticker']}: {alert['action']}\n"
                output += f"   Current: ${alert['current']:.2f}\n"
                output += f"   Level: ${alert['level']:.2f} ({alert['distance_pct']:.1f}% away)\n\n"
        else:
            output += "✅ No positions near key levels\n"
        
        return output


def quick_levels_check(ticker: str) -> str:
    """Quick levels check on one ticker"""
    
    tracker = KeyLevelsTracker()
    return tracker.format_levels_report(ticker)


# Test
if __name__ == '__main__':
    print("\n🐺 Testing Key Levels Tracker\n")
    
    tracker = KeyLevelsTracker()
    
    # Test on IBRX (should have levels from recent run)
    print("Calculating levels for IBRX...")
    print(tracker.format_levels_report('IBRX'))
    
    # Scan all positions
    print(tracker.scan_all_positions())
