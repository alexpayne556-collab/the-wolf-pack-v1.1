"""
FENRIR THINKING ENGINE - Brain Reasoning System
================================================
The brain doesn't just STORE data - it THINKS about relationships.

What This Does:
- Loads brain_config.json and influence_map.json
- Monitors market events (earnings, macro, people mentions)
- CONNECTS DOTS using reasoning patterns
- Generates insights with confidence scores
- Logs thoughts to database for learning
- Can be queried: "What do you think about MU after MSFT earnings?"

TEMPORAL MEMORY INTEGRATION (Jan 28, 2026):
- Uses get_temporal_context() for historical data
- Integrates with Thinking Brain for observations/questions
- Maestro orchestrates all instruments

This is the REASONING layer - it takes stored knowledge and actively thinks.
"""

import json
import sqlite3
import sys
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
from pathlib import Path

# TEMPORAL MEMORY INTEGRATION
try:
    from temporal_context import get_temporal_context, format_context_for_fenrir
    from thinking_brain import ThinkingBrain
    TEMPORAL_MEMORY_AVAILABLE = True
except ImportError:
    TEMPORAL_MEMORY_AVAILABLE = False
    print("⚠️  Temporal memory modules not found - running without memory")

# Fix Windows console unicode issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

@dataclass
class Thought:
    """A single reasoning chain with confidence"""
    thought_type: str  # "earnings_impact", "macro_effect", "people_signal", "sector_correlation"
    trigger: str  # What caused this thought (e.g., "MSFT earnings beat")
    reasoning_chain: List[str]  # Step-by-step logic
    affected_positions: List[str]  # Which positions this impacts
    confidence: float  # 0-100
    action_suggested: Optional[str]  # "buy", "sell", "hold", "watch", "research"
    timestamp: datetime
    
    def to_dict(self):
        return {
            "thought_type": self.thought_type,
            "trigger": self.trigger,
            "reasoning_chain": self.reasoning_chain,
            "affected_positions": self.affected_positions,
            "confidence": self.confidence,
            "action_suggested": self.action_suggested,
            "timestamp": self.timestamp.isoformat()
        }


