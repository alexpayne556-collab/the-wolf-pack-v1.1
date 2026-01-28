"""
THE THINKING BRAIN
==================
"The brain doesn't KNOW things. It THINKS about things."

This is NOT a rule engine.
This is NOT a pattern matcher.
This is a THINKER.

It watches EVERYTHING - not just what we own.
It asks QUESTIONS - not makes conclusions.
It builds INTUITION - through accumulated observation.
It notices WITHOUT JUDGING - no guilt, no "should have."
It holds MULTIPLE PERSPECTIVES - simultaneously.
It studies EXCEPTIONS - not just patterns.
It knows WHAT IT DOESN'T KNOW - uncertainty is honesty.

Designed by Fenrir. Built by br0kkr.
January 28, 2026
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

DB_PATH = 'data/wolfpack.db'


class ThinkingBrain:
    """
    A brain that THINKS, not RULES.
    
    Rules are dead. Thinking is alive.
    Rules break when the market changes. Thinking adapts.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _ensure_tables(self):
        """Create thinking brain tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # OBSERVATIONS - What the brain notices (not just our trades)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                date TEXT NOT NULL,
                
                -- What was observed
                observation_type TEXT NOT NULL,  -- 'market_move', 'runner', 'sector_rotation', 'correlation', 'exception'
                ticker TEXT,                      -- NULL for market-wide observations
                
                -- The raw observation
                what_happened TEXT NOT NULL,      -- "MRNO ran +45% after we exited at +20%"
                
                -- Context gathered
                context_data TEXT,                -- JSON: volume, float, sector, similar_names, etc.
                
                -- Initial questions this raises
                questions_raised TEXT,            -- JSON array of questions
                
                -- Is this an exception to a pattern?
                is_exception BOOLEAN DEFAULT 0,
                exception_to_pattern TEXT,        -- Which pattern this breaks
                
                -- Did we act on this? (Or just observe)
                we_participated BOOLEAN DEFAULT 0,
                our_action TEXT,
                our_result TEXT,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # QUESTIONS - What the brain is wondering about
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                
                -- The question
                question TEXT NOT NULL,           -- "What do these runners have in common?"
                question_type TEXT,               -- 'pattern', 'exception', 'correlation', 'causation'
                
                -- Context
                triggered_by TEXT,                -- What observation triggered this question
                related_tickers TEXT,             -- JSON array
                related_observations TEXT,        -- JSON array of observation IDs
                
                -- Current thinking (not conclusions!)
                current_thoughts TEXT,            -- JSON: evolving thoughts on this question
                
                -- Status
                status TEXT DEFAULT 'open',       -- 'open', 'has_thoughts', 'resolved', 'still_wondering'
                
                -- If resolved, what emerged (still held loosely)
                emerged_insight TEXT,             -- Not a rule - an insight held loosely
                confidence_in_insight REAL,       -- How sure are we? (Low is fine)
                what_would_change_view TEXT,      -- What would make us think differently
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        """)
        
        # PERSPECTIVES - Multiple views held simultaneously
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_perspectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ticker TEXT NOT NULL,
                
                -- Multiple perspectives (all can be true simultaneously)
                momentum_view TEXT,               -- "Looks strong, volume confirming"
                thesis_view TEXT,                 -- "Thesis intact, catalyst approaching"
                valuation_view TEXT,              -- "Extended, 30% above fair value"
                risk_view TEXT,                   -- "Already have 10% exposure here"
                sector_view TEXT,                 -- "Space is hot, rotation into sector"
                technical_view TEXT,              -- "Above all MAs, RSI elevated"
                
                -- The synthesis (not a conclusion - a current thinking)
                synthesis TEXT,                   -- "Given all this, here's how I'm thinking about it"
                
                -- What we're uncertain about
                uncertainties TEXT,               -- JSON array of unknowns
                what_would_change_view TEXT,      -- JSON: conditions that would shift thinking
                
                -- Current lean (NOT a decision - a lean)
                current_lean TEXT,                -- 'interested', 'cautious', 'watching', 'not_for_me'
                lean_confidence REAL,             -- 0-100, but LOW IS OKAY
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # INTUITIONS - Accumulated feel (not rules)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brain_intuitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- What this intuition is about
                domain TEXT NOT NULL,             -- 'runners', 'biotech', 'volume_spikes', etc.
                
                -- The accumulated observations
                observations_count INTEGER DEFAULT 0,
                positive_examples INTEGER DEFAULT 0,  -- Times it worked
                negative_examples INTEGER DEFAULT 0,  -- Times it didn't
                exception_count INTEGER DEFAULT 0,    -- Interesting exceptions
                
                -- The emerging FEEL (not a rule)
                current_feel TEXT,                -- "Runners with X often do Y, but not always"
                
                -- Key factors that SEEM to matter
                factors_that_seem_to_matter TEXT, -- JSON: observations about what correlates
                
                -- Key exceptions that keep us humble
                notable_exceptions TEXT,          -- JSON: times it broke
                
                -- Texture, not rules
                texture_notes TEXT,               -- Free-form accumulated wisdom
                
                -- How much we trust this intuition
                trust_level TEXT,                 -- 'forming', 'developing', 'established', 'questioning'
                
                last_updated TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    # =========================================================================
    # CORE FUNCTION: OBSERVE (The brain watches EVERYTHING)
    # =========================================================================
    
    def observe(self, 
                what_happened: str,
                observation_type: str = 'market_move',
                ticker: str = None,
                context: Dict = None,
                we_participated: bool = False,
                our_action: str = None,
                our_result: str = None,
                is_exception: bool = False,
                exception_to: str = None) -> int:
        """
        Log an observation. The brain WATCHES - it doesn't just trade.
        
        Args:
            what_happened: Plain english description of what occurred
            observation_type: 'market_move', 'runner', 'sector_rotation', 'correlation', 'exception'
            ticker: Specific ticker (None for market-wide)
            context: Dict with volume, float, sector, similar_names, etc.
            we_participated: Did we trade this?
            our_action: What we did (if we participated)
            our_result: How it turned out for us
            is_exception: Does this break a pattern?
            exception_to: Which pattern it breaks
            
        Returns:
            observation_id
            
        Example:
            brain.observe(
                what_happened="MRNO ran +45% after we exited at +20%",
                observation_type="runner",
                ticker="MRNO",
                context={
                    "volume": "4x average",
                    "float": "8M shares",
                    "sector": "biotech",
                    "similar_runners_today": ["FEED", "TIRX", "SLGB"]
                },
                we_participated=True,
                our_action="Exited at +20%",
                our_result="Left 25% on the table"
            )
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now()
        
        # Auto-generate initial questions based on the observation
        questions = self._generate_questions(what_happened, observation_type, context)
        
        cursor.execute("""
            INSERT INTO brain_observations (
                timestamp, date, observation_type, ticker,
                what_happened, context_data, questions_raised,
                is_exception, exception_to_pattern,
                we_participated, our_action, our_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now.isoformat(),
            now.strftime("%Y-%m-%d"),
            observation_type,
            ticker,
            what_happened,
            json.dumps(context) if context else None,
            json.dumps(questions),
            is_exception,
            exception_to,
            we_participated,
            our_action,
            our_result
        ))
        
        observation_id = cursor.lastrowid
        conn.commit()
        
        # Log any generated questions
        for q in questions:
            self.ask_question(q, triggered_by=what_happened, related_tickers=[ticker] if ticker else [])
        
        conn.close()
        
        print(f"🧠 Observed: {what_happened[:60]}...")
        if questions:
            print(f"   Questions raised: {len(questions)}")
        
        return observation_id
    
    def _generate_questions(self, what_happened: str, obs_type: str, context: Dict) -> List[str]:
        """
        The brain automatically generates questions from observations.
        This is KEY - we don't make conclusions, we ask questions.
        """
        questions = []
        
        if obs_type == 'runner':
            questions.append("What made this run?")
            questions.append("What else ran today? What do they have in common?")
            questions.append("What similar setups DIDN'T run? Why?")
            if context and context.get('similar_runners_today'):
                questions.append(f"Is there a theme connecting {context['similar_runners_today']}?")
        
        elif obs_type == 'exception':
            questions.append("Why did this break the pattern?")
            questions.append("What was different about this situation?")
            questions.append("Should I update my intuition, or is this just noise?")
        
        elif obs_type == 'sector_rotation':
            questions.append("What's driving money into this sector?")
            questions.append("Is this the start of something or a one-day move?")
            questions.append("What would tell me if this has legs?")
        
        # Always ask these meta-questions
        questions.append("Am I seeing a pattern or am I seeing noise?")
        
        return questions
    
    # =========================================================================
    # CORE FUNCTION: ASK QUESTIONS (The brain lives in questions)
    # =========================================================================
    
    def ask_question(self,
                     question: str,
                     question_type: str = 'pattern',
                     triggered_by: str = None,
                     related_tickers: List[str] = None,
                     related_observation_ids: List[int] = None) -> int:
        """
        The brain doesn't make conclusions. It asks questions.
        
        Args:
            question: The question we're wondering about
            question_type: 'pattern', 'exception', 'correlation', 'causation'
            triggered_by: What observation triggered this question
            related_tickers: Tickers involved
            related_observation_ids: Related observation IDs
            
        Returns:
            question_id
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO brain_questions (
                timestamp, question, question_type,
                triggered_by, related_tickers, related_observations,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, 'open')
        """, (
            datetime.now().isoformat(),
            question,
            question_type,
            triggered_by,
            json.dumps(related_tickers) if related_tickers else None,
            json.dumps(related_observation_ids) if related_observation_ids else None
        ))
        
        question_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return question_id
    
    def think_about_question(self,
                            question_id: int,
                            new_thought: str,
                            confidence: float = None,
                            what_would_change_view: str = None) -> bool:
        """
        Add thinking to a question. NOT a conclusion - just current thinking.
        
        The brain HOLDS thoughts loosely. It doesn't conclude.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get existing thoughts
        cursor.execute("SELECT current_thoughts FROM brain_questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()
        
        existing = json.loads(row[0]) if row and row[0] else []
        existing.append({
            "timestamp": datetime.now().isoformat(),
            "thought": new_thought,
            "confidence": confidence,
            "what_would_change": what_would_change_view
        })
        
        cursor.execute("""
            UPDATE brain_questions SET
                current_thoughts = ?,
                status = 'has_thoughts',
                updated_at = ?
            WHERE id = ?
        """, (json.dumps(existing), datetime.now().isoformat(), question_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    # =========================================================================
    # CORE FUNCTION: MULTIPLE PERSPECTIVES (Hold contradictions)
    # =========================================================================
    
    def analyze_from_all_angles(self,
                                ticker: str,
                                momentum_view: str = None,
                                thesis_view: str = None,
                                valuation_view: str = None,
                                risk_view: str = None,
                                sector_view: str = None,
                                technical_view: str = None,
                                uncertainties: List[str] = None,
                                what_would_change: Dict = None) -> Dict:
        """
        Analyze a ticker from MULTIPLE perspectives simultaneously.
        
        Markets ARE contradictions. The brain can hold them all.
        
        Returns a synthesis - not a conclusion.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Synthesize the perspectives
        synthesis = self._synthesize_perspectives(
            ticker, momentum_view, thesis_view, valuation_view,
            risk_view, sector_view, technical_view
        )
        
        # Determine current lean (NOT a decision)
        lean, lean_confidence = self._determine_lean(
            momentum_view, thesis_view, valuation_view,
            risk_view, sector_view, technical_view
        )
        
        cursor.execute("""
            INSERT INTO brain_perspectives (
                timestamp, ticker,
                momentum_view, thesis_view, valuation_view,
                risk_view, sector_view, technical_view,
                synthesis, uncertainties, what_would_change_view,
                current_lean, lean_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            ticker,
            momentum_view, thesis_view, valuation_view,
            risk_view, sector_view, technical_view,
            synthesis,
            json.dumps(uncertainties) if uncertainties else None,
            json.dumps(what_would_change) if what_would_change else None,
            lean,
            lean_confidence
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "ticker": ticker,
            "perspectives": {
                "momentum": momentum_view,
                "thesis": thesis_view,
                "valuation": valuation_view,
                "risk": risk_view,
                "sector": sector_view,
                "technical": technical_view
            },
            "synthesis": synthesis,
            "uncertainties": uncertainties,
            "what_would_change": what_would_change,
            "current_lean": lean,
            "lean_confidence": lean_confidence,
            "note": "This is current THINKING, not a conclusion. Hold loosely."
        }
    
    def _synthesize_perspectives(self, ticker, *views) -> str:
        """
        Synthesize multiple views into current thinking.
        NOT a conclusion - a synthesis.
        """
        filled_views = [v for v in views if v]
        
        if not filled_views:
            return f"Not enough perspective on {ticker} yet. Need more observation."
        
        if len(filled_views) == 1:
            return f"Only one perspective so far: {filled_views[0]}. Need more angles."
        
        return f"Holding {len(filled_views)} perspectives on {ticker}. They may conflict. That's okay."
    
    def _determine_lean(self, *views) -> tuple:
        """
        Determine current lean from perspectives.
        Low confidence is FINE - uncertainty is honest.
        """
        # This is placeholder - real implementation would be more sophisticated
        filled = [v for v in views if v]
        
        if not filled:
            return "watching", 20.0
        
        # Count positive/negative signals in views
        positive_words = ['strong', 'intact', 'hot', 'above', 'confirming', 'bullish']
        negative_words = ['extended', 'overbought', 'risk', 'uncertain', 'weak', 'bearish']
        
        pos_count = sum(1 for v in filled for w in positive_words if w in v.lower())
        neg_count = sum(1 for v in filled for w in negative_words if w in v.lower())
        
        if pos_count > neg_count + 2:
            return "interested", min(65.0, 40 + pos_count * 5)
        elif neg_count > pos_count + 2:
            return "cautious", min(65.0, 40 + neg_count * 5)
        else:
            return "watching", 50.0
    
    # =========================================================================
    # CORE FUNCTION: BUILD INTUITION (Not rules - FEEL)
    # =========================================================================
    
    def build_intuition(self,
                       domain: str,
                       observation: str,
                       was_positive: bool = None,
                       is_exception: bool = False,
                       factors_noticed: List[str] = None) -> bool:
        """
        Accumulate observations into intuition. NOT rules - FEEL.
        
        After watching 100 runners:
        - 60 kept running
        - 40 died
        
        We don't make a rule "60% chance."
        We build TEXTURE about what tends to happen.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get or create intuition for this domain
        cursor.execute("SELECT * FROM brain_intuitions WHERE domain = ?", (domain,))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("""
                INSERT INTO brain_intuitions (domain, observations_count)
                VALUES (?, 0)
            """, (domain,))
            conn.commit()
        
        # Update counts
        updates = ["observations_count = observations_count + 1"]
        if was_positive is True:
            updates.append("positive_examples = positive_examples + 1")
        elif was_positive is False:
            updates.append("negative_examples = negative_examples + 1")
        if is_exception:
            updates.append("exception_count = exception_count + 1")
        
        cursor.execute(f"""
            UPDATE brain_intuitions SET
                {', '.join(updates)},
                last_updated = ?
            WHERE domain = ?
        """, (datetime.now().isoformat(), domain))
        
        # Update factors if provided
        if factors_noticed:
            cursor.execute("SELECT factors_that_seem_to_matter FROM brain_intuitions WHERE domain = ?", (domain,))
            row = cursor.fetchone()
            existing = json.loads(row[0]) if row and row[0] else {}
            
            for factor in factors_noticed:
                existing[factor] = existing.get(factor, 0) + 1
            
            cursor.execute("""
                UPDATE brain_intuitions SET factors_that_seem_to_matter = ? WHERE domain = ?
            """, (json.dumps(existing), domain))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_intuition(self, domain: str) -> Dict:
        """
        Get current intuition for a domain.
        Returns FEEL, not rules.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM brain_intuitions WHERE domain = ?", (domain,))
        row = cursor.fetchone()
        
        if not row:
            return {
                "domain": domain,
                "status": "no_intuition_yet",
                "message": f"Haven't observed enough about '{domain}' yet. Keep watching."
            }
        
        # Get column names
        cursor.execute("PRAGMA table_info(brain_intuitions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        data = dict(zip(columns, row))
        conn.close()
        
        # Calculate texture
        total = data.get('positive_examples', 0) + data.get('negative_examples', 0)
        
        result = {
            "domain": domain,
            "observations": data.get('observations_count', 0),
            "total_with_outcomes": total,
            "positive": data.get('positive_examples', 0),
            "negative": data.get('negative_examples', 0),
            "exceptions": data.get('exception_count', 0),
            "trust_level": data.get('trust_level', 'forming'),
            "current_feel": data.get('current_feel'),
            "factors_that_seem_to_matter": json.loads(data.get('factors_that_seem_to_matter') or '{}'),
            "notable_exceptions": json.loads(data.get('notable_exceptions') or '[]'),
            "texture_notes": data.get('texture_notes'),
            
            # The key message
            "note": "This is accumulated FEEL, not a rule. Hold loosely. Exceptions matter."
        }
        
        # Generate a feel statement
        if total >= 10:
            pos_rate = data.get('positive_examples', 0) / total * 100
            result["current_feel_statement"] = (
                f"After {total} observations, positive outcomes happened {pos_rate:.0f}% of the time. "
                f"But {data.get('exception_count', 0)} interesting exceptions remind me this isn't a rule."
            )
        else:
            result["current_feel_statement"] = f"Only {total} observations so far. Still forming intuition."
        
        return result
    
    # =========================================================================
    # CORE FUNCTION: EMBRACE UNCERTAINTY (Know what you don't know)
    # =========================================================================
    
    def express_uncertainty(self, 
                           topic: str,
                           what_i_think: str,
                           confidence: float,
                           what_im_unsure_about: List[str],
                           what_would_increase_confidence: List[str],
                           what_would_decrease_confidence: List[str]) -> Dict:
        """
        Express a view WITH explicit uncertainty.
        
        "Based on what I'm seeing, this MIGHT continue. 
        Here's what would make me more confident. 
        Here's what would make me less confident. 
        I'm making a decision with incomplete information, and I'm okay with that."
        """
        return {
            "topic": topic,
            "current_thinking": what_i_think,
            "confidence": confidence,
            "confidence_note": "Low confidence is fine. Uncertainty is honesty.",
            
            "uncertainties": what_im_unsure_about,
            
            "what_would_increase_confidence": what_would_increase_confidence,
            "what_would_decrease_confidence": what_would_decrease_confidence,
            
            "meta": "I'm making a decision with incomplete information. That's okay. That's trading."
        }
    
    # =========================================================================
    # OUTPUT: Format thinking for display
    # =========================================================================
    
    def format_current_thinking(self, ticker: str = None) -> str:
        """
        Format the brain's current THINKING (not conclusions) for display.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("🧠 CURRENT THINKING")
        lines.append("   (Not conclusions. Not rules. Just what I'm noticing.)")
        lines.append("=" * 60)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Recent observations
        if ticker:
            cursor.execute("""
                SELECT what_happened, questions_raised, we_participated, our_result
                FROM brain_observations
                WHERE ticker = ?
                ORDER BY timestamp DESC LIMIT 5
            """, (ticker,))
        else:
            cursor.execute("""
                SELECT what_happened, questions_raised, we_participated, our_result
                FROM brain_observations
                ORDER BY timestamp DESC LIMIT 5
            """)
        
        observations = cursor.fetchall()
        
        if observations:
            lines.append("\n📝 RECENT OBSERVATIONS:")
            for obs in observations:
                lines.append(f"  • {obs[0]}")
                if obs[2]:  # we participated
                    lines.append(f"    (We: {obs[3] or 'participated'})")
        
        # Open questions
        cursor.execute("""
            SELECT question, current_thoughts
            FROM brain_questions
            WHERE status IN ('open', 'has_thoughts')
            ORDER BY timestamp DESC LIMIT 5
        """)
        
        questions = cursor.fetchall()
        
        if questions:
            lines.append("\n❓ QUESTIONS I'M WONDERING ABOUT:")
            for q in questions:
                lines.append(f"  • {q[0]}")
                if q[1]:
                    thoughts = json.loads(q[1])
                    if thoughts:
                        latest = thoughts[-1]
                        lines.append(f"    Current thought: {latest.get('thought', '')[:50]}...")
        
        # Intuitions
        cursor.execute("""
            SELECT domain, observations_count, positive_examples, negative_examples, exception_count
            FROM brain_intuitions
            WHERE observations_count > 0
            ORDER BY observations_count DESC LIMIT 3
        """)
        
        intuitions = cursor.fetchall()
        
        if intuitions:
            lines.append("\n🎯 DEVELOPING INTUITIONS:")
            for i in intuitions:
                total = i[2] + i[3]
                if total > 0:
                    rate = i[2] / total * 100
                    lines.append(f"  • {i[0]}: {rate:.0f}% positive after {total} observations")
                    lines.append(f"    ({i[4]} exceptions remind me this isn't a rule)")
        
        conn.close()
        
        lines.append("\n" + "-" * 60)
        lines.append("Remember: This is THINKING, not knowing.")
        lines.append("Rules are dead. Thinking is alive.")
        lines.append("-" * 60)
        
        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def observe_market(what_happened: str, **kwargs):
    """Quick observation logging"""
    brain = ThinkingBrain()
    return brain.observe(what_happened, **kwargs)

def ask(question: str, **kwargs):
    """Quick question asking"""
    brain = ThinkingBrain()
    return brain.ask_question(question, **kwargs)

def analyze_ticker(ticker: str, **perspectives):
    """Quick multi-perspective analysis"""
    brain = ThinkingBrain()
    return brain.analyze_from_all_angles(ticker, **perspectives)

def get_feel(domain: str):
    """Quick intuition retrieval"""
    brain = ThinkingBrain()
    return brain.get_intuition(domain)


# =============================================================================
# DEMO / TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("THE THINKING BRAIN - DEMO")
    print("=" * 60)
    
    brain = ThinkingBrain()
    
    # Example: Observe MRNO running after we exited
    print("\n1. OBSERVING (not just our trades - EVERYTHING)")
    brain.observe(
        what_happened="MRNO ran +45% after we exited at +20%",
        observation_type="runner",
        ticker="MRNO",
        context={
            "volume": "4x average",
            "float": "8M shares", 
            "sector": "biotech",
            "similar_runners_today": ["FEED", "TIRX", "SLGB"],
            "our_exit_reason": "Hit +20% profit target"
        },
        we_participated=True,
        our_action="Exited at +20%",
        our_result="Left 25% on the table"
    )
    
    # Example: Analyze from multiple perspectives
    print("\n2. MULTIPLE PERSPECTIVES (hold contradictions)")
    analysis = brain.analyze_from_all_angles(
        ticker="MU",
        momentum_view="Strong - 3 consecutive green days, volume confirming",
        thesis_view="Thesis intact - HBM demand growing, Azure partnership solid",
        valuation_view="Extended - 15% above 50-day MA, approaching resistance",
        risk_view="Already have 10% portfolio exposure to semis",
        sector_view="Tech sector hot this week, but rotating fast",
        uncertainties=[
            "Earnings in 3 weeks - could go either way",
            "Macro uncertainty with Fed decision next week",
            "Not sure if this is real buying or short covering"
        ],
        what_would_change={
            "more_bullish": ["Break above $95 on volume", "Positive AMD earnings"],
            "more_bearish": ["Lose $85 support", "Sector rotation out of tech"]
        }
    )
    
    print(f"\n   Synthesis: {analysis['synthesis']}")
    print(f"   Current lean: {analysis['current_lean']} ({analysis['lean_confidence']:.0f}% confidence)")
    print(f"   Uncertainties: {len(analysis['uncertainties'])}")
    
    # Example: Build intuition
    print("\n3. BUILDING INTUITION (not rules - FEEL)")
    brain.build_intuition(
        domain="biotech_runners",
        observation="MRNO kept running after +20%",
        was_positive=True,
        factors_noticed=["low_float", "sector_hot", "volume_sustained"]
    )
    
    intuition = brain.get_intuition("biotech_runners")
    print(f"   Domain: {intuition['domain']}")
    print(f"   Observations: {intuition['observations']}")
    print(f"   Feel statement: {intuition.get('current_feel_statement', 'Still forming')}")
    
    # Show current thinking
    print("\n4. CURRENT THINKING (not conclusions)")
    print(brain.format_current_thinking())
