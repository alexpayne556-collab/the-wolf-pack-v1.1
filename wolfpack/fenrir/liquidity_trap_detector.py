# 🐺 FENRIR QUANTUM LEAP - LIQUIDITY TRAP DETECTOR
# "This will be impossible to exit"

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf

class LiquidityTrapDetector:
    """
    Warn BEFORE you get stuck in illiquid stock
    
    You can get in, but can you get out?
    
    Checks:
    - Spread (bid-ask): Wide spreads = you lose 2-5% on entry/exit
    - Average daily volume: <100k shares = you might move the price
    - Float: Tiny float = extreme volatility both ways
    - Market cap: <$10M = possible P&D or manipulation
    - Time of day: AH trading on low volume = trap
    - Your position size vs daily volume: Are you 10% of volume?
    """
    
    def __init__(self):
        pass
    
    def check_liquidity(self, ticker: str, your_position_size: int = 0) -> Dict:
        """
        Analyze liquidity and warn about traps
        
        Args:
            ticker: Stock to check
            your_position_size: Number of shares you plan to buy
        
        Returns:
            {
                'liquidity_score': 0-100,
                'warnings': List[str],
                'risk_level': 'green'|'yellow'|'red',
                'exit_difficulty': 'easy'|'moderate'|'hard'|'trapped',
                'recommendations': List[str]
            }
        """
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='5d')
            
            if hist.empty:
                return {'error': 'No data available'}
            
            warnings = []
            risk_level = 'green'
            score = 100
            
            # Get key metrics
            avg_volume = hist['Volume'].mean()
            latest_volume = hist['Volume'].iloc[-1]
            price = hist['Close'].iloc[-1]
            market_cap = info.get('marketCap', 0)
            
            # Get bid-ask spread (simplified - using price volatility as proxy)
            intraday_volatility = ((hist['High'] - hist['Low']) / hist['Close']).mean()
            spread_pct = intraday_volatility * 100
            
            # Check 1: Average daily volume
            if avg_volume < 50000:
                warnings.append(f"🔴 ULTRA LOW VOLUME: {avg_volume:,.0f} shares/day avg")
                risk_level = 'red'
                score -= 40
            elif avg_volume < 200000:
                warnings.append(f"🟡 LOW VOLUME: {avg_volume:,.0f} shares/day avg")
                risk_level = self._escalate_risk(risk_level, 'yellow')
                score -= 20
            elif avg_volume < 500000:
                warnings.append(f"🟡 MODERATE VOLUME: {avg_volume:,.0f} shares/day avg")
                score -= 10
            
            # Check 2: Today's volume vs average
            if latest_volume < avg_volume * 0.5:
                warnings.append(f"⚠️  VOLUME DRYING UP: Today {latest_volume:,.0f} vs {avg_volume:,.0f} avg")
                risk_level = self._escalate_risk(risk_level, 'yellow')
                score -= 15
            
            # Check 3: Market cap
            if market_cap > 0:
                if market_cap < 10_000_000:
                    warnings.append(f"🔴 MICRO CAP: ${market_cap/1_000_000:.1f}M - High manipulation risk")
                    risk_level = 'red'
                    score -= 30
                elif market_cap < 50_000_000:
                    warnings.append(f"🟡 SMALL CAP: ${market_cap/1_000_000:.1f}M - Volatile")
                    risk_level = self._escalate_risk(risk_level, 'yellow')
                    score -= 15
            
            # Check 4: Spread estimate
            if spread_pct > 5:
                warnings.append(f"🔴 WIDE SPREAD: ~{spread_pct:.1f}% intraday volatility - Exit will be painful")
                risk_level = 'red'
                score -= 25
            elif spread_pct > 3:
                warnings.append(f"🟡 MODERATE SPREAD: ~{spread_pct:.1f}% - Plan exits carefully")
                risk_level = self._escalate_risk(risk_level, 'yellow')
                score -= 10
            
            # Check 5: Your position vs daily volume
            if your_position_size > 0:
                your_pct_of_volume = (your_position_size / avg_volume) * 100
                
                if your_pct_of_volume > 10:
                    warnings.append(f"🔴 POSITION TOO LARGE: You'd be {your_pct_of_volume:.1f}% of daily volume")
                    risk_level = 'red'
                    score -= 30
                elif your_pct_of_volume > 5:
                    warnings.append(f"🟡 LARGE POSITION: You'd be {your_pct_of_volume:.1f}% of daily volume")
                    risk_level = self._escalate_risk(risk_level, 'yellow')
                    score -= 15
            
            # Check 6: Time of day risk
            hour = datetime.now().hour
            if (hour < 10 or hour >= 16) and avg_volume < 500000:
                warnings.append("🟡 OFF-HOURS + LOW VOLUME: Extra liquidity risk")
                risk_level = self._escalate_risk(risk_level, 'yellow')
                score -= 10
            
            # Check 7: Price level risk
            if price < 1.0:
                warnings.append(f"🔴 SUB-DOLLAR: ${price:.2f} - Extreme volatility risk")
                risk_level = 'red'
                score -= 20
            elif price < 2.0:
                warnings.append(f"🟡 LOW PRICE: ${price:.2f} - Higher volatility")
                risk_level = self._escalate_risk(risk_level, 'yellow')
                score -= 10
            
            # Determine exit difficulty
            exit_difficulty = self._determine_exit_difficulty(score, risk_level)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, warnings, your_position_size, avg_volume)
            
            return {
                'ticker': ticker,
                'liquidity_score': max(0, score),
                'warnings': warnings,
                'risk_level': risk_level,
                'exit_difficulty': exit_difficulty,
                'avg_daily_volume': avg_volume,
                'latest_volume': latest_volume,
                'market_cap': market_cap,
                'estimated_spread_pct': spread_pct,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _escalate_risk(self, current: str, new: str) -> str:
        """Escalate risk level"""
        levels = {'green': 0, 'yellow': 1, 'red': 2}
        if levels[new] > levels.get(current, 0):
            return new
        return current
    
    def _determine_exit_difficulty(self, score: int, risk_level: str) -> str:
        """Determine how hard it will be to exit"""
        
        if risk_level == 'red' or score < 40:
            return 'trapped'
        elif score < 60:
            return 'hard'
        elif score < 80:
            return 'moderate'
        else:
            return 'easy'
    
    def _generate_recommendations(self, risk_level: str, warnings: List[str], 
                                  position_size: int, avg_volume: float) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if risk_level == 'red':
            recommendations.append("🛑 DO NOT TRADE THIS - Liquidity trap risk too high")
            recommendations.append("If you must trade: Use LIMIT ORDERS only, never market orders")
            recommendations.append(f"Max position: {int(avg_volume * 0.02)} shares (2% of daily volume)")
            recommendations.append("Plan exit strategy BEFORE entering - where's your stop?")
        
        elif risk_level == 'yellow':
            recommendations.append("⚠️  REDUCE POSITION SIZE by 50%")
            recommendations.append("Use LIMIT ORDERS with tight spreads")
            recommendations.append("Exit during high volume hours (10am-3pm)")
            recommendations.append(f"Max position: {int(avg_volume * 0.05)} shares (5% of daily volume)")
            recommendations.append("Set price alerts to monitor - don't chase")
        
        else:
            recommendations.append("✅ Liquidity acceptable")
            recommendations.append("Still use LIMIT ORDERS for better fills")
            recommendations.append(f"Safe position: up to {int(avg_volume * 0.1)} shares (10% of volume)")
        
        return recommendations
    
    def check_exit_now(self, ticker: str, your_shares: int) -> Dict:
        """
        Check if you can exit RIGHT NOW
        
        Critical for when you need to get out fast
        """
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d', interval='1m')
            
            if hist.empty:
                return {'can_exit': False, 'reason': 'No intraday data'}
            
            # Get last hour's volume
            recent_volume = hist['Volume'].tail(60).sum()
            recent_avg_per_min = recent_volume / 60
            
            # Estimate: can you exit your shares in 5 minutes without moving price?
            shares_per_min_safe = recent_avg_per_min * 0.1  # Be 10% of volume
            minutes_to_exit = your_shares / shares_per_min_safe if shares_per_min_safe > 0 else 999
            
            can_exit = minutes_to_exit < 15
            
            return {
                'ticker': ticker,
                'can_exit_quickly': can_exit,
                'estimated_minutes_to_exit': int(minutes_to_exit),
                'recent_volume_per_min': recent_avg_per_min,
                'your_shares': your_shares,
                'recommendation': self._exit_recommendation(minutes_to_exit)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _exit_recommendation(self, minutes: float) -> str:
        """Recommend exit strategy"""
        
        if minutes < 5:
            return "✅ Can exit quickly - normal limit order strategy"
        elif minutes < 15:
            return "⚠️  Will take 5-15 min - use smaller tranches"
        elif minutes < 30:
            return "🟡 Will take 15-30 min - break into 3-5 orders over time"
        else:
            return "🔴 Cannot exit quickly - may take 30+ min and move price. Break into many small orders."
    
    def format_liquidity_check(self, result: Dict) -> str:
        """Format liquidity check for display"""
        
        if 'error' in result:
            return f"\nError: {result['error']}\n"
        
        output = f"\n{'='*60}\n"
        output += f"💧 LIQUIDITY TRAP DETECTOR: {result['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        # Score and risk
        risk_display = {
            'green': '🟢 LOW RISK',
            'yellow': '🟡 MODERATE RISK',
            'red': '🔴 HIGH RISK'
        }
        
        output += f"LIQUIDITY SCORE: {result['liquidity_score']}/100\n"
        output += f"RISK LEVEL: {risk_display[result['risk_level']]}\n"
        output += f"EXIT DIFFICULTY: {result['exit_difficulty'].upper()}\n\n"
        
        # Key metrics
        output += "METRICS:\n"
        output += f"  Avg Daily Volume: {result['avg_daily_volume']:,.0f} shares\n"
        output += f"  Today's Volume: {result['latest_volume']:,.0f} shares\n"
        if result['market_cap'] > 0:
            output += f"  Market Cap: ${result['market_cap']/1_000_000:.1f}M\n"
        output += f"  Est. Spread: {result['estimated_spread_pct']:.1f}%\n\n"
        
        # Warnings
        if result['warnings']:
            output += "WARNINGS:\n"
            for warning in result['warnings']:
                output += f"  {warning}\n"
            output += "\n"
        
        # Recommendations
        output += "RECOMMENDATIONS:\n"
        for rec in result['recommendations']:
            output += f"  {rec}\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    detector = LiquidityTrapDetector()
    
    # Check IBRX liquidity
    result = detector.check_liquidity('IBRX', your_position_size=37)
    print(detector.format_liquidity_check(result))
    
    # Can we exit now?
    exit_check = detector.check_exit_now('IBRX', your_shares=37)
    if 'error' not in exit_check:
        print(f"\nEXIT CHECK:")
        print(f"  Can exit quickly: {exit_check['can_exit_quickly']}")
        print(f"  Estimated time: {exit_check['estimated_minutes_to_exit']} minutes")
        print(f"  {exit_check['recommendation']}")
