"""
SECTOR FLOW TRACKER (Layer 7)
The Basket Intelligence System

Tracks sector rotation, correlation baskets, small cap outperformance.
Provides 4th signal type for convergence engine.

From THE_BIG_PICTURE.md:
- Daily sector % change tracking
- Correlation matrix (identify baskets)
- Rotation detection (money moving where?)
- Small cap vs large cap spread
- Integration with convergence scoring

Edge: Know which sectors are HOT vs COLD. Avoid traps (quantum basket dump).
Ride sector waves (defense +12% = hunt defense names).
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os


# =============================================================================
# SECTOR DEFINITIONS
# =============================================================================

class SectorETF(Enum):
    """Sector ETF proxies for tracking flow"""
    # Major sectors
    TECH = "XLK"          # Technology
    HEALTHCARE = "XLV"    # Healthcare
    FINANCIALS = "XLF"    # Financials
    ENERGY = "XLE"        # Energy
    INDUSTRIALS = "XLI"   # Industrials
    CONSUMER_DISC = "XLY" # Consumer Discretionary
    CONSUMER_STAPLES = "XLP"  # Consumer Staples
    UTILITIES = "XLU"     # Utilities
    MATERIALS = "XLB"     # Materials
    REAL_ESTATE = "XLRE"  # Real Estate
    COMM_SERVICES = "XLC" # Communication Services
    
    # Special tracking
    DEFENSE = "ITA"       # Defense & Aerospace
    BIOTECH = "XBI"       # Biotech
    SEMIS = "SOXX"        # Semiconductors
    URANIUM = "URA"       # Uranium & Nuclear
    QUANTUM = "QTUM"      # Quantum Computing
    AI = "BOTZ"           # AI & Robotics


# Friendly sector names
SECTOR_NAMES = {
    "XLK": "Technology",
    "XLV": "Healthcare", 
    "XLF": "Financials",
    "XLE": "Energy",
    "XLI": "Industrials",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
    "ITA": "Defense & Aerospace",
    "XBI": "Biotech",
    "SOXX": "Semiconductors",
    "URA": "Uranium & Nuclear",
    "QTUM": "Quantum Computing",
    "BOTZ": "AI & Robotics",
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class SectorSnapshot:
    """Single sector performance snapshot"""
    ticker: str
    name: str
    change_1d: float
    change_5d: float
    change_1m: float
    volume_ratio: float  # vs 20-day avg
    heat_score: int  # 0-100, combination of % change + volume
    
    def get_heat_emoji(self) -> str:
        """Visual heat indicator"""
        if self.heat_score >= 80:
            return "🔥"
        elif self.heat_score >= 60:
            return "🟠"
        elif self.heat_score >= 40:
            return "🟡"
        elif self.heat_score >= 20:
            return "❄️"
        else:
            return "🧊"


@dataclass
class SectorFlow:
    """Complete sector flow analysis"""
    timestamp: datetime
    sectors: List[SectorSnapshot]
    hottest_sector: SectorSnapshot
    coldest_sector: SectorSnapshot
    small_cap_spread: float  # IWM vs SPY performance
    rotation_signal: Optional[str]  # "INTO_CYCLICALS", "INTO_DEFENSIVES", None


class RotationState(Enum):
    """Market rotation states"""
    INTO_CYCLICALS = "INTO_CYCLICALS"  # Energy, Industrials, Materials heating
    INTO_DEFENSIVES = "INTO_DEFENSIVES"  # Utilities, Staples, Healthcare heating
    INTO_GROWTH = "INTO_GROWTH"  # Tech, Comm Services heating
    INTO_VALUE = "INTO_VALUE"  # Financials, Energy heating
    RISK_ON = "RISK_ON"  # Small caps outperforming
    RISK_OFF = "RISK_OFF"  # Small caps underperforming
    NO_ROTATION = "NO_ROTATION"


# =============================================================================
# SECTOR FLOW TRACKER
# =============================================================================

class SectorFlowTracker:
    """
    Track sector rotation and basket performance
    Provides sector heat signal for convergence
    """
    
    def __init__(self, cache_path: str = "services/data/sector_flow.json"):
        self.cache_path = cache_path
        self.sectors = [etf.value for etf in SectorETF]
        self.last_flow: Optional[SectorFlow] = None
        
    def fetch_sector_data(self, lookback_days: int = 30) -> List[SectorSnapshot]:
        """
        Fetch sector ETF performance data
        Returns list of sector snapshots
        """
        snapshots = []
        
        for ticker in self.sectors:
            try:
                etf = yf.Ticker(ticker)
                hist = etf.history(period="2mo")  # Get 2 months for volume avg
                
                if len(hist) < 20:
                    continue
                
                # Calculate metrics
                current = hist['Close'].iloc[-1]
                day_1 = hist['Close'].iloc[-2]
                day_5 = hist['Close'].iloc[-6] if len(hist) >= 6 else day_1
                day_30 = hist['Close'].iloc[-31] if len(hist) >= 31 else day_5
                
                change_1d = ((current - day_1) / day_1) * 100
                change_5d = ((current - day_5) / day_5) * 100
                change_1m = ((current - day_30) / day_30) * 100
                
                # Volume analysis
                current_vol = hist['Volume'].iloc[-1]
                avg_vol = hist['Volume'].iloc[-21:-1].mean()
                volume_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
                
                # Heat score (weighted: 1d=20%, 5d=50%, 1m=30% + volume bonus)
                price_score = (
                    (change_1d * 0.2) + 
                    (change_5d * 0.5) + 
                    (change_1m * 0.3)
                )
                
                # Normalize to 0-100 range (assume -10% to +10% is normal range)
                normalized_score = ((price_score + 10) / 20) * 80  # 80 points for price
                volume_bonus = min((volume_ratio - 1.0) * 20, 20)  # Up to 20 points for volume
                heat_score = max(0, min(100, int(normalized_score + volume_bonus)))
                
                snapshot = SectorSnapshot(
                    ticker=ticker,
                    name=SECTOR_NAMES.get(ticker, ticker),
                    change_1d=change_1d,
                    change_5d=change_5d,
                    change_1m=change_1m,
                    volume_ratio=volume_ratio,
                    heat_score=heat_score
                )
                
                snapshots.append(snapshot)
                
            except Exception as e:
                print(f"⚠️  Error fetching {ticker}: {e}")
                continue
        
        return snapshots
    
    def analyze_rotation(self, snapshots: List[SectorSnapshot]) -> Optional[RotationState]:
        """
        Detect sector rotation patterns
        Returns rotation signal
        """
        if len(snapshots) < 5:
            return RotationState.NO_ROTATION
        
        # Group sectors by type
        cyclicals = [s for s in snapshots if s.ticker in ['XLE', 'XLI', 'XLB']]
        defensives = [s for s in snapshots if s.ticker in ['XLU', 'XLP', 'XLV']]
        growth = [s for s in snapshots if s.ticker in ['XLK', 'XLC']]
        value = [s for s in snapshots if s.ticker in ['XLF', 'XLE']]
        
        # Calculate average 5-day performance
        cyc_avg = sum(s.change_5d for s in cyclicals) / len(cyclicals) if cyclicals else 0
        def_avg = sum(s.change_5d for s in defensives) / len(defensives) if defensives else 0
        growth_avg = sum(s.change_5d for s in growth) / len(growth) if growth else 0
        value_avg = sum(s.change_5d for s in value) / len(value) if value else 0
        
        # Detect rotation (threshold: >2% difference)
        if cyc_avg - def_avg > 2:
            return RotationState.INTO_CYCLICALS
        elif def_avg - cyc_avg > 2:
            return RotationState.INTO_DEFENSIVES
        elif growth_avg - value_avg > 2:
            return RotationState.INTO_GROWTH
        elif value_avg - growth_avg > 2:
            return RotationState.INTO_VALUE
        else:
            return RotationState.NO_ROTATION
    
    def calculate_small_cap_spread(self) -> float:
        """
        Calculate small cap vs large cap performance
        Positive = small caps outperforming (RISK ON)
        Negative = small caps underperforming (RISK OFF)
        """
        try:
            # IWM = Russell 2000 (small caps)
            # SPY = S&P 500 (large caps)
            iwm = yf.Ticker("IWM")
            spy = yf.Ticker("SPY")
            
            iwm_hist = iwm.history(period="1mo")
            spy_hist = spy.history(period="1mo")
            
            if len(iwm_hist) < 20 or len(spy_hist) < 20:
                return 0.0
            
            # 20-day performance
            iwm_change = ((iwm_hist['Close'].iloc[-1] - iwm_hist['Close'].iloc[-21]) / iwm_hist['Close'].iloc[-21]) * 100
            spy_change = ((spy_hist['Close'].iloc[-1] - spy_hist['Close'].iloc[-21]) / spy_hist['Close'].iloc[-21]) * 100
            
            spread = iwm_change - spy_change
            return spread
            
        except Exception as e:
            print(f"⚠️  Error calculating small cap spread: {e}")
            return 0.0
    
    def scan_sector_flow(self) -> SectorFlow:
        """
        Main entry point: Scan all sectors and analyze flow
        Returns complete sector flow analysis
        """
        print("📊 Scanning sector flow...")
        
        # Fetch sector data
        snapshots = self.fetch_sector_data()
        
        if not snapshots:
            raise Exception("Failed to fetch sector data")
        
        # Sort by heat score
        snapshots.sort(key=lambda s: s.heat_score, reverse=True)
        
        # Identify hottest and coldest
        hottest = snapshots[0]
        coldest = snapshots[-1]
        
        # Detect rotation
        rotation = self.analyze_rotation(snapshots)
        
        # Small cap spread
        spread = self.calculate_small_cap_spread()
        
        # Create flow object
        flow = SectorFlow(
            timestamp=datetime.now(),
            sectors=snapshots,
            hottest_sector=hottest,
            coldest_sector=coldest,
            small_cap_spread=spread,
            rotation_signal=rotation.value if rotation else None
        )
        
        self.last_flow = flow
        self._save_cache(flow)
        
        return flow
    
    def get_sector_signal_for_convergence(self, ticker: str) -> Optional[Dict]:
        """
        Get sector heat signal for convergence engine
        
        Returns signal dict: {'score': int, 'reasoning': str, 'data': dict}
        """
        if not self.last_flow:
            self.scan_sector_flow()
        
        # Map ticker to sector (simplified - would use real sector mapping)
        # For now, return sector heat based on ticker's sector
        sector_map = {
            'IBRX': 'XBI',  # Biotech
            'MU': 'SOXX',   # Semis
            'KTOS': 'ITA',  # Defense
            'SMCI': 'SOXX', # Semis
            'IONQ': 'QTUM', # Quantum
            'RGTI': 'QTUM', # Quantum
        }
        
        sector_etf = sector_map.get(ticker.upper())
        if not sector_etf:
            return None
        
        # Find sector snapshot
        sector = next((s for s in self.last_flow.sectors if s.ticker == sector_etf), None)
        if not sector:
            return None
        
        # Generate signal
        score = sector.heat_score
        emoji = sector.get_heat_emoji()
        reasoning = f"{sector.name} sector {emoji} ({sector.change_5d:+.1f}% this week)"
        
        return {
            'score': score,
            'reasoning': reasoning,
            'data': {
                'sector': sector.name,
                'sector_ticker': sector.ticker,
                'change_1d': sector.change_1d,
                'change_5d': sector.change_5d,
                'change_1m': sector.change_1m,
                'heat_score': sector.heat_score
            }
        }
    
    def _save_cache(self, flow: SectorFlow):
        """Save sector flow to cache file"""
        try:
            data = {
                'timestamp': flow.timestamp.isoformat(),
                'sectors': [
                    {
                        'ticker': s.ticker,
                        'name': s.name,
                        'change_1d': s.change_1d,
                        'change_5d': s.change_5d,
                        'change_1m': s.change_1m,
                        'volume_ratio': s.volume_ratio,
                        'heat_score': s.heat_score
                    }
                    for s in flow.sectors
                ],
                'small_cap_spread': flow.small_cap_spread,
                'rotation_signal': flow.rotation_signal
            }
            
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Error saving cache: {e}")


# =============================================================================
# FORMATTING & DISPLAY
# =============================================================================

def format_sector_heatmap(flow: SectorFlow) -> str:
    """
    Format sector flow as visual heatmap
    """
    lines = []
    lines.append("\n🌊 SECTOR FLOW ANALYSIS")
    lines.append("━" * 60)
    
    # Heatmap
    lines.append("\n🔥 SECTOR HEATMAP (5-Day Performance):")
    for sector in flow.sectors:
        emoji = sector.get_heat_emoji()
        bar_length = int((sector.heat_score / 100) * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        lines.append(f"  {emoji} {sector.name:25s} {bar} {sector.heat_score}/100 ({sector.change_5d:+.1f}%)")
    
    # Key insights
    lines.append(f"\n🔥 HOTTEST: {flow.hottest_sector.name} ({flow.hottest_sector.change_5d:+.1f}%)")
    lines.append(f"❄️  COLDEST: {flow.coldest_sector.name} ({flow.coldest_sector.change_5d:+.1f}%)")
    
    # Small cap spread
    if flow.small_cap_spread > 2:
        lines.append(f"\n🟢 SMALL CAPS: Outperforming (+{flow.small_cap_spread:.1f}% vs SPY) - RISK ON")
    elif flow.small_cap_spread < -2:
        lines.append(f"\n🔴 SMALL CAPS: Underperforming ({flow.small_cap_spread:.1f}% vs SPY) - RISK OFF")
    else:
        lines.append(f"\n🟡 SMALL CAPS: In-line ({flow.small_cap_spread:+.1f}% vs SPY)")
    
    # Rotation signal
    if flow.rotation_signal and flow.rotation_signal != "NO_ROTATION":
        lines.append(f"\n💫 ROTATION DETECTED: {flow.rotation_signal.replace('_', ' ')}")
    
    return "\n".join(lines)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == '__main__':
    print("🔥 SECTOR FLOW TRACKER TEST")
    print("="*60)
    
    tracker = SectorFlowTracker()
    
    # Scan sector flow
    flow = tracker.scan_sector_flow()
    
    # Display heatmap
    print(format_sector_heatmap(flow))
    
    # Test convergence integration
    print("\n\n🧠 CONVERGENCE INTEGRATION TEST:")
    print("━" * 60)
    
    test_tickers = ['IBRX', 'MU', 'KTOS', 'SMCI', 'IONQ']
    for ticker in test_tickers:
        signal = tracker.get_sector_signal_for_convergence(ticker)
        if signal:
            print(f"\n{ticker}: {signal['score']}/100")
            print(f"  → {signal['reasoning']}")
        else:
            print(f"\n{ticker}: No sector mapping")
    
    print("\n" + "="*60)
    print("✅ Sector flow tracker test complete")
