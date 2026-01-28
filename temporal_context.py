"""
TEMPORAL CONTEXT ENGINE
=======================
The brain that remembers is the brain that learns.

This module provides get_temporal_context() - the function that gives
Fenrir memory. Instead of reacting to today's snapshot, Fenrir can now
see patterns, history, and learn from experience.

Approved by Fenrir: January 28, 2026
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

DB_PATH = 'data/wolfpack.db'

class TemporalContextEngine:
    """
    Provides temporal memory context for trading decisions.
    
    "A brain without memory is reactive. A brain WITH memory is predictive."
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    # =========================================================================
    # CORE FUNCTION: get_temporal_context
    # =========================================================================
    
    def get_temporal_context(self, ticker: str, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Get complete temporal context for a ticker.
        
        This is THE function that turns snapshot analysis into memory-powered analysis.
        
        Returns:
            {
                "ticker": "MU",
                "as_of": "2026-01-28",
                
                "price_history": {
                    "current_price": 87.20,
                    "price_30d_ago": 92.50,
                    "cumulative_30d_return": -5.8,
                    "consecutive_days": -3,  # negative = down
                    "current_run_pct": -6.2,
                    "volume_trend": "decreasing"
                },
                
                "our_history": {
                    "total_trades": 6,
                    "wins": 5,
                    "losses": 1,
                    "win_rate": 83.3,
                    "avg_return": 4.2,
                    "last_action": "ADD",
                    "last_action_date": "2026-01-15",
                    "last_action_result": "+8.2%"
                },
                
                "pattern_matches": [
                    {
                        "pattern": "3_day_dip_low_volume",
                        "occurrences": 4,
                        "success_rate": 75.0,
                        "avg_recovery_days": 2.5,
                        "avg_return": 4.2
                    }
                ],
                
                "thesis_status": {
                    "thesis_type": "thesis",
                    "original_thesis": "AI memory demand",
                    "thesis_intact": True,
                    "days_to_catalyst": 23
                },
                
                "calibration": {
                    "our_confidence": 75,
                    "historical_accuracy_at_75": 68.5,
                    "calibration_note": "Slightly overconfident historically"
                },
                
                "recommendation_context": {
                    "similar_situations": 4,
                    "similar_outcomes": "75% recovered within 5 days",
                    "our_edge": "85.7% win rate on this ticker",
                    "risk_factors": ["earnings in 23 days", "tech sector volatility"]
                }
            }
        """
        context = {
            "ticker": ticker,
            "as_of": datetime.now().strftime("%Y-%m-%d"),
            "lookback_days": lookback_days,
        }
        
        # Gather all context components
        context["price_history"] = self._get_price_history(ticker, lookback_days)
        context["our_history"] = self._get_our_trading_history(ticker)
        context["pattern_matches"] = self._get_pattern_matches(ticker)
        context["thesis_status"] = self._get_thesis_status(ticker)
        context["calibration"] = self._get_calibration_context()
        context["recommendation_context"] = self._build_recommendation_context(context)
        
        return context
    
    # =========================================================================
    # COMPONENT FUNCTIONS
    # =========================================================================
    
    def _get_price_history(self, ticker: str, lookback_days: int) -> Dict[str, Any]:
        """Get price history from daily_records table"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        result = {
            "current_price": None,
            "price_lookback_ago": None,
            "cumulative_return_pct": None,
            "consecutive_days": 0,
            "current_run_pct": None,
            "volume_trend": "unknown",
            "above_sma_20": None,
            "above_sma_50": None,
            "rsi_14": None,
            "data_available": False
        }
        
        try:
            # Get recent price data
            cutoff_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
            
            cursor.execute("""
                SELECT date, close, volume, consecutive_green, consecutive_red,
                       above_sma_20, above_sma_50, rsi_14, return_5d, return_20d
                FROM daily_records
                WHERE ticker = ? AND date >= ?
                ORDER BY date DESC
            """, (ticker, cutoff_date))
            
            rows = cursor.fetchall()
            
            if rows:
                result["data_available"] = True
                latest = rows[0]
                oldest = rows[-1] if len(rows) > 1 else rows[0]
                
                result["current_price"] = latest[1]
                result["price_lookback_ago"] = oldest[1]
                
                if latest[1] and oldest[1]:
                    result["cumulative_return_pct"] = round(
                        ((latest[1] - oldest[1]) / oldest[1]) * 100, 2
                    )
                
                # Consecutive days (positive = green, negative = red)
                if latest[3]:  # consecutive_green
                    result["consecutive_days"] = latest[3]
                elif latest[4]:  # consecutive_red
                    result["consecutive_days"] = -latest[4]
                
                result["above_sma_20"] = bool(latest[5])
                result["above_sma_50"] = bool(latest[6])
                result["rsi_14"] = latest[7]
                
                # Volume trend (compare recent vs older)
                if len(rows) >= 5:
                    recent_vol = sum(r[2] or 0 for r in rows[:5]) / 5
                    older_vol = sum(r[2] or 0 for r in rows[5:10]) / max(1, len(rows[5:10]))
                    if older_vol > 0:
                        vol_ratio = recent_vol / older_vol
                        if vol_ratio > 1.2:
                            result["volume_trend"] = "increasing"
                        elif vol_ratio < 0.8:
                            result["volume_trend"] = "decreasing"
                        else:
                            result["volume_trend"] = "stable"
        
        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()
        
        return result
    
    def _get_our_trading_history(self, ticker: str) -> Dict[str, Any]:
        """Get our trading history on this ticker"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        result = {
            "total_trades": 0,
            "buys": 0,
            "sells": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": None,
            "avg_return": None,
            "last_action": None,
            "last_action_date": None,
            "last_action_price": None,
            "thesis_trades": 0,
            "momentum_trades": 0,
            "speculative_trades": 0
        }
        
        try:
            # Get all trades for this ticker
            cursor.execute("""
                SELECT timestamp, action, price, thesis, thesis_type,
                       outcome_classification, day5_pct, convergence_score
                FROM trades
                WHERE ticker = ?
                ORDER BY timestamp DESC
            """, (ticker,))
            
            rows = cursor.fetchall()
            result["total_trades"] = len(rows)
            
            if rows:
                # Count actions
                for row in rows:
                    action = row[1]
                    if action in ('BUY', 'ADD'):
                        result["buys"] += 1
                    elif action in ('SELL', 'CUT'):
                        result["sells"] += 1
                    
                    # Count by thesis type
                    thesis_type = row[4]
                    if thesis_type == 'thesis':
                        result["thesis_trades"] += 1
                    elif thesis_type == 'momentum':
                        result["momentum_trades"] += 1
                    elif thesis_type == 'speculative':
                        result["speculative_trades"] += 1
                    
                    # Count wins/losses
                    outcome = row[5]
                    if outcome == 'win':
                        result["wins"] += 1
                    elif outcome == 'loss':
                        result["losses"] += 1
                
                # Calculate win rate
                completed = result["wins"] + result["losses"]
                if completed > 0:
                    result["win_rate"] = round((result["wins"] / completed) * 100, 1)
                
                # Get returns
                returns = [r[6] for r in rows if r[6] is not None]
                if returns:
                    result["avg_return"] = round(sum(returns) / len(returns), 2)
                
                # Last action
                latest = rows[0]
                result["last_action"] = latest[1]
                result["last_action_date"] = latest[0][:10] if latest[0] else None
                result["last_action_price"] = latest[2]
        
        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()
        
        return result
    
    def _get_pattern_matches(self, ticker: str) -> List[Dict[str, Any]]:
        """Get relevant patterns for this ticker"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        patterns = []
        
        try:
            # Get patterns that match this ticker or are universal
            cursor.execute("""
                SELECT pattern_name, occurrences, win_rate, avg_return,
                       avg_duration_days, confidence_score, description,
                       thesis_win_rate, momentum_win_rate
                FROM learned_patterns
                WHERE ticker = ? OR ticker IS NULL
                ORDER BY occurrences DESC
                LIMIT 5
            """, (ticker,))
            
            for row in cursor.fetchall():
                if row[1] and row[1] > 0:  # Has occurrences
                    patterns.append({
                        "pattern": row[0],
                        "occurrences": row[1],
                        "win_rate": row[2],
                        "avg_return": row[3],
                        "avg_duration_days": row[4],
                        "confidence": row[5],
                        "description": row[6],
                        "thesis_win_rate": row[7],
                        "momentum_win_rate": row[8]
                    })
        
        except Exception as e:
            patterns.append({"error": str(e)})
        finally:
            conn.close()
        
        return patterns
    
    def _get_thesis_status(self, ticker: str) -> Dict[str, Any]:
        """Get thesis status for this ticker"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        result = {
            "has_thesis": False,
            "thesis_type": None,
            "original_thesis": None,
            "thesis_intact": None,
            "convergence_score": None,
            "entry_signals": []
        }
        
        try:
            # Get most recent trade with thesis info
            cursor.execute("""
                SELECT thesis, thesis_type, convergence_score, notes
                FROM trades
                WHERE ticker = ? AND thesis IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1
            """, (ticker,))
            
            row = cursor.fetchone()
            if row:
                result["has_thesis"] = True
                result["original_thesis"] = row[0]
                result["thesis_type"] = row[1]
                result["convergence_score"] = row[2]
                
                # Parse notes for signals
                if row[3]:
                    try:
                        notes = json.loads(row[3])
                        result["entry_signals"] = notes.get("signals", [])
                    except:
                        pass
        
        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()
        
        return result
    
    def _get_calibration_context(self, confidence_level: int = None) -> Dict[str, Any]:
        """Get calibration data for confidence assessment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        result = {
            "calibration_available": False,
            "buckets": []
        }
        
        try:
            cursor.execute("""
                SELECT confidence_bucket, actual_win_rate, expected_win_rate,
                       calibration_error, trades_in_bucket
                FROM confidence_calibration
                WHERE trades_in_bucket > 0
                ORDER BY confidence_bucket
            """)
            
            for row in cursor.fetchall():
                result["buckets"].append({
                    "bucket": row[0],
                    "actual_win_rate": row[1],
                    "expected_win_rate": row[2],
                    "calibration_error": row[3],
                    "sample_size": row[4]
                })
            
            if result["buckets"]:
                result["calibration_available"] = True
                
                # Calculate overall calibration
                total_error = sum(abs(b["calibration_error"] or 0) for b in result["buckets"])
                result["avg_calibration_error"] = round(total_error / len(result["buckets"]), 2)
                
                if result["avg_calibration_error"] > 10:
                    result["calibration_note"] = "Significantly miscalibrated - review confidence estimates"
                elif result["avg_calibration_error"] > 5:
                    result["calibration_note"] = "Slightly overconfident historically"
                else:
                    result["calibration_note"] = "Well calibrated"
        
        except Exception as e:
            result["error"] = str(e)
        finally:
            conn.close()
        
        return result
    
    def _build_recommendation_context(self, context: Dict) -> Dict[str, Any]:
        """Build recommendation context from gathered data"""
        rec = {
            "similar_situations": 0,
            "similar_outcomes": None,
            "our_edge": None,
            "risk_factors": [],
            "confidence_factors": []
        }
        
        # Check pattern matches
        patterns = context.get("pattern_matches", [])
        if patterns:
            total_occurrences = sum(p.get("occurrences", 0) for p in patterns)
            rec["similar_situations"] = total_occurrences
            
            best_pattern = max(patterns, key=lambda p: p.get("occurrences", 0))
            if best_pattern.get("win_rate"):
                rec["similar_outcomes"] = f"{best_pattern['win_rate']}% success rate on '{best_pattern['pattern']}'"
        
        # Check our history
        history = context.get("our_history", {})
        if history.get("win_rate"):
            rec["our_edge"] = f"{history['win_rate']}% win rate on {context['ticker']} ({history['total_trades']} trades)"
            rec["confidence_factors"].append(f"Strong track record: {history['win_rate']}% win rate")
        
        # Check thesis
        thesis = context.get("thesis_status", {})
        if thesis.get("has_thesis"):
            rec["confidence_factors"].append(f"Has thesis: {thesis.get('original_thesis', 'defined')[:50]}")
        else:
            rec["risk_factors"].append("No defined thesis")
        
        # Check price trends
        price = context.get("price_history", {})
        if price.get("consecutive_days"):
            if price["consecutive_days"] < -3:
                rec["risk_factors"].append(f"Extended downtrend: {abs(price['consecutive_days'])} days red")
            elif price["consecutive_days"] > 3:
                rec["risk_factors"].append(f"Extended uptrend: {price['consecutive_days']} days green - watch for pullback")
        
        if price.get("rsi_14"):
            if price["rsi_14"] > 70:
                rec["risk_factors"].append(f"Overbought: RSI {price['rsi_14']}")
            elif price["rsi_14"] < 30:
                rec["confidence_factors"].append(f"Oversold: RSI {price['rsi_14']} - potential bounce")
        
        return rec
    
    # =========================================================================
    # TIER 1 FUNCTIONS
    # =========================================================================
    
    def analyze_trade_outcome(self, trade_id: int, 
                              signal_correct: bool,
                              timing_correct: bool,
                              execution_correct: bool,
                              allocation_correct: bool,
                              outcome: str,
                              lessons: str = None) -> bool:
        """
        Analyze a completed trade and update the database.
        
        This is TIER 1 functionality - granular loss attribution.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE trades SET
                    signal_was_correct = ?,
                    timing_was_correct = ?,
                    execution_was_correct = ?,
                    capital_allocation_correct = ?,
                    outcome_classification = ?,
                    review_complete = 1
                WHERE id = ?
            """, (signal_correct, timing_correct, execution_correct, 
                  allocation_correct, outcome, trade_id))
            
            conn.commit()
            print(f"✓ Trade {trade_id} analyzed: {outcome}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to analyze trade {trade_id}: {e}")
            return False
        finally:
            conn.close()
    
    def update_calibration_tracking(self, confidence_level: int, was_win: bool,
                                    thesis_type: str = None) -> bool:
        """
        Update confidence calibration after a trade completes.
        
        This is TIER 1 functionality - calibration tracking.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Round to nearest bucket (10, 20, 30, etc.)
        bucket = ((confidence_level + 5) // 10) * 10
        bucket = max(10, min(100, bucket))  # Clamp to 10-100
        
        try:
            # Update counts
            cursor.execute("""
                UPDATE confidence_calibration SET
                    trades_in_bucket = trades_in_bucket + 1,
                    wins_in_bucket = wins_in_bucket + ?,
                    losses_in_bucket = losses_in_bucket + ?,
                    last_updated = ?
                WHERE confidence_bucket = ?
            """, (1 if was_win else 0, 0 if was_win else 1, 
                  datetime.now().isoformat(), bucket))
            
            # Update by thesis type if provided
            if thesis_type == 'thesis':
                cursor.execute("""
                    UPDATE confidence_calibration SET
                        thesis_trades = thesis_trades + 1,
                        thesis_wins = thesis_wins + ?
                    WHERE confidence_bucket = ?
                """, (1 if was_win else 0, bucket))
            elif thesis_type == 'momentum':
                cursor.execute("""
                    UPDATE confidence_calibration SET
                        momentum_trades = momentum_trades + 1,
                        momentum_wins = momentum_wins + ?
                    WHERE confidence_bucket = ?
                """, (1 if was_win else 0, bucket))
            elif thesis_type == 'speculative':
                cursor.execute("""
                    UPDATE confidence_calibration SET
                        speculative_trades = speculative_trades + 1,
                        speculative_wins = speculative_wins + ?
                    WHERE confidence_bucket = ?
                """, (1 if was_win else 0, bucket))
            
            # Recalculate actual win rate and calibration error
            cursor.execute("""
                UPDATE confidence_calibration SET
                    actual_win_rate = CAST(wins_in_bucket AS REAL) / NULLIF(trades_in_bucket, 0) * 100,
                    calibration_error = (CAST(wins_in_bucket AS REAL) / NULLIF(trades_in_bucket, 0) * 100) - (expected_win_rate * 100)
                WHERE confidence_bucket = ?
            """, (bucket,))
            
            conn.commit()
            print(f"✓ Calibration updated: {bucket}% bucket, {'WIN' if was_win else 'LOSS'}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to update calibration: {e}")
            return False
        finally:
            conn.close()
    
    def log_decision(self, ticker: str, action: str, price: float,
                     reasoning: str, thesis_type: str,
                     convergence_score: int = None,
                     signals: List[str] = None,
                     market_regime: str = None,
                     regime_confidence: float = None) -> int:
        """
        Log a trading decision to user_decisions table.
        
        Returns the decision ID.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_decisions (
                    timestamp, ticker, action, price, reasoning,
                    thesis_type, convergence_score, entry_signals,
                    market_regime, regime_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                ticker, action, price, reasoning,
                thesis_type, convergence_score,
                json.dumps(signals) if signals else None,
                market_regime, regime_confidence
            ))
            
            conn.commit()
            decision_id = cursor.lastrowid
            print(f"✓ Decision logged: {action} {ticker} @ ${price} (ID: {decision_id})")
            return decision_id
            
        except Exception as e:
            print(f"✗ Failed to log decision: {e}")
            return None
        finally:
            conn.close()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_temporal_context(ticker: str, lookback_days: int = 30) -> Dict[str, Any]:
    """
    Convenience function to get temporal context.
    
    Usage:
        from temporal_context import get_temporal_context
        context = get_temporal_context("MU")
    """
    engine = TemporalContextEngine()
    return engine.get_temporal_context(ticker, lookback_days)


