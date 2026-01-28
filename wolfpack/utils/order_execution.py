"""
Unified Order Execution Module
Single source of truth for all Alpaca order submissions.

Consolidates order execution from:
- wolfpack/portfolio_executor.py
- src/wolf_brain/terminal_brain.py (Line 424)
- src/wolf_brain/autonomous_brain.py (Lines 1524, 1728)
- src/wolf_brain/wolf_terminal.py (Lines 368, 377, 409)
- src/wolf_brain/autonomous_trader.py (Lines 384, 485, 549)
"""

import os
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import (
        MarketOrderRequest,
        LimitOrderRequest,
        StopLossRequest,
        TakeProfitRequest
    )
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False


class OrderType(Enum):
    """Order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderAction(Enum):
    """Order actions"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class OrderRequest:
    """Unified order request"""
    ticker: str
    shares: int
    action: OrderAction
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    time_in_force: str = "day"
    client_order_id: Optional[str] = None


@dataclass
class OrderResult:
    """Unified order result"""
    ticker: str
    shares: int
    action: str
    order_id: Optional[str]
    status: str  # 'success', 'failed', 'pending'
    filled_price: Optional[float]
    error: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class UnifiedOrderExecutor:
    """
    Unified order execution for all systems
    
    Features:
    - Single Alpaca connection (no duplicates)
    - Market, limit, stop orders
    - Bracket orders (entry + stop + target)
    - Error handling & retry logic
    - Execution logging
    - Paper/live trading support
    """
    
    def __init__(self, paper_trading: bool = True, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None):
        """
        Initialize executor
        
        Args:
            paper_trading: Use paper trading (default True for safety)
            api_key: Alpaca API key (or from env)
            api_secret: Alpaca API secret (or from env)
        """
        self.paper_trading = paper_trading
        self.client = None
        self.account = None
        
        if not ALPACA_AVAILABLE:
            raise ImportError("alpaca-py not installed. Run: pip install alpaca-py")
        
        # Load .env file
        try:
            from dotenv import load_dotenv
            # Try loading from multiple locations
            env_paths = [
                os.path.join(os.path.dirname(__file__), '..', '..', '.env'),  # brokkr/.env
                os.path.join(os.path.dirname(__file__), '..', '.env'),  # wolfpack/.env
                '.env'  # current directory
            ]
            for env_path in env_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    break
        except ImportError:
            pass  # dotenv not installed, will use os.getenv directly
        
        # Load credentials
        if not api_key or not api_secret:
            if paper_trading:
                api_key = os.getenv('ALPACA_PAPER_KEY_ID')
                api_secret = os.getenv('ALPACA_PAPER_SECRET_KEY')
            else:
                api_key = os.getenv('ALPACA_LIVE_KEY_ID')
                api_secret = os.getenv('ALPACA_LIVE_SECRET_KEY')
        
        if not api_key or not api_secret:
            raise ValueError("Alpaca credentials not found in environment")
        
        # Initialize client
        self.client = TradingClient(api_key, api_secret, paper=paper_trading)
        
        # Get account info
        try:
            self.account = self.client.get_account()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Alpaca: {e}")
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.account:
            self.account = self.client.get_account()
        
        return {
            'equity': float(self.account.equity),
            'cash': float(self.account.cash),
            'buying_power': float(self.account.buying_power),
            'portfolio_value': float(self.account.portfolio_value),
            'pattern_day_trader': self.account.pattern_day_trader,
            'trading_blocked': self.account.trading_blocked,
            'account_blocked': self.account.account_blocked
        }
    
    def submit_market_order(self, ticker: str, shares: int, action: OrderAction,
                           stop_loss: Optional[float] = None,
                           take_profit: Optional[float] = None) -> OrderResult:
        """
        Submit market order (immediate execution at best price)
        
        Args:
            ticker: Stock symbol
            shares: Number of shares
            action: BUY or SELL
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
            
        Returns:
            OrderResult
        """
        try:
            side = OrderSide.BUY if action == OrderAction.BUY else OrderSide.SELL
            
            # Build order request
            order_data = MarketOrderRequest(
                symbol=ticker,
                qty=shares,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            
            # Add bracket orders if stop/target specified
            if stop_loss and take_profit:
                order_data.order_class = OrderClass.BRACKET
                order_data.stop_loss = StopLossRequest(stop_price=stop_loss)
                order_data.take_profit = TakeProfitRequest(limit_price=take_profit)
            elif stop_loss:
                order_data.order_class = OrderClass.OTO  # One-triggers-other
                order_data.stop_loss = StopLossRequest(stop_price=stop_loss)
            
            # Submit order
            order = self.client.submit_order(order_data)
            
            return OrderResult(
                ticker=ticker,
                shares=shares,
                action=action.value,
                order_id=order.id,
                status='success',
                filled_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                error=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return OrderResult(
                ticker=ticker,
                shares=shares,
                action=action.value,
                order_id=None,
                status='failed',
                filled_price=None,
                error=str(e),
                timestamp=datetime.now()
            )
    
    def submit_limit_order(self, ticker: str, shares: int, action: OrderAction,
                          limit_price: float, stop_loss: Optional[float] = None,
                          take_profit: Optional[float] = None) -> OrderResult:
        """
        Submit limit order (execute only at specified price or better)
        
        Args:
            ticker: Stock symbol
            shares: Number of shares
            action: BUY or SELL
            limit_price: Maximum buy price or minimum sell price
            stop_loss: Optional stop loss price
            take_profit: Optional take profit price
            
        Returns:
            OrderResult
        """
        try:
            side = OrderSide.BUY if action == OrderAction.BUY else OrderSide.SELL
            
            order_data = LimitOrderRequest(
                symbol=ticker,
                qty=shares,
                side=side,
                limit_price=limit_price,
                time_in_force=TimeInForce.DAY
            )
            
            # Add bracket orders if specified
            if stop_loss and take_profit:
                order_data.order_class = OrderClass.BRACKET
                order_data.stop_loss = StopLossRequest(stop_price=stop_loss)
                order_data.take_profit = TakeProfitRequest(limit_price=take_profit)
            elif stop_loss:
                order_data.order_class = OrderClass.OTO
                order_data.stop_loss = StopLossRequest(stop_price=stop_loss)
            
            order = self.client.submit_order(order_data)
            
            return OrderResult(
                ticker=ticker,
                shares=shares,
                action=action.value,
                order_id=order.id,
                status='success',
                filled_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                error=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return OrderResult(
                ticker=ticker,
                shares=shares,
                action=action.value,
                order_id=None,
                status='failed',
                filled_price=None,
                error=str(e),
                timestamp=datetime.now()
            )
    
    def submit_batch_orders(self, orders: List[OrderRequest]) -> List[OrderResult]:
        """
        Submit multiple orders (for portfolio execution)
        
        Args:
            orders: List of OrderRequest objects
            
        Returns:
            List of OrderResult objects
        """
        results = []
        
        for order in orders:
            if order.order_type == OrderType.MARKET:
                result = self.submit_market_order(
                    ticker=order.ticker,
                    shares=order.shares,
                    action=order.action,
                    stop_loss=order.stop_loss_price,
                    take_profit=order.take_profit_price
                )
            elif order.order_type == OrderType.LIMIT:
                result = self.submit_limit_order(
                    ticker=order.ticker,
                    shares=order.shares,
                    action=order.action,
                    limit_price=order.limit_price,
                    stop_loss=order.stop_loss_price,
                    take_profit=order.take_profit_price
                )
            else:
                result = OrderResult(
                    ticker=order.ticker,
                    shares=order.shares,
                    action=order.action.value,
                    order_id=None,
                    status='failed',
                    filled_price=None,
                    error=f"Unsupported order type: {order.order_type}",
                    timestamp=datetime.now()
                )
            
            results.append(result)
        
        return results
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            positions = self.client.get_all_positions()
            return [
                {
                    'ticker': pos.symbol,
                    'shares': int(pos.qty),
                    'entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'pnl': float(pos.unrealized_pl),
                    'pnl_pct': float(pos.unrealized_plpc) * 100
                }
                for pos in positions
            ]
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            self.client.cancel_orders()
            return True
        except Exception as e:
            print(f"Error canceling orders: {e}")
            return False
    
    def close_position(self, ticker: str) -> OrderResult:
        """Close an open position (market sell)"""
        try:
            # Get position
            position = self.client.get_open_position(ticker)
            shares = abs(int(position.qty))
            
            # Close position
            self.client.close_position(ticker)
            
            return OrderResult(
                ticker=ticker,
                shares=shares,
                action='sell',
                order_id=None,
                status='success',
                filled_price=float(position.current_price),
                error=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return OrderResult(
                ticker=ticker,
                shares=0,
                action='sell',
                order_id=None,
                status='failed',
                filled_price=None,
                error=str(e),
                timestamp=datetime.now()
            )


# Convenience functions for quick usage
def quick_buy(ticker: str, shares: int, stop_loss: Optional[float] = None) -> OrderResult:
    """Quick market buy"""
    executor = UnifiedOrderExecutor(paper_trading=True)
    return executor.submit_market_order(ticker, shares, OrderAction.BUY, stop_loss=stop_loss)


def quick_sell(ticker: str, shares: int) -> OrderResult:
    """Quick market sell"""
    executor = UnifiedOrderExecutor(paper_trading=True)
    return executor.submit_market_order(ticker, shares, OrderAction.SELL)
