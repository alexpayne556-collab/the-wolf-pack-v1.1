# 🐺 FENRIR V2 - MASTER INTEGRATOR
# Tie everything together into one intelligent system

from datetime import datetime
from typing import Dict, List, Optional

from setup_scorer import SetupScorer
from run_tracker import RunTracker
from user_behavior import UserBehaviorTracker
from momentum_shift_detector import MomentumShiftDetector, SectorRotationDetector
from trade_journal import TradeJournal
from game_plan import GamePlanGenerator
from fenrir_memory import get_memory, fenrir_should_know

class FenrirV2:
    """
    FENRIR V2 - Next-gen trading assistant
    
    Combines all quantum leap features:
    - Setup quality scoring (prioritize what to watch)
    - Multi-day run tracking (full context)
    - User behavior learning (know thyself)
    - Momentum shift detection (real-time character changes)
    - Automated trade journaling (learn from every trade)
    - Morning game plans (synthesize everything)
    """
    
    def __init__(self):
        self.scorer = SetupScorer()
        self.run_tracker = RunTracker()
        self.behavior = UserBehaviorTracker()
        self.momentum = MomentumShiftDetector()
        self.sector_rotation = SectorRotationDetector()
        self.journal = TradeJournal()
        self.planner = GamePlanGenerator()
        self.memory = get_memory()
        
        print("🐺 FENRIR V2 ONLINE")
        print("=" * 60)
    
    def analyze_stock(self, ticker: str, full_context: bool = False) -> Dict:
        """
        Complete stock analysis combining all systems
        
        Args:
            ticker: Stock to analyze
            full_context: Include run tracking and momentum (slower)
        
        Returns:
            Complete analysis dict
        """
        
        print(f"\n🐺 Analyzing {ticker}...")
        
        analysis = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat()
        }
        
        # 1. Setup Quality Score
        print("  • Scoring setup quality...")
        # Get basic data first
        import yfinance as yf
        stock = yf.Ticker(ticker)
        hist = stock.history(period='2d')
        
        if not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
            prev_price = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current_price
            change_pct = ((current_price - prev_price) / prev_price) * 100
            
            vol_current = float(hist['Volume'].iloc[-1])
            vol_prev = float(hist['Volume'].iloc[-2]) if len(hist) >= 2 else vol_current
            volume_ratio = vol_current / vol_prev if vol_prev > 0 else 1
            
            setup_data = {
                'price': current_price,
                'change_pct': change_pct,
                'volume_ratio': volume_ratio
            }
            
            score_result = self.scorer.score_setup(ticker, setup_data)
            analysis['quality_score'] = score_result
        
        # 2. Run Tracking (if full context)
        if full_context:
            print("  • Tracking run history...")
            run_data = self.run_tracker.track_run(ticker)
            analysis['run_data'] = run_data
        
        # 3. Momentum Shifts (if full context)
        if full_context:
            print("  • Detecting momentum shifts...")
            shifts = self.momentum.detect_shifts(ticker)
            analysis['momentum_shifts'] = shifts
        
        # 4. User's history with this stock
        print("  • Checking your history...")
        stock_memory = self.memory.get_stock_history(ticker)
        analysis['your_history'] = stock_memory
        
        # 5. Psychology check for this specific stock
        behavior_context = {
            'ticker': ticker,
            'sector': self._get_sector(ticker)
        }
        psychology = self.behavior.check_psychology_alerts(behavior_context)
        analysis['psychology_alerts'] = psychology
        
        return analysis
    
    def morning_briefing(self) -> str:
        """Generate complete morning briefing"""
        
        print("\n🐺 Generating morning briefing...\n")
        
        # Generate game plan
        plan = self.planner.generate_plan()
        
        # Format and return
        return self.planner.format_game_plan(plan)
    
    def log_trade_entry(self, ticker: str, shares: float, entry_price: float,
                       setup_type: str, thesis: str) -> int:
        """
        Log a trade entry with auto-scoring
        
        Returns trade ID
        """
        
        # Score the setup
        setup_data = {
            'price': entry_price,
            'change_pct': 0,  # Will be filled from real data
            'volume_ratio': 1
        }
        score_result = self.scorer.score_setup(ticker, setup_data)
        
        # Log to journal
        trade_id = self.journal.log_entry(
            ticker, shares, entry_price, setup_type, thesis,
            quality_score=score_result['score']
        )
        
        # Memory logging
        fenrir_should_know(
            f"Entered {ticker} @ ${entry_price:.2f}: {setup_type} (score {score_result['score']}/100)"
        )
        
        print(f"✅ Trade entry logged (ID: {trade_id})")
        print(f"   Setup quality: {score_result['score']}/100 ({score_result['grade']})")
        
        return trade_id
    
    def log_trade_exit(self, ticker: str, shares: float, exit_price: float,
                      entry_price: float, reason: str, emotions: str = None) -> Dict:
        """Log a trade exit with auto-analysis"""
        
        exit_analysis = self.journal.log_exit(
            ticker, shares, exit_price, entry_price, reason, emotions
        )
        
        print(f"\n{'='*60}")
        print(f"🐺 TRADE EXIT ANALYSIS: {ticker}")
        print(f"{'='*60}")
        print(f"Outcome: {exit_analysis['outcome']}")
        print(f"P/L: ${exit_analysis['pnl']:.2f} ({exit_analysis['pnl_pct']:+.1f}%)")
        print(f"Reason: {exit_analysis['reason']}")
        
        if exit_analysis['lessons']:
            print(f"\nLESSONS LEARNED:")
            for lesson in exit_analysis['lessons']:
                print(f"  {lesson}")
        
        print(f"{'='*60}\n")
        
        return exit_analysis
    
    def check_momentum_now(self, ticker: str) -> str:
        """Quick momentum check for a stock"""
        
        shifts = self.momentum.detect_shifts(ticker)
        return self.momentum.format_shift_report(shifts)
    
    def get_sector_flow(self) -> str:
        """Check where money is flowing today"""
        
        rotation = self.sector_rotation.detect_rotation()
        return self.sector_rotation.format_rotation_report(rotation)
    
    def analyze_your_edge(self) -> str:
        """Analyze your trading edge"""
        
        behavior = self.behavior.analyze_behavior()
        return self.behavior.format_behavior_report(behavior)
    
    def format_analysis(self, analysis: Dict) -> str:
        """Format complete stock analysis"""
        
        output = f"\n{'='*60}\n"
        output += f"🐺 FENRIR V2 ANALYSIS: {analysis['ticker']}\n"
        output += f"{'='*60}\n\n"
        
        # Quality Score
        if 'quality_score' in analysis:
            score = analysis['quality_score']
            output += f"SETUP QUALITY: {score['score']}/100 ({score['grade']})\n"
            output += f"{score['reasoning']}\n\n"
        
        # Run Data
        if 'run_data' in analysis and 'error' not in analysis['run_data']:
            run = analysis['run_data']
            output += f"RUN CONTEXT:\n"
            output += f"  Day {run['days_running']} of run\n"
            output += f"  Started ${run['run_start_price']:.2f} → Now ${run['current_price']:.2f}\n"
            output += f"  Total gain: {run['total_gain_pct']:.1f}%\n"
            
            if run['volume_fading']:
                output += f"  ⚠️  Volume fading\n"
            output += "\n"
        
        # Momentum Shifts
        if 'momentum_shifts' in analysis and 'error' not in analysis['momentum_shifts']:
            shifts = analysis['momentum_shifts']
            if shifts['shifts_detected'] > 0:
                output += f"MOMENTUM: {shifts['overall_momentum']}\n"
                output += f"  {shifts['shifts_detected']} shift(s) detected\n\n"
        
        # Psychology Alerts
        if analysis.get('psychology_alerts'):
            output += f"PSYCHOLOGY:\n"
            for alert in analysis['psychology_alerts']:
                output += f"  {alert}\n"
            output += "\n"
        
        # Your History
        if analysis.get('your_history'):
            output += f"YOUR HISTORY:\n"
            for entry in analysis['your_history'][:3]:  # Last 3 entries
                output += f"  • {entry.get('note', 'No notes')}\n"
            output += "\n"
        
        output += f"{'='*60}\n"
        
        return output
    
    def _get_sector(self, ticker: str) -> str:
        """Get sector for ticker"""
        import config
        
        for sector, tickers in config.WATCHLIST.items():
            if ticker in tickers:
                return sector
        
        return 'unknown'


# Convenience functions for quick access
def analyze(ticker: str, full: bool = False):
    """Quick analysis of a stock"""
    fenrir = FenrirV2()
    analysis = fenrir.analyze_stock(ticker, full_context=full)
    print(fenrir.format_analysis(analysis))
    return analysis


def morning_brief():
    """Get morning game plan"""
    fenrir = FenrirV2()
    print(fenrir.morning_briefing())


def check_momentum(ticker: str):
    """Quick momentum check"""
    fenrir = FenrirV2()
    print(fenrir.check_momentum_now(ticker))


def sector_flow():
    """Check sector rotation"""
    fenrir = FenrirV2()
    print(fenrir.get_sector_flow())


def my_edge():
    """Analyze your trading edge"""
    fenrir = FenrirV2()
    print(fenrir.analyze_your_edge())


if __name__ == '__main__':
    # Demo
    print("🐺 FENRIR V2 - QUANTUM LEAP FEATURES DEMO\n")
    
    fenrir = FenrirV2()
    
    # Quick analysis
    analysis = fenrir.analyze_stock('IBRX', full_context=True)
    print(fenrir.format_analysis(analysis))
