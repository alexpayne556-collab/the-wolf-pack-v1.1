"""
🧠 TRADING BOT DASHBOARD - INTERACT WITH THE WOLF BRAIN
Built: January 20, 2026

This dashboard lets you:
- CHAT with the Wolf Brain
- TEACH it new strategies
- SEE what it's thinking
- APPROVE or REJECT trade suggestions
- MONITOR its learning progress

Run: python -m wolf_brain.dashboards.trading_dashboard
Then open: http://localhost:8051
"""

import os
import sys
from datetime import datetime
from typing import Dict, List
import json

try:
    import dash
    from dash import dcc, html, Input, Output, State
    import plotly.graph_objects as go
    import pandas as pd
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("⚠️  Dash not installed. Run: pip install dash plotly pandas")

# Import Wolf Brain components
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from brain_core import WolfBrain
    from strategy_plugins import StrategyPluginManager
    from memory_system import MemorySystem, WorkingMemory
    BRAIN_AVAILABLE = True
except ImportError as e:
    BRAIN_AVAILABLE = False
    print(f"⚠️  Wolf Brain components not available: {e}")


class TradingBotInterface:
    """
    Interface for the trading dashboard to interact with the Wolf Brain
    """
    
    def __init__(self):
        """Initialize the brain interface"""
        self.brain = None
        self.strategies = None
        self.memory = None
        self.working_memory = WorkingMemory()
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize Wolf Brain components"""
        try:
            # Initialize brain with Fenrir model (Tyr's custom model)
            self.brain = WolfBrain(model='fenrir:latest')
            
            # Initialize strategy manager with brain connection
            self.strategies = StrategyPluginManager(brain=self.brain if self.brain.ollama_connected else None)
            
            # Initialize memory
            self.memory = MemorySystem()
            
            print("✅ Trading Bot Interface initialized")
            
        except Exception as e:
            print(f"⚠️  Partial initialization: {e}")
            # Initialize what we can
            if self.strategies is None:
                self.strategies = StrategyPluginManager(brain=None)
            if self.memory is None:
                self.memory = MemorySystem()
    
    def chat(self, message: str) -> str:
        """Send a message to the brain and get response"""
        if self.brain and self.brain.ollama_connected:
            return self.brain.chat(message)
        else:
            return "[Brain Offline] Ollama not running. Start with: ollama serve"
    
    def ask(self, question: str) -> str:
        """Ask the brain a question"""
        if self.brain and self.brain.ollama_connected:
            return self.brain.ask(question)
        else:
            return "[Brain Offline] Cannot answer questions without Ollama."
    
    def teach_strategy(self, name: str, description: str) -> str:
        """Teach the brain a new strategy"""
        if self.strategies:
            strategy = self.strategies.add_strategy_from_description(name, description)
            
            # Store in memory
            if self.memory:
                self.memory.store_taught_strategy(name, description)
            
            return f"✅ Strategy '{name}' has been learned!"
        else:
            return "❌ Strategy manager not available"
    
    def analyze_ticker(self, ticker: str) -> Dict:
        """Run full analysis on a ticker"""
        # Get basic data (would integrate with real data sources)
        data = self._get_ticker_data(ticker)
        
        # Run all strategies
        if self.strategies:
            strategy_results = self.strategies.analyze_with_all(ticker, data)
        else:
            strategy_results = {}
        
        # Get brain reasoning if available
        brain_reasoning = None
        if self.brain and self.brain.ollama_connected:
            analysis = self.brain.reason_about_opportunity(ticker, data)
            brain_reasoning = analysis
        
        return {
            'ticker': ticker,
            'data': data,
            'strategy_results': strategy_results,
            'brain_reasoning': brain_reasoning,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_ticker_data(self, ticker: str) -> Dict:
        """Get ticker data (would integrate with yfinance/Alpaca)"""
        # Placeholder - would fetch real data
        return {
            'ticker': ticker,
            'current_price': 10.00,
            'high_52w': 15.00,
            'low_52w': 5.00,
            'float': 10_000_000,
            'market_cap': 100_000_000,
            'volume': 1_000_000,
            'relative_volume': 1.5,
            'sector': 'biotech',
            'chart_health': 'HEALTHY'
        }
    
    def get_strategy_performance(self) -> Dict:
        """Get all strategy performance"""
        if self.memory:
            return self.memory.get_strategy_performance()
        return {}
    
    def get_taught_strategies(self) -> List[Dict]:
        """Get list of taught strategies"""
        if self.memory:
            return self.memory.get_taught_strategies()
        return []
    
    def get_learning_insights(self) -> Dict:
        """Get learning insights"""
        if self.memory:
            return self.memory.get_learning_insights()
        return {}


def create_trading_dashboard(bot: TradingBotInterface = None):
    """
    Create the trading bot dashboard
    """
    if not DASH_AVAILABLE:
        print("❌ Cannot create dashboard - Dash not installed")
        return None
    
    if bot is None:
        bot = TradingBotInterface()
    
    app = dash.Dash(__name__, title='🧠 Wolf Brain Dashboard')
    
    # Dashboard layout
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("🧠 WOLF BRAIN TRADING DASHBOARD", 
                   style={'textAlign': 'center', 'color': '#ff6b6b'}),
            html.P("Not a robot. A THINKING brain.", 
                   style={'textAlign': 'center', 'color': '#888', 'fontStyle': 'italic'})
        ], style={'backgroundColor': '#1a1a2e', 'padding': '20px'}),
        
        # Status Bar
        html.Div([
            html.Div([
                html.Span("🧠 Brain: ", style={'color': '#888'}),
                html.Span(id='brain-status', style={'fontWeight': 'bold'})
            ], style={'flex': '1'}),
            html.Div([
                html.Span("📚 Strategies: ", style={'color': '#888'}),
                html.Span(id='strategy-count', style={'fontWeight': 'bold', 'color': '#00d4ff'})
            ], style={'flex': '1'}),
            html.Div([
                html.Span("💾 Memories: ", style={'color': '#888'}),
                html.Span(id='memory-count', style={'fontWeight': 'bold', 'color': '#ffd700'})
            ], style={'flex': '1'}),
        ], style={'display': 'flex', 'padding': '10px 20px', 'backgroundColor': '#16213e'}),
        
        # Main content - 2 columns
        html.Div([
            # Left column - Chat & Teach
            html.Div([
                # Chat with Brain
                html.Div([
                    html.H3("💬 CHAT WITH THE BRAIN", style={'color': '#ff6b6b'}),
                    
                    # Chat history
                    html.Div(id='chat-history', style={
                        'height': '300px',
                        'overflowY': 'auto',
                        'backgroundColor': '#0f0f23',
                        'borderRadius': '10px',
                        'padding': '10px',
                        'marginBottom': '10px'
                    }),
                    
                    # Input
                    html.Div([
                        dcc.Input(
                            id='chat-input',
                            type='text',
                            placeholder='Ask or tell the brain something...',
                            style={
                                'flex': '1',
                                'padding': '10px',
                                'backgroundColor': '#0f0f23',
                                'border': '1px solid #333',
                                'borderRadius': '5px',
                                'color': 'white',
                                'marginRight': '10px'
                            }
                        ),
                        html.Button('Send', id='chat-send', style={
                            'padding': '10px 20px',
                            'backgroundColor': '#ff6b6b',
                            'border': 'none',
                            'borderRadius': '5px',
                            'color': 'white',
                            'cursor': 'pointer'
                        })
                    ], style={'display': 'flex'})
                ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'padding': '15px', 'marginBottom': '15px'}),
                
                # Teach New Strategy
                html.Div([
                    html.H3("📚 TEACH NEW STRATEGY", style={'color': '#00ff88'}),
                    
                    dcc.Input(
                        id='strategy-name',
                        type='text',
                        placeholder='Strategy Name (e.g., "Trump Policy Play")',
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'backgroundColor': '#0f0f23',
                            'border': '1px solid #333',
                            'borderRadius': '5px',
                            'color': 'white',
                            'marginBottom': '10px'
                        }
                    ),
                    
                    dcc.Textarea(
                        id='strategy-description',
                        placeholder='Describe the strategy in plain English...\n\nExample:\nLook for defense stocks when Trump announces military spending.\nEntry signals: Contract news, insider buying\nExit: +20% or news reversal',
                        style={
                            'width': '100%',
                            'height': '150px',
                            'padding': '10px',
                            'backgroundColor': '#0f0f23',
                            'border': '1px solid #333',
                            'borderRadius': '5px',
                            'color': 'white',
                            'marginBottom': '10px',
                            'resize': 'vertical'
                        }
                    ),
                    
                    html.Button('Teach Strategy', id='teach-button', style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': '#00ff88',
                        'border': 'none',
                        'borderRadius': '5px',
                        'color': '#1a1a2e',
                        'fontWeight': 'bold',
                        'cursor': 'pointer'
                    }),
                    
                    html.Div(id='teach-result', style={'marginTop': '10px', 'color': '#888'})
                ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'padding': '15px'})
                
            ], style={'flex': '1', 'marginRight': '15px'}),
            
            # Right column - Analysis & Monitoring
            html.Div([
                # Quick Analyze
                html.Div([
                    html.H3("🔍 ANALYZE TICKER", style={'color': '#00d4ff'}),
                    
                    html.Div([
                        dcc.Input(
                            id='analyze-ticker',
                            type='text',
                            placeholder='Enter ticker (e.g., GLSI)',
                            style={
                                'flex': '1',
                                'padding': '10px',
                                'backgroundColor': '#0f0f23',
                                'border': '1px solid #333',
                                'borderRadius': '5px',
                                'color': 'white',
                                'marginRight': '10px',
                                'textTransform': 'uppercase'
                            }
                        ),
                        html.Button('Analyze', id='analyze-button', style={
                            'padding': '10px 20px',
                            'backgroundColor': '#00d4ff',
                            'border': 'none',
                            'borderRadius': '5px',
                            'color': '#1a1a2e',
                            'fontWeight': 'bold',
                            'cursor': 'pointer'
                        })
                    ], style={'display': 'flex', 'marginBottom': '10px'}),
                    
                    html.Div(id='analysis-result', style={
                        'backgroundColor': '#0f0f23',
                        'borderRadius': '10px',
                        'padding': '15px',
                        'minHeight': '200px',
                        'maxHeight': '400px',
                        'overflowY': 'auto'
                    })
                ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'padding': '15px', 'marginBottom': '15px'}),
                
                # Strategy Performance
                html.Div([
                    html.H3("📊 STRATEGY PERFORMANCE", style={'color': '#ffd700'}),
                    html.Div(id='strategy-performance')
                ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'padding': '15px', 'marginBottom': '15px'}),
                
                # Taught Strategies
                html.Div([
                    html.H3("🎓 LEARNED STRATEGIES", style={'color': '#9b59b6'}),
                    html.Div(id='taught-strategies')
                ], style={'backgroundColor': '#16213e', 'borderRadius': '10px', 'padding': '15px'})
                
            ], style={'flex': '1'})
            
        ], style={'display': 'flex', 'padding': '15px', 'backgroundColor': '#0f0f23'}),
        
        # Hidden stores
        dcc.Store(id='chat-history-store', data=[]),
        dcc.Interval(id='refresh-interval', interval=30*1000, n_intervals=0)
        
    ], style={'backgroundColor': '#0f0f23', 'minHeight': '100vh', 'fontFamily': 'Arial, sans-serif'})
    
    # ========== CALLBACKS ==========
    
    @app.callback(
        [Output('brain-status', 'children'),
         Output('brain-status', 'style'),
         Output('strategy-count', 'children'),
         Output('memory-count', 'children'),
         Output('strategy-performance', 'children'),
         Output('taught-strategies', 'children')],
        [Input('refresh-interval', 'n_intervals')]
    )
    def update_status(n):
        # Brain status
        if bot.brain and bot.brain.ollama_connected:
            brain_text = f"ONLINE ({bot.brain.model})"
            brain_style = {'color': '#00ff88', 'fontWeight': 'bold'}
        else:
            brain_text = "OFFLINE (start Ollama)"
            brain_style = {'color': '#ff4444', 'fontWeight': 'bold'}
        
        # Strategy count
        strat_count = str(len(bot.strategies.strategies)) if bot.strategies else "0"
        
        # Memory count
        insights = bot.get_learning_insights()
        mem_count = str(insights.get('total_trades', 0))
        
        # Strategy performance
        perf = bot.get_strategy_performance()
        if perf:
            perf_rows = []
            for name, stats in perf.items():
                trades = stats.get('trades', 0)
                if trades > 0:
                    win_rate = stats.get('wins', 0) / trades * 100
                    avg_ret = stats.get('total_return', 0) / trades * 100
                    perf_rows.append(html.Tr([
                        html.Td(name, style={'color': '#00d4ff'}),
                        html.Td(str(trades)),
                        html.Td(f"{win_rate:.0f}%", style={
                            'color': '#00ff88' if win_rate >= 60 else '#ffd700' if win_rate >= 50 else '#ff4444'
                        }),
                        html.Td(f"{avg_ret:+.1f}%", style={
                            'color': '#00ff88' if avg_ret > 0 else '#ff4444'
                        })
                    ]))
            
            perf_table = html.Table([
                html.Thead(html.Tr([
                    html.Th("Strategy", style={'color': '#888'}),
                    html.Th("Trades", style={'color': '#888'}),
                    html.Th("Win %", style={'color': '#888'}),
                    html.Th("Avg Return", style={'color': '#888'})
                ])),
                html.Tbody(perf_rows)
            ], style={'width': '100%', 'color': 'white'}) if perf_rows else html.P("No trade history yet", style={'color': '#888'})
        else:
            perf_table = html.P("No performance data", style={'color': '#888'})
        
        # Taught strategies
        taught = bot.get_taught_strategies()
        if taught:
            taught_items = []
            for strat in taught:
                taught_items.append(html.Div([
                    html.Strong(strat['name'], style={'color': '#9b59b6'}),
                    html.P(strat['description'][:100] + '...' if len(strat.get('description', '')) > 100 else strat.get('description', ''),
                          style={'color': '#888', 'fontSize': '12px', 'margin': '5px 0'})
                ], style={'marginBottom': '10px', 'borderBottom': '1px solid #333', 'paddingBottom': '10px'}))
            taught_div = html.Div(taught_items)
        else:
            taught_div = html.P("No custom strategies taught yet", style={'color': '#888'})
        
        return brain_text, brain_style, strat_count, mem_count, perf_table, taught_div
    
    @app.callback(
        [Output('chat-history', 'children'),
         Output('chat-history-store', 'data'),
         Output('chat-input', 'value')],
        [Input('chat-send', 'n_clicks')],
        [State('chat-input', 'value'),
         State('chat-history-store', 'data')]
    )
    def handle_chat(n_clicks, message, history):
        if not n_clicks or not message:
            # Render existing history
            chat_elements = []
            for item in (history or []):
                chat_elements.append(html.Div([
                    html.Div([
                        html.Strong("You: ", style={'color': '#00d4ff'}),
                        html.Span(item['user'])
                    ], style={'marginBottom': '5px'}),
                    html.Div([
                        html.Strong("Brain: ", style={'color': '#ff6b6b'}),
                        html.Span(item['brain'])
                    ], style={'marginBottom': '15px', 'paddingLeft': '10px', 'borderLeft': '2px solid #ff6b6b'})
                ]))
            return chat_elements, history or [], ''
        
        # Get brain response
        response = bot.chat(message)
        
        # Update history
        history = history or []
        history.append({
            'user': message,
            'brain': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 20 messages
        history = history[-20:]
        
        # Render history
        chat_elements = []
        for item in history:
            chat_elements.append(html.Div([
                html.Div([
                    html.Strong("You: ", style={'color': '#00d4ff'}),
                    html.Span(item['user'])
                ], style={'marginBottom': '5px'}),
                html.Div([
                    html.Strong("Brain: ", style={'color': '#ff6b6b'}),
                    html.Span(item['brain'][:500] + '...' if len(item['brain']) > 500 else item['brain'])
                ], style={'marginBottom': '15px', 'paddingLeft': '10px', 'borderLeft': '2px solid #ff6b6b'})
            ]))
        
        return chat_elements, history, ''
    
    @app.callback(
        Output('teach-result', 'children'),
        [Input('teach-button', 'n_clicks')],
        [State('strategy-name', 'value'),
         State('strategy-description', 'value')]
    )
    def handle_teach(n_clicks, name, description):
        if not n_clicks or not name or not description:
            return ""
        
        result = bot.teach_strategy(name, description)
        return html.Div(result, style={'color': '#00ff88' if '✅' in result else '#ff4444'})
    
    @app.callback(
        Output('analysis-result', 'children'),
        [Input('analyze-button', 'n_clicks')],
        [State('analyze-ticker', 'value')]
    )
    def handle_analyze(n_clicks, ticker):
        if not n_clicks or not ticker:
            return html.P("Enter a ticker and click Analyze", style={'color': '#888'})
        
        ticker = ticker.upper().strip()
        
        analysis = bot.analyze_ticker(ticker)
        
        # Build result display
        result_elements = []
        
        # Strategy signals
        result_elements.append(html.H4(f"Strategy Signals for ${ticker}", style={'color': '#00d4ff', 'marginBottom': '10px'}))
        
        for strategy, signal in analysis.get('strategy_results', {}).items():
            sig = signal.get('signal', 'PASS')
            conf = signal.get('confidence', 0)
            reason = signal.get('reason', '')[:80]
            
            color = '#00ff88' if sig == 'BUY' else '#888'
            icon = '✅' if sig == 'BUY' else '⬜'
            
            result_elements.append(html.Div([
                html.Span(f"{icon} {strategy}: ", style={'color': color, 'fontWeight': 'bold'}),
                html.Span(f"{sig} ({conf}/100)"),
                html.Br(),
                html.Span(reason, style={'color': '#888', 'fontSize': '12px'})
            ], style={'marginBottom': '10px'}))
        
        # Brain reasoning
        if analysis.get('brain_reasoning'):
            brain = analysis['brain_reasoning']
            result_elements.append(html.Hr(style={'borderColor': '#333'}))
            result_elements.append(html.H4("🧠 Brain Reasoning", style={'color': '#ff6b6b', 'marginTop': '15px'}))
            result_elements.append(html.Div([
                html.P([
                    html.Strong("Decision: "),
                    html.Span(brain.get('decision', 'N/A'), style={
                        'color': '#00ff88' if brain.get('decision') == 'TRADE' else '#ffd700'
                    })
                ]),
                html.P([
                    html.Strong("Confidence: "),
                    html.Span(f"{brain.get('confidence', 0)}/100")
                ]),
                html.P([
                    html.Strong("Thesis: "),
                    html.Span(brain.get('thesis', 'N/A'))
                ]),
                html.P([
                    html.Strong("Bear Case: "),
                    html.Span(brain.get('bear_case', 'N/A'), style={'color': '#ff6b6b'})
                ])
            ], style={'paddingLeft': '10px', 'borderLeft': '2px solid #ff6b6b'}))
        
        return result_elements
    
    return app


# ============ STANDALONE RUN ============

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧠 LAUNCHING TRADING BOT DASHBOARD")
    print("="*80)
    
    bot = TradingBotInterface()
    app = create_trading_dashboard(bot)
    
    if app:
        print("\n🌐 Dashboard running at: http://localhost:8051")
        print("   Press Ctrl+C to stop\n")
        app.run(debug=True, port=8051)
    else:
        print("❌ Could not create dashboard")
