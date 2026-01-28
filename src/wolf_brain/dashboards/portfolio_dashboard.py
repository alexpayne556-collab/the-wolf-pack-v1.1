"""
📊 PORTFOLIO DASHBOARD - ALPACA HOLDINGS VIEW
Built: January 20, 2026

Shows:
- Current positions and P&L
- Account value over time
- Today's trades
- Position health (HEALTHY vs UNHEALTHY charts)
- Risk exposure by sector

Usage:
    from wolf_brain.dashboards.portfolio_dashboard import create_portfolio_dashboard
    
    app = create_portfolio_dashboard()
    app.run_server(debug=True)
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

try:
    import dash
    from dash import dcc, html, Input, Output, State
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import pandas as pd
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("⚠️  Dash not installed. Run: pip install dash plotly pandas")

try:
    import alpaca_trade_api as tradeapi
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  Alpaca API not installed. Run: pip install alpaca-trade-api")


class AlpacaPortfolioData:
    """
    Fetch portfolio data from Alpaca
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None, 
                 paper: bool = True):
        """
        Initialize Alpaca connection
        
        Args:
            api_key: Alpaca API key (or from env ALPACA_API_KEY)
            secret_key: Alpaca secret key (or from env ALPACA_SECRET_KEY)
            paper: Use paper trading (default True for safety)
        """
        self.api_key = api_key or os.getenv('ALPACA_API_KEY', '')
        self.secret_key = secret_key or os.getenv('ALPACA_SECRET_KEY', '')
        self.base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
        
        self.api = None
        self.connected = False
        
        if ALPACA_AVAILABLE and self.api_key and self.secret_key:
            try:
                self.api = tradeapi.REST(
                    self.api_key,
                    self.secret_key,
                    self.base_url
                )
                # Test connection
                self.api.get_account()
                self.connected = True
                print("✅ Alpaca connected")
            except Exception as e:
                print(f"⚠️  Alpaca connection failed: {e}")
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected:
            return self._get_mock_account()
        
        try:
            account = self.api.get_account()
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'day_trade_count': account.daytrade_count,
                'pdt_status': account.pattern_day_trader,
                'last_equity': float(account.last_equity),
                'day_change': float(account.equity) - float(account.last_equity),
                'day_change_pct': (float(account.equity) - float(account.last_equity)) / float(account.last_equity) * 100 if float(account.last_equity) > 0 else 0
            }
        except Exception as e:
            print(f"Error fetching account: {e}")
            return self._get_mock_account()
    
    def get_positions(self) -> List[Dict]:
        """Get all current positions"""
        if not self.connected:
            return self._get_mock_positions()
        
        try:
            positions = self.api.list_positions()
            result = []
            
            for pos in positions:
                result.append({
                    'ticker': pos.symbol,
                    'shares': float(pos.qty),
                    'avg_cost': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_pl_pct': float(pos.unrealized_plpc) * 100,
                    'day_change': float(pos.unrealized_intraday_pl),
                    'day_change_pct': float(pos.unrealized_intraday_plpc) * 100,
                    'side': pos.side
                })
            
            return result
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return self._get_mock_positions()
    
    def get_recent_orders(self, limit: int = 20) -> List[Dict]:
        """Get recent orders"""
        if not self.connected:
            return self._get_mock_orders()
        
        try:
            orders = self.api.list_orders(
                status='all',
                limit=limit
            )
            
            result = []
            for order in orders:
                result.append({
                    'id': order.id,
                    'ticker': order.symbol,
                    'side': order.side,
                    'qty': float(order.qty),
                    'type': order.type,
                    'status': order.status,
                    'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0,
                    'submitted_at': str(order.submitted_at),
                    'filled_at': str(order.filled_at) if order.filled_at else None
                })
            
            return result
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return self._get_mock_orders()
    
    def get_portfolio_history(self, days: int = 30) -> pd.DataFrame:
        """Get portfolio value history"""
        if not self.connected:
            return self._get_mock_history(days)
        
        try:
            history = self.api.get_portfolio_history(
                period=f"{days}D",
                timeframe="1D"
            )
            
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(history.timestamp, unit='s'),
                'equity': history.equity,
                'profit_loss': history.profit_loss,
                'profit_loss_pct': history.profit_loss_pct
            })
            
            return df
        except Exception as e:
            print(f"Error fetching history: {e}")
            return self._get_mock_history(days)
    
    # ========== MOCK DATA FOR TESTING ==========
    
    def _get_mock_account(self) -> Dict:
        """Mock account for testing without API keys"""
        return {
            'equity': 10240.72,
            'cash': 5000.00,
            'buying_power': 10000.00,
            'portfolio_value': 10240.72,
            'day_trade_count': 0,
            'pdt_status': False,
            'last_equity': 10000.00,
            'day_change': 240.72,
            'day_change_pct': 2.41
        }
    
    def _get_mock_positions(self) -> List[Dict]:
        """Mock positions for testing"""
        return [
            {
                'ticker': 'IBRX',
                'shares': 37.08,
                'avg_cost': 2.18,
                'current_price': 6.48,
                'market_value': 240.28,
                'unrealized_pl': 159.39,
                'unrealized_pl_pct': 197.25,
                'day_change': 12.50,
                'day_change_pct': 5.49,
                'side': 'long'
            },
            {
                'ticker': 'ONCY',
                'shares': 80,
                'avg_cost': 1.04,
                'current_price': 1.13,
                'market_value': 90.40,
                'unrealized_pl': 7.20,
                'unrealized_pl_pct': 8.65,
                'day_change': 7.20,
                'day_change_pct': 8.65,
                'side': 'long'
            },
            {
                'ticker': 'UUUU',
                'shares': 3,
                'avg_cost': 7.25,
                'current_price': 7.89,
                'market_value': 23.67,
                'unrealized_pl': 1.92,
                'unrealized_pl_pct': 8.83,
                'day_change': 0.45,
                'day_change_pct': 1.93,
                'side': 'long'
            },
            {
                'ticker': 'KTOS',
                'shares': 0.72,
                'avg_cost': 28.50,
                'current_price': 30.18,
                'market_value': 21.73,
                'unrealized_pl': 1.21,
                'unrealized_pl_pct': 5.89,
                'day_change': 0.22,
                'day_change_pct': 1.02,
                'side': 'long'
            },
            {
                'ticker': 'MU',
                'shares': 1.27,
                'avg_cost': 87.50,
                'current_price': 94.37,
                'market_value': 119.85,
                'unrealized_pl': 8.73,
                'unrealized_pl_pct': 7.85,
                'day_change': 2.15,
                'day_change_pct': 1.83,
                'side': 'long'
            }
        ]
    
    def _get_mock_orders(self) -> List[Dict]:
        """Mock orders for testing"""
        return [
            {
                'id': 'mock-001',
                'ticker': 'ONCY',
                'side': 'buy',
                'qty': 80,
                'type': 'market',
                'status': 'filled',
                'filled_qty': 80,
                'filled_avg_price': 1.04,
                'submitted_at': '2026-01-19T10:30:00',
                'filled_at': '2026-01-19T10:30:05'
            },
            {
                'id': 'mock-002',
                'ticker': 'IBRX',
                'side': 'buy',
                'qty': 37.08,
                'type': 'market',
                'status': 'filled',
                'filled_qty': 37.08,
                'filled_avg_price': 2.18,
                'submitted_at': '2026-01-10T09:45:00',
                'filled_at': '2026-01-10T09:45:02'
            }
        ]
    
    def _get_mock_history(self, days: int) -> pd.DataFrame:
        """Mock portfolio history for testing"""
        import numpy as np
        
        dates = pd.date_range(
            end=datetime.now(),
            periods=days,
            freq='D'
        )
        
        # Simulate portfolio growth
        base = 10000
        returns = np.random.normal(0.002, 0.02, days)
        equity = [base]
        for r in returns[1:]:
            equity.append(equity[-1] * (1 + r))
        
        return pd.DataFrame({
            'timestamp': dates,
            'equity': equity,
            'profit_loss': [e - base for e in equity],
            'profit_loss_pct': [(e - base) / base * 100 for e in equity]
        })


