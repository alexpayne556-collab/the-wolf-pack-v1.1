# 🐺 FENRIR V2 - MOMENTUM SHIFT DETECTOR
# Detect when character changes in real-time

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf

class MomentumShiftDetector:
    """Detect real-time character changes in price action"""
    
    def detect_shifts(self, ticker: str) -> Dict:
        """
        Detect momentum shifts in real-time
        
        Shifts to detect:
        - Volume surge/fade
        - Price acceleration/deceleration
        - Bid/ask pressure changes
        - Character break (from grind to explosive or vice versa)
        """
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get intraday data (1 minute bars)
            intraday = stock.history(period='1d', interval='1m')
            
            if intraday.empty:
                return {'error': 'No intraday data'}
            
            # Recent data (last 30 mins)
            recent = intraday.iloc[-30:]
            
            # Earlier data (30-60 mins ago)
            earlier = intraday.iloc[-60:-30] if len(intraday) >= 60 else intraday.iloc[:30]
            
            shifts = []
            
            # 1. Volume shift
            recent_vol = recent['Volume'].mean()
            earlier_vol = earlier['Volume'].mean()
            
            if recent_vol > earlier_vol * 1.5:
                shifts.append({
                    'type': 'VOLUME_SURGE',
                    'severity': 'HIGH',
                    'message': f"Volume surging: {recent_vol/earlier_vol:.1f}x last 30min",
                    'bullish': True
                })
            elif recent_vol < earlier_vol * 0.6:
                shifts.append({
                    'type': 'VOLUME_FADE',
                    'severity': 'HIGH',
                    'message': f"Volume fading: {recent_vol/earlier_vol:.0%} of earlier",
                    'bullish': False
                })
            
            # 2. Price acceleration
            recent_volatility = recent['Close'].std()
            earlier_volatility = earlier['Close'].std()
            
            if recent_volatility > earlier_volatility * 1.5:
                shifts.append({
                    'type': 'ACCELERATION',
                    'severity': 'MEDIUM',
                    'message': "Price action accelerating (bigger moves)",
                    'bullish': None  # Can go either way
                })
            elif recent_volatility < earlier_volatility * 0.6:
                shifts.append({
                    'type': 'DECELERATION',
                    'severity': 'MEDIUM',
                    'message': "Tightening up (smaller moves)",
                    'bullish': False
                })
            
            # 3. Trend change
            recent_trend = recent['Close'].iloc[-1] - recent['Close'].iloc[0]
            earlier_trend = earlier['Close'].iloc[-1] - earlier['Close'].iloc[0]
            
            if recent_trend > 0 and earlier_trend < 0:
                shifts.append({
                    'type': 'REVERSAL_UP',
                    'severity': 'HIGH',
                    'message': "Reversed higher (was fading, now pumping)",
                    'bullish': True
                })
            elif recent_trend < 0 and earlier_trend > 0:
                shifts.append({
                    'type': 'REVERSAL_DOWN',
                    'severity': 'HIGH',
                    'message': "Reversed lower (was pumping, now fading)",
                    'bullish': False
                })
            
            # 4. Character break detection
            # Grind vs explosive
            recent_max_move = max(abs((recent['High'] - recent['Low']) / recent['Close']).max() * 100, 0.1)
            earlier_max_move = max(abs((earlier['High'] - earlier['Low']) / earlier['Close']).max() * 100, 0.1)
            
            if recent_max_move > earlier_max_move * 2:
                shifts.append({
                    'type': 'GOING_EXPLOSIVE',
                    'severity': 'CRITICAL',
                    'message': f"Breaking character: grind → explosive ({recent_max_move:.1f}% bars)",
                    'bullish': True
                })
            elif recent_max_move < earlier_max_move * 0.5:
                shifts.append({
                    'type': 'GOING_QUIET',
                    'severity': 'CRITICAL',
                    'message': "Breaking character: explosive → quiet (losing steam)",
                    'bullish': False
                })
            
            # 5. Higher highs / lower lows pattern
            recent_high = recent['High'].max()
            earlier_high = earlier['High'].max()
            recent_low = recent['Low'].min()
            earlier_low = earlier['Low'].min()
            
            if recent_high > earlier_high and recent_low > earlier_low:
                shifts.append({
                    'type': 'HIGHER_HIGHS_LOWS',
                    'severity': 'MEDIUM',
                    'message': "Strong uptrend: higher highs AND higher lows",
                    'bullish': True
                })
            elif recent_high < earlier_high and recent_low < earlier_low:
                shifts.append({
                    'type': 'LOWER_HIGHS_LOWS',
                    'severity': 'HIGH',
                    'message': "⚠️  Downtrend forming: lower highs AND lower lows",
                    'bullish': False
                })
            
            return {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'current_price': float(recent['Close'].iloc[-1]),
                'shifts_detected': len(shifts),
                'shifts': shifts,
                'overall_momentum': self._assess_overall_momentum(shifts)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _assess_overall_momentum(self, shifts: List[Dict]) -> str:
        """Assess overall momentum from shifts"""
        
        if not shifts:
            return "NEUTRAL - No significant shifts"
        
        bullish_count = sum(1 for s in shifts if s.get('bullish') == True)
        bearish_count = sum(1 for s in shifts if s.get('bullish') == False)
        critical_count = sum(1 for s in shifts if s.get('severity') == 'CRITICAL')
        
        if critical_count > 0:
            if bullish_count > bearish_count:
                return "🚀 CRITICAL BULLISH - Character breaking to upside"
            else:
                return "🛑 CRITICAL BEARISH - Losing momentum"
        
        if bullish_count > bearish_count + 1:
            return "📈 BULLISH - Momentum building"
        elif bearish_count > bullish_count + 1:
            return "📉 BEARISH - Momentum fading"
        else:
            return "⚖️  NEUTRAL - Mixed signals"
    
    def format_shift_report(self, data: Dict) -> str:
        """Format momentum shift report"""
        
        if 'error' in data:
            return f"❌ Error: {data['error']}"
        
        output = f"\n{'='*60}\n"
        output += f"🐺 MOMENTUM SHIFT DETECTOR: {data['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        output += f"Current Price: ${data['current_price']:.2f}\n"
        output += f"Overall Momentum: {data['overall_momentum']}\n\n"
        
        if data['shifts']:
            output += f"DETECTED SHIFTS ({data['shifts_detected']}):\n\n"
            
            for shift in data['shifts']:
                severity_emoji = {
                    'CRITICAL': '🚨',
                    'HIGH': '⚠️',
                    'MEDIUM': '📊',
                    'LOW': 'ℹ️'
                }.get(shift['severity'], '•')
                
                output += f"{severity_emoji} {shift['type']}\n"
                output += f"   {shift['message']}\n\n"
        else:
            output += "No significant momentum shifts detected\n"
        
        output += f"{'='*60}\n"
        
        return output


class SectorRotationDetector:
    """Detect money flow between sectors"""
    
    def detect_rotation(self) -> Dict:
        """Detect which sectors are getting money flow"""
        
        import config
        
        sector_performance = {}
        
        try:
            for sector, tickers in config.WATCHLIST.items():
                # Sample 3 tickers from each sector
                sample_tickers = tickers[:3]
                
                total_change = 0
                total_volume_ratio = 0
                count = 0
                
                for ticker in sample_tickers:
                    try:
                        stock = yf.Ticker(ticker)
                        hist = stock.history(period='2d')
                        
                        if len(hist) >= 2:
                            change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                            
                            # Volume ratio
                            vol_ratio = hist['Volume'].iloc[-1] / hist['Volume'].iloc[-2] if hist['Volume'].iloc[-2] > 0 else 1
                            
                            total_change += change
                            total_volume_ratio += vol_ratio
                            count += 1
                    except:
                        pass
                
                if count > 0:
                    sector_performance[sector] = {
                        'avg_change': total_change / count,
                        'avg_volume_ratio': total_volume_ratio / count,
                        'strength': (total_change / count) * (total_volume_ratio / count)
                    }
            
            # Sort by strength
            sorted_sectors = sorted(sector_performance.items(), key=lambda x: x[1]['strength'], reverse=True)
            
            # Identify rotation
            rotation_signals = []
            
            if sorted_sectors:
                strongest = sorted_sectors[0]
                weakest = sorted_sectors[-1]
                
                if strongest[1]['strength'] > 2:
                    rotation_signals.append(f"💰 MONEY FLOWING INTO: {strongest[0]} (strength: {strongest[1]['strength']:.1f})")
                
                if weakest[1]['strength'] < -1:
                    rotation_signals.append(f"🔻 MONEY LEAVING: {weakest[0]} (strength: {weakest[1]['strength']:.1f})")
            
            return {
                'sectors': sector_performance,
                'rotation_signals': rotation_signals,
                'sorted_sectors': sorted_sectors
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def format_rotation_report(self, data: Dict) -> str:
        """Format sector rotation report"""
        
        if 'error' in data:
            return f"❌ Error: {data['error']}"
        
        output = f"\n{'='*60}\n"
        output += f"🐺 SECTOR ROTATION DETECTOR\n"
        output += f"{'='*60}\n\n"
        
        if data['rotation_signals']:
            output += "ROTATION SIGNALS:\n"
            for signal in data['rotation_signals']:
                output += f"  {signal}\n"
            output += "\n"
        
        output += "SECTOR RANKINGS (by strength):\n\n"
        
        for i, (sector, perf) in enumerate(data['sorted_sectors'], 1):
            emoji = "🟢" if perf['strength'] > 0 else "🔴"
            output += f"{i}. {emoji} {sector.upper()}\n"
            output += f"     Change: {perf['avg_change']:+.2f}% | Volume: {perf['avg_volume_ratio']:.2f}x | Strength: {perf['strength']:.2f}\n\n"
        
        output += f"{'='*60}\n"
        
        return output


if __name__ == '__main__':
    # Test momentum detector
    detector = MomentumShiftDetector()
    shifts = detector.detect_shifts('IBRX')
    print(detector.format_shift_report(shifts))
    
    # Test sector rotation
    rotation = SectorRotationDetector()
    data = rotation.detect_rotation()
    print(rotation.format_rotation_report(data))
