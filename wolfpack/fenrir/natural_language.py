# 🐺 FENRIR V2 - NATURAL LANGUAGE INTERFACE
# Understand what user means, not just keywords

import re
from typing import Dict, List, Optional
from fenrir_v2 import FenrirV2
from fenrir_memory import get_memory

class NaturalLanguageInterface:
    """
    Parse natural language queries and route to appropriate modules
    
    Examples:
    - "what's moving after hours?" → ah_anomaly_detector
    - "check IBRX" → full stock analysis
    - "why is TLN down?" → news search + context
    - "scan defense" → sector scan
    - "any insider selling?" → insider analysis
    """
    
    def __init__(self):
        self.fenrir = FenrirV2()
        self.memory = get_memory()
        self.session_context = {}  # Remember context within session
    
    def parse_and_execute(self, user_input: str) -> str:
        """
        Main entry point - parse user's natural language and execute
        
        Args:
            user_input: What the user said/typed
            
        Returns:
            Response string with results
        """
        
        # Normalize input
        query = user_input.lower().strip()
        
        # Extract tickers if mentioned (pass original input to preserve case)
        tickers = self._extract_tickers(user_input)
        if tickers:
            self.session_context['last_ticker'] = tickers[0]
        
        # Pattern matching for common queries
        # (In production, use Ollama LLM for more sophisticated parsing)
        
        # After hours queries
        if any(word in query for word in ['after hours', 'ah', 'afterhours', 'extended']):
            if any(word in query for word in ['moving', 'movers', "what's", 'whats']):
                return self._handle_ah_movers(query)
        
        # Stock analysis
        if tickers:
            if any(word in query for word in ['check', 'analyze', 'look at', 'whats', "what's", 'how', 'status']):
                return self._handle_stock_analysis(tickers[0], query)
            
            if any(word in query for word in ['why', 'down', 'up', 'moving', 'catalyst']):
                return self._handle_why_moving(tickers[0], query)
        
        # Sector queries
        sectors = self._extract_sectors(query)
        if sectors or any(word in query for word in ['sector', 'sectors']):
            if any(word in query for word in ['scan', 'check', 'look', 'whats', "what's"]):
                return self._handle_sector_scan(sectors[0] if sectors else None)
            
            if 'rotation' in query or 'flow' in query or 'money' in query:
                return self.fenrir.get_sector_flow()
        
        # Insider queries
        if any(word in query for word in ['insider', 'insiders', 'selling', 'buying', 'form 144', 'form 4']):
            return self._handle_insider_query(query, tickers)
        
        # Portfolio queries
        if any(word in query for word in ['portfolio', 'positions', 'holdings', 'my stocks', 'what i own']):
            return self._handle_portfolio_query(query)
        
        # Morning briefing
        if any(word in query for word in ['morning', 'briefing', 'plan', 'game plan', 'today']):
            return self.fenrir.morning_briefing()
        
        # My edge
        if any(word in query for word in ['my edge', 'my stats', 'how am i', 'my performance']):
            return self.fenrir.analyze_your_edge()
        
        # Momentum check
        if any(word in query for word in ['momentum', 'character', 'shift', 'changing']):
            if tickers:
                return self.fenrir.check_momentum_now(tickers[0])
            else:
                return "Which ticker should I check momentum on?"
        
        # Memory queries
        if any(word in query for word in ['remember', 'memory', 'history', 'last time', 'before']):
            return self._handle_memory_query(query, tickers)
        
        # Default: try to be helpful
        return self._handle_unclear_query(query, tickers)
    
    def _extract_tickers(self, user_input: str) -> List[str]:
        """Extract ticker symbols from query"""
        
        # Look for $TICKER or uppercase 2-5 letter words
        tickers = []
        
        # $TICKER format (most reliable)
        dollar_tickers = re.findall(r'\$([A-Z]{1,5})', user_input.upper())
        tickers.extend(dollar_tickers)
        
        # Exclude common command words
        command_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'CHECK', 'SCAN', 'SHOW', 'WHATS', 'WHY', 'WHAT', 'WHERE', 'WHEN', 'LOOK', 'FIND', 'DOWN', 'MOVING', 'AFTER', 'HOURS', 'SECTOR', 'ANY', 'SOME', 'MORE', 'ABOUT', 'THAN', 'BEEN', 'HAVE', 'FROM', 'THEY', 'KNOW', 'WILL', 'WOULD', 'MAKE', 'OVER', 'THINK', 'ALSO', 'BACK', 'YEAR', 'WORK', 'JUST', 'INTO', 'GIVE', 'MOST', 'VERY', 'AFTER', 'BEING', 'COULD', 'STILL', 'WHICH', 'THEIR', 'THERE', 'FIRST', 'THESE', 'OTHER', 'SUCH', 'ONLY', 'WELL', 'THEN', 'MUCH', 'EVEN', 'TAKE', 'MANY', 'TELL'}
        
        # Only extract UPPERCASE words that look like tickers
        # Must be 2-5 chars and ALREADY UPPERCASE in original query
        for match in re.finditer(r'\b([A-Z]{2,5})\b', user_input):
            ticker = match.group(1)
            if ticker not in command_words and ticker not in ['IS', 'IT', 'IN', 'ON', 'AT', 'TO', 'OF', 'BY', 'UP']:
                tickers.append(ticker)
        
        return list(set(tickers))  # Remove duplicates
    
    def _extract_sectors(self, query: str) -> List[str]:
        """Extract sector names from query"""
        
        sector_keywords = {
            'defense': ['defense', 'military', 'weapons', 'drones'],
            'biotech': ['biotech', 'bio', 'pharma', 'drug', 'fda'],
            'ai_semis': ['ai', 'chips', 'semis', 'semiconductors', 'nvidia', 'memory'],
            'nuclear': ['nuclear', 'uranium', 'smr', 'reactors'],
            'space': ['space', 'satellite', 'rockets', 'lunar'],
            'quantum': ['quantum', 'computing'],
            'crypto': ['crypto', 'bitcoin', 'blockchain']
        }
        
        sectors = []
        query_lower = query.lower()
        
        for sector, keywords in sector_keywords.items():
            if any(kw in query_lower for kw in keywords):
                sectors.append(sector)
        
        return sectors
    
    def _handle_ah_movers(self, query: str) -> str:
        """Handle after hours mover queries"""
        
        output = "\n🔥 AFTER HOURS MOVERS\n"
        output += "=" * 60 + "\n\n"
        output += "Scanning for significant after hours moves...\n\n"
        
        # In production, actually scan for AH movers
        # For now, return instructions
        output += "This would scan for stocks with:\n"
        output += "  • >10% move in after hours\n"
        output += "  • Significant volume\n"
        output += "  • Auto-search for catalyst\n"
        output += "  • Flag reversals (day up, AH down)\n\n"
        
        output += "MODULE NEEDED: ah_anomaly_detector.py (from Training Note #15)\n"
        
        return output
    
    def _handle_stock_analysis(self, ticker: str, query: str) -> str:
        """Handle stock analysis queries"""
        
        # Determine depth of analysis needed
        full_analysis = any(word in query for word in ['full', 'complete', 'deep', 'everything'])
        
        analysis = self.fenrir.analyze_stock(ticker, full_context=full_analysis)
        return self.fenrir.format_analysis(analysis)
    
    def _handle_why_moving(self, ticker: str, query: str) -> str:
        """Handle 'why is X moving' queries"""
        
        output = f"\n🔍 WHY IS {ticker} MOVING?\n"
        output += "=" * 60 + "\n\n"
        
        # Get analysis
        analysis = self.fenrir.analyze_stock(ticker, full_context=True)
        
        # Extract key info
        if 'quality_score' in analysis:
            score = analysis['quality_score']
            output += f"Setup Quality: {score['score']}/100\n"
            output += f"{score['reasoning']}\n\n"
        
        if 'run_data' in analysis and 'error' not in analysis['run_data']:
            run = analysis['run_data']
            output += f"Run Context:\n"
            output += f"  Day {run['days_running']} of run\n"
            output += f"  Total gain: {run['total_gain_pct']:.1f}%\n"
            if run['volume_fading']:
                output += f"  ⚠️  Volume fading\n"
            output += "\n"
        
        output += f"Check news for {ticker} for recent catalysts.\n"
        output += f"\nMODULE NEEDED: news_price_connector.py (Training Note #17)\n"
        
        return output
    
    def _handle_sector_scan(self, sector: Optional[str]) -> str:
        """Handle sector scan queries"""
        
        if sector:
            output = f"\n📊 SCANNING {sector.upper()} SECTOR\n"
        else:
            output = f"\n📊 SECTOR SCAN\n"
        
        output += "=" * 60 + "\n\n"
        output += "This would:\n"
        output += "  • Scan all tickers in sector\n"
        output += "  • Score setups by quality\n"
        output += "  • Show top movers\n"
        output += "  • Include sector rotation data\n\n"
        
        # Get sector flow
        output += "Meanwhile, here's sector rotation:\n"
        output += self.fenrir.get_sector_flow()
        
        return output
    
    def _handle_insider_query(self, query: str, tickers: List[str]) -> str:
        """Handle insider trading queries"""
        
        output = "\n📋 INSIDER ACTIVITY\n"
        output += "=" * 60 + "\n\n"
        
        if tickers:
            output += f"Checking insider activity for {', '.join(tickers)}...\n\n"
        else:
            output += "Checking insider activity for watchlist...\n\n"
        
        output += "This would:\n"
        output += "  • Scan Form 144 and Form 4 filings\n"
        output += "  • Calculate % of float\n"
        output += "  • Check if plan adoption or discretionary\n"
        output += "  • Score concern level (green/yellow/red)\n\n"
        
        output += "MODULE NEEDED: insider_analyzer.py (Training Note #1)\n"
        
        return output
    
    def _handle_portfolio_query(self, query: str) -> str:
        """Handle portfolio queries"""
        
        from portfolio import get_portfolio_status
        
        try:
            return get_portfolio_status()
        except Exception as e:
            return f"Error getting portfolio: {e}"
    
    def _handle_memory_query(self, query: str, tickers: List[str]) -> str:
        """Handle memory/history queries"""
        
        if tickers:
            ticker = tickers[0]
            history = self.memory.get_stock_history(ticker)
            
            if history:
                output = f"\n🧠 MEMORY: {ticker}\n"
                output += "=" * 60 + "\n\n"
                for entry in history[:5]:
                    output += f"• {entry.get('note', 'No note')}\n"
                return output
            else:
                return f"No history for {ticker} in memory."
        else:
            # General memory recall
            search_terms = query.split()
            results = self.memory.recall(' '.join(search_terms[-3:]))  # Last 3 words
            
            if results:
                output = "\n🧠 MEMORY RECALL\n"
                output += "=" * 60 + "\n\n"
                for entry in results[:10]:
                    output += f"• {entry.get('note', 'No note')}\n"
                return output
            else:
                return "No relevant memories found."
    
    def _handle_unclear_query(self, query: str, tickers: List[str]) -> str:
        """Handle queries we couldn't parse"""
        
        output = "I'm not sure what you're asking. Here are some things I can do:\n\n"
        output += "📊 Stock Analysis:\n"
        output += "  • 'check IBRX' or 'analyze MU'\n"
        output += "  • 'why is TLN down?'\n"
        output += "  • 'IBRX momentum'\n\n"
        
        output += "🔥 Market Scanning:\n"
        output += "  • 'what's moving after hours?'\n"
        output += "  • 'scan defense sector'\n"
        output += "  • 'sector rotation'\n\n"
        
        output += "📋 Information:\n"
        output += "  • 'show portfolio'\n"
        output += "  • 'any insider selling?'\n"
        output += "  • 'what's my edge?'\n\n"
        
        output += "📅 Planning:\n"
        output += "  • 'morning briefing'\n"
        output += "  • 'game plan'\n\n"
        
        if tickers:
            output += f"\nI noticed you mentioned {', '.join(tickers)}. Try:\n"
            output += f"  • 'check {tickers[0]}'\n"
            output += f"  • 'why is {tickers[0]} moving?'\n"
        
        return output


def chat(user_input: str) -> str:
    """
    Main chat function - understands natural language
    
    Usage:
        >>> chat("what's moving after hours?")
        >>> chat("check IBRX")
        >>> chat("why is TLN down?")
        >>> chat("scan defense")
        >>> chat("show portfolio")
    """
    
    interface = NaturalLanguageInterface()
    return interface.parse_and_execute(user_input)


if __name__ == '__main__':
    # Test queries
    test_queries = [
        "what's moving after hours?",
        "check IBRX",
        "why is TLN down?",
        "scan defense sector",
        "any insider selling?",
        "show portfolio",
        "morning briefing",
        "what's my edge?",
        "IBRX momentum",
        "sector rotation"
    ]
    
    print("🐺 NATURAL LANGUAGE INTERFACE TEST\n")
    
    interface = NaturalLanguageInterface()
    
    for query in test_queries[:3]:  # Test first 3
        print(f"\n{'='*60}")
        print(f"USER: {query}")
        print(f"{'='*60}")
        response = interface.parse_and_execute(query)
        print(response)
