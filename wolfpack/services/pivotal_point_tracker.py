#!/usr/bin/env python3
"""
PIVOTAL POINT TRACKER
Jesse Livermore's System - Identify key price levels where stocks make decisions
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class PivotalPointType(Enum):
    ROUND_NUMBER = "round_number"
    PREVIOUS_HIGH = "previous_high"
    PREVIOUS_LOW = "previous_low"
    CONSOLIDATION_TOP = "consolidation_top"
    CONSOLIDATION_BOTTOM = "consolidation_bottom"

class PatternState(Enum):
    CONSOLIDATING = "consolidating"
    BREAKOUT = "breakout"
    CONFIRMED = "confirmed"
    NORMAL_REACTION = "normal_reaction"
    TRENDING = "trending"
    FAILED = "failed"

@dataclass
class PivotalPoint:
    price: float
    point_type: PivotalPointType
    identified_date: datetime
    strength: float  # 0-100, how significant is this level

@dataclass
class LivermorePattern:
    ticker: str
    current_price: float
    pivotal_points: List[PivotalPoint]
    state: PatternState
    entry_price: Optional[float]
    volume_confirmation: bool
    avg_volume_20d: float
    current_volume: float
    volume_ratio: float
    consolidation_range: Optional[tuple]  # (low, high)
    days_consolidating: int
    breakout_price: Optional[float]
    score: int  # 0-100 for convergence

class PivotalPointTracker:
    """
    Livermore's Pivotal Point System
    
    The Pattern:
    1. Identify pivotal point (round number, previous high/low, consolidation edge)
    2. Wait for breakout (price breaks level)
    3. Confirm with volume (volume increases on breakout)
    4. Watch for normal reaction (pullback on lower volume)
    5. Trend resumes (volume increases again)
    6. Exit on abnormal behavior (pattern breaks)
    """
    
    def __init__(self):
        self.round_numbers = [10, 20, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500]
    
    def identify_pivotal_points(self, ticker: str, lookback_days: int = 90) -> List[PivotalPoint]:
        """Find all pivotal points for a ticker"""
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{lookback_days}d")
            
            if hist.empty:
                return []
            
            pivotal_points = []
            current_price = hist['Close'].iloc[-1]
            
            # 1. Round numbers near current price
            for num in self.round_numbers:
                if abs(current_price - num) / current_price < 0.15:  # Within 15%
                    strength = 100 if num in [50, 100, 200] else 75
                    pivotal_points.append(PivotalPoint(
                        price=num,
                        point_type=PivotalPointType.ROUND_NUMBER,
                        identified_date=datetime.now(),
                        strength=strength
                    ))
            
            # 2. Previous highs (resistance levels)
            high_52w = hist['High'].max()
            if high_52w > current_price * 1.05:  # Only if above current price
                pivotal_points.append(PivotalPoint(
                    price=high_52w,
                    point_type=PivotalPointType.PREVIOUS_HIGH,
                    identified_date=datetime.now(),
                    strength=90
                ))
            
            # 3. Previous lows (support levels)
            low_52w = hist['Low'].min()
            if low_52w < current_price * 0.95:  # Only if below current price
                pivotal_points.append(PivotalPoint(
                    price=low_52w,
                    point_type=PivotalPointType.PREVIOUS_LOW,
                    identified_date=datetime.now(),
                    strength=85
                ))
            
            # 4. Consolidation boundaries (last 30 days)
            recent = hist.tail(30)
            high_30d = recent['High'].max()
            low_30d = recent['Low'].min()
            range_pct = (high_30d - low_30d) / low_30d
            
            if range_pct < 0.20:  # If trading in < 20% range = consolidation
                pivotal_points.append(PivotalPoint(
                    price=high_30d,
                    point_type=PivotalPointType.CONSOLIDATION_TOP,
                    identified_date=datetime.now(),
                    strength=80
                ))
                pivotal_points.append(PivotalPoint(
                    price=low_30d,
                    point_type=PivotalPointType.CONSOLIDATION_BOTTOM,
                    identified_date=datetime.now(),
                    strength=80
                ))
            
            return pivotal_points
            
        except Exception as e:
            print(f"Error identifying pivotal points for {ticker}: {e}")
            return []
    
    def detect_pattern_state(self, ticker: str) -> LivermorePattern:
        """
        Detect what stage of Livermore's pattern the stock is in
        """
        
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="90d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            pivotal_points = self.identify_pivotal_points(ticker)
            
            # Calculate volume metrics
            avg_volume_20d = hist['Volume'].tail(20).mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 1.0
            
            # Check for consolidation (last 30 days)
            recent = hist.tail(30)
            high_30d = recent['High'].max()
            low_30d = recent['Low'].min()
            range_pct = (high_30d - low_30d) / low_30d
            
            consolidation_range = None
            days_consolidating = 0
            
            if range_pct < 0.20:  # Consolidating
                consolidation_range = (low_30d, high_30d)
                days_consolidating = 30
            
            # Determine state
            state = PatternState.CONSOLIDATING
            breakout_price = None
            entry_price = None
            volume_confirmation = False
            score = 50  # Base score
            
            # Check if we broke out of consolidation
            if consolidation_range:
                if current_price > consolidation_range[1] * 1.02:  # 2% above top
                    state = PatternState.BREAKOUT
                    breakout_price = consolidation_range[1]
                    score = 60
                    
                    # Check volume confirmation (Livermore's rule)
                    if volume_ratio > 1.5:  # 50% above average
                        state = PatternState.CONFIRMED
                        volume_confirmation = True
                        entry_price = current_price
                        score = 75
                        
                        # Check if we're trending (sustained move with volume)
                        last_5_days = hist.tail(5)
                        if last_5_days['Close'].is_monotonic_increasing:
                            state = PatternState.TRENDING
                            score = 85
                
                elif current_price < consolidation_range[0] * 0.98:  # 2% below bottom
                    state = PatternState.BREAKOUT
                    breakout_price = consolidation_range[0]
                    score = 60
                    
                    if volume_ratio > 1.5:
                        state = PatternState.CONFIRMED
                        volume_confirmation = True
                        entry_price = current_price
                        score = 75
            
            # Check for normal reaction (pullback on lower volume)
            if state in [PatternState.CONFIRMED, PatternState.TRENDING]:
                last_3_days = hist.tail(3)
                if last_3_days['Close'].iloc[-1] < last_3_days['Close'].iloc[0]:
                    if volume_ratio < 0.8:  # Volume decreased
                        state = PatternState.NORMAL_REACTION
                        score = 70  # Still valid, just resting
                    else:
                        # Pullback on HIGH volume = warning sign
                        score -= 15
            
            return LivermorePattern(
                ticker=ticker,
                current_price=current_price,
                pivotal_points=pivotal_points,
                state=state,
                entry_price=entry_price,
                volume_confirmation=volume_confirmation,
                avg_volume_20d=avg_volume_20d,
                current_volume=current_volume,
                volume_ratio=volume_ratio,
                consolidation_range=consolidation_range,
                days_consolidating=days_consolidating,
                breakout_price=breakout_price,
                score=score
            )
            
        except Exception as e:
            print(f"Error detecting pattern for {ticker}: {e}")
            return None
    
    def get_signal_for_convergence(self, ticker: str) -> Optional[Dict]:
        """
        Generate signal for convergence engine
        Returns dict with score, reasoning, data
        """
        
        pattern = self.detect_pattern_state(ticker)
        
        if not pattern:
            return None
        
        # Build reasoning
        reasoning_parts = []
        
        if pattern.state == PatternState.CONSOLIDATING:
            if pattern.consolidation_range:
                reasoning_parts.append(f"📊 Consolidating {pattern.days_consolidating}d in ${pattern.consolidation_range[0]:.2f}-${pattern.consolidation_range[1]:.2f}")
            else:
                reasoning_parts.append(f"📊 Price action stable")
        
        elif pattern.state == PatternState.BREAKOUT:
            reasoning_parts.append(f"🚀 Breakout at ${pattern.breakout_price:.2f}")
            if not pattern.volume_confirmation:
                reasoning_parts.append("⚠️ No volume confirmation yet")
        
        elif pattern.state == PatternState.CONFIRMED:
            reasoning_parts.append(f"✅ Breakout CONFIRMED with {pattern.volume_ratio:.1f}x volume")
            reasoning_parts.append(f"Entry: ${pattern.entry_price:.2f}")
        
        elif pattern.state == PatternState.NORMAL_REACTION:
            reasoning_parts.append(f"📉 Normal reaction (pullback on low volume {pattern.volume_ratio:.1f}x)")
            reasoning_parts.append("💪 Pattern intact - SIT TIGHT")
        
        elif pattern.state == PatternState.TRENDING:
            reasoning_parts.append(f"🔥 TRENDING with volume confirmation")
            reasoning_parts.append(f"Entry: ${pattern.entry_price:.2f} → ${pattern.current_price:.2f}")
        
        # Add pivotal points
        strong_pivotals = [p for p in pattern.pivotal_points if p.strength >= 80]
        if strong_pivotals:
            reasoning_parts.append(f"🎯 {len(strong_pivotals)} strong pivotal points identified")
        
        reasoning = " | ".join(reasoning_parts)
        
        return {
            'score': pattern.score,
            'reasoning': reasoning,
            'data': {
                'state': pattern.state.value,
                'volume_confirmation': pattern.volume_confirmation,
                'volume_ratio': pattern.volume_ratio,
                'consolidation_range': pattern.consolidation_range,
                'breakout_price': pattern.breakout_price,
                'pivotal_points': len(pattern.pivotal_points),
                'strong_pivotals': len(strong_pivotals)
            }
        }

def format_livermore_report(ticker: str, pattern: LivermorePattern) -> str:
    """Format pattern for display"""
    
    if not pattern:
        return f"\n❌ {ticker}: No pattern data"
    
    report = f"\n{'=' * 70}\n"
    report += f"📊 {ticker} - LIVERMORE PATTERN ANALYSIS\n"
    report += f"{'=' * 70}\n"
    
    report += f"\n💰 Current Price: ${pattern.current_price:.2f}\n"
    report += f"📈 Pattern State: {pattern.state.value.upper()}\n"
    
    if pattern.consolidation_range:
        report += f"📦 Consolidation: ${pattern.consolidation_range[0]:.2f} - ${pattern.consolidation_range[1]:.2f} ({pattern.days_consolidating} days)\n"
    
    if pattern.breakout_price:
        report += f"🚀 Breakout Price: ${pattern.breakout_price:.2f}\n"
    
    if pattern.entry_price:
        report += f"🎯 Entry Price: ${pattern.entry_price:.2f}\n"
    
    report += f"\n📊 Volume Analysis:\n"
    report += f"   Current: {pattern.current_volume:,.0f}\n"
    report += f"   20-day Avg: {pattern.avg_volume_20d:,.0f}\n"
    report += f"   Ratio: {pattern.volume_ratio:.2f}x\n"
    report += f"   Confirmation: {'✅ YES' if pattern.volume_confirmation else '❌ NO'}\n"
    
    report += f"\n🎯 Pivotal Points ({len(pattern.pivotal_points)}):\n"
    for pp in sorted(pattern.pivotal_points, key=lambda x: x.strength, reverse=True)[:5]:
        report += f"   ${pp.price:.2f} - {pp.point_type.value} (strength: {pp.strength}/100)\n"
    
    report += f"\n🎲 Livermore Score: {pattern.score}/100\n"
    
    return report

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("🎯 LIVERMORE PIVOTAL POINT TRACKER TEST")
    print("=" * 70)
    
    tracker = PivotalPointTracker()
    
    # Test with current holdings
    test_tickers = ['IBRX', 'MU', 'SMCI', 'IONQ', 'NVDA']
    
    for ticker in test_tickers:
        print(f"\n🔍 Analyzing {ticker}...")
        pattern = tracker.detect_pattern_state(ticker)
        
        if pattern:
            print(format_livermore_report(ticker, pattern))
            
            signal = tracker.get_signal_for_convergence(ticker)
            print(f"\n📡 Signal for Convergence:")
            print(f"   Score: {signal['score']}/100")
            print(f"   Reasoning: {signal['reasoning']}")
        else:
            print(f"   ❌ No pattern detected")
    
    print("\n" + "=" * 70)
    print("✅ LIVERMORE TRACKER TEST COMPLETE")
    print("=" * 70)
