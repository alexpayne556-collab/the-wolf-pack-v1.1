"""
🤖 AUTONOMOUS TRADER - THE WOLF THAT HUNTS ALONE
Built: January 20, 2026

Full autonomous trading execution with:
- BUY/SELL permissions on Alpaca paper trading
- Dual strategy: STEADY_HUNTER + HEAD_HUNTER
- Full exit management (stops, targets, trailing stops)
- Position sizing based on conviction and risk

This is where the brain takes ACTION.

Usage:
    from wolf_brain.autonomous_trader import AutonomousTrader
    
    trader = AutonomousTrader(paper_trading=True)
    
    # Execute a trade
    result = trader.execute_trade(opportunity)
    
    # Manage existing positions
    trader.manage_positions()
"""

import os
import sys
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json


# Try to import Alpaca
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import (
        MarketOrderRequest, LimitOrderRequest, StopOrderRequest,
        StopLimitOrderRequest, TrailingStopOrderRequest
    )
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  alpaca-trade-api not installed. Run: pip install alpaca-trade-api")


class TradeStrategy(Enum):
    """Trading strategy types"""
    STEADY_HUNTER = "steady_hunter"  # 5-20% targets, higher win rate
    HEAD_HUNTER = "head_hunter"      # 50-500%+ targets, explosive


