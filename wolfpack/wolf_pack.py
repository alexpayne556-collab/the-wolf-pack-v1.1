#!/usr/bin/env python3
"""
🐺 WOLF PACK - UNIFIED TRADING INTELLIGENCE SYSTEM
All modules feeding each other. One interface. Complete edge.

NOW CONNECTED TO:
- Fenrir position tracker (your holdings)
- Fenrir scanner v2 (market opportunities)
- WolfPack database (99 stocks daily, pattern learnings)
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import pandas as pd

# Add paths for all modules
fenrir_path = os.path.join(os.path.dirname(__file__), 'fenrir')
services_path = os.path.join(os.path.dirname(__file__), 'services')
sys.path.insert(0, fenrir_path)
sys.path.insert(0, services_path)

# Import all Fenrir modules
from position_health_checker import check_all_positions, HOLDINGS
from thesis_tracker import THESIS_DATABASE

# Import WolfPack database helpers
from config import DB_PATH

# Import BR0KKR service
try:
    from br0kkr_service import scan_institutional_activity
    BR0KKR_AVAILABLE = True
except ImportError:
    print("⚠️  BR0KKR service not available")
    BR0KKR_AVAILABLE = False

# Import Convergence service
try:
    from convergence_service import ConvergenceEngine, format_convergence_report
    CONVERGENCE_AVAILABLE = True
except ImportError:
    print("⚠️  Convergence service not available")
    CONVERGENCE_AVAILABLE = False

# Import Catalyst service
try:
    from catalyst_service import CatalystService, format_catalyst_calendar
    CATALYST_AVAILABLE = True
except ImportError:
    print("⚠️  Catalyst service not available")
    CATALYST_AVAILABLE = False

# Import Sector Flow Tracker
try:
    from sector_flow_tracker import SectorFlowTracker, format_sector_heatmap
    SECTOR_AVAILABLE = True
except ImportError:
    print("⚠️  Sector flow tracker not available")
    SECTOR_AVAILABLE = False

# Import Risk Manager
try:
    from risk_manager import RiskManager, format_position_size_report, format_portfolio_risk_report
    RISK_AVAILABLE = True
except ImportError:
    print("⚠️  Risk manager not available")
    RISK_AVAILABLE = False

# Import Danger Zone - Layer 0 trap detection
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'core'))
    from danger_zone import DangerZone
    DANGER_ZONE_AVAILABLE = True
except ImportError:
    print("⚠️  Danger Zone not available")
    DANGER_ZONE_AVAILABLE = False

# Import News Service
try:
    from news_service import NewsService, format_news_report
    NEWS_AVAILABLE = True
except ImportError:
    print("⚠️  News service not available")
    NEWS_AVAILABLE = False

# Import Earnings Service
try:
    from earnings_service import EarningsService, format_earnings_report
    EARNINGS_AVAILABLE = True
except ImportError:
    print("⚠️  Earnings service not available")
    EARNINGS_AVAILABLE = False

# Scanner V2 - import the main scanning function
try:
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError:
    print("⚠️  Missing dependencies. Run: pip install yfinance")
    sys.exit(1)

class WolfPack:
    """Unified trading intelligence - all systems working together"""
    
    def __init__(self, account_value: float = 100000):
        self.portfolio_data = None
        
        # Initialize danger zone (Layer 0 - runs FIRST)
        self.danger_zone = DangerZone() if DANGER_ZONE_AVAILABLE else None
        self.market_scan = None
        self.br0kkr_data = None  # BR0KKR institutional tracking
        self.catalyst_data = None  # Catalyst calendar
        self.sector_flow = None  # Sector flow tracker
        self.news_data = None  # News intelligence
        self.earnings_data = None  # Earnings intelligence
        self.convergence_signals = None  # Convergence engine results
        self.pattern_data = None  # WolfPack database patterns
        self.db_connection = None
        self.account_value = account_value
        
        # Initialize convergence engine
        if CONVERGENCE_AVAILABLE:
            self.convergence_engine = ConvergenceEngine()
        else:
            self.convergence_engine = None
        
        # Initialize catalyst service
        if CATALYST_AVAILABLE:
            self.catalyst_service = CatalystService(db_path="services/data/catalysts.json")
        else:
            self.catalyst_service = None
        
        # Initialize sector flow tracker
        if SECTOR_AVAILABLE:
            self.sector_tracker = SectorFlowTracker(cache_path="services/data/sector_flow.json")
        else:
            self.sector_tracker = None
        
        # Initialize risk manager
        if RISK_AVAILABLE:
            self.risk_manager = RiskManager(account_value=account_value)
        else:
            self.risk_manager = None
        
        # Initialize news service
        if NEWS_AVAILABLE:
            try:
                self.news_service = NewsService()
            except ValueError as e:
                print(f"⚠️  News service disabled: {e}")
                self.news_service = None
        else:
            self.news_service = None
        
        # Initialize earnings service
        if EARNINGS_AVAILABLE:
            try:
                self.earnings_service = EarningsService()
            except ValueError as e:
                print(f"⚠️  Earnings service disabled: {e}")
                self.earnings_service = None
        else:
            self.earnings_service = None
        
        # Scanner tickers - Load from wounded prey universe or use defaults
        self.scan_universe = self._load_scan_universe()
    
    def _load_scan_universe(self):
        """Load scan universe from wounded prey file or use defaults"""
        universe_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'wounded_prey_universe.json')
        
        if os.path.exists(universe_file):
            try:
                with open(universe_file, 'r') as f:
                    data = json.load(f)
                wounded_prey = data.get('wounded_prey', [])
                
                # Extract tickers, sorted by score
                tickers = [p['ticker'] for p in wounded_prey]
                
                print(f"📊 Loaded {len(tickers)} wounded prey from universe scan")
                return tickers
            except:
                pass
        
        # Default universe if file doesn't exist
        return [
            # AI MEGA CAPS
            'NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'TSLA', 'AAPL',
            # AI PURE PLAYS
            'PLTR', 'ARM', 'SMCI', 'AVGO',
            # QUANTUM
            'IONQ', 'RGTI', 'QBTS',
            # SEMICONDUCTORS
            'TSM', 'INTC', 'QCOM', 'AMAT', 'ASML',
            # BIOTECH
            'MRNA', 'BNTX', 'GILD', 'VRTX', 'CRSP', 'IBRX',
            # DEFENSE
            'LMT', 'RTX', 'NOC', 'BA', 'KTOS', 'ASTS', 'RKLB',
            # URANIUM
            'UUUU', 'UEC', 'CCJ', 'DNN',
            # CRYPTO
            'MARA', 'RIOT', 'CLSK', 'COIN',
            # SPACE
            'LUNR', 'PL',
            # CLOUD/SAAS
            'SNOW', 'DDOG', 'NET', 'CRWD'
        ]
        
    def initialize(self):
        """Load all systems once at startup"""
        print("🐺 WOLF PACK INITIALIZING...")
        print("=" * 60)
        
        # Connect to WolfPack database
        print("\n🗄️  Connecting to WolfPack database...", end=" ")
        try:
            self.db_connection = sqlite3.connect(DB_PATH)
            # Quick check: how many records do we have?
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM daily_records")
            record_count = cursor.fetchone()[0]
            print(f"✅ {record_count} records available")
        except Exception as e:
            print(f"⚠️  Database not initialized (run wolfpack_db.py first)")
            self.db_connection = None
            self.db_connection = None
        
        # Load portfolio analysis
        print("📊 Loading portfolio data...", end=" ")
        health_results = check_all_positions()
        
        self.portfolio_data = {
            'positions': {},
            'dead_money': [],
            'weak': [],
            'watch': [],
            'healthy': [],
            'runners': []
        }
        
        for result in health_results:
            if 'error' in result:
                continue
                
            ticker = result['ticker']
            score = result.get('health_score', 0)
            thesis = THESIS_DATABASE.get(ticker)
            thesis_score = thesis.thesis_strength if thesis else 0
            thesis_text = thesis.what_they_do if thesis else 'No thesis'
            
            pos_data = {
                'ticker': ticker,
                'score': score,
                'thesis_score': thesis_score,
                'thesis': thesis_text,
                'health': result,
                'current_price': result.get('current_price', 0),
                'pnl_percent': result.get('pnl_percent', 0)
            }
            
            self.portfolio_data['positions'][ticker] = pos_data
            
            if score <= -5:
                self.portfolio_data['dead_money'].append(pos_data)
            elif score <= -3:
                self.portfolio_data['weak'].append(pos_data)
            elif score <= -1:
                self.portfolio_data['watch'].append(pos_data)
            elif score >= 5:
                self.portfolio_data['runners'].append(pos_data)
            else:
                self.portfolio_data['healthy'].append(pos_data)
        
        print(f"✅ {len(health_results)} positions loaded")
        
        # Load market opportunities (integrate scanner v2 logic)
        print("🔍 Scanning market...", end=" ")
        self.market_scan = self._scan_market_v2()
        print(f"✅ {len(self.market_scan)} setups found")
        
        # Scan institutional activity (BR0KKR)
        if BR0KKR_AVAILABLE:
            print("🔍 Scanning institutional activity (BR0KKR)...", end=" ")
            try:
                # Scan our holdings + watchlist tickers
                our_tickers = list(HOLDINGS.keys())
                self.br0kkr_data = scan_institutional_activity(tickers=our_tickers, days_back=14)
                alert_count = len(self.br0kkr_data.get('alerts', []))
                print(f"✅ {alert_count} signals found")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                self.br0kkr_data = {'alerts': [], 'cluster_buys': [], 'activist_filings': []}
        
        # Load catalyst calendar
        if CATALYST_AVAILABLE and self.catalyst_service:
            print("📅 Loading catalyst calendar...", end=" ")
            try:
                our_tickers = list(HOLDINGS.keys())
                self.catalyst_data = self.catalyst_service.get_catalysts_for_tickers(our_tickers)
                catalyst_count = sum(len(cats) for cats in self.catalyst_data.values())
                print(f"✅ {catalyst_count} catalysts found")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                self.catalyst_data = {}
        
        # Scan sector flow
        if SECTOR_AVAILABLE and self.sector_tracker:
            print("🌊 Scanning sector flow...", end=" ")
            try:
                self.sector_flow = self.sector_tracker.scan_sector_flow()
                print(f"✅ {len(self.sector_flow.sectors)} sectors analyzed")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                self.sector_flow = None
        
        # Scan news (only for holdings + top scanner signals)
        if NEWS_AVAILABLE and self.news_service:
            print("📰 Scanning news intelligence...", end=" ")
            try:
                self.news_data = {}
                our_tickers = list(HOLDINGS.keys())
                # Add top scanner signals
                if self.market_scan:
                    scanner_tickers = [s['ticker'] for s in self.market_scan[:10]]  # Top 10
                    our_tickers.extend(scanner_tickers)
                
                our_tickers = list(set(our_tickers))  # Deduplicate
                
                # Fetch news for each ticker (respecting API rate limits)
                for ticker in our_tickers[:15]:  # Limit to 15 to conserve API calls
                    signal = self.news_service.get_news_signal_for_convergence(ticker)
                    if signal:
                        self.news_data[ticker] = signal
                
                print(f"✅ {len(self.news_data)} tickers analyzed")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                self.news_data = {}
        
        # Scan earnings (only for holdings + watchlist)
        if EARNINGS_AVAILABLE and self.earnings_service:
            print("📊 Scanning earnings calendar...", end=" ")
            try:
                self.earnings_data = {}
                our_tickers = list(HOLDINGS.keys())
                
                # Fetch upcoming earnings
                for ticker in our_tickers:
                    signal = self.earnings_service.get_earnings_signal_for_convergence(ticker)
                    if signal:
                        self.earnings_data[ticker] = signal
                
                print(f"✅ {len(self.earnings_data)} upcoming earnings")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                self.earnings_data = {}
        
        # Calculate convergence signals (now with ALL 7 signals!)
        if CONVERGENCE_AVAILABLE and self.convergence_engine and self.market_scan:
            print("🧠 Calculating convergence signals...", end=" ")
            try:
                # Build catalyst signals for convergence
                catalyst_signals = {}
                if self.catalyst_service:
                    for ticker in [s['ticker'] for s in self.market_scan]:
                        signal = self.catalyst_service.get_catalyst_for_convergence(ticker)
                        if signal:
                            catalyst_signals[ticker] = signal
                
                # Build sector signals for convergence
                sector_signals = {}
                if self.sector_tracker:
                    for ticker in [s['ticker'] for s in self.market_scan]:
                        signal = self.sector_tracker.get_sector_signal_for_convergence(ticker)
                        if signal:
                            sector_signals[ticker] = signal
                
                # Calculate convergence with all signals
                convergence_list = []
                for setup in self.market_scan:
                    ticker = setup['ticker']
                    
                    # Scanner signal
                    scanner_signal = {
                        'score': setup.get('score', 50),
                        'reasoning': setup.get('reasoning', setup.get('type', 'Setup')),
                        'data': setup
                    }
                    
                    # BR0KKR signal (if exists)
                    br0kkr_signal = None
                    if self.br0kkr_data:
                        # Check cluster buys
                        for cluster in self.br0kkr_data.get('cluster_buys', []):
                            if cluster.ticker == ticker:
                                br0kkr_signal = {
                                    'score': cluster.get_score(),
                                    'reasoning': f"{cluster.unique_insiders} insiders bought ${cluster.total_value:,.0f}",
                                    'data': cluster
                                }
                                break
                    
                    # Catalyst signal (if exists)
                    catalyst_signal = catalyst_signals.get(ticker)
                    
                    # Sector signal (if exists)
                    sector_signal = sector_signals.get(ticker)
                    
                    # News signal (if exists)
                    news_signal = self.news_data.get(ticker) if self.news_data else None
                    
                    # Earnings signal (if exists)
                    earnings_signal = self.earnings_data.get(ticker) if self.earnings_data else None
                    
                    # Calculate convergence with ALL 7 signals
                    conv = self.convergence_engine.calculate_convergence(
                        ticker=ticker,
                        scanner_signal=scanner_signal,
                        br0kkr_signal=br0kkr_signal,
                        catalyst_signal=catalyst_signal,
                        sector_signal=sector_signal,
                        news_signal=news_signal,
                        earnings_signal=earnings_signal,
                    )
                    
                    if conv:
                        convergence_list.append(conv)
                
                self.convergence_signals = convergence_list
                print(f"✅ {len(self.convergence_signals)} convergence signals found")
            except Exception as e:
                print(f"⚠️  Error: {e}")
                import traceback
                traceback.print_exc()
                self.convergence_signals = []
        
        print("\n" + "=" * 60)
        print("✅ WOLF PACK READY\n")
    
    def _scan_market_v2(self):
        """Integrated market scanner with V2 logic"""
        setups = []
        
        def analyze_ticker(ticker):
            """Simplified scanner logic with DANGER ZONE filter (Layer 0)"""
            try:
                # LAYER 0: DANGER ZONE CHECK (RUNS FIRST!)
                # THE WOLF DOESN'T WALK INTO TRAPS.
                if DANGER_ZONE_AVAILABLE and self.danger_zone:
                    danger_result = self.danger_zone.scan(ticker)
                    
                    if danger_result['status'] == 'BLOCKED':
                        # Trap detected - skip this ticker
                        print(f"   🚫 {ticker} BLOCKED: {', '.join(danger_result['dangers'])}")
                        
                        # Add to wounded prey watchlist for later
                        self.danger_zone.add_to_wounded_prey_watchlist(
                            ticker, 
                            danger_result['dangers']
                        )
                        return None
                    # If CLEAR, proceed to opportunity analysis
                
                stock = yf.Ticker(ticker)
                hist = stock.history(period="6mo")
                
                if hist.empty or len(hist) < 50:
                    return None
                
                current_price = hist['Close'].iloc[-1]
                high_52w = hist['High'].max()
                low_52w = hist['Low'].min()
                
                # Calculate momentum
                change_7d = ((current_price / hist['Close'].iloc[-7] - 1) * 100) if len(hist) >= 7 else 0
                change_30d = ((current_price / hist['Close'].iloc[-30] - 1) * 100) if len(hist) >= 30 else 0
                
                # Distance from highs
                distance_from_high = ((current_price / high_52w - 1) * 100)
                
                # Simple pattern detection
                signal_type = "UNKNOWN"
                score = 50
                reasoning = f"{change_7d:+.1f}% (7d), {change_30d:+.1f}% (30d)"
                
                # TOO_LATE filter (from V2)
                if change_30d > 30:
                    return None  # Skip extended runners
                
                # WOUNDED PREY (core strategy)
                if distance_from_high < -30 and change_7d > 0:
                    signal_type = "WOUNDED_PREY"
                    score = 65
                    reasoning = f"Down {distance_from_high:.1f}% from highs, starting bounce"
                
                # EARLY MOMENTUM
                elif 5 < change_7d < 20 and change_30d < 25:
                    signal_type = "EARLY_MOMENTUM"
                    score = 55
                    reasoning = f"Early move: {change_7d:+.1f}% (7d), {change_30d:+.1f}% (30d)"
                
                else:
                    return None  # No clear setup
                
                # Calculate stop loss (simple version)
                stop_loss = low_52w * 1.05 if distance_from_high < -20 else current_price * 0.85
                
                return {
                    'ticker': ticker,
                    'type': signal_type,
                    'score': score,
                    'entry': current_price,
                    'stop': stop_loss,
                    'reasoning': reasoning,
                    'change_7d': change_7d,
                    'change_30d': change_30d
                }
                
            except Exception:
                return None
        
        # Parallel scanning
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(analyze_ticker, t): t for t in self.scan_universe}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    setups.append(result)
        
        # Sort by score
        setups.sort(key=lambda x: x['score'], reverse=True)
        return setups
        
    def morning_briefing(self):
        """Complete morning intelligence report"""
        print("🐺 WOLF PACK MORNING BRIEFING")
        print(f"📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}")
        print("=" * 60)
        
        # CRITICAL ALERTS
        critical_items = []
        
        # Dead money check
        if self.portfolio_data['dead_money']:
            critical_items.append({
                'level': 'CRITICAL',
                'category': 'DEAD MONEY',
                'items': self.portfolio_data['dead_money']
            })
        
        # BR0KKR institutional alerts
        if self.br0kkr_data and self.br0kkr_data.get('alerts'):
            critical_alerts = [a for a in self.br0kkr_data['alerts'] if '🔴' in a['priority'] or '🟠' in a['priority']]
            if critical_alerts:
                critical_items.append({
                    'level': 'CRITICAL',
                    'category': 'INSTITUTIONAL ACTIVITY',
                    'items': critical_alerts
                })
        
        if critical_items:
            print("\n🔴 CRITICAL ALERTS:")
            print("━" * 60)
            for alert in critical_items:
                print(f"\n{alert['category']}:")
                for item in alert['items']:
                    # Handle position alerts (dead money)
                    if 'ticker' in item and 'thesis_score' in item:
                        print(f"  • {item['ticker']}: Score {item['score']}, Thesis {item['thesis_score']}/10")
                        print(f"    → {item['thesis'][:80]}")
                    # Handle BR0KKR alerts
                    elif 'ticker' in item and 'message' in item:
                        print(f"  {item['priority']} {item['ticker']}: {item['message']} (Score: {item['score']})")
        else:
            print("\n✅ NO CRITICAL ALERTS")
        
        # YOUR POSITIONS
        print("\n\n📊 YOUR POSITIONS:")
        print("━" * 60)
        
        if self.portfolio_data['runners']:
            print("\n🔥 RUNNING HOT:")
            for pos in self.portfolio_data['runners']:
                print(f"  {pos['ticker']}: Score {pos['score']}, Thesis {pos['thesis_score']}/10")
        
        if self.portfolio_data['healthy']:
            print("\n✅ HEALTHY:")
            for pos in self.portfolio_data['healthy']:
                print(f"  {pos['ticker']}: Score {pos['score']}, Thesis {pos['thesis_score']}/10")
        
        if self.portfolio_data['watch']:
            print("\n⚠️  WATCH LIST:")
            for pos in self.portfolio_data['watch']:
                print(f"  {pos['ticker']}: Score {pos['score']}, Thesis {pos['thesis_score']}/10")
        
        if self.portfolio_data['weak']:
            print("\n🟡 WEAK (Hold if thesis strong):")
            for pos in self.portfolio_data['weak']:
                print(f"  {pos['ticker']}: Score {pos['score']}, Thesis {pos['thesis_score']}/10")
        
        # MARKET OPPORTUNITIES
        if self.market_scan:
            print("\n\n🎯 NEW OPPORTUNITIES:")
            print("━" * 60)
            
            # Group by pattern type
            patterns = {}
            for setup in self.market_scan:
                pattern = setup.get('type', 'OTHER')
                if pattern not in patterns:
                    patterns[pattern] = []
                patterns[pattern].append(setup)
            
            for pattern, setups in patterns.items():
                print(f"\n{pattern}:")
                for setup in setups[:3]:  # Top 3 per pattern
                    ticker = setup['ticker']
                    score = setup.get('score', 0)
                    reasoning = setup.get('reasoning', 'No details')
                    entry = setup.get('entry', 0)
                    stop = setup.get('stop', 0)
                    
                    print(f"  {ticker}: Score {score}/100")
                    print(f"    Entry: ${entry:.2f} | Stop: ${stop:.2f}")
                    print(f"    → {reasoning[:80]}")
        
        # CATALYST CALENDAR
        if CATALYST_AVAILABLE and self.catalyst_data:
            print("\n\n📅 CATALYST CALENDAR:")
            print("━" * 60)
            
            # Get all catalysts from holdings
            all_catalysts = []
            for ticker, catalysts in self.catalyst_data.items():
                all_catalysts.extend(catalysts)
            
            if all_catalysts:
                # Sort by days_until
                all_catalysts.sort(key=lambda c: c.days_until)
                
                # Group by urgency
                imminent = [c for c in all_catalysts if c.days_until <= 7]
                upcoming = [c for c in all_catalysts if 8 <= c.days_until <= 30]
                distant = [c for c in all_catalysts if c.days_until > 30]
                
                if imminent:
                    print("\n🔴 IMMINENT (This Week):")
                    for cat in imminent:
                        score = cat.get_signal_score()
                        print(f"  {cat.ticker}: {cat.description}")
                        print(f"    → {cat.days_until} days | {cat.event_date} | Score: {score}/100")
                
                if upcoming:
                    print("\n🟡 UPCOMING (This Month):")
                    for cat in upcoming:
                        score = cat.get_signal_score()
                        print(f"  {cat.ticker}: {cat.description}")
                        print(f"    → {cat.days_until} days | {cat.event_date} | Score: {score}/100")
                
                if distant:
                    print("\n⚪ DISTANT (Future):")
                    for cat in distant[:3]:  # Only show first 3
                        print(f"  {cat.ticker}: {cat.description} → {cat.days_until} days")
            else:
                print("\n⏳ No catalysts tracked yet")
                print("   Add catalysts manually: python services/catalyst_service.py")
        
        # SECTOR FLOW
        if SECTOR_AVAILABLE and self.sector_flow:
            print("\n\n🌊 SECTOR FLOW:")
            print("━" * 60)
            
            # Show top 5 hottest and bottom 3 coldest
            print("\n🔥 HOTTEST SECTORS:")
            for sector in self.sector_flow.sectors[:5]:
                emoji = sector.get_heat_emoji()
                print(f"  {emoji} {sector.name}: {sector.change_5d:+.1f}% (Heat: {sector.heat_score}/100)")
            
            print("\n❄️  COLDEST SECTORS:")
            for sector in self.sector_flow.sectors[-3:]:
                emoji = sector.get_heat_emoji()
                print(f"  {emoji} {sector.name}: {sector.change_5d:+.1f}% (Heat: {sector.heat_score}/100)")
            
            # Small cap spread
            if self.sector_flow.small_cap_spread > 2:
                print(f"\n🟢 SMALL CAPS: Outperforming (+{self.sector_flow.small_cap_spread:.1f}% vs SPY) - RISK ON")
            elif self.sector_flow.small_cap_spread < -2:
                print(f"\n🔴 SMALL CAPS: Underperforming ({self.sector_flow.small_cap_spread:.1f}% vs SPY) - RISK OFF")
            else:
                print(f"\n🟡 SMALL CAPS: In-line ({self.sector_flow.small_cap_spread:+.1f}% vs SPY)")
        
        # CONVERGENCE SIGNALS (when BR0KKR is active)
        print("\n\n🎯 CONVERGENCE SIGNALS:")
        print("━" * 60)
        
        if self.convergence_signals and len(self.convergence_signals) > 0:
            print(f"🧠 {len(self.convergence_signals)} multi-signal setups detected:\n")
            
            for signal in self.convergence_signals[:5]:  # Top 5
                emoji = signal.get_priority_emoji()
                print(f"{emoji} {signal.ticker}: {signal.convergence_score}/100 ({signal.convergence_level.value})")
                print(f"   {signal.signal_count} signals converging:")
                for s in signal.signals:
                    print(f"      • {s.signal_type.value.upper()}: {s.score}/100 - {s.reasoning}")
                print()
        else:
            print("⏳ Awaiting convergence signals...")
            print("   (Need 2+ independent signals to converge)")
            print("   Current signals available:")
            print(f"   • Scanner: {len(self.market_scan) if self.market_scan else 0} setups")
            if self.br0kkr_data:
                print(f"   • BR0KKR: {len(self.br0kkr_data.get('cluster_buys', []))} cluster buys, {len(self.br0kkr_data.get('activist_filings', []))} activist filings")
            if self.catalyst_data:
                catalyst_count = sum(len(cats) for cats in self.catalyst_data.values())
                print(f"   • Catalyst: {catalyst_count} events tracked")
            if self.sector_flow:
                print(f"   • Sector: {len(self.sector_flow.sectors)} sectors analyzed")
            if not self.br0kkr_data and not self.catalyst_data and not self.sector_flow:
                print("   • BR0KKR: Coming soon")
                print("   • Catalyst: Coming soon")
                print("   • Sector: Coming soon")
        
        # PATTERN INSIGHTS from WolfPack database
        if self.db_connection:
            print("\n\n🔬 PATTERN INSIGHTS (Historical Data):")
            print("━" * 60)
            try:
                self._show_pattern_insights()
            except Exception as e:
                print(f"⚠️  Could not load patterns: {e}")
        
        print("\n" + "=" * 60)
        print("🐺 LLHR - Complete Intelligence")
        print()
    
    def _show_pattern_insights(self):
        """Query WolfPack database for pattern insights"""
        
        # Get recent big moves
        query = '''
        SELECT ticker, date, daily_return_pct, volume_ratio, 
               sector, dist_52w_high_pct, return_60d
        FROM daily_records
        WHERE ABS(daily_return_pct) > 5
        ORDER BY date DESC
        LIMIT 10
        '''
        
        df = pd.read_sql_query(query, self.db_connection)
        
        if len(df) > 0:
            print("\n📈 RECENT BIG MOVES (Last 10 from database):")
            for _, row in df.iterrows():
                print(f"  {row['ticker']} ({row['sector']}): {row['daily_return_pct']:+.1f}% "
                      f"on {row['volume_ratio']:.1f}x volume | {row['date']}")
                print(f"    → {row['dist_52w_high_pct']:+.1f}% from 52w high, "
                      f"{row['return_60d']:+.1f}% over 60d")
        
        # Check if any of YOUR positions are in the database
        your_tickers = list(HOLDINGS.keys())
        if your_tickers:
            print("\n📊 YOUR HOLDINGS IN DATABASE:")
            for ticker in your_tickers:
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM daily_records 
                    WHERE ticker = ?
                ''', (ticker,))
                count = cursor.fetchone()[0]
                if count > 0:
                    # Get most recent record
                    cursor.execute('''
                        SELECT date, daily_return_pct, volume_ratio, 
                               return_60d, dist_52w_high_pct
                        FROM daily_records
                        WHERE ticker = ?
                        ORDER BY date DESC
                        LIMIT 1
                    ''', (ticker,))
                    row = cursor.fetchone()
                    if row:
                        print(f"  {ticker}: {count} days tracked, last: {row[0]}")
                        print(f"    → {row[1]:+.1f}% today, {row[2]:.1f}x vol, "
                              f"60d: {row[3]:+.1f}%, from high: {row[4]:+.1f}%")
        
        # Show wounded prey patterns if any
        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT ticker, date, daily_return_pct, dist_52w_high_pct
            FROM daily_records
            WHERE dist_52w_high_pct < -30 
            AND daily_return_pct > 3
            ORDER BY date DESC
            LIMIT 5
        ''')
        wounded = cursor.fetchall()
        
        if wounded:
            print("\n🎯 WOUNDED PREY BOUNCES (From database):")
            for row in wounded:
                print(f"  {row[0]}: +{row[2]:.1f}% bounce from {row[3]:.1f}% below highs | {row[1]}")
    
    def check_position(self, ticker: str):
        """Deep dive on specific position"""
        ticker = ticker.upper()
        
        if ticker not in self.portfolio_data['positions']:
            print(f"❌ {ticker} not in your portfolio")
            return
        
        pos = self.portfolio_data['positions'][ticker]
        
        print(f"\n🔍 DEEP DIVE: {ticker}")
        print("=" * 60)
        
        print(f"\n📊 HEALTH SCORE: {pos['score']}")
        print(f"💡 THESIS SCORE: {pos['thesis_score']}/10")
        
        if pos['score'] <= -5:
            print("🔴 STATUS: DEAD MONEY - CUT IT")
        elif pos['score'] <= -3:
            print("🟡 STATUS: WEAK - Review thesis")
        elif pos['score'] <= -1:
            print("⚠️  STATUS: WATCH - Monitor closely")
        elif pos['score'] >= 5:
            print("🔥 STATUS: RUNNING - Consider adding")
        else:
            print("✅ STATUS: HEALTHY - Hold")
        
        print(f"\n📝 THESIS:")
        print(f"{pos['thesis']}")
        
        print("\n💰 POSITION DETAILS:")
        health = pos['health']
        if 'position_value' in health:
            print(f"Value: ${health['position_value']:.2f}")
        if 'pl_pct' in health:
            print(f"P/L: {health['pl_pct']:+.1f}%")
        
        print("\n" + "=" * 60)
    
    def find_replacements(self, ticker: Optional[str] = None):
        """Find market opportunities to replace weak positions"""
        print("\n🔍 FINDING REPLACEMENTS")
        print("=" * 60)
        
        if ticker:
            ticker = ticker.upper()
            if ticker in self.portfolio_data['positions']:
                old_pos = self.portfolio_data['positions'][ticker]
                print(f"\n🔴 Replacing: {ticker} (Score {old_pos['score']})")
        
        if not self.market_scan:
            print("\n❌ No market data available")
            return
        
        print(f"\n✅ Found {len(self.market_scan)} opportunities:")
        
        # Show top opportunities
        for i, setup in enumerate(self.market_scan[:5], 1):
            ticker = setup['ticker']
            score = setup.get('score', 0)
            pattern = setup.get('type', 'UNKNOWN')
            entry = setup.get('entry', 0)
            stop = setup.get('stop', 0)
            reasoning = setup.get('reasoning', 'No details')
            
            print(f"\n{i}. {ticker} - {pattern}")
            print(f"   Score: {score}/100")
            print(f"   Entry: ${entry:.2f} | Stop: ${stop:.2f}")
            print(f"   → {reasoning[:100]}")
        
        print("\n" + "=" * 60)
    
    def chat(self, query: str):
        """Natural language interface"""
        query = query.lower()
        
        # Dead money check
        if "dead money" in query or "dead" in query:
            if self.portfolio_data['dead_money']:
                print("\n🔴 DEAD MONEY ALERT!")
                print("=" * 60)
                for pos in self.portfolio_data['dead_money']:
                    print(f"\n{pos['ticker']}: Score {pos['score']}")
                    print(f"Thesis: {pos['thesis_score']}/10")
                    print("→ CUT THIS POSITION")
            else:
                print("\n✅ NO DEAD MONEY")
                if self.portfolio_data['weak']:
                    print(f"\nYou have {len(self.portfolio_data['weak'])} weak position(s):")
                    for pos in self.portfolio_data['weak']:
                        print(f"  {pos['ticker']}: Score {pos['score']}, Thesis {pos['thesis_score']}/10")
                        if pos['thesis_score'] >= 8:
                            print("    → HOLD (strong thesis)")
                        else:
                            print("    → REVIEW (weak thesis)")
        
        # What to buy
        elif "buy" in query or "worth" in query or "opportunities" in query:
            if self.portfolio_data['runners']:
                print("\n🔥 IN YOUR PORTFOLIO (Already running):")
                for pos in self.portfolio_data['runners']:
                    print(f"  {pos['ticker']}: Score {pos['score']}, Thesis {pos['thesis_score']}/10")
                    print("    → Consider adding if thesis intact")
            
            if self.market_scan:
                print(f"\n🎯 NEW OPPORTUNITIES ({len(self.market_scan)} found):")
                for setup in self.market_scan[:3]:
                    print(f"  {setup['ticker']}: Score {setup.get('score', 0)}/100")
                    print(f"    Entry ${setup.get('entry', 0):.2f} | Stop ${setup.get('stop', 0):.2f}")
        
        # Check specific ticker
        elif any(ticker in query.upper() for ticker in self.portfolio_data['positions']):
            for ticker in self.portfolio_data['positions']:
                if ticker.lower() in query:
                    self.check_position(ticker)
                    return
        
        # Scanner status
        elif "scan" in query or "market" in query:
            if self.market_scan:
                print(f"\n✅ Market scan complete: {len(self.market_scan)} setups")
                print("Use 'opportunities' to see them")
            else:
                print("\n⏳ No market data loaded")
        
        # Help
        else:
            print("\n🐺 WOLF PACK COMMANDS:")
            print("━" * 60)
            print("  'brief' or 'briefing'    → Morning intelligence report")
            print("  'dead money'             → Check for dead positions")
            print("  'buy' or 'opportunities' → What to buy now")
            print("  'check TICKER'           → Deep dive on position")
            print("  'replace TICKER'         → Find replacements")
            print("  'scan' or 'market'       → Market scan status")
            print("  'quit' or 'exit'         → Exit")
    
    def interactive(self):
        """Interactive chat mode"""
        print("\n🐺 WOLF PACK INTERACTIVE MODE")
        print("Type 'help' for commands, 'quit' to exit\n")
        
        while True:
            try:
                query = input("🐺 > ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n🐺 Hunt well. LLHR.\n")
                    break
                
                if query.lower() in ['brief', 'briefing', 'morning']:
                    self.morning_briefing()
                elif 'replace' in query.lower():
                    parts = query.split()
                    ticker = parts[1] if len(parts) > 1 else None
                    self.find_replacements(ticker)
                elif 'check' in query.lower():
                    parts = query.split()
                    if len(parts) > 1:
                        self.check_position(parts[1])
                else:
                    self.chat(query)
                
                print()  # Blank line for readability
                
            except KeyboardInterrupt:
                print("\n\n🐺 Hunt well. LLHR.\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Entry point - one command for everything"""
    
    # Initialize Wolf Pack
    pack = WolfPack()
    pack.initialize()
    
    # If command line argument provided, execute and exit
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        
        if query.lower() in ['brief', 'briefing', 'morning']:
            pack.morning_briefing()
        elif 'replace' in query.lower():
            parts = query.split()
            ticker = parts[1] if len(parts) > 1 else None
            pack.find_replacements(ticker)
        elif 'check' in query.lower():
            parts = query.split()
            if len(parts) > 1:
                pack.check_position(parts[1])
        else:
            pack.chat(query)
    else:
        # Interactive mode
        pack.interactive()


if __name__ == "__main__":
    main()
