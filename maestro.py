"""
THE MAESTRO
===========
The conductor that orchestrates ALL instruments.

INSTRUMENTS AVAILABLE:
1. Temporal Context Engine (temporal_context.py) - MEMORY/DATA
   - Price history, our trading history, patterns, calibration
   
2. Thinking Brain (thinking_brain.py) - REASONING
   - Observations, questions, multiple perspectives, intuition
   
3. Database Schema (data/wolfpack.db) - STORAGE
   - trades, user_decisions, learned_patterns, confidence_calibration
   - brain_observations, brain_questions, brain_perspectives, brain_intuitions

The Maestro knows WHEN to use each instrument.

"An autonomous learning intelligence that learns HOW to think, not WHAT to do."

Designed by Fenrir. Built by br0kkr.
January 28, 2026
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Import ALL instruments
from temporal_context import TemporalContextEngine, get_temporal_context, format_context_for_fenrir
from thinking_brain import ThinkingBrain, observe_market, ask, analyze_ticker, get_feel


class Maestro:
    """
    The Maestro - conducts all instruments together.
    
    Not a trading bot. Not a rule engine.
    An autonomous learning intelligence.
    """
    
    def __init__(self, db_path: str = 'data/wolfpack.db'):
        self.db_path = db_path
        
        # Initialize all instruments
        self.memory = TemporalContextEngine(db_path)   # DATA layer
        self.thinker = ThinkingBrain(db_path)          # REASONING layer
        
        print("🎼 Maestro initialized with all instruments:")
        print("   📊 Temporal Memory - for DATA and HISTORY")
        print("   🧠 Thinking Brain - for REASONING and QUESTIONS")
    
    # =========================================================================
    # CORE: Full Analysis (uses ALL instruments)
    # =========================================================================
    
    def full_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Complete analysis using ALL instruments.
        
        1. Gets temporal context (MEMORY)
        2. Analyzes from multiple perspectives (THINKING)
        3. Checks relevant intuitions (FEEL)
        4. Generates questions (CURIOSITY)
        5. Expresses uncertainty (HONESTY)
        
        Returns a complete picture, not a simple buy/sell.
        """
        print(f"\n🎼 Maestro analyzing {ticker}...")
        print("=" * 60)
        
        result = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "instruments_used": []
        }
        
        # =====================================================================
        # INSTRUMENT 1: Temporal Memory (DATA)
        # =====================================================================
        print("\n📊 Consulting temporal memory...")
        temporal_context = self.memory.get_temporal_context(ticker)
        result["temporal_context"] = temporal_context
        result["instruments_used"].append("temporal_memory")
        
        # Extract key facts from memory
        price_history = temporal_context.get("price_history", {})
        our_history = temporal_context.get("our_history", {})
        patterns = temporal_context.get("pattern_matches", [])
        thesis = temporal_context.get("thesis_status", {})
        
        # =====================================================================
        # INSTRUMENT 2: Multi-Perspective Analysis (THINKING)
        # =====================================================================
        print("🧠 Analyzing from multiple perspectives...")
        
        # Build perspectives from temporal data
        momentum_view = self._build_momentum_view(price_history)
        thesis_view = self._build_thesis_view(thesis)
        history_view = self._build_history_view(our_history)
        
        perspectives = self.thinker.analyze_from_all_angles(
            ticker=ticker,
            momentum_view=momentum_view,
            thesis_view=thesis_view,
            risk_view=history_view,
            uncertainties=self._identify_uncertainties(temporal_context),
            what_would_change=self._identify_inflection_points(temporal_context)
        )
        
        result["perspectives"] = perspectives
        result["instruments_used"].append("thinking_brain")
        
        # =====================================================================
        # INSTRUMENT 3: Intuition Check (FEEL)
        # =====================================================================
        print("🎯 Checking relevant intuitions...")
        
        # Determine which intuition domains are relevant
        relevant_domains = self._identify_relevant_domains(ticker, temporal_context)
        intuitions = {}
        
        for domain in relevant_domains:
            feel = self.thinker.get_intuition(domain)
            if feel.get("status") != "no_intuition_yet":
                intuitions[domain] = feel
        
        result["intuitions"] = intuitions
        
        # =====================================================================
        # INSTRUMENT 4: Question Generation (CURIOSITY)
        # =====================================================================
        print("❓ Generating questions...")
        
        questions = self._generate_analysis_questions(ticker, temporal_context, perspectives)
        result["questions_to_explore"] = questions
        
        # Log these questions to the thinking brain
        for q in questions[:3]:  # Top 3
            self.thinker.ask_question(q, triggered_by=f"Analysis of {ticker}")
        
        # =====================================================================
        # INSTRUMENT 5: Uncertainty Expression (HONESTY)
        # =====================================================================
        print("⚖️ Expressing uncertainty...")
        
        uncertainty = self._express_analysis_uncertainty(
            ticker, temporal_context, perspectives, intuitions
        )
        result["uncertainty"] = uncertainty
        
        # =====================================================================
        # SYNTHESIS (Not a conclusion - a current thinking)
        # =====================================================================
        print("🎼 Synthesizing...")
        
        result["synthesis"] = self._synthesize_all(
            ticker, temporal_context, perspectives, intuitions, uncertainty
        )
        
        print("\n" + "=" * 60)
        print(f"✅ Analysis complete for {ticker}")
        
        return result
    
    # =========================================================================
    # Helper: Build views from data
    # =========================================================================
    
    def _build_momentum_view(self, price_history: Dict) -> str:
        """Build momentum perspective from price data"""
        if not price_history.get("data_available"):
            return "No price data available for momentum analysis"
        
        parts = []
        
        if price_history.get("consecutive_days"):
            days = price_history["consecutive_days"]
            direction = "green" if days > 0 else "red"
            parts.append(f"{abs(days)} consecutive {direction} days")
        
        if price_history.get("volume_trend"):
            parts.append(f"Volume {price_history['volume_trend']}")
        
        if price_history.get("cumulative_return_pct"):
            ret = price_history["cumulative_return_pct"]
            parts.append(f"{ret:+.1f}% over lookback period")
        
        return " | ".join(parts) if parts else "Insufficient data"
    
    def _build_thesis_view(self, thesis: Dict) -> str:
        """Build thesis perspective"""
        if not thesis.get("has_thesis"):
            return "No thesis defined - CAUTION (85.7% win rate WITH thesis, 0% without)"
        
        parts = [f"Thesis: {thesis.get('original_thesis', 'defined')[:40]}"]
        
        if thesis.get("thesis_type"):
            parts.append(f"Type: {thesis['thesis_type']}")
        
        if thesis.get("convergence_score"):
            parts.append(f"Convergence: {thesis['convergence_score']}/100")
        
        return " | ".join(parts)
    
    def _build_history_view(self, history: Dict) -> str:
        """Build our trading history perspective"""
        if history.get("total_trades", 0) == 0:
            return "No trading history on this ticker yet"
        
        parts = [f"{history['total_trades']} trades"]
        
        if history.get("win_rate"):
            parts.append(f"{history['win_rate']}% win rate")
        
        if history.get("avg_return"):
            parts.append(f"Avg return: {history['avg_return']:+.1f}%")
        
        if history.get("last_action"):
            parts.append(f"Last: {history['last_action']} on {history.get('last_action_date', '?')}")
        
        return " | ".join(parts)
    
    def _identify_uncertainties(self, context: Dict) -> List[str]:
        """Identify what we're uncertain about"""
        uncertainties = []
        
        price = context.get("price_history", {})
        if not price.get("data_available"):
            uncertainties.append("No price history available")
        
        history = context.get("our_history", {})
        if history.get("total_trades", 0) < 3:
            uncertainties.append(f"Limited trading history ({history.get('total_trades', 0)} trades)")
        
        thesis = context.get("thesis_status", {})
        if not thesis.get("has_thesis"):
            uncertainties.append("No defined thesis")
        
        patterns = context.get("pattern_matches", [])
        if not patterns:
            uncertainties.append("No pattern matches found")
        
        calibration = context.get("calibration", {})
        if not calibration.get("calibration_available"):
            uncertainties.append("No calibration data yet")
        
        return uncertainties
    
    def _identify_inflection_points(self, context: Dict) -> Dict[str, List[str]]:
        """What would change our view?"""
        return {
            "more_bullish": [
                "Volume confirmation of move",
                "Break above key resistance",
                "Positive catalyst news"
            ],
            "more_bearish": [
                "Thesis breaks",
                "Volume spike on selling",
                "Sector rotation out"
            ]
        }
    
    def _identify_relevant_domains(self, ticker: str, context: Dict) -> List[str]:
        """Which intuition domains are relevant to this analysis?"""
        domains = []
        
        thesis = context.get("thesis_status", {})
        if thesis.get("thesis_type") == "thesis":
            domains.append("thesis_trades")
        elif thesis.get("thesis_type") == "momentum":
            domains.append("momentum_trades")
        
        # Add sector-specific domains
        # (In real implementation, would look up ticker's sector)
        domains.append("runners")
        domains.append("dip_recovery")
        
        return domains
    
    def _generate_analysis_questions(self, ticker: str, context: Dict, perspectives: Dict) -> List[str]:
        """Generate questions this analysis raises"""
        questions = []
        
        # Always ask the meta question
        questions.append(f"What am I not seeing about {ticker}?")
        
        # Context-specific questions
        history = context.get("our_history", {})
        if history.get("total_trades", 0) > 0:
            questions.append(f"What worked and what didn't on previous {ticker} trades?")
        
        if perspectives.get("current_lean") == "interested":
            questions.append(f"What would need to happen for me to ACT on {ticker}?")
        
        if context.get("thesis_status", {}).get("has_thesis"):
            questions.append(f"Is the original thesis for {ticker} still valid?")
        
        questions.append("Am I seeing what I want to see, or what's actually there?")
        
        return questions
    
    def _express_analysis_uncertainty(self, ticker: str, context: Dict, 
                                     perspectives: Dict, intuitions: Dict) -> Dict:
        """Express what we're uncertain about"""
        
        # Calculate base confidence from available data
        confidence = 50  # Start neutral
        
        # Adjust based on data availability
        if context.get("price_history", {}).get("data_available"):
            confidence += 10
        
        history = context.get("our_history", {})
        if history.get("win_rate"):
            confidence += 10
        
        if context.get("thesis_status", {}).get("has_thesis"):
            confidence += 15
        
        if intuitions:
            confidence += 5
        
        # Cap at reasonable level - we're never certain
        confidence = min(75, confidence)
        
        return {
            "confidence": confidence,
            "confidence_note": "This is how much data supports analysis, NOT prediction certainty",
            "what_im_unsure_about": self._identify_uncertainties(context),
            "honest_assessment": f"I have {'moderate' if confidence > 60 else 'limited'} data on {ticker}. This analysis is my current THINKING, not a prediction."
        }
    
    def _synthesize_all(self, ticker: str, context: Dict, perspectives: Dict,
                       intuitions: Dict, uncertainty: Dict) -> Dict:
        """
        Synthesize all instruments into current thinking.
        NOT a conclusion - a synthesis.
        """
        return {
            "ticker": ticker,
            
            "current_thinking": (
                f"Analyzing {ticker} from multiple angles. "
                f"Confidence in analysis: {uncertainty['confidence']}%. "
                f"Current lean: {perspectives.get('current_lean', 'watching')}."
            ),
            
            "key_observations": [
                f"Temporal: {context.get('price_history', {}).get('cumulative_return_pct', 'N/A')}% over lookback",
                f"History: {context.get('our_history', {}).get('total_trades', 0)} trades, {context.get('our_history', {}).get('win_rate', 'N/A')}% win rate",
                f"Thesis: {'Defined' if context.get('thesis_status', {}).get('has_thesis') else 'NOT DEFINED - CAUTION'}"
            ],
            
            "perspectives_held": perspectives.get("perspectives", {}),
            
            "questions_im_sitting_with": [
                f"What am I not seeing about {ticker}?",
                "Am I being curious or confirming what I want to believe?"
            ],
            
            "what_would_change_my_view": {
                "more_bullish": ["Volume confirmation", "Thesis catalyst"],
                "more_bearish": ["Thesis breaks", "Sector rotation"]
            },
            
            "meta_note": (
                "This is THINKING, not knowing. "
                "I'm holding these observations loosely. "
                "The market will tell me if I'm wrong."
            )
        }
    
    # =========================================================================
    # OBSERVATION: Log what we see (uses Thinking Brain)
    # =========================================================================
    
    def observe(self, what_happened: str, **kwargs) -> int:
        """
        Log an observation. The Maestro WATCHES everything.
        Delegates to Thinking Brain.
        """
        return self.thinker.observe(what_happened, **kwargs)
    
    # =========================================================================
    # DECISION LOGGING: Record our decisions (uses Temporal Context)
    # =========================================================================
    
    def log_decision(self, ticker: str, action: str, price: float,
                    reasoning: str, thesis_type: str, **kwargs) -> int:
        """
        Log a trading decision. 
        Delegates to Temporal Context Engine.
        """
        return self.memory.log_decision(
            ticker=ticker,
            action=action,
            price=price,
            reasoning=reasoning,
            thesis_type=thesis_type,
            **kwargs
        )
    
    # =========================================================================
    # OUTCOME ANALYSIS: Analyze completed trades (uses both)
    # =========================================================================
    
    def analyze_outcome(self, trade_id: int, 
                       signal_correct: bool,
                       timing_correct: bool,
                       execution_correct: bool,
                       allocation_correct: bool,
                       outcome: str,
                       lessons: str = None) -> bool:
        """
        Analyze a completed trade outcome.
        Uses Temporal Context for data update.
        Uses Thinking Brain for observation/learning.
        """
        # Update the data
        self.memory.analyze_trade_outcome(
            trade_id, signal_correct, timing_correct,
            execution_correct, allocation_correct, outcome, lessons
        )
        
        # Log as observation for thinking
        self.thinker.observe(
            what_happened=f"Trade {trade_id} completed: {outcome}",
            observation_type="trade_outcome",
            context={
                "signal_correct": signal_correct,
                "timing_correct": timing_correct,
                "execution_correct": execution_correct,
                "allocation_correct": allocation_correct,
                "lessons": lessons
            },
            we_participated=True,
            our_result=outcome
        )
        
        # Build intuition based on outcome
        domain = "trades"  # Could be more specific based on trade type
        self.thinker.build_intuition(
            domain=domain,
            observation=f"Trade {trade_id}: {outcome}",
            was_positive=(outcome == "win"),
            factors_noticed=[
                f"signal_{'correct' if signal_correct else 'wrong'}",
                f"timing_{'correct' if timing_correct else 'wrong'}"
            ]
        )
        
        return True
    
    # =========================================================================
    # OUTPUT: Format for display
    # =========================================================================
    
    def format_analysis(self, analysis: Dict) -> str:
        """Format a full analysis for human reading"""
        lines = []
        
        lines.append("=" * 70)
        lines.append(f"🎼 MAESTRO ANALYSIS: {analysis['ticker']}")
        lines.append(f"   {analysis['timestamp']}")
        lines.append("=" * 70)
        
        # Synthesis
        synth = analysis.get("synthesis", {})
        lines.append(f"\n📌 CURRENT THINKING:")
        lines.append(f"   {synth.get('current_thinking', 'N/A')}")
        
        # Key observations
        lines.append(f"\n📊 KEY OBSERVATIONS:")
        for obs in synth.get("key_observations", []):
            lines.append(f"   • {obs}")
        
        # Perspectives
        perspectives = analysis.get("perspectives", {}).get("perspectives", {})
        if perspectives:
            lines.append(f"\n🔍 PERSPECTIVES HELD:")
            for view_name, view_text in perspectives.items():
                if view_text:
                    lines.append(f"   {view_name}: {view_text}")
        
        # Uncertainties
        uncertainty = analysis.get("uncertainty", {})
        lines.append(f"\n⚖️ UNCERTAINTY:")
        lines.append(f"   Confidence: {uncertainty.get('confidence', 'N/A')}%")
        lines.append(f"   ({uncertainty.get('confidence_note', '')})")
        
        for u in uncertainty.get("what_im_unsure_about", [])[:3]:
            lines.append(f"   • {u}")
        
        # Questions
        questions = analysis.get("questions_to_explore", [])
        if questions:
            lines.append(f"\n❓ QUESTIONS TO EXPLORE:")
            for q in questions[:3]:
                lines.append(f"   • {q}")
        
        # Meta note
        lines.append(f"\n" + "-" * 70)
        lines.append(f"💭 {synth.get('meta_note', 'This is thinking, not knowing.')}")
        lines.append("-" * 70)
        
        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def analyze(ticker: str) -> Dict:
    """Quick full analysis"""
    maestro = Maestro()
    return maestro.full_analysis(ticker)

def watch(what_happened: str, **kwargs) -> int:
    """Quick observation"""
    maestro = Maestro()
    return maestro.observe(what_happened, **kwargs)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("THE MAESTRO - ALL INSTRUMENTS TOGETHER")
    print("=" * 70)
    
    maestro = Maestro()
    
    # Full analysis of a ticker
    analysis = maestro.full_analysis("MU")
    
    # Format for display
    print(maestro.format_analysis(analysis))
    
    # Show that observation still works
    print("\n\n" + "=" * 70)
    print("OBSERVING THE MARKET (Thinking Brain)")
    print("=" * 70)
    
    maestro.observe(
        what_happened="MRNO ran +45% today - didn't own it",
        observation_type="runner",
        ticker="MRNO",
        context={
            "volume": "4x average",
            "sector": "biotech",
            "we_considered": True,
            "why_passed": "Hit +20% target, exited earlier"
        },
        we_participated=True,
        our_result="Exited at +20%, watched it run to +45%"
    )
    
    print("\n✅ All instruments working together")
    print("   The Maestro conducts. The instruments play. The music emerges.")
