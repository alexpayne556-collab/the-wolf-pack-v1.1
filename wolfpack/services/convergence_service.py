#!/usr/bin/env python3
"""
CONVERGENCE SERVICE - The Brain
Combines multiple independent signals into unified scores
Scanner + BR0KKR + Patterns + Sector = CONVERGENCE

The magic: When multiple signals agree independently = HIGH CONVICTION
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# DATA MODELS
# =============================================================================

class SignalType(Enum):
    """Types of signals that can converge"""
    SCANNER = "scanner"  # Price action, technical setup
    INSTITUTIONAL = "institutional"  # BR0KKR insider/activist activity
    CATALYST = "catalyst"  # Upcoming binary event
    SECTOR = "sector"  # Sector momentum
    PATTERN = "pattern"  # Historical pattern match
    NEWS = "news"  # News sentiment and context
    EARNINGS = "earnings"  # Earnings proximity and history


class ConvergenceLevel(Enum):
    """Convergence strength levels"""
    CRITICAL = "CRITICAL"  # 85-100: Multiple strong signals
    HIGH = "HIGH"  # 70-84: Good multi-signal setup
    MEDIUM = "MEDIUM"  # 50-69: Some convergence
    LOW = "LOW"  # 0-49: Weak or single signal


@dataclass
class Signal:
    """Individual signal component"""
    signal_type: SignalType
    score: int  # 0-100
    reasoning: str
    data: Dict  # Raw signal data


@dataclass
class ConvergenceSignal:
    """Multi-signal convergence result"""
    ticker: str
    convergence_score: int  # 0-100 (weighted combination)
    convergence_level: ConvergenceLevel
    signals: List[Signal]
    signal_count: int
    
    def get_priority_emoji(self) -> str:
        """Get priority emoji for display"""
        if self.convergence_level == ConvergenceLevel.CRITICAL:
            return "🔴"
        elif self.convergence_level == ConvergenceLevel.HIGH:
            return "🟠"
        elif self.convergence_level == ConvergenceLevel.MEDIUM:
            return "🟡"
        else:
            return "🟢"
    
    def get_signal_breakdown(self) -> str:
        """Get formatted breakdown of signals"""
        lines = []
        for signal in self.signals:
            lines.append(f"  • {signal.signal_type.value.upper()}: {signal.score}/100 - {signal.reasoning}")
        return "\n".join(lines)


# =============================================================================
# CONVERGENCE ENGINE
# =============================================================================

class ConvergenceEngine:
    """
    Combines multiple independent signals to identify high-conviction setups
    
    Philosophy:
    - Multiple independent signals agreeing = higher conviction
    - Each signal type has weight based on validation/reliability
    - Convergence score combines weighted signals
    - Only actionable when 2+ signals present
    """
    
    def __init__(self):
        # Signal weights (how much each signal type contributes)
        # Total must equal 1.0 for proper weighted averaging
        self.weights = {
            SignalType.INSTITUTIONAL: 0.30,  # BR0KKR (highest weight - smart money)
            SignalType.SCANNER: 0.20,        # Price action / technical setup
            SignalType.CATALYST: 0.15,       # Upcoming events / timing
            SignalType.EARNINGS: 0.10,       # Earnings proximity and history
            SignalType.NEWS: 0.10,           # News sentiment and context
            SignalType.SECTOR: 0.08,         # Sector momentum
            SignalType.PATTERN: 0.07,        # Historical patterns
        }
        
        # Minimum requirements
        self.min_signals = 2  # Need at least 2 independent signals
        self.min_score = 50   # Minimum convergence score to report
    
    def calculate_convergence(
        self,
        ticker: str,
        scanner_signal: Optional[Dict] = None,
        br0kkr_signal: Optional[Dict] = None,
        catalyst_signal: Optional[Dict] = None,
        sector_signal: Optional[Dict] = None,
        pattern_signal: Optional[Dict] = None,
        news_signal: Optional[Dict] = None,
        earnings_signal: Optional[Dict] = None,
    ) -> Optional[ConvergenceSignal]:
        """
        Calculate convergence score from available signals
        
        Args:
            ticker: Stock ticker
            scanner_signal: {score: int, reasoning: str, data: dict}
            br0kkr_signal: {score: int, reasoning: str, data: dict}
            catalyst_signal: {score: int, reasoning: str, data: dict}
            sector_signal: {score: int, reasoning: str, data: dict}
            pattern_signal: {score: int, reasoning: str, data: dict}
            news_signal: {score: int, reasoning: str, data: dict}
            earnings_signal: {score: int, reasoning: str, data: dict}
        
        Returns:
            ConvergenceSignal if convergence detected, None otherwise
        """
        signals = []
        
        # Collect all available signals
        if scanner_signal:
            signals.append(Signal(
                signal_type=SignalType.SCANNER,
                score=scanner_signal['score'],
                reasoning=scanner_signal['reasoning'],
                data=scanner_signal.get('data', {})
            ))
        
        if br0kkr_signal:
            signals.append(Signal(
                signal_type=SignalType.INSTITUTIONAL,
                score=br0kkr_signal['score'],
                reasoning=br0kkr_signal['reasoning'],
                data=br0kkr_signal.get('data', {})
            ))
        
        if catalyst_signal:
            signals.append(Signal(
                signal_type=SignalType.CATALYST,
                score=catalyst_signal['score'],
                reasoning=catalyst_signal['reasoning'],
                data=catalyst_signal.get('data', {})
            ))
        
        if sector_signal:
            signals.append(Signal(
                signal_type=SignalType.SECTOR,
                score=sector_signal['score'],
                reasoning=sector_signal['reasoning'],
                data=sector_signal.get('data', {})
            ))
        
        if pattern_signal:
            signals.append(Signal(
                signal_type=SignalType.PATTERN,
                score=pattern_signal['score'],
                reasoning=pattern_signal['reasoning'],
                data=pattern_signal.get('data', {})
            ))
        
        if news_signal:
            signals.append(Signal(
                signal_type=SignalType.NEWS,
                score=news_signal['score'],
                reasoning=news_signal['reasoning'],
                data=news_signal.get('data', {})
            ))
        
        if earnings_signal:
            signals.append(Signal(
                signal_type=SignalType.EARNINGS,
                score=earnings_signal['score'],
                reasoning=earnings_signal['reasoning'],
                data=earnings_signal.get('data', {})
            ))
        
        # Need at least 2 signals for convergence
        if len(signals) < self.min_signals:
            return None
        
        # Calculate weighted convergence score
        convergence_score = self._calculate_weighted_score(signals)
        
        # Apply convergence bonus (more signals = higher conviction)
        convergence_score = self._apply_convergence_bonus(convergence_score, len(signals))
        
        # Must meet minimum score threshold
        if convergence_score < self.min_score:
            return None
        
        # Determine convergence level
        if convergence_score >= 85:
            level = ConvergenceLevel.CRITICAL
        elif convergence_score >= 70:
            level = ConvergenceLevel.HIGH
        elif convergence_score >= 50:
            level = ConvergenceLevel.MEDIUM
        else:
            level = ConvergenceLevel.LOW
        
        return ConvergenceSignal(
            ticker=ticker,
            convergence_score=convergence_score,
            convergence_level=level,
            signals=signals,
            signal_count=len(signals)
        )
    
    def _calculate_weighted_score(self, signals: List[Signal]) -> int:
        """Calculate weighted average of signal scores"""
        total_weight = 0
        weighted_sum = 0
        
        for signal in signals:
            weight = self.weights.get(signal.signal_type, 0.1)
            weighted_sum += signal.score * weight
            total_weight += weight
        
        # Normalize to 0-100
        if total_weight > 0:
            base_score = (weighted_sum / total_weight)
        else:
            base_score = 0
        
        return int(base_score)
    
    def _apply_convergence_bonus(self, base_score: int, signal_count: int) -> int:
        """
        Apply bonus for multiple signals converging
        
        Philosophy: More independent signals agreeing = higher conviction
        - 2 signals: +5 points
        - 3 signals: +10 points
        - 4 signals: +15 points
        - 5 signals: +20 points
        """
        bonus_map = {
            2: 5,
            3: 10,
            4: 15,
            5: 20,
        }
        
        bonus = bonus_map.get(signal_count, 0)
        return min(base_score + bonus, 100)  # Cap at 100
    
    def batch_analyze(
        self,
        scanner_results: List[Dict],
        br0kkr_results: Dict,
        catalyst_results: Optional[Dict] = None,
        sector_results: Optional[Dict] = None,
        pattern_results: Optional[Dict] = None,
    ) -> List[ConvergenceSignal]:
        """
        Analyze multiple tickers for convergence
        
        Args:
            scanner_results: List of scanner signals [{'ticker': 'X', 'score': 65, ...}]
            br0kkr_results: BR0KKR data {'cluster_buys': [...], 'activist_filings': [...]}
            catalyst_results: Catalyst data by ticker (future)
            sector_results: Sector momentum data by ticker (future)
            pattern_results: Pattern match data by ticker (future)
        
        Returns:
            List of ConvergenceSignal objects, sorted by score (highest first)
        """
        convergence_signals = []
        
        # Build lookup dictionaries
        scanner_by_ticker = {s['ticker']: s for s in scanner_results}
        
        # BR0KKR signals by ticker
        br0kkr_by_ticker = {}
        
        # Process cluster buys
        for cluster in br0kkr_results.get('cluster_buys', []):
            ticker = cluster.ticker
            score = cluster.get_score()
            
            roles = []
            if cluster.has_ceo:
                roles.append('CEO')
            if cluster.has_cfo:
                roles.append('CFO')
            if cluster.has_director:
                roles.append('Director')
            
            br0kkr_by_ticker[ticker] = {
                'score': score,
                'reasoning': f"{cluster.unique_insiders} insiders bought ${cluster.total_value:,.0f} ({', '.join(roles)})",
                'data': {'type': 'cluster_buy', 'cluster': cluster}
            }
        
        # Process activist filings
        for filing in br0kkr_results.get('activist_filings', []):
            ticker = filing.ticker
            score = filing.get_score()
            
            # If ticker already has cluster buy, keep higher score
            if ticker in br0kkr_by_ticker:
                if score > br0kkr_by_ticker[ticker]['score']:
                    br0kkr_by_ticker[ticker] = {
                        'score': score,
                        'reasoning': f"{filing.filer_name} filed 13D ({filing.activist_tier})",
                        'data': {'type': 'activist', 'filing': filing}
                    }
            else:
                br0kkr_by_ticker[ticker] = {
                    'score': score,
                    'reasoning': f"{filing.filer_name} filed 13D ({filing.activist_tier})",
                    'data': {'type': 'activist', 'filing': filing}
                }
        
        # Get all unique tickers
        all_tickers = set(scanner_by_ticker.keys()) | set(br0kkr_by_ticker.keys())
        
        # Calculate convergence for each ticker
        for ticker in all_tickers:
            scanner_signal = None
            if ticker in scanner_by_ticker:
                s = scanner_by_ticker[ticker]
                scanner_signal = {
                    'score': s.get('score', 50),
                    'reasoning': s.get('reasoning', s.get('type', 'Setup detected')),
                    'data': s
                }
            
            br0kkr_signal = br0kkr_by_ticker.get(ticker)
            
            # For now, catalyst/sector/pattern are None (future enhancement)
            convergence = self.calculate_convergence(
                ticker=ticker,
                scanner_signal=scanner_signal,
                br0kkr_signal=br0kkr_signal,
                catalyst_signal=None,
                sector_signal=None,
                pattern_signal=None,
            )
            
            if convergence:
                convergence_signals.append(convergence)
        
        # Sort by convergence score (highest first)
        convergence_signals.sort(key=lambda c: c.convergence_score, reverse=True)
        
        return convergence_signals


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_convergence_report(convergence_signals: List[ConvergenceSignal], top_n: int = 10) -> str:
    """
    Format convergence signals for display
    
    Args:
        convergence_signals: List of ConvergenceSignal objects
        top_n: Number of top signals to show
    
    Returns:
        Formatted string report
    """
    if not convergence_signals:
        return "No convergence signals detected."
    
    lines = []
    lines.append(f"🎯 TOP {min(top_n, len(convergence_signals))} CONVERGENCE SIGNALS:")
    lines.append("=" * 60)
    
    for i, signal in enumerate(convergence_signals[:top_n], 1):
        emoji = signal.get_priority_emoji()
        lines.append(f"\n{i}. {emoji} {signal.ticker}: {signal.convergence_score}/100 ({signal.convergence_level.value})")
        lines.append(f"   {signal.signal_count} signals converging:")
        lines.append(signal.get_signal_breakdown())
    
    return "\n".join(lines)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("🧠 CONVERGENCE ENGINE TEST\n")
    
    # Create engine
    engine = ConvergenceEngine()
    
    # Test Case 1: Single signal (should return None)
    print("Test 1: Single signal (scanner only)")
    result = engine.calculate_convergence(
        ticker="TEST1",
        scanner_signal={'score': 65, 'reasoning': 'Wounded prey setup'},
    )
    print(f"Result: {result}\n")
    
    # Test Case 2: Two signals (scanner + BR0KKR)
    print("Test 2: Two signals converging")
    result = engine.calculate_convergence(
        ticker="TEST2",
        scanner_signal={'score': 65, 'reasoning': 'Wounded prey setup'},
        br0kkr_signal={'score': 85, 'reasoning': 'CEO + CFO bought $1.2M'},
    )
    if result:
        print(f"✅ Convergence detected!")
        print(f"   Score: {result.convergence_score}/100")
        print(f"   Level: {result.convergence_level.value}")
        print(f"   Signals: {result.signal_count}")
        print(result.get_signal_breakdown())
    print()
    
    # Test Case 3: Three signals
    print("Test 3: Three signals converging")
    result = engine.calculate_convergence(
        ticker="TEST3",
        scanner_signal={'score': 70, 'reasoning': 'Early momentum + volume'},
        br0kkr_signal={'score': 80, 'reasoning': '3 Directors bought $800k'},
        catalyst_signal={'score': 75, 'reasoning': 'Earnings in 2 weeks'},
    )
    if result:
        print(f"✅ Convergence detected!")
        print(f"   Score: {result.convergence_score}/100")
        print(f"   Level: {result.convergence_level.value}")
        print(f"   Signals: {result.signal_count}")
        print(result.get_signal_breakdown())
    print()
    
    # Test Case 4: Batch analysis
    print("Test 4: Batch analysis")
    scanner_results = [
        {'ticker': 'SMCI', 'score': 65, 'reasoning': 'Wounded prey', 'type': 'WOUNDED_PREY'},
        {'ticker': 'AMD', 'score': 55, 'reasoning': 'Early momentum', 'type': 'EARLY_MOMENTUM'},
    ]
    
    # Mock BR0KKR results (empty for test)
    br0kkr_results = {
        'cluster_buys': [],
        'activist_filings': []
    }
    
    convergence_list = engine.batch_analyze(scanner_results, br0kkr_results)
    print(f"Found {len(convergence_list)} convergence signals")
    if convergence_list:
        print(format_convergence_report(convergence_list, top_n=3))
    
    print("\n✅ Convergence engine test complete")
