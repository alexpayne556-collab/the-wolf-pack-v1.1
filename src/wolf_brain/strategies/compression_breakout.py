#!/usr/bin/env python3
"""
🐺 WOLF PACK EDGE #2: COMPRESSION BREAKOUT STRATEGY

"Find stocks sleeping (flat + low volume), wait for catalyst to wake them up,
ride the boom. Enter on first pullback to VWAP, not the initial spike."

THE PROCESS:
1. 4AM - Scanner runs, finds pre-market movers
2. Check chart - Was it FLAT before today? (compression)
3. Check news - Is there a REAL catalyst?
4. Check volume - Is volume 10x+ normal?
5. IF ALL YES → Flag for entry on first pullback to VWAP

ENTRY RULES:
- Wait for first pullback to VWAP (not the spike!)
- Volume must confirm (still elevated)
- Set stop below VWAP or LOD

EXIT RULES:
- Scale out at 1R, 2R, 3R
- Trail stop after 2R
- Never give back more than 50% of gains
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

log = logging.getLogger('wolf_brain')


class CompressionBreakoutStrategy:
    """
    COMPRESSION BREAKOUT DETECTOR
    
    Finds stocks that were "sleeping" (flat, low volume) and just woke up
    with a catalyst. These are the CLEANEST setups because:
    - No bag holders from recent moves
    - Clear support/resistance levels
    - Fresh momentum = strong follow-through
    """
    
    def __init__(self):
        self.name = "Compression Breakout"
        self.min_compression_days = 5  # At least 5 days of flatness
        self.max_range_pct = 10  # Max 10% range during compression
        self.min_volume_ratio = 5  # Today's volume must be 5x+ average
        self.min_gap_pct = 5  # Minimum gap to trigger
        
    def check_compression(self, ticker: str, days: int = 20) -> Optional[Dict]:
        """
        Check if a stock has been in compression (flat, boring, sleeping)
        
        COMPRESSION CRITERIA:
        - Trading in tight range (< 10% high-to-low)
        - Volume below average (sleeping)
        - No major news/moves for 5+ days
        """
        if not YF_AVAILABLE:
            return None
            
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f'{days}d')
            
            if len(hist) < 10:
                return None
            
            # Exclude today - we want PRIOR compression
            prior_hist = hist[:-1] if len(hist) > 1 else hist
            
            # Calculate range during compression period
            high = prior_hist['High'].max()
            low = prior_hist['Low'].min()
            range_pct = (high - low) / low * 100 if low > 0 else 0
            
            # Average volume during compression
            avg_volume = prior_hist['Volume'].mean()
            
            # Check for declining volume (sleeping)
            recent_vol = prior_hist['Volume'].tail(5).mean() if len(prior_hist) >= 5 else avg_volume
            vol_declining = recent_vol < avg_volume
            
            # Calculate "flatness score" (lower = more compressed)
            daily_ranges = ((prior_hist['High'] - prior_hist['Low']) / prior_hist['Low'] * 100)
            avg_daily_range = daily_ranges.mean()
            
            # Compression score (0-100, higher = better compression)
            compression_score = 0
            
            if range_pct < 5:
                compression_score += 40
            elif range_pct < 10:
                compression_score += 25
            elif range_pct < 15:
                compression_score += 10
                
            if avg_daily_range < 2:
                compression_score += 30
            elif avg_daily_range < 4:
                compression_score += 20
            elif avg_daily_range < 6:
                compression_score += 10
                
            if vol_declining:
                compression_score += 20
                
            # Count consecutive flat days
            flat_days = 0
            for i in range(len(daily_ranges) - 1, -1, -1):
                if daily_ranges.iloc[i] < 3:  # Less than 3% daily range
                    flat_days += 1
                else:
                    break
            
            compression_score += min(flat_days * 2, 10)  # Bonus for consecutive flat days
            
            return {
                'ticker': ticker,
                'is_compressed': compression_score >= 50,
                'compression_score': compression_score,
                'range_pct': range_pct,
                'avg_daily_range': avg_daily_range,
                'avg_volume': avg_volume,
                'flat_days': flat_days,
                'vol_declining': vol_declining,
                'high': high,
                'low': low,
            }
            
        except Exception as e:
            log.debug(f"Compression check error {ticker}: {e}")
            return None
    
    def check_breakout(self, ticker: str, compression_data: Dict) -> Optional[Dict]:
        """
        Check if the compressed stock is NOW breaking out
        
        BREAKOUT CRITERIA:
        - Gap up 5%+ from compression range
        - Volume 5x+ average (waking up!)
        - Breaking above compression high
        """
        if not YF_AVAILABLE:
            return None
            
        try:
            stock = yf.Ticker(ticker)
            
            # Get today's data
            today = stock.history(period='1d')
            if today.empty:
                return None
            
            current_price = today['Close'].iloc[-1]
            today_volume = today['Volume'].iloc[-1]
            today_open = today['Open'].iloc[-1]
            
            # Calculate gap from compression high
            compression_high = compression_data['high']
            compression_low = compression_data['low']
            avg_volume = compression_data['avg_volume']
            
            gap_from_high = (current_price - compression_high) / compression_high * 100
            gap_from_close = (today_open - compression_high) / compression_high * 100
            
            # Volume ratio
            volume_ratio = today_volume / avg_volume if avg_volume > 0 else 1
            
            # Is it breaking out?
            is_breakout = (
                gap_from_high > 0 and  # Above compression high
                volume_ratio >= self.min_volume_ratio  # Volume confirming
            )
            
            # Breakout strength score
            breakout_score = 0
            
            if gap_from_high > 20:
                breakout_score += 40
            elif gap_from_high > 10:
                breakout_score += 30
            elif gap_from_high > 5:
                breakout_score += 20
            elif gap_from_high > 0:
                breakout_score += 10
                
            if volume_ratio > 20:
                breakout_score += 40
            elif volume_ratio > 10:
                breakout_score += 30
            elif volume_ratio > 5:
                breakout_score += 20
            elif volume_ratio > 2:
                breakout_score += 10
            
            return {
                'ticker': ticker,
                'is_breakout': is_breakout,
                'breakout_score': breakout_score,
                'current_price': current_price,
                'compression_high': compression_high,
                'compression_low': compression_low,
                'gap_from_high_pct': gap_from_high,
                'volume_ratio': volume_ratio,
                'today_volume': today_volume,
                'avg_volume': avg_volume,
            }
            
        except Exception as e:
            log.debug(f"Breakout check error {ticker}: {e}")
            return None
    
    def calculate_entry_levels(self, ticker: str, breakout_data: Dict) -> Dict:
        """
        Calculate entry levels for the pullback entry
        
        ENTRY STRATEGY:
        - Wait for pullback to VWAP
        - Or pullback to breakout level (old resistance = new support)
        - Stop below VWAP or LOD
        """
        current = breakout_data['current_price']
        compression_high = breakout_data['compression_high']
        compression_low = breakout_data['compression_low']
        
        # Entry zones
        vwap_estimate = current * 0.97  # Rough VWAP estimate (3% below current)
        pullback_entry = compression_high * 1.02  # Just above breakout level
        
        # Stop loss
        stop_loss = min(vwap_estimate * 0.97, compression_high * 0.95)
        
        # Risk calculation
        risk_per_share = current - stop_loss
        
        # Targets (R multiples)
        target_1r = current + risk_per_share
        target_2r = current + (risk_per_share * 2)
        target_3r = current + (risk_per_share * 3)
        
        return {
            'ticker': ticker,
            'current_price': current,
            'entry_zone_high': current,  # Can enter now if strong
            'entry_zone_low': pullback_entry,  # Better entry on pullback
            'vwap_estimate': vwap_estimate,
            'stop_loss': stop_loss,
            'risk_per_share': risk_per_share,
            'target_1r': target_1r,
            'target_2r': target_2r,
            'target_3r': target_3r,
            'risk_reward': (target_2r - current) / risk_per_share if risk_per_share > 0 else 0,
        }
    
    def scan_for_setups(self, tickers: List[str]) -> List[Dict]:
        """
        Scan a list of tickers for compression breakout setups
        
        Returns ranked list of setups with all data
        """
        setups = []
        
        for ticker in tickers:
            try:
                # Step 1: Check compression
                compression = self.check_compression(ticker)
                if not compression or not compression['is_compressed']:
                    continue
                
                # Step 2: Check breakout
                breakout = self.check_breakout(ticker, compression)
                if not breakout or not breakout['is_breakout']:
                    continue
                
                # Step 3: Calculate entry levels
                entry = self.calculate_entry_levels(ticker, breakout)
                
                # Combined score
                total_score = compression['compression_score'] + breakout['breakout_score']
                
                setups.append({
                    'ticker': ticker,
                    'total_score': total_score,
                    'compression': compression,
                    'breakout': breakout,
                    'entry': entry,
                    'signal': 'COMPRESSION_BREAKOUT',
                    'action': 'BUY_ON_PULLBACK',
                })
                
            except Exception as e:
                log.debug(f"Setup scan error {ticker}: {e}")
        
        # Sort by total score
        setups.sort(key=lambda x: x['total_score'], reverse=True)
        
        return setups
    
    def format_alert(self, setup: Dict) -> str:
        """Format a setup for display/logging"""
        ticker = setup['ticker']
        comp = setup['compression']
        brk = setup['breakout']
        entry = setup['entry']
        
        return f"""