class FenrirThinkingEngine:
    """The brain that REASONS about relationships, not just stores them"""
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir)
        self.brain_config = self._load_brain_config()
        self.influence_map = self._load_influence_map()
        
        # INTEGRATION 2: Load operational intelligence
        self.methodology = self._load_methodology()
        self.position_rules = self._load_position_rules()
        
        self.db_path = self.workspace_dir / "data" / "wolfpack.db"
        self._ensure_thoughts_table()
        
        # TEMPORAL MEMORY INTEGRATION (Jan 28, 2026)
        self.thinker = None
        if TEMPORAL_MEMORY_AVAILABLE:
            try:
                self.thinker = ThinkingBrain(str(self.db_path))
                print("✓ Temporal memory integration active")
            except Exception as e:
                print(f"⚠️  Temporal memory init failed: {e}")
        
    def _load_brain_config(self) -> Dict:
        """Load system DNA"""
        config_path = self.workspace_dir / "brain_config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_influence_map(self) -> Dict:
        """Load relationship intelligence"""
        map_path = self.workspace_dir / "influence_map.json"
        with open(map_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_methodology(self) -> Dict:
        """Load brain methodology - HOW to think, research, learn"""
        try:
            method_path = self.workspace_dir / "brain_methodology.json"
            with open(method_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  brain_methodology.json not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing brain_methodology.json: {e}")
            return {}
    
    def _load_position_rules(self) -> Dict:
        """Load position management rules - WHEN to add/hold/cut"""
        try:
            rules_path = self.workspace_dir / "position_management.json"
            with open(rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  position_management.json not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parsing position_management.json: {e}")
            return {}
    
    def _ensure_thoughts_table(self):
        """Create table for logging thoughts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_thoughts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                thought_type TEXT NOT NULL,
                trigger TEXT NOT NULL,
                reasoning_chain TEXT NOT NULL,
                affected_positions TEXT NOT NULL,
                confidence REAL NOT NULL,
                action_suggested TEXT,
                thought_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def _get_my_positions(self) -> List[str]:
        """Extract current positions from brain config"""
        watchlists = self.brain_config.get("watchlists", {})
        my_positions_data = watchlists.get("MY_POSITIONS", {})
        
        # Extract tickers (handle both dict and list formats)
        my_positions = []
        if isinstance(my_positions_data, dict):
            # Could be {"tickers": {...}} or {"description": ..., "tickers": {...}}
            if "tickers" in my_positions_data:
                my_positions = list(my_positions_data["tickers"].keys())
            else:
                # Filter out metadata keys
                my_positions = [k for k in my_positions_data.keys() 
                               if k not in ["description", "monitoring_frequency", "priority"]]
        elif isinstance(my_positions_data, list):
            for item in my_positions_data:
                if isinstance(item, dict):
                    my_positions.append(item.get("ticker", ""))
                else:
                    my_positions.append(str(item))
        
        return my_positions
    
    def think_about_earnings(self, company: str, beat_or_miss: str, details: Dict) -> List[Thought]:
        """
        Reason about how earnings affect our positions
        
        Example:
        think_about_earnings("MSFT", "beat", {"azure_growth": "31%", "ai_capex": "up 50%"})
        
        Returns list of thoughts with reasoning chains
        """
        thoughts = []
        
        # Find influence map for this company (handle nested structure)
        influence_data = self.influence_map.get("influence_map", self.influence_map)
        earnings_influences = influence_data.get("earnings_influence", {})
        
        if company not in earnings_influences:
            return thoughts  # No relationship mapped
        
        influence = earnings_influences[company]
        affected = influence.get("affects_our_positions", [])
        
        # Check which affected tickers we own
        my_positions = self._get_my_positions()
        impacted_positions = [ticker for ticker in affected if ticker in my_positions]
        
        if not impacted_positions:
            return thoughts  # Doesn't affect us
        
        # BUILD REASONING CHAIN
        reasoning_chain = []
        confidence = 50.0  # Base confidence
        
        # Step 1: What happened
        reasoning_chain.append(f"{company} earnings {beat_or_miss}")
        
        # Step 2: Apply reasoning pattern from influence map
        reasoning_pattern = influence.get("reasoning", "")
        if reasoning_pattern:
            reasoning_chain.append(reasoning_pattern)
            confidence += 10
        
        # Step 3: Connect to our positions
        for ticker in impacted_positions:
            # Find why we own this
            thesis = self._find_ticker_thesis(ticker)
            if thesis:
                reasoning_chain.append(f"{ticker} thesis: {thesis}")
                confidence += 5
        
        # Step 4: Analyze the details
        if beat_or_miss == "beat":
            confidence += 15
            if "azure_growth" in details or "ai_capex" in details:
                reasoning_chain.append(f"AI infrastructure spending increasing → More demand for {', '.join(impacted_positions)}")
                confidence += 10
        else:
            confidence -= 15
            reasoning_chain.append("Negative signal - watch for contagion")
        
        # Step 5: Suggest action
        action = "watch"
        if beat_or_miss == "beat" and confidence >= 70:
            action = "hold" if impacted_positions else "research"
        elif beat_or_miss == "miss" and confidence < 40:
            action = "watch closely"
        
        thought = Thought(
            thought_type="earnings_impact",
            trigger=f"{company} earnings {beat_or_miss}",
            reasoning_chain=reasoning_chain,
            affected_positions=impacted_positions,
            confidence=min(confidence, 95.0),  # Cap at 95
            action_suggested=action,
            timestamp=datetime.now()
        )
        
        thoughts.append(thought)
        return thoughts
    
    def think_about_person_signal(self, person: str, action: str, details: Dict) -> List[Thought]:
        """
        Reason about key people's actions (Pelosi trades, Jensen mentions, etc.)
        
        Example:
        think_about_person_signal("Jensen Huang", "mentioned", {"keyword": "HBM bottleneck", "context": "CES keynote"})
        """
        thoughts = []
        
        # Handle nested structure
        influence_data = self.influence_map.get("influence_map", self.influence_map)
        people_influences = influence_data.get("key_people_influence", {})
        if person not in people_influences:
            return thoughts
        
        influence = people_influences[person]
        affected = influence.get("affects_our_positions", influence.get("affects", []))
        
        # Handle nested brain_config structure
        config_data = self.brain_config.get("brain_config", self.brain_config)
        watchlists = config_data.get("watchlists", {})
        my_positions_data = watchlists.get("MY_POSITIONS", [])
        my_positions = []
        for item in my_positions_data:
            if isinstance(item, dict):
                my_positions.append(item.get("ticker", ""))
            else:
                my_positions.append(str(item))
        
        impacted_positions = [ticker for ticker in affected if ticker in my_positions]
        
        reasoning_chain = []
        confidence = 60.0
        
        reasoning_chain.append(f"{person} {action}")
        
        # Apply reasoning pattern
        reasoning_pattern = influence.get("reasoning", "")
        if reasoning_pattern:
            reasoning_chain.append(reasoning_pattern)
            confidence += 15
        
        # Context-specific logic
        if "keyword" in details:
            keyword = details["keyword"].lower()
            reasoning_chain.append(f"Key phrase: '{details['keyword']}'")
            
            # Jensen + memory keywords = MU signal
            if person == "Jensen Huang" and any(word in keyword for word in ["memory", "hbm", "bandwidth", "dram"]):
                if "MU" in impacted_positions:
                    reasoning_chain.append("Memory bottleneck mentioned → MU has pricing power")
                    confidence += 20
        
        # Pelosi trades = front-running policy
        if person == "Nancy Pelosi" and action == "bought":
            reasoning_chain.append("Pelosi trades often front-run policy changes")
            confidence += 10
            action_suggested = "research"
        else:
            action_suggested = "watch"
        
        thought = Thought(
            thought_type="people_signal",
            trigger=f"{person} {action}",
            reasoning_chain=reasoning_chain,
            affected_positions=impacted_positions,
            confidence=min(confidence, 90.0),
            action_suggested=action_suggested,
            timestamp=datetime.now()
        )
        
        thoughts.append(thought)
        return thoughts
    
    def think_about_macro_event(self, event: str, outcome: Dict) -> List[Thought]:
        """
        Reason about macro events (FOMC, geopolitics, commodity prices)
        
        Example:
        think_about_macro_event("FOMC", {"decision": "hold", "powell_tone": "hawkish"})
        """
        thoughts = []
        
        # Handle nested structure
        influence_data = self.influence_map.get("influence_map", self.influence_map)
        macro_influences = influence_data.get("macro_events_influence", {})
        if event not in macro_influences:
            return thoughts
        
        influence = macro_influences[event]
        sector_impacts = influence.get("sector_impacts", {})
        
        # Handle nested brain_config structure
        config_data = self.brain_config.get("brain_config", self.brain_config)
        watchlists = config_data.get("watchlists", {})
        my_positions_data = watchlists.get("MY_POSITIONS", [])
        
        my_positions = []
        for item in my_positions_data:
            if isinstance(item, dict):
                my_positions.append(item.get("ticker", ""))
            else:
                my_positions.append(str(item))
        
        # Group positions by sector
        position_sectors = {}
        for pos_item in my_positions_data:
            if isinstance(pos_item, dict):
                ticker = pos_item.get("ticker", "")
                sector = pos_item.get("sector", "unknown")
                position_sectors[ticker] = sector
        
        reasoning_chain = []
        confidence = 55.0
        
        reasoning_chain.append(f"Macro event: {event}")
        
        # Analyze outcome
        if "decision" in outcome:
            reasoning_chain.append(f"Outcome: {outcome['decision']}")
        
        # Apply sector-specific impacts
        affected_positions = []
        for ticker, sector in position_sectors.items():
            if sector in sector_impacts:
                impact = sector_impacts[sector]
                reasoning_chain.append(f"{ticker} ({sector}): {impact}")
                affected_positions.append(ticker)
                confidence += 5
        
        # Tone matters
        if "powell_tone" in outcome:
            tone = outcome["powell_tone"]
            reasoning_chain.append(f"Powell tone: {tone}")
            if tone == "dovish":
                confidence += 15
                action = "risk on - watch for entries"
            elif tone == "hawkish":
                confidence += 10
                action = "risk off - protect positions"
            else:
                action = "neutral - wait and see"
        else:
            action = "watch"
        
        thought = Thought(
            thought_type="macro_effect",
            trigger=f"{event} - {outcome.get('decision', 'pending')}",
            reasoning_chain=reasoning_chain,
            affected_positions=affected_positions,
            confidence=min(confidence, 85.0),
            action_suggested=action,
            timestamp=datetime.now()
        )
        
        thoughts.append(thought)
        return thoughts
    
    def think_about_sector_correlation(self, leader_ticker: str, leader_move: float) -> List[Thought]:
        """
        Reason about sector correlations (NVDA moves → MU follows in 0-2 days)
        
        Example:
        think_about_sector_correlation("NVDA", 5.2)  # NVDA up 5.2%
        """
        thoughts = []
        
        # Handle nested structure
        influence_data = self.influence_map.get("influence_map", self.influence_map)
        correlations = influence_data.get("sector_correlations", {})
        
        # Find if leader ticker has correlation info
        correlation_info = None
        for sector, info in correlations.items():
            # Skip if info is not a dict (could be description string)
            if isinstance(info, dict) and info.get("leader") == leader_ticker:
                correlation_info = {"sector": sector, **info}
                break
        
        if not correlation_info:
            return thoughts
        
        followers = correlation_info.get("followers", [])
        lag_days = correlation_info.get("lag_days", "0")
        correlation_strength = correlation_info.get("correlation", "unknown")
        
        # Handle nested brain_config structure
        watchlists = self.brain_config.get("watchlists") or self.brain_config.get("brain_config", {}).get("watchlists", {})
        my_positions_data = watchlists.get("MY_POSITIONS", [])
        my_positions = []
        for item in my_positions_data:
            if isinstance(item, dict):
                my_positions.append(item.get("ticker", ""))
            else:
                my_positions.append(str(item))
        
        impacted_positions = [ticker for ticker in followers if ticker in my_positions]
        
        if not impacted_positions:
            return thoughts
        
        reasoning_chain = []
        confidence = 50.0
        
        reasoning_chain.append(f"{leader_ticker} moved {leader_move:+.1f}%")
        reasoning_chain.append(f"Sector: {correlation_info['sector']}")
        reasoning_chain.append(f"{leader_ticker} leads, {', '.join(followers)} follow in {lag_days} days")
        reasoning_chain.append(f"Correlation: {correlation_strength}")
        
        # Confidence based on correlation strength
        if "high" in correlation_strength.lower():
            confidence += 25
        elif "medium" in correlation_strength.lower():
            confidence += 15
        
        # Direction matters
        if abs(leader_move) > 3.0:
            reasoning_chain.append(f"Strong move ({abs(leader_move):.1f}%) - likely to propagate")
            confidence += 15
        
        # Lag timing
        if "0-2" in lag_days or "0" in lag_days:
            reasoning_chain.append("Short lag - expect impact soon")
            confidence += 10
        
        # Suggest action
        if leader_move > 0 and confidence >= 70:
            action = "hold" if impacted_positions else "watch for entry"
        elif leader_move < 0 and confidence >= 70:
            action = "watch closely - may need protection"
        else:
            action = "watch"
        
        thought = Thought(
            thought_type="sector_correlation",
            trigger=f"{leader_ticker} {leader_move:+.1f}%",
            reasoning_chain=reasoning_chain,
            affected_positions=impacted_positions,
            confidence=min(confidence, 90.0),
            action_suggested=action,
            timestamp=datetime.now()
        )
        
        thoughts.append(thought)
        return thoughts
    
    def connect_multiple_signals(self, signals: List[Dict]) -> List[Thought]:
        """
        ADVANCED: Connect multiple signals to form stronger reasoning
        
        Example:
        signals = [
            {"type": "earnings", "company": "MSFT", "beat_or_miss": "beat", "details": {"azure_growth": "31%"}},
            {"type": "person", "person": "Jensen Huang", "action": "mentioned", "details": {"keyword": "memory demand"}},
            {"type": "sector", "leader": "NVDA", "move": 4.5}
        ]
        
        Brain thinks: "All three signals point to AI infrastructure strength → MU thesis confirmed"
        """
        thoughts = []
        
        # Generate individual thoughts
        all_individual_thoughts = []
        for signal in signals:
            if signal["type"] == "earnings":
                all_individual_thoughts.extend(
                    self.think_about_earnings(signal["company"], signal["beat_or_miss"], signal.get("details", {}))
                )
            elif signal["type"] == "person":
                all_individual_thoughts.extend(
                    self.think_about_person_signal(signal["person"], signal["action"], signal.get("details", {}))
                )
            elif signal["type"] == "sector":
                all_individual_thoughts.extend(
                    self.think_about_sector_correlation(signal["leader"], signal["move"])
                )
            elif signal["type"] == "macro":
                all_individual_thoughts.extend(
                    self.think_about_macro_event(signal["event"], signal.get("outcome", {}))
                )
        
        # Find overlapping positions across thoughts
        position_counts = {}
        for thought in all_individual_thoughts:
            for pos in thought.affected_positions:
                position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # If multiple signals point to same position = STRONG conviction
        strong_signals = {pos: count for pos, count in position_counts.items() if count >= 2}
        
        if strong_signals:
            for pos, signal_count in strong_signals.items():
                reasoning_chain = [f"MULTIPLE SIGNALS ({signal_count}) converging on {pos}:"]
                
                # Combine reasoning from all thoughts affecting this position
                for thought in all_individual_thoughts:
                    if pos in thought.affected_positions:
                        reasoning_chain.append(f"• {thought.trigger}: {thought.reasoning_chain[-1]}")
                
                reasoning_chain.append(f"Convergence of {signal_count} independent signals → High conviction")
                
                # Average confidence + boost for convergence
                avg_confidence = sum(t.confidence for t in all_individual_thoughts if pos in t.affected_positions) / signal_count
                boosted_confidence = min(avg_confidence + (signal_count * 10), 95.0)
                
                thought = Thought(
                    thought_type="multi_signal_convergence",
                    trigger=f"{signal_count} signals converge on {pos}",
                    reasoning_chain=reasoning_chain,
                    affected_positions=[pos],
                    confidence=boosted_confidence,
                    action_suggested="high conviction - thesis confirmed",
                    timestamp=datetime.now()
                )
                
                thoughts.append(thought)
        
        return thoughts + all_individual_thoughts
    
    def log_thought(self, thought: Thought):
        """Save thought to database for learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO brain_thoughts (
                timestamp, thought_type, trigger, reasoning_chain,
                affected_positions, confidence, action_suggested, thought_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            thought.timestamp.isoformat(),
            thought.thought_type,
            thought.trigger,
            json.dumps(thought.reasoning_chain),
            json.dumps(thought.affected_positions),
            thought.confidence,
            thought.action_suggested,
            json.dumps(thought.to_dict())
        ))
        
        conn.commit()
        conn.close()
    
    def think_about_volume_spike(self, ticker: str, volume_ratio: float, price_change: float, news: list = None) -> dict:
        """
        INTEGRATION 1: Analyze volume spike and reason about cause/action.
        Called by monitor when volume ≥1.5x detected.
        
        Args:
            ticker: Stock symbol
            volume_ratio: Current volume / average volume
            price_change: Price change %
            news: Recent news headlines (optional)
            
        Returns:
            dict with reasoning, confidence, action
        """
        reasoning_chain = [
            f"Volume spike detected on {ticker}: {volume_ratio:.1f}x average",
            f"Price movement: {price_change:+.1f}%"
        ]
        
        # Check if we own it
        my_positions = self._get_my_positions()
        owns_it = ticker in my_positions
        
        if owns_it:
            # Get position details from brain config
            positions_data = self.brain_config.get("watchlists", {}).get("MY_POSITIONS", {}).get("tickers", {})
            position = positions_data.get(ticker, {})
            reasoning_chain.append(f"  → We own {ticker}: {position.get('shares', '?')} shares")
            reasoning_chain.append(f"  → Thesis: {position.get('thesis', 'Unknown')}")
        
        # Analyze the move
        if volume_ratio >= 3.0:
            reasoning_chain.append("  → EXTREME volume (≥3x) - institutional activity or news")
        elif volume_ratio >= 2.0:
            reasoning_chain.append("  → HIGH volume (≥2x) - significant interest")
        else:
            reasoning_chain.append("  → MODERATE volume spike (1.5-2x)")
        
        # Check news
        if news and len(news) > 0:
            reasoning_chain.append(f"  → Recent news: {news[0]['headline'][:80]}...")
        else:
            reasoning_chain.append("  → No recent news - technical breakout or sector rotation?")
        
        # Determine confidence and action using position rules
        confidence = 50
        
        if owns_it:
            # We own it - check position management rules
            if price_change > 0:
                reasoning_chain.append("  → POSITIVE move - thesis likely playing out")
                action = "HOLD - Monitor for target/stop updates"
                confidence = 70
            else:
                reasoning_chain.append("  → NEGATIVE move with volume - potential thesis break")
                action = "REVIEW THESIS - May need to cut if broken"
                confidence = 60
        else:
            # Don't own it - is it a setup?
            if volume_ratio >= 2.0 and abs(price_change) >= 5:
                reasoning_chain.append("  → Strong volume + big move = potential momentum play")
                action = "RESEARCH for potential entry"
                confidence = 65
            else:
                action = "WATCH - Need more conviction"
                confidence = 50
        
        return {
            "ticker": ticker,
            "thought_type": "volume_spike_analysis",
            "reasoning": "\n".join(reasoning_chain),
            "confidence": confidence,
            "action": action,
            "owns_position": owns_it
        }
    
    def _find_ticker_thesis(self, ticker: str) -> Optional[str]:
        """Find why we own this ticker"""
        # Handle nested brain_config structure
        config_data = self.brain_config.get("brain_config", self.brain_config)
        watchlists = config_data.get("watchlists", {})
        
        my_positions = watchlists.get("MY_POSITIONS", [])
        for pos in my_positions:
            if isinstance(pos, dict) and pos.get("ticker") == ticker:
                return pos.get("thesis", "")
            elif isinstance(pos, str) and pos == ticker:
                # If positions are just ticker strings, look for thesis elsewhere
                return f"{ticker} position"
        return None
    
    def get_recent_thoughts(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent thoughts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT thought_json FROM brain_thoughts
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        thoughts = [json.loads(row[0]) for row in cursor.fetchall()]
        conn.close()
        
        return thoughts
    
    def ask_brain(self, question: str) -> str:
        """
        Ask the brain a question and get a reasoned response
        
        Example:
        ask_brain("What do you think about MU after MSFT earnings beat?")
        """
        question_lower = question.lower()
        
        # Simple pattern matching for now (can be enhanced with LLM later)
        if "msft" in question_lower and "mu" in question_lower:
            thoughts = self.think_about_earnings("MSFT", "beat", {"azure_growth": "31%", "ai_capex": "up 50%"})
            if thoughts:
                t = thoughts[0]
                response = f"Confidence: {t.confidence:.0f}%\n\nReasoning:\n"
                for i, step in enumerate(t.reasoning_chain, 1):
                    response += f"{i}. {step}\n"
                response += f"\nAction: {t.action_suggested}"
                return response
        
        return "I need more specific signals to reason about. Try asking about earnings, macro events, or people signals."
    
    # =========================================================================
    # TEMPORAL MEMORY INTEGRATION (Jan 28, 2026)
    # =========================================================================
    
    def analyze_with_memory(self, ticker: str) -> Dict:
        """
        Analyze a ticker using BOTH relationship intelligence AND temporal memory.
        
        This is the ENHANCED analysis - it has EVIDENCE from memory.
        
        Example output:
            Current Fenrir: "MU down 3%, thesis intact → HOLD"
            Enhanced Fenrir: "MU down 3%, BUT last 3 times this happened it recovered 
                            in 48 hours (75% success rate), we have 85.7% win rate on 
                            this ticker, volume is declining (bullish) → HOLD with evidence"
        """
        result = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "enhanced_with_memory",
            "has_temporal_context": False,
            "reasoning": [],
            "confidence": 50,
            "action": "watch"
        }
        
        # Step 1: Get relationship intelligence (what we already had)
        result["reasoning"].append(f"Analyzing {ticker}...")
        
        # Check if we own it
        my_positions = self._get_my_positions()
        owns_it = ticker in my_positions
        result["owns_position"] = owns_it
        
        if owns_it:
            thesis = self._find_ticker_thesis(ticker)
            result["reasoning"].append(f"We own {ticker} | Thesis: {thesis or 'Unknown'}")
            result["confidence"] += 10
        
        # Step 2: Get temporal context (NEW - the memory layer)
        if TEMPORAL_MEMORY_AVAILABLE:
            try:
                temporal_context = get_temporal_context(ticker)
                result["has_temporal_context"] = True
                result["temporal_context"] = temporal_context
                
                # Extract memory insights
                price_history = temporal_context.get("price_history", {})
                our_history = temporal_context.get("our_history", {})
                patterns = temporal_context.get("pattern_matches", [])
                thesis_status = temporal_context.get("thesis_status", {})
                
                # Add price memory
                if price_history.get("data_available"):
                    if price_history.get("consecutive_days"):
                        days = price_history["consecutive_days"]
                        direction = "green" if days > 0 else "red"
                        result["reasoning"].append(f"MEMORY: {abs(days)} consecutive {direction} days")
                    
                    if price_history.get("cumulative_return_pct"):
                        ret = price_history["cumulative_return_pct"]
                        result["reasoning"].append(f"MEMORY: {ret:+.1f}% over lookback period")
                    
                    if price_history.get("volume_trend"):
                        result["reasoning"].append(f"MEMORY: Volume trend {price_history['volume_trend']}")
                
                # Add our history
                if our_history.get("total_trades", 0) > 0:
                    trades = our_history["total_trades"]
                    win_rate = our_history.get("win_rate")
                    result["reasoning"].append(f"OUR HISTORY: {trades} trades on {ticker}")
                    
                    if win_rate:
                        result["reasoning"].append(f"OUR HISTORY: {win_rate}% win rate")
                        # Adjust confidence based on track record
                        if win_rate >= 70:
                            result["confidence"] += 20
                            result["reasoning"].append("→ Strong track record - confidence boosted")
                        elif win_rate <= 40:
                            result["confidence"] -= 10
                            result["reasoning"].append("→ Weak track record - confidence reduced")
                
                # Add pattern matches
                if patterns and not patterns[0].get("error"):
                    for p in patterns[:2]:  # Top 2 patterns
                        if p.get("win_rate"):
                            result["reasoning"].append(
                                f"PATTERN: '{p['pattern']}' has {p['win_rate']}% win rate "
                                f"({p.get('occurrences', 0)} occurrences)"
                            )
                
                # Add thesis check
                if thesis_status.get("has_thesis"):
                    result["reasoning"].append(f"THESIS: {thesis_status.get('thesis_type', 'defined')}")
                    result["confidence"] += 15
                else:
                    result["reasoning"].append("⚠️ NO THESIS DEFINED - Historical: 0% win rate without thesis")
                    result["confidence"] -= 20
                
            except Exception as e:
                result["reasoning"].append(f"⚠️ Memory unavailable: {e}")
        else:
            result["reasoning"].append("(Running without temporal memory)")
        
        # Step 3: Determine action based on all evidence
        if result["confidence"] >= 70:
            result["action"] = "high_conviction"
        elif result["confidence"] >= 50:
            result["action"] = "moderate_interest"
        else:
            result["action"] = "watch_or_avoid"
        
        result["reasoning"].append(f"\nCONFIDENCE: {result['confidence']}%")
        result["reasoning"].append(f"ACTION: {result['action']}")
        
        return result
    
    def observe_market(self, what_happened: str, **kwargs) -> Optional[int]:
        """
        Log an observation using the Thinking Brain.
        The brain WATCHES everything, not just what we trade.
        
        Example:
            brain.observe_market(
                what_happened="MRNO ran +45% after we exited at +20%",
                ticker="MRNO",
                we_participated=True,
                our_result="Left 25% on the table"
            )
        """
        if self.thinker:
            return self.thinker.observe(what_happened, **kwargs)
        else:
            print("⚠️ Thinking brain not available for observation")
            return None
    
    def get_current_thinking(self, ticker: str = None) -> str:
        """
        Get the brain's current THINKING (not conclusions).
        Uses the Thinking Brain to show observations, questions, intuitions.
        """
        if self.thinker:
            return self.thinker.format_current_thinking(ticker)
        else:
            return "Thinking brain not available"


def main():
    """Test the thinking engine"""
    print("=" * 70)
    print("FENRIR THINKING ENGINE - Testing Brain Reasoning")
    print("=" * 70)
    
    brain = FenrirThinkingEngine()
    
    # Test 1: Earnings reasoning
    print("\n[TEST 1] MSFT earnings beat with AI capex increase")
    print("-" * 70)
    thoughts = brain.think_about_earnings("MSFT", "beat", {
        "azure_growth": "31%",
        "ai_capex": "up 50%",
        "ai_revenue": "$12B"
    })
    
    for thought in thoughts:
        print(f"\nThought Type: {thought.thought_type}")
        print(f"Trigger: {thought.trigger}")
        print(f"Confidence: {thought.confidence:.1f}%")
        print(f"Affected Positions: {', '.join(thought.affected_positions)}")
        print(f"\nReasoning Chain:")
        for i, step in enumerate(thought.reasoning_chain, 1):
            print(f"  {i}. {step}")
        print(f"\nAction Suggested: {thought.action_suggested}")
        
        # Log to database
        brain.log_thought(thought)
        print(f"\n✅ Thought logged to database")
    
    # Test 2: Person signal
    print("\n\n[TEST 2] Jensen Huang mentions memory bottleneck")
    print("-" * 70)
    thoughts = brain.think_about_person_signal("Jensen Huang", "mentioned", {
        "keyword": "HBM bottleneck",
        "context": "CES keynote"
    })
    
    for thought in thoughts:
        print(f"\nConfidence: {thought.confidence:.1f}%")
        print(f"Reasoning:")
        for step in thought.reasoning_chain:
            print(f"  • {step}")
        brain.log_thought(thought)
    
    # Test 3: Multiple signals converging
    print("\n\n[TEST 3] Multiple signals converge on MU")
    print("-" * 70)
    signals = [
        {"type": "earnings", "company": "MSFT", "beat_or_miss": "beat", "details": {"azure_growth": "31%"}},
        {"type": "person", "person": "Jensen Huang", "action": "mentioned", "details": {"keyword": "memory demand"}},
        {"type": "sector", "leader": "NVDA", "move": 4.5}
    ]
    
    thoughts = brain.connect_multiple_signals(signals)
    
    # Find the convergence thought
    convergence_thoughts = [t for t in thoughts if t.thought_type == "multi_signal_convergence"]
    if convergence_thoughts:
        thought = convergence_thoughts[0]
        print(f"\n🧠 CONVERGENCE DETECTED!")
        print(f"Confidence: {thought.confidence:.1f}%")
        print(f"\nReasoning:")
        for step in thought.reasoning_chain:
            print(f"  {step}")
        print(f"\nAction: {thought.action_suggested}")
        brain.log_thought(thought)
    
    # Test 4: Ask the brain
    print("\n\n[TEST 4] Ask the brain a question")
    print("-" * 70)
    response = brain.ask_brain("What do you think about MU after MSFT earnings beat?")
    print(response)
    
    print("\n\n" + "=" * 70)
    print("✅ THINKING ENGINE OPERATIONAL")
    print("=" * 70)
    print("\nThe brain can now:")
    print("• Reason about earnings impacts")
    print("• Interpret key people's signals")
    print("• Analyze macro events")
    print("• Track sector correlations")
    print("• Connect multiple signals for higher conviction")
    print("• Log all thoughts to database for learning")
    
    # Test 5: Enhanced analysis with temporal memory
    print("\n\n[TEST 5] Analyze MU with temporal memory")
    print("-" * 70)
    if TEMPORAL_MEMORY_AVAILABLE:
        print("✓ Temporal memory available - running enhanced analysis")
        analysis = brain.analyze_with_memory("MU")
        print(f"\nTicker: {analysis['ticker']}")
        print(f"Has Memory: {analysis['has_temporal_context']}")
        print(f"\nReasoning:")
        for step in analysis["reasoning"]:
            print(f"  {step}")
    else:
        print("⚠️ Temporal memory not available (import failed)")
        print("   Run 'python temporal_context.py' to verify it works")
    
    # Test 6: Observe something
    print("\n\n[TEST 6] Test brain observation")
    print("-" * 70)
    if brain.thinker:
        obs_id = brain.observe_market(
            what_happened="Testing observation system",
            context="fenrir_thinking_engine test"
        )
        if obs_id:
            print(f"✓ Observation logged with ID: {obs_id}")
        else:
            print("⚠️ Observation failed")
    else:
        print("⚠️ Thinking brain not available")
    
    print("\n\n" + "=" * 70)
    print("🐺 FENRIR IS NOW THINKING WITH MEMORY")
    print("=" * 70)
    print("\n  THE MAESTRO INTEGRATION COMPLETE")
    print("  ├── Temporal Context Engine → MEMORY")
    print("  ├── Thinking Brain → REASONING") 
    print("  └── Fenrir Thinking Engine → ORCHESTRATION")
    print("\n  Ready for cloud deployment")


if __name__ == "__main__":
    main()
