# 🐺 FENRIR V2 - MORNING GAME PLAN GENERATOR
# Synthesize everything into daily action plan

from datetime import datetime, date
from typing import Dict, List
import yfinance as yf

from setup_scorer import SetupScorer
from run_tracker import RunTracker
from user_behavior import UserBehaviorTracker
from momentum_shift_detector import SectorRotationDetector
from full_scanner import full_market_scan
from fenrir_memory import get_memory
import config

class GamePlanGenerator:
    """Generate daily trading game plan"""
    
    def __init__(self):
        self.scorer = SetupScorer()
        self.run_tracker = RunTracker()
        self.behavior = UserBehaviorTracker()
        self.sector_rotation = SectorRotationDetector()
        self.memory = get_memory()
    
    def generate_plan(self) -> Dict:
        """
        Generate complete morning game plan
        
        Returns actionable plan with:
        - Top setups to watch
        - Positions to manage
        - Sectors to focus/avoid
        - Psychology reminders
        - Key price levels
        """
        
        print("🐺 Generating game plan...")
        
        # 1. Scan market for new setups
        print("  Scanning market...")
        movers = full_market_scan()
        
        # 2. Score all setups
        print("  Scoring setups...")
        scored = self.scorer.score_multiple(movers[:20])  # Top 20 movers
        
        # 3. Get user behavior insights
        print("  Analyzing your behavior...")
        behavior_analysis = self.behavior.analyze_behavior()
        
        # 4. Check sector rotation
        print("  Checking sector rotation...")
        sector_data = self.sector_rotation.detect_rotation()
        
        # 5. Analyze existing positions
        print("  Analyzing positions...")
        position_plans = self._analyze_positions()
        
        # 6. Psychology check
        psychology_alerts = self.behavior.check_psychology_alerts({})
        
        return {
            'date': date.today().strftime('%Y-%m-%d'),
            'top_setups': scored[:3],  # Top 3 by quality
            'watch_list': scored[3:10],  # Next 7 to monitor
            'position_plans': position_plans,
            'sector_focus': self._get_sector_focus(sector_data, behavior_analysis),
            'avoid': self._get_avoid_list(scored, behavior_analysis),
            'psychology': psychology_alerts,
            'key_levels': self._get_key_levels(position_plans),
            'user_edge': behavior_analysis.get('best_sector', 'Unknown')
        }
    
    def _analyze_positions(self) -> List[Dict]:
        """Analyze each position for action plan"""
        
        plans = []
        
        for ticker, details in config.HOLDINGS.items():
            # Get run data
            run_data = self.run_tracker.track_run(ticker)
            
            if 'error' in run_data:
                continue
            
            # Create action plan
            plan = {
                'ticker': ticker,
                'current_price': run_data['current_price'],
                'day_of_run': run_data['days_running'],
                'support_levels': run_data['support_levels']
            }
            
            # Determine action
            if run_data['volume_fading'] and run_data['days_running'] >= 10:
                plan['action'] = 'TRIM'
                plan['reason'] = f"Day {run_data['days_running']}, volume fading"
            elif run_data['days_running'] <= 3 and not run_data['volume_fading']:
                plan['action'] = 'HOLD'
                plan['reason'] = "Early in run, strong volume"
            elif run_data['support_levels']:
                plan['action'] = 'WATCH'
                plan['reason'] = f"Monitor support at ${run_data['support_levels'][0]:.2f}"
            else:
                plan['action'] = 'HOLD'
                plan['reason'] = "Holding position"
            
            plans.append(plan)
        
        return plans
    
    def _get_sector_focus(self, sector_data: Dict, behavior: Dict) -> Dict:
        """Determine which sectors to focus on"""
        
        focus = {}
        
        # User's edge sector
        edge_sector = behavior.get('best_sector')
        if edge_sector:
            focus['your_edge'] = edge_sector
        
        # Hot sectors today
        if sector_data.get('sorted_sectors'):
            hottest = sector_data['sorted_sectors'][0]
            if hottest[1]['strength'] > 2:
                focus['hot_today'] = hottest[0]
        
        return focus
    
    def _get_avoid_list(self, scored: List[Dict], behavior: Dict) -> List[Dict]:
        """What to avoid today"""
        
        avoid = []
        
        # Weak setups
        for setup in scored:
            if setup['score'] < 40:
                avoid.append({
                    'ticker': setup['ticker'],
                    'reason': f"Low quality score ({setup['score']}/100)"
                })
        
        # User's weak sector
        weak_sector = behavior.get('worst_sector')
        if weak_sector:
            avoid.append({
                'sector': weak_sector,
                'reason': f"Your weak sector ({behavior.get('worst_sector_wr', 0):.0%} WR)"
            })
        
        return avoid[:5]  # Top 5 things to avoid
    
    def _get_key_levels(self, position_plans: List[Dict]) -> Dict:
        """Key price levels to watch today"""
        
        levels = {}
        
        for plan in position_plans:
            ticker = plan['ticker']
            
            if plan.get('support_levels'):
                levels[ticker] = {
                    'current': plan['current_price'],
                    'support': plan['support_levels'][0] if plan['support_levels'] else None,
                    'action_level': plan['support_levels'][0] if plan['support_levels'] else plan['current_price'] * 0.95
                }
        
        return levels
    
    def format_game_plan(self, plan: Dict) -> str:
        """Format game plan for display"""
        
        output = f"\n{'='*60}\n"
        output += f"🐺 FENRIR MORNING GAME PLAN - {plan['date']}\n"
        output += f"{'='*60}\n\n"
        
        # Top setups
        output += "TOP 3 SETUPS TO WATCH:\n\n"
        for i, setup in enumerate(plan['top_setups'], 1):
            output += f"{i}. {setup['ticker']} (Score: {setup['score']}/100 - {setup['grade']})\n"
            output += f"   ${setup['price']:.2f} | {setup['reasoning']}\n\n"
        
        # Position management
        if plan['position_plans']:
            output += "POSITION MANAGEMENT:\n\n"
            for pos in plan['position_plans']:
                action_emoji = {
                    'TRIM': '📉',
                    'HOLD': '✋',
                    'WATCH': '👀',
                    'ADD': '📈'
                }.get(pos['action'], '•')
                
                output += f"{action_emoji} {pos['ticker']}: {pos['action']}\n"
                output += f"   Day {pos['day_of_run']} | ${pos['current_price']:.2f}\n"
                output += f"   Plan: {pos['reason']}\n\n"
        
        # Sector focus
        if plan['sector_focus']:
            output += "SECTOR FOCUS:\n"
            if 'your_edge' in plan['sector_focus']:
                output += f"  💪 YOUR EDGE: {plan['sector_focus']['your_edge']}\n"
            if 'hot_today' in plan['sector_focus']:
                output += f"  🔥 HOT TODAY: {plan['sector_focus']['hot_today']}\n"
            output += "\n"
        
        # Avoid list
        if plan['avoid']:
            output += "AVOID TODAY:\n"
            for avoid in plan['avoid']:
                if 'ticker' in avoid:
                    output += f"  ❌ {avoid['ticker']}: {avoid['reason']}\n"
                elif 'sector' in avoid:
                    output += f"  ❌ {avoid['sector']} sector: {avoid['reason']}\n"
            output += "\n"
        
        # Psychology
        if plan['psychology']:
            output += "PSYCHOLOGY ALERTS:\n"
            for alert in plan['psychology']:
                output += f"  {alert}\n"
            output += "\n"
        
        # Key levels
        if plan['key_levels']:
            output += "KEY PRICE LEVELS:\n"
            for ticker, levels in plan['key_levels'].items():
                output += f"  {ticker}: Current ${levels['current']:.2f}\n"
                if levels['support']:
                    output += f"    Watch support: ${levels['support']:.2f}\n"
            output += "\n"
        
        output += f"{'='*60}\n"
        output += "🐺 STICK TO THE PLAN. TRUST YOUR PROCESS.\n"
        output += f"{'='*60}\n"
        
        return output


if __name__ == '__main__':
    planner = GamePlanGenerator()
    plan = planner.generate_plan()
    print(planner.format_game_plan(plan))
