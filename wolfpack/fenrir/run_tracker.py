# 🐺 FENRIR V2 - MULTI-DAY RUN TRACKER
# Track ENTIRE runs, not just today

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
try:
    from fenrir import database
except ImportError:
    import database

class RunTracker:
    """Track multi-day runs and their characteristics"""
    
    def track_run(self, ticker: str) -> Dict:
        """
        Track the full run for a ticker
        
        Returns complete run context
        """
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='30d')
            
            if hist.empty:
                return {'error': 'No data'}
            
            # Find run start (first big move)
            run_start_idx = self._find_run_start(hist)
            run_start_date = hist.index[run_start_idx]
            run_start_price = hist['Close'].iloc[run_start_idx]
            
            current_price = hist['Close'].iloc[-1]
            
            # Count green vs red days
            green_days = 0
            red_days = 0
            for i in range(run_start_idx + 1, len(hist)):
                if hist['Close'].iloc[i] > hist['Close'].iloc[i-1]:
                    green_days += 1
                else:
                    red_days += 1
            
            # Find support levels (recent lows that held)
            support_levels = self._find_support_levels(hist, run_start_idx)
            
            # Volume trend
            recent_vol = hist['Volume'].iloc[-5:].mean()
            early_vol = hist['Volume'].iloc[run_start_idx:run_start_idx+5].mean()
            volume_fading = recent_vol < (early_vol * 0.7)
            
            # Calculate run metrics
            total_gain = ((current_price - run_start_price) / run_start_price) * 100
            days_running = len(hist) - run_start_idx
            
            # Get original catalyst (if stored)
            original_catalyst = self._get_original_catalyst(ticker, run_start_date)
            
            # Find similar historical runs
            similar_runs = self._find_similar_runs(ticker, total_gain, days_running)
            
            return {
                'ticker': ticker,
                'run_start_date': run_start_date.strftime('%Y-%m-%d'),
                'run_start_price': float(run_start_price),
                'current_price': float(current_price),
                'days_running': days_running,
                'total_gain_pct': float(total_gain),
                'green_days': green_days,
                'red_days': red_days,
                'support_levels': support_levels,
                'volume_fading': volume_fading,
                'volume_ratio': float(recent_vol / early_vol) if early_vol > 0 else 1,
                'original_catalyst': original_catalyst,
                'similar_runs': similar_runs
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _find_run_start(self, hist) -> int:
        """Find where the run started - first big move"""
        
        # Look for first day with 10%+ move or significant volume
        for i in range(len(hist) - 15, len(hist)):
            if i < 1:
                continue
            
            change = ((hist['Close'].iloc[i] - hist['Close'].iloc[i-1]) / hist['Close'].iloc[i-1]) * 100
            
            if abs(change) >= 10:
                return i
        
        # Default to 10 days ago
        return max(0, len(hist) - 10)
    
    def _find_support_levels(self, hist, start_idx: int) -> List[float]:
        """Find pullback support levels during the run"""
        
        support = []
        
        # Find local lows that held
        for i in range(start_idx + 2, len(hist) - 1):
            if (hist['Low'].iloc[i] < hist['Low'].iloc[i-1] and
                hist['Low'].iloc[i] < hist['Low'].iloc[i+1]):
                support.append(float(hist['Low'].iloc[i]))
        
        # Return top 3 most recent
        return sorted(support, reverse=True)[:3]
    
    def _get_original_catalyst(self, ticker: str, run_start_date) -> str:
        """Get the original catalyst for the run"""
        
        # Check database for stored catalyst
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT catalyst_type, description
            FROM catalysts
            WHERE ticker = ? AND date >= ? AND date <= ?
            ORDER BY date ASC
            LIMIT 1
        ''', (ticker, 
              (run_start_date - timedelta(days=2)).strftime('%Y-%m-%d'),
              (run_start_date + timedelta(days=2)).strftime('%Y-%m-%d')))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"{result[0]}: {result[1]}"
        
        return "Unknown catalyst"
    
    def _find_similar_runs(self, ticker: str, total_gain: float, days: int) -> Dict:
        """Find similar historical runs for this ticker"""
        
        # TODO: Query historical data or memory
        # For now, return placeholder
        
        return {
            'avg_duration': 12,
            'avg_gain': 45.0,
            'typical_pullback_pct': 15.0
        }
    
    def format_run_report(self, run_data: Dict) -> str:
        """Format run tracking report"""
        
        if 'error' in run_data:
            return f"❌ Error: {run_data['error']}"
        
        output = f"\n{'='*60}\n"
        output += f"🐺 RUN TRACKER: {run_data['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        output += f"DAY {run_data['days_running']} OF RUN\n"
        output += f"Started: {run_data['run_start_date']} @ ${run_data['run_start_price']:.2f}\n"
        output += f"Current: ${run_data['current_price']:.2f} (+{run_data['total_gain_pct']:.1f}%)\n\n"
        
        output += f"MOMENTUM:\n"
        output += f"  Green days: {run_data['green_days']} | Red days: {run_data['red_days']}\n"
        
        if run_data['volume_fading']:
            output += f"  ⚠️  VOLUME FADING (now {run_data['volume_ratio']:.0%} of early volume)\n"
        else:
            output += f"  ✅ Volume holding ({run_data['volume_ratio']:.0%})\n"
        
        if run_data['support_levels']:
            output += f"\nSUPPORT LEVELS:\n"
            for level in run_data['support_levels']:
                distance = ((run_data['current_price'] - level) / run_data['current_price']) * 100
                output += f"  ${level:.2f} (-{distance:.1f}%)\n"
        
        output += f"\nORIGINAL CATALYST:\n  {run_data['original_catalyst']}\n"
        
        if run_data['similar_runs']:
            similar = run_data['similar_runs']
            output += f"\nHISTORICAL PATTERN:\n"
            output += f"  Similar runs averaged {similar['avg_duration']} days\n"
            output += f"  Average gain: {similar['avg_gain']:.0f}%\n"
            output += f"  Typical pullback: {similar['typical_pullback_pct']:.0f}%\n"
        
        output += f"\n{'='*60}\n"
        
        return output


if __name__ == '__main__':
    tracker = RunTracker()
    
    # Test on IBRX
    run = tracker.track_run('IBRX')
    print(tracker.format_run_report(run))