def create_portfolio_dashboard(portfolio: AlpacaPortfolioData = None):
    """
    Create the portfolio dashboard Dash app
    """
    if not DASH_AVAILABLE:
        print("❌ Cannot create dashboard - Dash not installed")
        print("   Run: pip install dash plotly pandas")
        return None
    
    if portfolio is None:
        portfolio = AlpacaPortfolioData()
    
    app = dash.Dash(__name__, title='🐺 Wolf Pack Portfolio')
    
    # Dashboard layout
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("🐺 WOLF PACK PORTFOLIO", style={'textAlign': 'center', 'color': '#00d4ff'}),
            html.P(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                   id='last-update', style={'textAlign': 'center', 'color': '#888'})
        ], style={'backgroundColor': '#1a1a2e', 'padding': '20px'}),
        
        # Account Summary Row
        html.Div([
            html.Div([
                html.H3("EQUITY", style={'color': '#888', 'marginBottom': '5px'}),
                html.H2(id='equity-value', style={'color': '#00d4ff', 'margin': '0'})
            ], style={'flex': '1', 'textAlign': 'center', 'padding': '20px', 
                     'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px'}),
            
            html.Div([
                html.H3("DAY P&L", style={'color': '#888', 'marginBottom': '5px'}),
                html.H2(id='day-pnl', style={'margin': '0'})
            ], style={'flex': '1', 'textAlign': 'center', 'padding': '20px',
                     'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px'}),
            
            html.Div([
                html.H3("BUYING POWER", style={'color': '#888', 'marginBottom': '5px'}),
                html.H2(id='buying-power', style={'color': '#ffd700', 'margin': '0'})
            ], style={'flex': '1', 'textAlign': 'center', 'padding': '20px',
                     'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px'}),
            
            html.Div([
                html.H3("POSITIONS", style={'color': '#888', 'marginBottom': '5px'}),
                html.H2(id='position-count', style={'color': '#00ff88', 'margin': '0'})
            ], style={'flex': '1', 'textAlign': 'center', 'padding': '20px',
                     'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px'}),
        ], style={'display': 'flex', 'padding': '10px', 'backgroundColor': '#0f0f23'}),
        
        # Charts Row
        html.Div([
            # Equity Chart
            html.Div([
                html.H3("📈 EQUITY CURVE", style={'color': '#00d4ff', 'padding': '10px'}),
                dcc.Graph(id='equity-chart')
            ], style={'flex': '2', 'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px'}),
            
            # Allocation Pie
            html.Div([
                html.H3("📊 ALLOCATION", style={'color': '#00d4ff', 'padding': '10px'}),
                dcc.Graph(id='allocation-chart')
            ], style={'flex': '1', 'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px'}),
        ], style={'display': 'flex', 'padding': '10px', 'backgroundColor': '#0f0f23'}),
        
        # Positions Table
        html.Div([
            html.H3("📋 POSITIONS", style={'color': '#00d4ff', 'padding': '10px'}),
            html.Div(id='positions-table')
        ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px', 'padding': '10px'}),
        
        # Recent Orders
        html.Div([
            html.H3("📝 RECENT ORDERS", style={'color': '#00d4ff', 'padding': '10px'}),
            html.Div(id='orders-table')
        ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'margin': '10px', 'padding': '10px'}),
        
        # Refresh interval
        dcc.Interval(
            id='refresh-interval',
            interval=60*1000,  # 60 seconds
            n_intervals=0
        ),
        
        # Store for data
        dcc.Store(id='portfolio-data')
        
    ], style={'backgroundColor': '#0f0f23', 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'})
    
    # Callbacks
    @app.callback(
        [Output('equity-value', 'children'),
         Output('day-pnl', 'children'),
         Output('day-pnl', 'style'),
         Output('buying-power', 'children'),
         Output('position-count', 'children'),
         Output('equity-chart', 'figure'),
         Output('allocation-chart', 'figure'),
         Output('positions-table', 'children'),
         Output('orders-table', 'children'),
         Output('last-update', 'children')],
        [Input('refresh-interval', 'n_intervals')]
    )
    def update_dashboard(n):
        # Fetch data
        account = portfolio.get_account_info()
        positions = portfolio.get_positions()
        orders = portfolio.get_recent_orders()
        history = portfolio.get_portfolio_history(30)
        
        # Account values
        equity = f"${account['equity']:,.2f}"
        day_pnl = f"${account['day_change']:+,.2f} ({account['day_change_pct']:+.2f}%)"
        day_pnl_style = {
            'color': '#00ff88' if account['day_change'] >= 0 else '#ff4444',
            'margin': '0'
        }
        buying_power = f"${account['buying_power']:,.2f}"
        pos_count = str(len(positions))
        
        # Equity chart
        equity_fig = go.Figure()
        equity_fig.add_trace(go.Scatter(
            x=history['timestamp'],
            y=history['equity'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#00d4ff'),
            fillcolor='rgba(0, 212, 255, 0.2)'
        ))
        equity_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=20, t=20, b=40),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        
        # Allocation pie
        if positions:
            alloc_fig = go.Figure(data=[go.Pie(
                labels=[p['ticker'] for p in positions],
                values=[p['market_value'] for p in positions],
                hole=0.4,
                marker=dict(colors=['#00d4ff', '#00ff88', '#ffd700', '#ff6b6b', '#9b59b6'])
            )])
            alloc_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
        else:
            alloc_fig = go.Figure()
            alloc_fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text='No positions', showarrow=False, font=dict(color='white', size=20))]
            )
        
        # Positions table
        if positions:
            pos_rows = []
            for p in sorted(positions, key=lambda x: x['unrealized_pl'], reverse=True):
                pl_color = '#00ff88' if p['unrealized_pl'] >= 0 else '#ff4444'
                pos_rows.append(html.Tr([
                    html.Td(p['ticker'], style={'fontWeight': 'bold', 'color': '#00d4ff'}),
                    html.Td(f"{p['shares']:.2f}"),
                    html.Td(f"${p['avg_cost']:.2f}"),
                    html.Td(f"${p['current_price']:.2f}"),
                    html.Td(f"${p['market_value']:.2f}"),
                    html.Td(f"${p['unrealized_pl']:+.2f}", style={'color': pl_color}),
                    html.Td(f"{p['unrealized_pl_pct']:+.1f}%", style={'color': pl_color, 'fontWeight': 'bold'}),
                ], style={'borderBottom': '1px solid #333'}))
            
            pos_table = html.Table([
                html.Thead(html.Tr([
                    html.Th("TICKER"),
                    html.Th("SHARES"),
                    html.Th("AVG COST"),
                    html.Th("PRICE"),
                    html.Th("VALUE"),
                    html.Th("P&L"),
                    html.Th("P&L %"),
                ], style={'color': '#888', 'textAlign': 'left'})),
                html.Tbody(pos_rows)
            ], style={'width': '100%', 'color': 'white', 'borderCollapse': 'collapse'})
        else:
            pos_table = html.P("No open positions", style={'color': '#888'})
        
        # Orders table
        if orders:
            order_rows = []
            for o in orders[:10]:
                status_color = '#00ff88' if o['status'] == 'filled' else '#ffd700'
                order_rows.append(html.Tr([
                    html.Td(o['ticker'], style={'color': '#00d4ff'}),
                    html.Td(o['side'].upper(), style={
                        'color': '#00ff88' if o['side'] == 'buy' else '#ff4444'
                    }),
                    html.Td(f"{o['qty']:.2f}"),
                    html.Td(f"${o['filled_avg_price']:.2f}" if o['filled_avg_price'] else '-'),
                    html.Td(o['status'].upper(), style={'color': status_color}),
                    html.Td(o['submitted_at'][:16] if o['submitted_at'] else '-'),
                ], style={'borderBottom': '1px solid #333'}))
            
            orders_table = html.Table([
                html.Thead(html.Tr([
                    html.Th("TICKER"),
                    html.Th("SIDE"),
                    html.Th("QTY"),
                    html.Th("FILLED PRICE"),
                    html.Th("STATUS"),
                    html.Th("TIME"),
                ], style={'color': '#888', 'textAlign': 'left'})),
                html.Tbody(order_rows)
            ], style={'width': '100%', 'color': 'white', 'borderCollapse': 'collapse'})
        else:
            orders_table = html.P("No recent orders", style={'color': '#888'})
        
        update_time = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return (equity, day_pnl, day_pnl_style, buying_power, pos_count,
                equity_fig, alloc_fig, pos_table, orders_table, update_time)
    
    return app


# ============ STANDALONE RUN ============

if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 LAUNCHING PORTFOLIO DASHBOARD")
    print("="*80)
    
    portfolio = AlpacaPortfolioData()
    app = create_portfolio_dashboard(portfolio)
    
    if app:
        print("\n🌐 Dashboard running at: http://localhost:8050")
        print("   Press Ctrl+C to stop\n")
        app.run(debug=True, port=8050)
    else:
        print("❌ Could not create dashboard")
