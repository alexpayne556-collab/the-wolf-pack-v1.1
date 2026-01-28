"""
📊 WOLF PACK UNIFIED DASHBOARD

Real-time view of all autonomous trading activity:
- Active positions with P&L
- Recent trades (wins/losses)
- Strategy performance
- Pending trade ideas
- Lessons learned
- System health

Run with: python dashboard.py
Or integrate into main brain loop
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import os

log = logging.getLogger('Dashboard')


class WolfDashboard:
    """Unified dashboard for all Wolf Pack activity"""
    
    def __init__(self, db_path: str = "data/wolf_brain/autonomous_memory.db"):
        self.db_path = db_path
        
        # Ensure db exists
        if not os.path.exists(db_path):
            log.warning(f"Database not found: {db_path}")
    
    def get_active_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT ticker, quantity, entry_price, stop_price, target_price, 
                       strategy, timestamp
                FROM trades
                WHERE status = 'open'
                ORDER BY timestamp DESC
            """)
            
            positions = []
            for row in c.fetchall():
                positions.append({
                    'ticker': row[0],
                    'quantity': row[1],
                    'entry': row[2],
                    'stop': row[3],
                    'target': row[4],
                    'strategy': row[5],
                    'opened': row[6]
                })
            
            conn.close()
            return positions
            
        except Exception as e:
            log.error(f"Error fetching positions: {e}")
            return []
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict]:
        """Get recent closed trades"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT ticker, side, quantity, entry_price, exit_price, 
                       pnl, strategy, timestamp, status
                FROM trades
                WHERE status LIKE 'closed%'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            trades = []
            for row in c.fetchall():
                trades.append({
                    'ticker': row[0],
                    'side': row[1],
                    'quantity': row[2],
                    'entry': row[3],
                    'exit': row[4],
                    'pnl': row[5],
                    'strategy': row[6],
                    'timestamp': row[7],
                    'status': row[8]
                })
            
            conn.close()
            return trades
            
        except Exception as e:
            log.error(f"Error fetching trades: {e}")
            return []
    
    def get_strategy_performance(self) -> Dict:
        """Calculate win rate and P&L by strategy"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT strategy, 
                       COUNT(*) as total,
                       SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                       AVG(pnl) as avg_pnl,
                       SUM(pnl) as total_pnl
                FROM trades
                WHERE status LIKE 'closed%' AND strategy IS NOT NULL
                GROUP BY strategy
                ORDER BY total_pnl DESC
            """)
            
            performance = {}
            for row in c.fetchall():
                strategy = row[0]
                total = row[1]
                wins = row[2]
                losses = row[3]
                avg_pnl = row[4]
                total_pnl = row[5]
                
                win_rate = (wins / total * 100) if total > 0 else 0
                
                performance[strategy] = {
                    'total_trades': total,
                    'wins': wins,
                    'losses': losses,
                    'win_rate': win_rate,
                    'avg_pnl': avg_pnl,
                    'total_pnl': total_pnl
                }
            
            conn.close()
            return performance
            
        except Exception as e:
            log.error(f"Error calculating performance: {e}")
            return {}
    
    def get_pending_ideas(self) -> List[Dict]:
        """Get pending paper trade ideas"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT ticker, strategy, confidence, entry_price, 
                       target_price, timestamp, status
                FROM paper_trade_ideas
                WHERE status = 'PENDING'
                ORDER BY confidence DESC
                LIMIT 10
            """)
            
            ideas = []
            for row in c.fetchall():
                ideas.append({
                    'ticker': row[0],
                    'strategy': row[1],
                    'confidence': row[2],
                    'entry': row[3],
                    'target': row[4],
                    'timestamp': row[5],
                    'status': row[6]
                })
            
            conn.close()
            return ideas
            
        except Exception as e:
            log.error(f"Error fetching ideas: {e}")
            return []
    
    def get_lessons_learned(self, limit: int = 5) -> List[Dict]:
        """Get recent lessons from losses"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT ticker, strategy, pnl_pct, lesson, timestamp
                FROM lessons_learned
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            lessons = []
            for row in c.fetchall():
                lessons.append({
                    'ticker': row[0],
                    'strategy': row[1],
                    'pnl': row[2],
                    'lesson': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            return lessons
            
        except Exception as e:
            # Table might not exist yet
            return []
    
    def get_portfolio_stats(self) -> Dict:
        """Calculate overall portfolio statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Total P&L
            c.execute("SELECT SUM(pnl) FROM trades WHERE status LIKE 'closed%'")
            total_pnl = c.fetchone()[0] or 0
            
            # Win rate
            c.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins
                FROM trades
                WHERE status LIKE 'closed%'
            """)
            row = c.fetchone()
            total_trades = row[0] or 0
            wins = row[1] or 0
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            
            # Today's P&L
            today = datetime.now().date().isoformat()
            c.execute("""
                SELECT SUM(pnl) 
                FROM trades 
                WHERE status LIKE 'closed%' 
                AND DATE(timestamp) = ?
            """, (today,))
            today_pnl = c.fetchone()[0] or 0
            
            # Active positions count
            c.execute("SELECT COUNT(*) FROM trades WHERE status = 'open'")
            open_positions = c.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_pnl': total_pnl,
                'total_trades': total_trades,
                'wins': wins,
                'losses': total_trades - wins,
                'win_rate': win_rate,
                'today_pnl': today_pnl,
                'open_positions': open_positions
            }
            
        except Exception as e:
            log.error(f"Error calculating stats: {e}")
            return {}
    
    def render_terminal_dashboard(self) -> str:
        """Render a text-based dashboard for terminal display"""
        
        dashboard = "\n"
        dashboard += "╔═══════════════════════════════════════════════════════════════════════╗\n"
        dashboard += "║                   🐺 WOLF PACK DASHBOARD 🐺                           ║\n"
        dashboard += "╚═══════════════════════════════════════════════════════════════════════╝\n"
        dashboard += f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Portfolio Stats
        stats = self.get_portfolio_stats()
        dashboard += "┌─ PORTFOLIO STATS ─────────────────────────────────────────────────────┐\n"
        if stats:
            dashboard += f"│  Total P&L: ${stats.get('total_pnl', 0):.2f}\n"
            dashboard += f"│  Today's P&L: ${stats.get('today_pnl', 0):.2f}\n"
            dashboard += f"│  Win Rate: {stats.get('win_rate', 0):.1f}% ({stats.get('wins', 0)}W / {stats.get('losses', 0)}L)\n"
            dashboard += f"│  Total Trades: {stats.get('total_trades', 0)}\n"
            dashboard += f"│  Open Positions: {stats.get('open_positions', 0)}\n"
        else:
            dashboard += "│  No trade data yet\n"
        dashboard += "└───────────────────────────────────────────────────────────────────────┘\n\n"
        
        # Active Positions
        positions = self.get_active_positions()
        dashboard += "┌─ ACTIVE POSITIONS ────────────────────────────────────────────────────┐\n"
        if positions:
            for pos in positions:
                dashboard += f"│  {pos['ticker']:6s} × {pos['quantity']:4d}  "
                dashboard += f"Entry: ${pos['entry']:6.2f}  "
                dashboard += f"Stop: ${pos['stop']:6.2f}  "
                dashboard += f"Target: ${pos['target']:6.2f}\n"
                dashboard += f"│         Strategy: {pos['strategy']}\n"
        else:
            dashboard += "│  No open positions\n"
        dashboard += "└───────────────────────────────────────────────────────────────────────┘\n\n"
        
        # Strategy Performance
        performance = self.get_strategy_performance()
        dashboard += "┌─ STRATEGY PERFORMANCE ────────────────────────────────────────────────┐\n"
        if performance:
            for strategy, stats in performance.items():
                dashboard += f"│  {strategy:20s}  "
                dashboard += f"{stats['win_rate']:5.1f}%  "
                dashboard += f"({stats['wins']}W/{stats['losses']}L)  "
                dashboard += f"P&L: {stats['total_pnl']:+.2f}%\n"
        else:
            dashboard += "│  No strategy data yet\n"
        dashboard += "└───────────────────────────────────────────────────────────────────────┘\n\n"
        
        # Recent Trades
        trades = self.get_recent_trades(5)
        dashboard += "┌─ RECENT TRADES (Last 5) ──────────────────────────────────────────────┐\n"
        if trades:
            for trade in trades:
                pnl_symbol = "✅" if trade['pnl'] > 0 else "❌"
                dashboard += f"│  {pnl_symbol} {trade['ticker']:6s}  "
                dashboard += f"{trade['strategy']:20s}  "
                dashboard += f"P&L: {trade['pnl']:+6.2f}%\n"
        else:
            dashboard += "│  No closed trades yet\n"
        dashboard += "└───────────────────────────────────────────────────────────────────────┘\n\n"
        
        # Pending Ideas
        ideas = self.get_pending_ideas()
        dashboard += "┌─ PENDING TRADE IDEAS ─────────────────────────────────────────────────┐\n"
        if ideas:
            for idea in ideas[:5]:
                dashboard += f"│  {idea['ticker']:6s}  "
                dashboard += f"{idea['strategy']:20s}  "
                dashboard += f"Confidence: {idea['confidence']*100:5.1f}%\n"
        else:
            dashboard += "│  No pending ideas\n"
        dashboard += "└───────────────────────────────────────────────────────────────────────┘\n\n"
        
        # Lessons Learned
        lessons = self.get_lessons_learned(3)
        dashboard += "┌─ LESSONS LEARNED (Recent Losses) ─────────────────────────────────────┐\n"
        if lessons:
            for lesson in lessons:
                dashboard += f"│  📚 {lesson['ticker']} ({lesson['strategy']}) - {lesson['pnl']:.1f}%\n"
                dashboard += f"│     {lesson['lesson'][:65]}\n"
        else:
            dashboard += "│  No lessons yet (no losses!) 🎉\n"
        dashboard += "└───────────────────────────────────────────────────────────────────────┘\n\n"
        
        return dashboard
    
    def save_dashboard_to_file(self, output_path: str = "data/wolf_brain/DASHBOARD.txt"):
        """Save dashboard to a text file"""
        dashboard = self.render_terminal_dashboard()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        print(f"📊 Dashboard saved to: {output_path}")


def main():
    """Generate and display the dashboard"""
    import sys
    
    db_path = "data/wolf_brain/autonomous_memory.db"
    
    # Allow custom db path
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    dashboard = WolfDashboard(db_path)
    
    # Render and print
    output = dashboard.render_terminal_dashboard()
    print(output)
    
    # Save to file
    dashboard.save_dashboard_to_file()


if __name__ == '__main__':
    main()
