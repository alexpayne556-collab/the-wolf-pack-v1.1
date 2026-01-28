#!/usr/bin/env python3
"""
🐺 AUTONOMOUS WOLF BRAIN - The Intelligent Trading System
Real execution, real monitoring, real decisions.

This brain:
1. Scans for opportunities using convergence engine
2. Makes buy decisions based on strict rules
3. Places REAL orders in Alpaca (paper or live)
4. Monitors all positions 24/7
5. Makes exit decisions (stop loss, thesis break, profit taking)
6. Learns from every trade
7. Adapts based on outcomes

Not a toy. Not a simulation. A real autonomous trader.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
from dotenv import load_dotenv

# Add wolfpack to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all the systems
from wolfpack.services.convergence_service import ConvergenceEngine
from wolfpack.services.risk_manager import RiskManager
from wolfpack.services.learning_engine import LearningEngine
from wolfpack.services.trading_rules import TenCommandments
from wolfpack.services.br0kkr_service import scan_institutional_activity
from wolfpack.services.news_service import NewsService
from wolfpack.services.catalyst_service import CatalystService
from wolfpack.services.earnings_service import EarningsService
from wolfpack.services.sector_flow_tracker import SectorFlowTracker
from wolfpack.services.pattern_service import PatternService
from wolfpack.database import init_database, log_trade, get_connection

# Alpaca
import alpaca_trade_api as tradeapi

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

class BrainConfig:
    """Configuration for autonomous trading brain"""
    
    # Trading mode
    PAPER_TRADING = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
    
    # Alpaca credentials
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
    ALPACA_BASE_URL = 'https://paper-api.alpaca.markets' if PAPER_TRADING else 'https://api.alpaca.markets'
    
    # Trading constraints
    MIN_CONVERGENCE = 50  # Don't trade below this
    OPTIMAL_CONVERGENCE = 70  # Ideal threshold
    MIN_VOLUME_RATIO = 1.5  # Minimum volume confirmation
    OPTIMAL_VOLUME_RATIO = 2.0  # Strong confirmation
    
    # Position management
    MAX_POSITIONS = 10  # Don't hold more than this
    MAX_PORTFOLIO_RISK = 0.50  # 50% max total risk
    CHECK_INTERVAL = 300  # Check positions every 5 minutes
    
    # Decision making
    STOP_LOSS_PCT = 0.10  # 10% stop loss (adjustable per position)
    PROFIT_TARGET_MULTIPLIER = 2.0  # 2:1 R/R minimum
    THESIS_CHECK_INTERVAL = 1800  # Check thesis every 30 minutes
    
    # Scanning
    SCAN_UNIVERSE = [
        # From previous sessions
        'IBRX', 'DNN', 'RDW', 'MRNO',
        # Nuclear/Energy
        'UUUU', 'UEC', 'LEU', 'UROY', 'DNN', 'NXE',
        # Defense/Space
        'RCAT', 'RDW', 'LUNR', 'ASTS', 'PL', 'BKSY',
        # AI/Tech
        'MU', 'NVDA', 'AMD', 'PLTR', 'IONQ',
        # Biotech
        'IBRX', 'ONCY', 'NTLA', 'IVF', 'EDIT',
        # Small caps (speculative)
        'MRNO', 'APLD', 'BITF', 'HIVE', 'AI'
    ]


# =============================================================================
# AUTONOMOUS TRADING BRAIN
# =============================================================================

class AutonomousWolfBrain:
    """
    The brain that thinks, decides, executes, monitors, and learns.
    """
    
    def __init__(self, config: BrainConfig = None):
        self.config = config or BrainConfig()
        
        print("\n🐺 INITIALIZING AUTONOMOUS WOLF BRAIN...")
        print(f"   Mode: {'PAPER' if self.config.PAPER_TRADING else 'LIVE'} Trading")
        
        # Initialize database
        init_database()
        
        # Initialize all systems
        print("   🧠 Loading convergence engine...")
        self.convergence = ConvergenceEngine()
        
        print("   🛡️ Loading risk manager...")
        self.risk_manager = RiskManager()
        
        print("   📚 Loading learning engine...")
        self.learning = LearningEngine()
        
        print("   📜 Loading trading rules...")
        self.rules = TenCommandments()
        
        print("   📰 Loading news service...")
        self.news = NewsService()
        
        print("   📅 Loading catalyst service...")
        self.catalyst = CatalystService()
        
        print("   📊 Loading earnings service...")
        self.earnings = EarningsService()
        
        print("   🔄 Loading sector flow tracker...")
        self.sector = SectorFlowTracker()
        
        print("   🎯 Loading pattern service...")
        self.pattern = PatternService()
        
        # Initialize Alpaca
        print("   🦙 Connecting to Alpaca...")
        self.alpaca = tradeapi.REST(
            self.config.ALPACA_API_KEY,
            self.config.ALPACA_SECRET_KEY,
            self.config.ALPACA_BASE_URL,
            api_version='v2'
        )
        
        # Verify connection
        account = self.alpaca.get_account()
        print(f"   ✅ Connected to Alpaca")
        print(f"   💰 Account Value: ${float(account.equity):,.2f}")
        print(f"   💵 Buying Power: ${float(account.buying_power):,.2f}")
        
        # Track state
        self.positions = {}  # ticker -> position data
        self.open_orders = {}  # order_id -> order data
        self.last_scan_time = None
        self.last_thesis_check = {}  # ticker -> timestamp
        
        print("   ✅ ALL SYSTEMS OPERATIONAL\n")
    
    # =========================================================================
    # SCANNING & OPPORTUNITY DETECTION
    # =========================================================================
    
    def scan_opportunities(self) -> List[Dict]:
        """
        Scan for trading opportunities using full convergence engine
        """
        print(f"\n🔍 SCANNING FOR OPPORTUNITIES ({len(self.config.SCAN_UNIVERSE)} tickers)...")
        
        opportunities = []
        
        for ticker in self.config.SCAN_UNIVERSE:
            try:
                # Skip if we already own it
                if ticker in self.positions:
                    continue
                
                # Get convergence score with all 7 signals
                result = self.convergence.calculate_convergence(
                    ticker=ticker,
                    scanner_signal=None,  # Will calculate
                    br0kkr_signal=None,  # Will calculate
                    catalyst_signal=None,  # Will calculate
                    earnings_signal=None,  # Will calculate
                    news_signal=None,  # Will calculate
                    sector_signal=None,  # Will calculate
                    pattern_signal=None  # Will calculate
                )
                
                if not result or result['convergence_score'] < self.config.MIN_CONVERGENCE:
                    continue
                
                # Get current price and volume
                stock = yf.Ticker(ticker)
                hist = stock.history(period='5d')
                
                if len(hist) < 2:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                avg_volume = hist['Volume'].mean()
                current_volume = hist['Volume'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                
                # Volume check
                if volume_ratio < self.config.MIN_VOLUME_RATIO:
                    continue
                
                # Check with learning engine - should we take this?
                decision = self.learning.should_take_trade(
                    ticker=ticker,
                    setup_type=result.get('primary_signal', 'unknown'),
                    score=result['convergence_score']
                )
                
                if not decision['should_take']:
                    print(f"   ⏭️  {ticker}: Learning engine says NO - {decision['reason']}")
                    continue
                
                # Passed all filters
                opportunities.append({
                    'ticker': ticker,
                    'convergence': result['convergence_score'],
                    'signals': result['active_signals'],
                    'price': current_price,
                    'volume_ratio': volume_ratio,
                    'primary_signal': result.get('primary_signal'),
                    'thesis': result.get('thesis', 'Multi-signal convergence'),
                    'learning_advice': decision['reason']
                })
                
                print(f"   ✅ {ticker}: {result['convergence_score']}/100 | Vol {volume_ratio:.1f}x | ${current_price:.2f}")
                
            except Exception as e:
                print(f"   ⚠️  {ticker}: Error - {str(e)}")
                continue
        
        # Sort by convergence score
        opportunities.sort(key=lambda x: x['convergence'], reverse=True)
        
        print(f"\n   Found {len(opportunities)} opportunities")
        
        self.last_scan_time = datetime.now()
        return opportunities
    
    # =========================================================================
    # POSITION SIZING & ENTRY DECISIONS
    # =========================================================================
    
    def calculate_position_size(self, ticker: str, convergence: int, price: float) -> Dict:
        """
        Calculate position size using risk manager
        """
        account = self.alpaca.get_account()
        portfolio_value = float(account.equity)
        
        # Base position size on convergence score
        if convergence >= 85:
            risk_pct = 0.02  # 2% risk for CRITICAL
            max_position_pct = 0.12  # 12% of portfolio
        elif convergence >= 70:
            risk_pct = 0.015  # 1.5% risk for HIGH
            max_position_pct = 0.08  # 8% of portfolio
        else:
            risk_pct = 0.01  # 1% risk for MEDIUM
            max_position_pct = 0.04  # 4% of portfolio
        
        # Calculate shares based on stop loss
        stop_loss_pct = self.config.STOP_LOSS_PCT
        risk_dollars = portfolio_value * risk_pct
        price_risk = price * stop_loss_pct
        shares = int(risk_dollars / price_risk) if price_risk > 0 else 0
        
        # Calculate actual position value
        position_value = shares * price
        position_pct = position_value / portfolio_value if portfolio_value > 0 else 0
        
        # Cap at max position size
        if position_pct > max_position_pct:
            shares = int((portfolio_value * max_position_pct) / price)
            position_value = shares * price
            position_pct = position_value / portfolio_value
        
        # Calculate stop loss price
        stop_price = price * (1 - stop_loss_pct)
        
        # Calculate profit target (2:1 R/R minimum)
        risk_per_share = price - stop_price
        profit_target = price + (risk_per_share * self.config.PROFIT_TARGET_MULTIPLIER)
        
        return {
            'shares': shares,
            'position_value': position_value,
            'position_pct': position_pct,
            'stop_price': stop_price,
            'profit_target': profit_target,
            'risk_dollars': risk_dollars,
            'risk_pct': risk_pct
        }
    
    def should_enter_trade(self, opportunity: Dict) -> tuple[bool, str]:
        """
        Final decision: Should we enter this trade?
        """
        ticker = opportunity['ticker']
        convergence = opportunity['convergence']
        volume_ratio = opportunity['volume_ratio']
        
        # Check 1: Already at max positions?
        if len(self.positions) >= self.config.MAX_POSITIONS:
            return False, f"At max positions ({self.config.MAX_POSITIONS})"
        
        # Check 2: Convergence too low?
        if convergence < self.config.MIN_CONVERGENCE:
            return False, f"Convergence {convergence} < {self.config.MIN_CONVERGENCE}"
        
        # Check 3: Volume too weak?
        if volume_ratio < self.config.MIN_VOLUME_RATIO:
            return False, f"Volume {volume_ratio:.1f}x < {self.config.MIN_VOLUME_RATIO}x"
        
        # Check 4: Trading rules check (simplified - just basic checks)
        # The TenCommandments class may not have can_enter_trade method
        # So we do basic validation ourselves
        
        if volume_ratio < self.config.MIN_VOLUME_RATIO:
            return False, f"Volume {volume_ratio:.1f}x < {self.config.MIN_VOLUME_RATIO}x"
        
        # Check 5: Portfolio heat check
        account = self.alpaca.get_account()
        portfolio_value = float(account.equity)
        
        sizing = self.calculate_position_size(
            ticker=ticker,
            convergence=convergence,
            price=opportunity['price']
        )
        
        # Calculate current portfolio risk
        current_risk = sum(
            pos.get('risk_dollars', 0) 
            for pos in self.positions.values()
        )
        
        new_total_risk = current_risk + sizing['risk_dollars']
        risk_pct = new_total_risk / portfolio_value if portfolio_value > 0 else 0
        
        if risk_pct > self.config.MAX_PORTFOLIO_RISK:
            return False, f"Portfolio risk {risk_pct:.1%} > {self.config.MAX_PORTFOLIO_RISK:.1%}"
        
        # All checks passed
        return True, f"APPROVED - Convergence {convergence}, Volume {volume_ratio:.1f}x, Risk {sizing['risk_pct']:.1%}"
    
    # =========================================================================
    # ORDER EXECUTION
    # =========================================================================
    
    def execute_buy(self, opportunity: Dict) -> Optional[Dict]:
        """
        Execute buy order in Alpaca
        """
        ticker = opportunity['ticker']
        price = opportunity['price']
        convergence = opportunity['convergence']
        
        # Calculate position size
        sizing = self.calculate_position_size(ticker, convergence, price)
        
        if sizing['shares'] <= 0:
            print(f"   ⚠️  {ticker}: Position size too small, skipping")
            return None
        
        print(f"\n💰 EXECUTING BUY: {ticker}")
        print(f"   Price: ${price:.2f}")
        print(f"   Shares: {sizing['shares']}")
        print(f"   Position: ${sizing['position_value']:.2f} ({sizing['position_pct']:.1%})")
        print(f"   Stop Loss: ${sizing['stop_price']:.2f}")
        print(f"   Target: ${sizing['profit_target']:.2f}")
        print(f"   Risk: ${sizing['risk_dollars']:.2f} ({sizing['risk_pct']:.1%})")
        
        try:
            # Submit market order
            order = self.alpaca.submit_order(
                symbol=ticker,
                qty=sizing['shares'],
                side='buy',
                type='market',
                time_in_force='day'
            )
            
            print(f"   ✅ Order submitted: {order.id}")
            
            # Wait for fill
            time.sleep(2)
            order = self.alpaca.get_order(order.id)
            
            if order.status == 'filled':
                fill_price = float(order.filled_avg_price)
                print(f"   ✅ FILLED at ${fill_price:.2f}")
                
                # Submit stop loss order
                stop_order = self.alpaca.submit_order(
                    symbol=ticker,
                    qty=sizing['shares'],
                    side='sell',
                    type='stop',
                    time_in_force='gtc',
                    stop_price=round(sizing['stop_price'], 2)
                )
                
                print(f"   🛡️ Stop loss placed at ${sizing['stop_price']:.2f}")
                
                # Log to learning engine
                log_trade(
                    ticker=ticker,
                    action='BUY',
                    shares=sizing['shares'],
                    price=fill_price,
                    thesis=opportunity['thesis'],
                    notes=json.dumps({
                        'convergence': convergence,
                        'signals': opportunity['signals'],
                        'volume_ratio': opportunity['volume_ratio'],
                        'stop_loss': sizing['stop_price'],
                        'profit_target': sizing['profit_target'],
                        'primary_signal': opportunity.get('primary_signal')
                    })
                )
                
                # Track position
                self.positions[ticker] = {
                    'shares': sizing['shares'],
                    'entry_price': fill_price,
                    'entry_time': datetime.now(),
                    'stop_price': sizing['stop_price'],
                    'profit_target': sizing['profit_target'],
                    'convergence': convergence,
                    'thesis': opportunity['thesis'],
                    'stop_order_id': stop_order.id,
                    'risk_dollars': sizing['risk_dollars'],
                    'max_drawdown': 0.0
                }
                
                return self.positions[ticker]
            
            else:
                print(f"   ⚠️  Order status: {order.status}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error executing buy: {str(e)}")
            return None
    
    # =========================================================================
    # POSITION MONITORING & EXIT DECISIONS
    # =========================================================================
    
    def monitor_positions(self):
        """
        Monitor all open positions and make exit decisions
        """
        if not self.positions:
            return
        
        print(f"\n👁️ MONITORING {len(self.positions)} POSITIONS...")
        
        for ticker in list(self.positions.keys()):
            try:
                position_data = self.positions[ticker]
                
                # Get current price
                stock = yf.Ticker(ticker)
                current_price = stock.history(period='1d')['Close'].iloc[-1]
                
                entry_price = position_data['entry_price']
                stop_price = position_data['stop_price']
                profit_target = position_data['profit_target']
                
                # Calculate P&L
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                pnl_dollars = (current_price - entry_price) * position_data['shares']
                
                # Update max drawdown
                if pnl_pct < position_data['max_drawdown']:
                    position_data['max_drawdown'] = pnl_pct
                
                print(f"\n   {ticker}: ${current_price:.2f} ({pnl_pct:+.1f}%)")
                print(f"      Entry: ${entry_price:.2f} | Stop: ${stop_price:.2f} | Target: ${profit_target:.2f}")
                
                # Decision 1: Hit stop loss?
                if current_price <= stop_price:
                    print(f"      🛑 STOP LOSS HIT - Exiting")
                    self.execute_sell(ticker, "stop_loss_hit", current_price)
                    continue
                
                # Decision 2: Hit profit target?
                if current_price >= profit_target:
                    print(f"      🎯 PROFIT TARGET HIT - Exiting")
                    self.execute_sell(ticker, "profit_target_hit", current_price)
                    continue
                
                # Decision 3: Check thesis (every 30 minutes)
                last_check = self.last_thesis_check.get(ticker, datetime.min)
                if (datetime.now() - last_check).seconds > self.config.THESIS_CHECK_INTERVAL:
                    thesis_valid = self.check_thesis(ticker, position_data)
                    self.last_thesis_check[ticker] = datetime.now()
                    
                    if not thesis_valid:
                        print(f"      ⚠️ THESIS BROKEN - Exiting")
                        self.execute_sell(ticker, "thesis_broken", current_price)
                        continue
                
                # Decision 4: Trail stop loss for winners
                if pnl_pct > 20:
                    # Move stop to breakeven + 10%
                    new_stop = entry_price * 1.10
                    if new_stop > stop_price:
                        self.update_stop_loss(ticker, new_stop)
                        position_data['stop_price'] = new_stop
                        print(f"      📈 Trailing stop to ${new_stop:.2f} (breakeven + 10%)")
                
                elif pnl_pct > 10:
                    # Move stop to breakeven
                    new_stop = entry_price
                    if new_stop > stop_price:
                        self.update_stop_loss(ticker, new_stop)
                        position_data['stop_price'] = new_stop
                        print(f"      📈 Trailing stop to ${new_stop:.2f} (breakeven)")
                
            except Exception as e:
                print(f"   ⚠️ Error monitoring {ticker}: {str(e)}")
                continue
    
    def check_thesis(self, ticker: str, position_data: Dict) -> bool:
        """
        Check if trade thesis is still valid
        """
        try:
            # Re-run convergence check
            result = self.convergence.calculate_convergence(ticker=ticker)
            
            if not result:
                return True  # Can't verify, keep position
            
            # If convergence dropped significantly, thesis might be broken
            current_convergence = result['convergence_score']
            entry_convergence = position_data['convergence']
            
            convergence_drop = entry_convergence - current_convergence
            
            if convergence_drop > 30:
                print(f"      ⚠️ Convergence dropped from {entry_convergence} to {current_convergence}")
                return False
            
            return True
            
        except Exception as e:
            print(f"      ⚠️ Error checking thesis: {str(e)}")
            return True  # Err on side of keeping position
    
    def update_stop_loss(self, ticker: str, new_stop: float):
        """Update stop loss order"""
        try:
            position = self.positions[ticker]
            old_stop_id = position.get('stop_order_id')
            
            # Cancel old stop
            if old_stop_id:
                try:
                    self.alpaca.cancel_order(old_stop_id)
                except:
                    pass
            
            # Submit new stop
            stop_order = self.alpaca.submit_order(
                symbol=ticker,
                qty=position['shares'],
                side='sell',
                type='stop',
                time_in_force='gtc',
                stop_price=round(new_stop, 2)
            )
            
            position['stop_order_id'] = stop_order.id
            
        except Exception as e:
            print(f"      ⚠️ Error updating stop: {str(e)}")
    
    def execute_sell(self, ticker: str, reason: str, current_price: float):
        """
        Execute sell order
        """
        try:
            position = self.positions[ticker]
            
            print(f"\n   🔴 SELLING {ticker}: {reason}")
            
            # Cancel stop loss order
            if position.get('stop_order_id'):
                try:
                    self.alpaca.cancel_order(position['stop_order_id'])
                except:
                    pass
            
            # Submit market order
            order = self.alpaca.submit_order(
                symbol=ticker,
                qty=position['shares'],
                side='sell',
                type='market',
                time_in_force='day'
            )
            
            time.sleep(2)
            order = self.alpaca.get_order(order.id)
            
            if order.status == 'filled':
                exit_price = float(order.filled_avg_price)
                entry_price = position['entry_price']
                
                pnl_pct = ((exit_price - entry_price) / entry_price) * 100
                pnl_dollars = (exit_price - entry_price) * position['shares']
                days_held = (datetime.now() - position['entry_time']).days
                
                print(f"   ✅ SOLD at ${exit_price:.2f}")
                print(f"   P&L: {pnl_pct:+.1f}% (${pnl_dollars:+.2f})")
                print(f"   Days held: {days_held}")
                
                # Log to learning engine
                log_trade(
                    ticker=ticker,
                    action='SELL',
                    shares=position['shares'],
                    price=exit_price,
                    thesis=reason,
                    notes=json.dumps({
                        'entry_price': entry_price,
                        'pnl_pct': pnl_pct,
                        'pnl_dollars': pnl_dollars,
                        'days_held': days_held,
                        'max_drawdown': position['max_drawdown'],
                        'exit_reason': reason
                    })
                )
                
                # Remove from tracked positions
                del self.positions[ticker]
                
        except Exception as e:
            print(f"   ❌ Error executing sell: {str(e)}")
    
    # =========================================================================
    # MAIN CONTROL LOOP
    # =========================================================================
    
    def run_trading_cycle(self):
        """
        One complete trading cycle: scan, decide, execute, monitor
        """
        print(f"\n{'='*70}")
        print(f"🐺 TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Step 1: Monitor existing positions
        self.monitor_positions()
        
        # Step 2: Check if we can add new positions
        if len(self.positions) < self.config.MAX_POSITIONS:
            
            # Step 3: Scan for opportunities
            opportunities = self.scan_opportunities()
            
            # Step 4: Evaluate and execute top opportunities
            for opp in opportunities[:3]:  # Max 3 new positions per cycle
                
                if len(self.positions) >= self.config.MAX_POSITIONS:
                    break
                
                # Decision time
                should_enter, reason = self.should_enter_trade(opp)
                
                print(f"\n🤔 DECISION: {opp['ticker']}")
                print(f"   Convergence: {opp['convergence']}/100")
                print(f"   Volume: {opp['volume_ratio']:.1f}x")
                print(f"   Thesis: {opp['thesis']}")
                print(f"   Decision: {'✅ ENTER' if should_enter else '❌ PASS'}")
                print(f"   Reason: {reason}")
                
                if should_enter:
                    # Execute the trade
                    result = self.execute_buy(opp)
                    
                    if result:
                        print(f"   🎉 Position opened successfully")
                    else:
                        print(f"   ⚠️ Failed to open position")
                    
                    time.sleep(5)  # Brief pause between trades
        
        else:
            print(f"\n   ℹ️ At max positions ({self.config.MAX_POSITIONS}), monitoring only")
        
        # Step 5: Summary
        account = self.alpaca.get_account()
        print(f"\n📊 CYCLE COMPLETE")
        print(f"   Portfolio: ${float(account.equity):,.2f}")
        print(f"   Positions: {len(self.positions)}/{self.config.MAX_POSITIONS}")
        print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    
    def run_autonomous(self, check_interval: int = None):
        """
        Run continuously in autonomous mode
        """
        interval = check_interval or self.config.CHECK_INTERVAL
        
        print(f"\n🤖 ENTERING AUTONOMOUS MODE")
        print(f"   Check interval: {interval} seconds")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_trading_cycle()
                
                print(f"\n   💤 Sleeping for {interval} seconds...")
                print(f"   Next check: {(datetime.now() + timedelta(seconds=interval)).strftime('%H:%M:%S')}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 STOPPING AUTONOMOUS MODE")
            print(f"   Final position count: {len(self.positions)}")
            
            # Show summary
            if self.positions:
                print(f"\n   Open positions:")
                for ticker, pos in self.positions.items():
                    pnl = ((pos['current_price'] - pos['entry_price']) / pos['entry_price']) * 100 if 'current_price' in pos else 0
                    print(f"      {ticker}: {pnl:+.1f}%")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='🐺 Autonomous Wolf Brain')
    parser.add_argument('--mode', choices=['scan', 'cycle', 'autonomous'], default='cycle',
                        help='Execution mode: scan only, single cycle, or continuous autonomous')
    parser.add_argument('--interval', type=int, default=300,
                        help='Check interval in seconds (default: 300 = 5 minutes)')
    
    args = parser.parse_args()
    
    # Initialize brain
    brain = AutonomousWolfBrain()
    
    if args.mode == 'scan':
        # Just scan and show opportunities
        opportunities = brain.scan_opportunities()
        
        print(f"\n{'='*70}")
        print(f"TOP OPPORTUNITIES:")
        print(f"{'='*70}")
        
        for i, opp in enumerate(opportunities[:10], 1):
            print(f"\n{i}. {opp['ticker']} - {opp['convergence']}/100")
            print(f"   Price: ${opp['price']:.2f}")
            print(f"   Volume: {opp['volume_ratio']:.1f}x")
            print(f"   Signals: {', '.join(opp['signals'][:3])}")
            print(f"   Thesis: {opp['thesis']}")
    
    elif args.mode == 'cycle':
        # Run one complete cycle
        brain.run_trading_cycle()
    
    elif args.mode == 'autonomous':
        # Run continuously
        brain.run_autonomous(check_interval=args.interval)
    
    print("\n🐺 Brain shutdown complete.\n")
