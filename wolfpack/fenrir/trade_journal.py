# 🐺 FENRIR V2 - AUTOMATED TRADE JOURNAL
# Learn from EVERY trade automatically

from datetime import datetime
from typing import Dict, List, Optional
import database
from fenrir_memory import get_memory

class TradeJournal:
    """Automatically journal trades and extract lessons"""
    
    def __init__(self):
        self.memory = get_memory()
    
    def log_entry(self, ticker: str, shares: float, entry_price: float, 
                  setup_type: str, thesis: str, quality_score: int = None) -> int:
        """Log a trade entry"""
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_journal 
            (ticker, action, shares, price, setup_type, thesis, quality_score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, 'BUY', shares, entry_price, setup_type, thesis, quality_score, datetime.now().isoformat()))
        
        trade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Log to memory
        self.memory.log_important_note(
            f"Entered {ticker}: {setup_type} setup, quality {quality_score}/100",
            "trade_entry"
        )
        
        return trade_id
    
    def log_exit(self, ticker: str, shares: float, exit_price: float, 
                 entry_price: float, reason: str, emotions: str = None) -> Dict:
        """
        Log a trade exit and auto-analyze
        
        Returns full trade analysis with lessons learned
        """
        
        # Calculate outcome
        pnl = (exit_price - entry_price) * shares
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        outcome = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        
        # Store in database
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_journal 
            (ticker, action, shares, price, pnl, pnl_pct, outcome, reason, emotions, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, 'SELL', shares, exit_price, pnl, pnl_pct, outcome, reason, emotions, datetime.now().isoformat()))
        
        conn.commit()
        
        # Get full trade history for this ticker
        cursor.execute('''
            SELECT * FROM trade_journal 
            WHERE ticker = ? 
            ORDER BY timestamp DESC 
            LIMIT 2
        ''', (ticker,))
        
        trades = cursor.fetchall()
        conn.close()
        
        # Extract lessons
        lessons = self._extract_lessons(ticker, pnl_pct, reason, emotions, trades)
        
        # Log to memory
        if outcome == "WIN":
            self.memory.log_winning_pattern(
                ticker, reason, pnl_pct, f"Exit reason: {reason}. Emotions: {emotions or 'calm'}"
            )
        else:
            self.memory.log_mistake(
                f"Lost {pnl_pct:.1f}% on {ticker}",
                f"Reason: {reason}. Lesson: {lessons[0] if lessons else 'Review setup quality'}"
            )
        
        return {
            'ticker': ticker,
            'outcome': outcome,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'reason': reason,
            'emotions': emotions,
            'lessons': lessons
        }
    
    def _extract_lessons(self, ticker: str, pnl_pct: float, reason: str, 
                        emotions: str, trades: List) -> List[str]:
        """Auto-extract lessons from trade"""
        
        lessons = []
        
        # Emotional lessons
        if emotions:
            if 'fomo' in emotions.lower():
                lessons.append("❌ FOMO entry - wait for pullback next time")
            if 'panic' in emotions.lower():
                lessons.append("❌ Panic exit - stick to plan")
            if 'greedy' in emotions.lower() or 'bag hold' in emotions.lower():
                lessons.append("❌ Held too long - take profits at target")
        
        # Exit reason lessons
        if 'extended' in reason.lower():
            lessons.append("✅ Smart exit: recognized extension")
        if 'stop' in reason.lower() and pnl_pct > -5:
            lessons.append("✅ Good risk management: cut loss early")
        if 'target' in reason.lower() and pnl_pct > 10:
            lessons.append("✅ Excellent: hit profit target")
        
        # P/L lessons
        if pnl_pct < -10:
            lessons.append("❌ Loss too large - tighter stops needed")
        if pnl_pct > 30:
            lessons.append("✅ BIG WIN - study this setup type")
        
        # Pattern recognition
        if len(trades) >= 2:
            # Check for repeat mistakes
            last_trade = trades[1]
            if last_trade[9] and 'LOSS' in str(last_trade[9]):  # outcome field
                lessons.append("⚠️  Second loss - review entry criteria")
        
        return lessons
    
    def log_paper_trade(self, ticker: str, action: str, reason: str):
        """Log a trade we DIDN'T take (paper trade)"""
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_journal 
            (ticker, action, reason, timestamp, is_paper)
            VALUES (?, ?, ?, ?, 1)
        ''', (ticker, f'PAPER_{action}', reason, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        self.memory.log_important_note(
            f"Passed on {ticker}: {reason}",
            "paper_trade"
        )
    
    def get_recent_journal(self, days: int = 7) -> List[Dict]:
        """Get recent journal entries"""
        
        conn = database.get_connection()
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT * FROM trade_journal 
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (since,))
        
        entries = cursor.fetchall()
        conn.close()
        
        return [self._parse_entry(e) for e in entries]
    
    def _parse_entry(self, entry: tuple) -> Dict:
        """Parse database entry to dict"""
        
        return {
            'id': entry[0],
            'ticker': entry[1],
            'action': entry[2],
            'shares': entry[3] if len(entry) > 3 else None,
            'price': entry[4] if len(entry) > 4 else None,
            'setup_type': entry[5] if len(entry) > 5 else None,
            'thesis': entry[6] if len(entry) > 6 else None,
            'quality_score': entry[7] if len(entry) > 7 else None,
            'pnl': entry[8] if len(entry) > 8 else None,
            'pnl_pct': entry[9] if len(entry) > 9 else None,
            'outcome': entry[10] if len(entry) > 10 else None,
            'reason': entry[11] if len(entry) > 11 else None,
            'emotions': entry[12] if len(entry) > 12 else None,
            'timestamp': entry[13] if len(entry) > 13 else None
        }
    
    def format_journal_report(self, entries: List[Dict]) -> str:
        """Format journal entries"""
        
        output = f"\n{'='*60}\n"
        output += f"🐺 TRADE JOURNAL (Last {len(entries)} entries)\n"
        output += f"{'='*60}\n\n"
        
        for entry in entries:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%m/%d %H:%M')
            
            output += f"[{timestamp}] {entry['action']} {entry['ticker']}\n"
            
            if entry['action'] == 'BUY':
                output += f"  Entry: ${entry['price']:.2f} x {entry['shares']} shares\n"
                output += f"  Setup: {entry['setup_type']} (Quality: {entry['quality_score']}/100)\n"
                output += f"  Thesis: {entry['thesis']}\n"
            
            elif entry['action'] == 'SELL':
                emoji = "✅" if entry['outcome'] == 'WIN' else "❌"
                output += f"  Exit: ${entry['price']:.2f} ({emoji} {entry['outcome']})\n"
                output += f"  P/L: ${entry['pnl']:.2f} ({entry['pnl_pct']:+.1f}%)\n"
                output += f"  Reason: {entry['reason']}\n"
                if entry['emotions']:
                    output += f"  Emotions: {entry['emotions']}\n"
            
            output += "\n"
        
        output += f"{'='*60}\n"
        
        return output


# Add table to database if doesn't exist
def init_journal_table():
    """Initialize trade journal table"""
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            action TEXT NOT NULL,
            shares REAL,
            price REAL,
            setup_type TEXT,
            thesis TEXT,
            quality_score INTEGER,
            pnl REAL,
            pnl_pct REAL,
            outcome TEXT,
            reason TEXT,
            emotions TEXT,
            timestamp TEXT NOT NULL,
            is_paper INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_journal_table()
    
    journal = TradeJournal()
    
    # Test entry
    trade_id = journal.log_entry(
        'IBRX', 37, 4.69, 
        'earnings_beat', 
        'Cancer drug revenue beat expectations',
        quality_score=85
    )
    
    print(f"Logged entry: Trade ID {trade_id}")
    
    # Test exit
    exit_analysis = journal.log_exit(
        'IBRX', 37, 5.52, 4.69,
        'Taking profit at +17%, volume fading on day 10',
        'Calm - stuck to plan'
    )
    
    print("\nExit Analysis:")
    print(f"  Outcome: {exit_analysis['outcome']}")
    print(f"  P/L: ${exit_analysis['pnl']:.2f} ({exit_analysis['pnl_pct']:+.1f}%)")
    print(f"  Lessons:")
    for lesson in exit_analysis['lessons']:
        print(f"    {lesson}")