🔥 COMPRESSION BREAKOUT: {ticker}
{'='*50}
📊 COMPRESSION:
   Score: {comp['compression_score']}/100
   Range: {comp['range_pct']:.1f}% over {comp['flat_days']} flat days
   Volume declining: {'Yes' if comp['vol_declining'] else 'No'}

🚀 BREAKOUT:
   Score: {brk['breakout_score']}/100
   Gap from high: +{brk['gap_from_high_pct']:.1f}%
   Volume: {brk['volume_ratio']:.1f}x average

💰 TRADE PLAN:
   Current: ${brk['current_price']:.2f}
   Entry Zone: ${entry['entry_zone_low']:.2f} - ${entry['entry_zone_high']:.2f}
   Stop Loss: ${entry['stop_loss']:.2f}
   Target 1R: ${entry['target_1r']:.2f}
   Target 2R: ${entry['target_2r']:.2f}
   Target 3R: ${entry['target_3r']:.2f}
   Risk/Reward: {entry['risk_reward']:.1f}:1

⚡ ACTION: Wait for pullback to ${entry['entry_zone_low']:.2f} or VWAP
"""


# ============ STANDALONE TEST ============

def test_strategy():
    """Test the compression breakout strategy"""
    print("🐺 COMPRESSION BREAKOUT SCANNER")
    print("=" * 60)
    
    strategy = CompressionBreakoutStrategy()
    
    # Test tickers - mix of potential setups
    test_tickers = [
        'AAPL', 'TSLA', 'NVDA', 'AMD', 'INTC',
        'SAVA', 'VRCA', 'AQST', 'IRON', 'VKTX',
        'IONQ', 'RGTI', 'PLTR', 'GME', 'AMC',
    ]
    
    print(f"Scanning {len(test_tickers)} tickers...")
    print()
    
    setups = strategy.scan_for_setups(test_tickers)
    
    if setups:
        print(f"Found {len(setups)} compression breakout setups:")
        print()
        for setup in setups[:5]:  # Top 5
            print(strategy.format_alert(setup))
    else:
        print("No compression breakout setups found.")
        print("This is normal - these setups are RARE but POWERFUL when they occur.")
        print()
        
        # Show compression data anyway
        print("Compression analysis (stocks may break out later):")
        for ticker in test_tickers[:5]:
            comp = strategy.check_compression(ticker)
            if comp:
                emoji = "💤" if comp['is_compressed'] else "📊"
                print(f"  {emoji} {ticker}: Score {comp['compression_score']}/100 | Range: {comp['range_pct']:.1f}% | Flat days: {comp['flat_days']}")


if __name__ == '__main__':
    test_strategy()