def format_context_for_fenrir(context: Dict) -> str:
    """
    Format temporal context for inclusion in Fenrir prompts.
    
    Returns a human-readable summary that can be injected into LLM prompts.
    """
    lines = []
    lines.append(f"=== TEMPORAL CONTEXT: {context['ticker']} ===")
    lines.append(f"As of: {context['as_of']}")
    lines.append("")
    
    # Price history
    price = context.get("price_history", {})
    if price.get("data_available"):
        lines.append("PRICE HISTORY:")
        if price.get("current_price"):
            lines.append(f"  Current: ${price['current_price']}")
        if price.get("cumulative_return_pct"):
            lines.append(f"  {context['lookback_days']}d return: {price['cumulative_return_pct']}%")
        if price.get("consecutive_days"):
            direction = "green" if price["consecutive_days"] > 0 else "red"
            lines.append(f"  Streak: {abs(price['consecutive_days'])} days {direction}")
        if price.get("volume_trend"):
            lines.append(f"  Volume trend: {price['volume_trend']}")
        lines.append("")
    
    # Our history
    history = context.get("our_history", {})
    if history.get("total_trades", 0) > 0:
        lines.append("OUR HISTORY:")
        lines.append(f"  Trades: {history['total_trades']}")
        if history.get("win_rate"):
            lines.append(f"  Win rate: {history['win_rate']}%")
        if history.get("avg_return"):
            lines.append(f"  Avg return: {history['avg_return']}%")
        if history.get("last_action"):
            lines.append(f"  Last action: {history['last_action']} on {history.get('last_action_date', 'unknown')}")
        lines.append("")
    
    # Pattern matches
    patterns = context.get("pattern_matches", [])
    if patterns and not patterns[0].get("error"):
        lines.append("PATTERN MATCHES:")
        for p in patterns[:3]:
            lines.append(f"  • {p['pattern']}: {p.get('win_rate', '?')}% win rate ({p.get('occurrences', 0)} occurrences)")
        lines.append("")
    
    # Thesis
    thesis = context.get("thesis_status", {})
    if thesis.get("has_thesis"):
        lines.append("THESIS:")
        lines.append(f"  Type: {thesis.get('thesis_type', 'unknown')}")
        lines.append(f"  Original: {thesis.get('original_thesis', 'N/A')[:60]}")
        if thesis.get("convergence_score"):
            lines.append(f"  Convergence: {thesis['convergence_score']}/100")
        lines.append("")
    
    # Recommendation context
    rec = context.get("recommendation_context", {})
    if rec.get("confidence_factors"):
        lines.append("CONFIDENCE FACTORS:")
        for f in rec["confidence_factors"]:
            lines.append(f"  + {f}")
    if rec.get("risk_factors"):
        lines.append("RISK FACTORS:")
        for f in rec["risk_factors"]:
            lines.append(f"  - {f}")
    
    lines.append("")
    lines.append("=" * 40)
    
    return "\n".join(lines)


# =============================================================================
# TEST / DEMO
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("TEMPORAL CONTEXT ENGINE - TEST")
    print("="*60)
    
    # Test with a ticker from our history
    test_tickers = ["MU", "UUUU", "MRNO", "DNN"]
    
    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"Testing: {ticker}")
        print("="*60)
        
        context = get_temporal_context(ticker)
        formatted = format_context_for_fenrir(context)
        print(formatted)