class TradeStatus(Enum):
    """Trade status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class TradeConfig:
    """Configuration for a trade"""
    ticker: str
    strategy: TradeStrategy
    conviction: float  # 0.0 to 1.0
    entry_price: float
    position_size_pct: float  # % of portfolio
    
    # Exit management
    stop_loss_pct: float
    target_1_pct: float
    target_2_pct: Optional[float] = None
    trailing_stop_pct: Optional[float] = None
    
    # Position splitting
    scale_out_at_target_1: bool = True
    scale_out_pct: float = 0.50  # Sell 50% at T1


@dataclass
class ExecutedTrade:
    """Record of an executed trade"""
    id: str
    ticker: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    timestamp: datetime
    strategy: str
    status: TradeStatus
    order_id: str
    
    # Tracking
    stop_loss_order_id: Optional[str] = None
    target_1_order_id: Optional[str] = None
    notes: str = ""


class PositionManager:
    """
    Manages open positions and exit orders
    """
    
    def __init__(self):
        """Initialize position manager"""
        self.positions = {}  # ticker -> position info
    
    def add_position(self, ticker: str, entry_price: float, quantity: float,
                    strategy: TradeStrategy, config: TradeConfig):
        """Add a new position to track"""
        self.positions[ticker] = {
            'entry_price': entry_price,
            'quantity': quantity,
            'strategy': strategy.value,
            'entry_time': datetime.now(),
            'config': config,
            'stop_loss_price': entry_price * (1 - config.stop_loss_pct),
            'target_1_price': entry_price * (1 + config.target_1_pct),
            'target_2_price': entry_price * (1 + config.target_2_pct) if config.target_2_pct else None,
            'partial_sold': False,
            'high_since_entry': entry_price
        }
        
        print(f"📊 New position: {ticker}")
        print(f"   Entry: ${entry_price:.2f} | Qty: {quantity}")
        print(f"   Stop: ${self.positions[ticker]['stop_loss_price']:.2f}")
        print(f"   T1: ${self.positions[ticker]['target_1_price']:.2f}")
    
    def update_position(self, ticker: str, current_price: float):
        """Update position tracking with current price"""
        if ticker not in self.positions:
            return
        
        pos = self.positions[ticker]
        
        # Update high water mark
        if current_price > pos['high_since_entry']:
            pos['high_since_entry'] = current_price
    
    def remove_position(self, ticker: str):
        """Remove a closed position"""
        if ticker in self.positions:
            del self.positions[ticker]
    
    def get_position(self, ticker: str) -> Optional[Dict]:
        """Get position info"""
        return self.positions.get(ticker)
    
    def get_all_positions(self) -> Dict:
        """Get all open positions"""
        return self.positions


class RiskManager:
    """
    Risk management for trades
    """
    
    def __init__(self, max_portfolio_risk_pct: float = 0.05,
                 max_single_position_pct: float = 0.10,
                 max_positions: int = 10,
                 max_same_sector_pct: float = 0.30):
        """
        Initialize risk manager
        
        Args:
            max_portfolio_risk_pct: Max % of portfolio at risk (default 5%)
            max_single_position_pct: Max % of portfolio in single position (default 10%)
            max_positions: Maximum number of concurrent positions
            max_same_sector_pct: Max % of portfolio in same sector
        """
        self.max_portfolio_risk = max_portfolio_risk_pct
        self.max_single_position = max_single_position_pct
        self.max_positions = max_positions
        self.max_same_sector = max_same_sector_pct
    
    def calculate_position_size(self, portfolio_value: float, 
                               entry_price: float, stop_loss_pct: float,
                               conviction: float = 0.5) -> Tuple[float, int]:
        """
        Calculate position size based on risk
        
        Returns: (position_value, quantity)
        """
        # Base position size (adjusted by conviction)
        base_pct = 0.05 + (conviction * 0.05)  # 5-10% of portfolio
        base_pct = min(base_pct, self.max_single_position)
        
        # Calculate max risk $ (what we'd lose if stopped out)
        max_risk_dollars = portfolio_value * self.max_portfolio_risk
        
        # Risk per share
        risk_per_share = entry_price * stop_loss_pct
        
        # Max quantity based on risk
        max_qty_by_risk = max_risk_dollars / risk_per_share if risk_per_share > 0 else 0
        
        # Max quantity based on position size
        position_value = portfolio_value * base_pct
        max_qty_by_size = position_value / entry_price if entry_price > 0 else 0
        
        # Take the smaller of the two
        quantity = int(min(max_qty_by_risk, max_qty_by_size))
        actual_position_value = quantity * entry_price
        
        return actual_position_value, quantity
    
    def check_can_trade(self, current_positions: Dict, sector: str = None) -> Tuple[bool, str]:
        """
        Check if we can take a new trade
        
        Returns: (can_trade, reason)
        """
        # Check max positions
        if len(current_positions) >= self.max_positions:
            return False, f"Max positions ({self.max_positions}) reached"
        
        # Would add sector concentration check here
        
        return True, "OK"


class AutonomousTrader:
    """
    The Wolf That Hunts Alone
    
    Full autonomous trading with BUY/SELL execution
    """
    
    def __init__(self, paper_trading: bool = True,
                 api_key: str = None, api_secret: str = None):
        """
        Initialize the autonomous trader
        
        Args:
            paper_trading: If True, use paper trading endpoint
            api_key: Alpaca API key (or from env)
            api_secret: Alpaca API secret (or from env)
        """
        self.paper_trading = paper_trading
        self.position_manager = PositionManager()
        self.risk_manager = RiskManager()
        self.executed_trades = []
        
        # Connect to Alpaca
        self.api_key = api_key or os.environ.get('APCA_API_KEY_ID')
        self.api_secret = api_secret or os.environ.get('APCA_API_SECRET_KEY')
        
        self.client = None
        self.connected = False
        
        self._connect()
        
        print(f"🤖 Autonomous Trader initialized")
        print(f"   Mode: {'PAPER' if paper_trading else '⚠️ LIVE'} Trading")
        print(f"   Connected: {self.connected}")
    
    def _connect(self):
        """Connect to Alpaca"""
        if not ALPACA_AVAILABLE:
            print("⚠️  Alpaca SDK not available")
            return
        
        if not self.api_key or not self.api_secret:
            print("⚠️  Alpaca credentials not configured")
            return
        
        try:
            self.client = TradingClient(
                self.api_key,
                self.api_secret,
                paper=self.paper_trading
            )
            
            # Verify connection
            account = self.client.get_account()
            self.connected = True
            print(f"✅ Connected to Alpaca ({account.status})")
            print(f"   Portfolio: ${float(account.portfolio_value):,.2f}")
            print(f"   Buying Power: ${float(account.buying_power):,.2f}")
            
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.connected = False
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected or not self.client:
            return {
                'portfolio_value': 100000,
                'buying_power': 50000,
                'cash': 50000,
                'positions_count': 0
            }
        
        try:
            account = self.client.get_account()
            return {
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'positions_count': len(self.client.get_all_positions())
            }
        except Exception as e:
            print(f"⚠️  Error getting account: {e}")
            return {'portfolio_value': 100000, 'buying_power': 50000}
    
    def execute_buy(self, ticker: str, strategy: TradeStrategy,
                   entry_price: float, conviction: float = 0.5,
                   reason: str = "") -> ExecutedTrade:
        """
        Execute a BUY order
        
        Args:
            ticker: Stock symbol
            strategy: STEADY_HUNTER or HEAD_HUNTER
            entry_price: Target entry price
            conviction: 0.0-1.0 confidence level
            reason: Why we're taking this trade
        
        Returns:
            ExecutedTrade record
        """
        print(f"\n🐺 EXECUTE BUY: {ticker}")
        print(f"   Strategy: {strategy.value}")
        print(f"   Conviction: {conviction:.0%}")
        print(f"   Reason: {reason}")
        
        # Get account info
        account = self.get_account_info()
        portfolio_value = account['portfolio_value']
        
        # Define stop loss based on strategy
        if strategy == TradeStrategy.STEADY_HUNTER:
            stop_loss_pct = 0.08  # 8% stop
            target_1_pct = 0.10   # 10% first target
            target_2_pct = 0.20   # 20% second target
        else:  # HEAD_HUNTER
            stop_loss_pct = 0.15  # 15% stop (need room for volatility)
            target_1_pct = 0.50   # 50% first target
            target_2_pct = 1.00   # 100% second target
        
        # Calculate position size
        position_value, quantity = self.risk_manager.calculate_position_size(
            portfolio_value=portfolio_value,
            entry_price=entry_price,
            stop_loss_pct=stop_loss_pct,
            conviction=conviction
        )
        
        if quantity <= 0:
            print("   ❌ Calculated quantity is 0, cannot trade")
            return None
        
        print(f"   Position Size: ${position_value:,.2f} ({quantity} shares)")
        
        # Create trade config
        config = TradeConfig(
            ticker=ticker,
            strategy=strategy,
            conviction=conviction,
            entry_price=entry_price,
            position_size_pct=position_value / portfolio_value,
            stop_loss_pct=stop_loss_pct,
            target_1_pct=target_1_pct,
            target_2_pct=target_2_pct,
            trailing_stop_pct=0.10  # 10% trailing after T1
        )
        
        # Execute order
        if self.connected and self.client:
            try:
                # Place market order
                order_request = MarketOrderRequest(
                    symbol=ticker,
                    qty=quantity,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                
                order = self.client.submit_order(order_request)
                
                print(f"   ✅ Order submitted: {order.id}")
                
                # Create trade record
                trade = ExecutedTrade(
                    id=f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ticker}",
                    ticker=ticker,
                    side='buy',
                    quantity=quantity,
                    price=entry_price,
                    timestamp=datetime.now(),
                    strategy=strategy.value,
                    status=TradeStatus.PENDING,
                    order_id=str(order.id),
                    notes=reason
                )
                
                # Track position
                self.position_manager.add_position(
                    ticker=ticker,
                    entry_price=entry_price,
                    quantity=quantity,
                    strategy=strategy,
                    config=config
                )
                
                self.executed_trades.append(trade)
                
                # Place stop loss order
                self._place_stop_loss(ticker, quantity, entry_price * (1 - stop_loss_pct))
                
                return trade
                
            except Exception as e:
                print(f"   ❌ Order failed: {e}")
                return None
        else:
            print(f"   📝 [SIMULATION] Would buy {quantity} {ticker} @ ${entry_price:.2f}")
            
            # Create simulated trade record
            trade = ExecutedTrade(
                id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ticker}",
                ticker=ticker,
                side='buy',
                quantity=quantity,
                price=entry_price,
                timestamp=datetime.now(),
                strategy=strategy.value,
                status=TradeStatus.FILLED,
                order_id='SIMULATED',
                notes=reason
            )
            
            self.position_manager.add_position(
                ticker=ticker,
                entry_price=entry_price,
                quantity=quantity,
                strategy=strategy,
                config=config
            )
            
            self.executed_trades.append(trade)
            return trade
    
    def execute_sell(self, ticker: str, quantity: int = None,
                    reason: str = "") -> ExecutedTrade:
        """
        Execute a SELL order
        
        Args:
            ticker: Stock symbol
            quantity: Number of shares (None = sell all)
            reason: Why we're selling
        
        Returns:
            ExecutedTrade record
        """
        print(f"\n💰 EXECUTE SELL: {ticker}")
        print(f"   Reason: {reason}")
        
        position = self.position_manager.get_position(ticker)
        
        if position:
            sell_qty = quantity or position['quantity']
        else:
            sell_qty = quantity or 0
        
        if sell_qty <= 0:
            print("   ❌ No position to sell")
            return None
        
        if self.connected and self.client:
            try:
                order_request = MarketOrderRequest(
                    symbol=ticker,
                    qty=sell_qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                
                order = self.client.submit_order(order_request)
                
                print(f"   ✅ Sell order submitted: {order.id}")
                
                # If selling full position, remove from tracking
                if not quantity or quantity >= position.get('quantity', 0):
                    self.position_manager.remove_position(ticker)
                
                trade = ExecutedTrade(
                    id=f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ticker}_sell",
                    ticker=ticker,
                    side='sell',
                    quantity=sell_qty,
                    price=0,  # Will update when filled
                    timestamp=datetime.now(),
                    strategy=position.get('strategy', 'unknown') if position else 'unknown',
                    status=TradeStatus.PENDING,
                    order_id=str(order.id),
                    notes=reason
                )
                
                self.executed_trades.append(trade)
                return trade
                
            except Exception as e:
                print(f"   ❌ Sell failed: {e}")
                return None
        else:
            print(f"   📝 [SIMULATION] Would sell {sell_qty} {ticker}")
            
            if position:
                self.position_manager.remove_position(ticker)
            
            trade = ExecutedTrade(
                id=f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ticker}_sell",
                ticker=ticker,
                side='sell',
                quantity=sell_qty,
                price=position['entry_price'] * 1.1 if position else 0,  # Simulate +10%
                timestamp=datetime.now(),
                strategy=position.get('strategy', 'unknown') if position else 'unknown',
                status=TradeStatus.FILLED,
                order_id='SIMULATED',
                notes=reason
            )
            
            self.executed_trades.append(trade)
            return trade
    
    def _place_stop_loss(self, ticker: str, quantity: int, stop_price: float):
        """Place a stop loss order"""
        if not self.connected or not self.client:
            print(f"   📝 [SIMULATION] Stop loss @ ${stop_price:.2f}")
            return
        
        try:
            stop_order = StopOrderRequest(
                symbol=ticker,
                qty=quantity,
                side=OrderSide.SELL,
                stop_price=stop_price,
                time_in_force=TimeInForce.GTC  # Good til cancelled
            )
            
            order = self.client.submit_order(stop_order)
            print(f"   🛑 Stop loss placed @ ${stop_price:.2f}")
            
            # Update position with stop order ID
            pos = self.position_manager.get_position(ticker)
            if pos:
                # Would track order ID here
                pass
                
        except Exception as e:
            print(f"   ⚠️  Failed to place stop: {e}")
    
    def execute_opportunity(self, opportunity: Dict) -> ExecutedTrade:
        """
        Execute a trade from a scanned opportunity
        
        Args:
            opportunity: From UniverseScanner with ticker, strategy, score, data
        """
        ticker = opportunity['ticker']
        strategy_str = opportunity['strategy']
        score = opportunity['score']
        data = opportunity['data']
        
        # Map strategy
        if strategy_str == 'STEADY_HUNTER':
            strategy = TradeStrategy.STEADY_HUNTER
        else:
            strategy = TradeStrategy.HEAD_HUNTER
        
        # Calculate conviction from score
        conviction = min(score / 100, 0.9)  # Cap at 90%
        
        # Get entry price
        entry_price = data.get('current_price', 10.0)
        
        # Build reason from analysis
        reasons = opportunity.get('reasons', [])
        reason = f"Score: {score} | " + " | ".join(reasons[:3])
        
        # Execute the buy
        return self.execute_buy(
            ticker=ticker,
            strategy=strategy,
            entry_price=entry_price,
            conviction=conviction,
            reason=reason
        )
    
    def manage_positions(self, current_prices: Dict[str, float] = None):
        """
        Check all positions and manage exits
        
        Args:
            current_prices: Dict of ticker -> current price
        """
        print("\n📊 MANAGING POSITIONS...")
        
        positions = self.position_manager.get_all_positions()
        
        if not positions:
            print("   No open positions")
            return
        
        for ticker, pos in positions.items():
            current_price = current_prices.get(ticker, pos['entry_price']) if current_prices else pos['entry_price']
            
            # Update position tracking
            self.position_manager.update_position(ticker, current_price)
            
            entry = pos['entry_price']
            pnl_pct = (current_price - entry) / entry
            
            print(f"\n   {ticker}: ${current_price:.2f} | P&L: {pnl_pct:+.1%}")
            
            # Check stop loss
            if current_price <= pos['stop_loss_price']:
                print(f"   🛑 STOP LOSS HIT")
                self.execute_sell(ticker, reason="Stop loss triggered")
                continue
            
            # Check target 1
            if current_price >= pos['target_1_price'] and not pos['partial_sold']:
                print(f"   🎯 TARGET 1 HIT")
                # Sell half
                half_qty = int(pos['quantity'] / 2)
                if half_qty > 0:
                    self.execute_sell(ticker, quantity=half_qty, reason="Target 1 reached - scale out")
                    pos['partial_sold'] = True
                    # Move stop to breakeven
                    pos['stop_loss_price'] = entry
                    print(f"   📈 Stop moved to breakeven")
            
            # Check target 2
            if pos['target_2_price'] and current_price >= pos['target_2_price']:
                print(f"   🎯 TARGET 2 HIT - Full exit")
                self.execute_sell(ticker, reason="Target 2 reached - full exit")
    
    def get_status(self) -> Dict:
        """Get trader status"""
        positions = self.position_manager.get_all_positions()
        account = self.get_account_info()
        
        return {
            'connected': self.connected,
            'mode': 'PAPER' if self.paper_trading else 'LIVE',
            'portfolio_value': account['portfolio_value'],
            'buying_power': account['buying_power'],
            'open_positions': len(positions),
            'positions': list(positions.keys()),
            'total_trades': len(self.executed_trades)
        }
    
    def get_open_positions(self) -> Dict:
        """Get all open positions with current P&L"""
        return self.position_manager.get_all_positions()
    
    def get_trade_history(self, limit: int = 50) -> List[ExecutedTrade]:
        """Get recent trade history"""
        return self.executed_trades[-limit:]


# ============ TESTING ============

def test_trader():
    """Test the autonomous trader"""
    print("\n" + "="*80)
    print("🤖 TESTING AUTONOMOUS TRADER")
    print("="*80)
    
    trader = AutonomousTrader(paper_trading=True)
    
    # Test status
    print("\n📊 Trader Status:")
    status = trader.get_status()
    for k, v in status.items():
        print(f"   {k}: {v}")
    
    # Test buy (simulated if no connection)
    print("\n📝 Test Buy Order:")
    trade = trader.execute_buy(
        ticker='ONCY',
        strategy=TradeStrategy.STEADY_HUNTER,
        entry_price=5.50,
        conviction=0.7,
        reason="Test trade - wounded prey setup"
    )
    
    if trade:
        print(f"\n   Trade executed: {trade.id}")
        print(f"   Status: {trade.status}")
    
    # Test position management
    print("\n📊 Positions after buy:")
    positions = trader.get_open_positions()
    for ticker, pos in positions.items():
        print(f"   {ticker}: Entry ${pos['entry_price']:.2f} | Qty: {pos['quantity']}")
    
    # Simulate price change and manage
    trader.manage_positions({'ONCY': 6.00})  # 9% gain
    
    print("\n✅ Trader tests complete!")


if __name__ == "__main__":
    test_trader()
