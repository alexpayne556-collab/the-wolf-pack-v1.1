# 🐺 FENRIR MEMORY - Context & Learning System
# "Wow, Fenrir should know this"

from datetime import datetime
from typing import Dict, List, Optional
import json
import os

MEMORY_FILE = 'data/fenrir_memory.json'

class FenrirMemory:
    """Store important context that Fenrir should remember"""
    
    def __init__(self):
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load memory from disk"""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'user_patterns': [],
            'stock_behaviors': {},
            'setup_outcomes': [],
            'important_notes': [],
            'mistakes_to_avoid': [],
            'winning_patterns': [],
            'market_conditions': []
        }
    
    def _save_memory(self):
        """Save memory to disk"""
        os.makedirs('data', exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def log_user_pattern(self, pattern: str, context: str = ''):
        """Log user trading behavior pattern"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'pattern': pattern,
            'context': context
        }
        self.memory['user_patterns'].append(entry)
        self._save_memory()
        print(f"🐺 Learned: {pattern}")
    
    def log_stock_behavior(self, ticker: str, behavior: str, outcome: str):
        """Log how a stock behaves"""
        if ticker not in self.memory['stock_behaviors']:
            self.memory['stock_behaviors'][ticker] = []
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'behavior': behavior,
            'outcome': outcome
        }
        self.memory['stock_behaviors'][ticker].append(entry)
        self._save_memory()
        print(f"🐺 Learned about {ticker}: {behavior} → {outcome}")
    
    def log_setup_outcome(self, ticker: str, setup_type: str, entry_price: float, 
                         exit_price: float, duration_days: int, won: bool):
        """Track setup outcomes for pattern learning"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'ticker': ticker,
            'setup_type': setup_type,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl_pct': ((exit_price - entry_price) / entry_price) * 100,
            'duration_days': duration_days,
            'won': won
        }
        self.memory['setup_outcomes'].append(entry)
        self._save_memory()
        print(f"🐺 Logged setup: {setup_type} on {ticker} - {'WIN' if won else 'LOSS'}")
    
    def log_important_note(self, note: str, category: str = 'general'):
        """Log something important Fenrir should remember"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'note': note
        }
        self.memory['important_notes'].append(entry)
        self._save_memory()
        print(f"🐺 Noted: {note}")
    
    def log_mistake(self, mistake: str, consequence: str):
        """Log mistakes to avoid repeating"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'mistake': mistake,
            'consequence': consequence
        }
        self.memory['mistakes_to_avoid'].append(entry)
        self._save_memory()
        print(f"🐺 Learned from mistake: {mistake}")
    
    def log_winning_pattern(self, pattern: str, win_rate: float, sample_size: int):
        """Log patterns that work"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'pattern': pattern,
            'win_rate': win_rate,
            'sample_size': sample_size
        }
        self.memory['winning_patterns'].append(entry)
        self._save_memory()
        print(f"🐺 Winning pattern identified: {pattern} ({win_rate:.0%} over {sample_size} trades)")
    
    def log_market_condition(self, condition: str, impact: str):
        """Log market conditions and their impact"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'condition': condition,
            'impact': impact
        }
        self.memory['market_conditions'].append(entry)
        self._save_memory()
        print(f"🐺 Market condition noted: {condition}")
    
    def get_stock_history(self, ticker: str) -> List[Dict]:
        """Get all logged behavior for a ticker"""
        return self.memory['stock_behaviors'].get(ticker, [])
    
    def get_recent_patterns(self, days: int = 30) -> List[Dict]:
        """Get recent user patterns"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        return [p for p in self.memory['user_patterns'] 
                if datetime.fromisoformat(p['timestamp']).timestamp() > cutoff]
    
    def get_setup_stats(self, setup_type: str = None) -> Dict:
        """Get win rate and stats for setup types"""
        outcomes = self.memory['setup_outcomes']
        
        if setup_type:
            outcomes = [o for o in outcomes if o['setup_type'] == setup_type]
        
        if not outcomes:
            return {'total': 0, 'wins': 0, 'losses': 0, 'win_rate': 0}
        
        wins = sum(1 for o in outcomes if o['won'])
        losses = len(outcomes) - wins
        
        return {
            'total': len(outcomes),
            'wins': wins,
            'losses': losses,
            'win_rate': wins / len(outcomes) if outcomes else 0,
            'avg_pnl': sum(o['pnl_pct'] for o in outcomes) / len(outcomes),
            'avg_duration': sum(o['duration_days'] for o in outcomes) / len(outcomes)
        }
    
    def recall(self, query: str) -> List[Dict]:
        """Search memory for relevant context"""
        results = []
        query_lower = query.lower()
        
        # Search all memory types
        for note in self.memory['important_notes']:
            if query_lower in note['note'].lower():
                results.append(note)
        
        for pattern in self.memory['user_patterns']:
            if query_lower in pattern['pattern'].lower():
                results.append(pattern)
        
        for mistake in self.memory['mistakes_to_avoid']:
            if query_lower in mistake['mistake'].lower():
                results.append(mistake)
        
        return results


# Global instance
_memory = None

def get_memory() -> FenrirMemory:
    """Get global memory instance"""
    global _memory
    if _memory is None:
        _memory = FenrirMemory()
    return _memory


def fenrir_should_know(note: str, category: str = 'general'):
    """Quick function: "Fenrir should know this" """
    memory = get_memory()
    memory.log_important_note(note, category)


# Example usage
if __name__ == '__main__':
    memory = get_memory()
    
    # User patterns
    memory.log_user_pattern("User tends to overtrade after good weeks", 
                           "After +8% weeks, gave back 5-7% next week")
    
    # Stock behaviors
    memory.log_stock_behavior('IBRX', 'Earnings beat with 3x volume', 
                             'Ran 40% over 10 days then pulled back 20%')
    
    # Setup outcomes
    memory.log_setup_outcome('KTOS', 'defense_pop', 118.50, 130.72, 8, True)
    
    # Important notes
    fenrir_should_know("User's edge is defense sector - 67% win rate")
    fenrir_should_know("User holds losers too long (avg 7 days vs winners 4 days)")
    
    # Mistakes
    memory.log_mistake("Chased QUBT at highs", "Lost $150 when it pulled back 15%")
    
    # Winning patterns
    memory.log_winning_pattern("Defense stocks on contract news", 0.72, 18)
    
    # Recall test
    print("\n🐺 Recall test for 'defense':")
    results = memory.recall('defense')
    for r in results[:3]:
        print(f"  - {r.get('note') or r.get('pattern')}")
