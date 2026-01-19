# 🐺 FENRIR V2 - PORTFOLIO TRACKER
# Real-time portfolio status with accurate P/L

from datetime import datetime
from typing import Dict
import yfinance as yf
import config

def get_portfolio_status() -> str:
    """Get current portfolio status with real P/L"""
    
    output = "\n" + "="*60 + "\n"
    output += "🐺 PORTFOLIO STATUS\n"
    output += "="*60 + "\n\n"
    
    total_value = 0
    total_cost = 0
    position_data = []
    
    for ticker, holding in config.HOLDINGS.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get current price - try multiple fields
            current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose', 0)
            
            if current_price == 0:
                # Fallback to history
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
            
            shares = holding['shares']
            entry_price = holding['avg_cost']
            
            # Calculate values
            position_value = shares * current_price
            position_cost = shares * entry_price
            pnl_dollar = position_value - position_cost
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Get today's change
            prev_close = info.get('previousClose', current_price)
            daily_change = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0
            daily_pnl = shares * (current_price - prev_close)
            
            total_value += position_value
            total_cost += position_cost
            
            position_data.append({
                'ticker': ticker,
                'shares': shares,
                'entry': entry_price,
                'current': current_price,
                'value': position_value,
                'cost': position_cost,
                'pnl_dollar': pnl_dollar,
                'pnl_pct': pnl_pct,
                'daily_change': daily_change,
                'daily_pnl': daily_pnl,
                'thesis': holding.get('thesis', 'N/A')
            })
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            continue
    
    # Sort by position size
    position_data.sort(key=lambda x: x['value'], reverse=True)
    
    # Display positions
    for pos in position_data:
        emoji = "🟢" if pos['pnl_pct'] > 0 else "🔴"
        daily_emoji = "📈" if pos['daily_change'] > 0 else "📉"
        
        output += f"{emoji} {pos['ticker']}\n"
        output += f"   {pos['shares']:.2f} shares @ ${pos['entry']:.2f}\n"
        output += f"   Current: ${pos['current']:.2f} {daily_emoji} ({pos['daily_change']:+.1f}% today)\n"
        output += f"   Value: ${pos['value']:.2f}\n"
        output += f"   P/L: ${pos['pnl_dollar']:+.2f} ({pos['pnl_pct']:+.1f}%)\n"
        output += f"   Today: ${pos['daily_pnl']:+.2f}\n"
        output += f"   Thesis: {pos['thesis']}\n\n"
    
    # Totals
    total_pnl = total_value - total_cost
    total_pnl_pct = ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    
    # Cash
    total_cash = config.ROBINHOOD_CASH + config.FIDELITY_CASH
    grand_total = total_value + total_cash
    
    output += "="*60 + "\n"
    output += f"POSITIONS VALUE: ${total_value:,.2f}\n"
    output += f"POSITIONS COST:  ${total_cost:,.2f}\n"
    output += f"POSITIONS P/L:   ${total_pnl:+,.2f} ({total_pnl_pct:+.1f}%)\n\n"
    output += f"CASH: ${total_cash:,.2f} (RH: ${config.ROBINHOOD_CASH:.2f}, Fid: ${config.FIDELITY_CASH:.2f})\n"
    output += f"TOTAL PORTFOLIO: ${grand_total:,.2f}\n"
    output += "="*60 + "\n"
    
    return output


def get_position_pnl(ticker: str) -> Dict:
    """Get P/L for single position"""
    
    if ticker not in config.HOLDINGS:
        return {'error': 'Not in holdings'}
    
    holding = config.HOLDINGS[ticker]
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose', 0)
        
        if current_price == 0:
            hist = stock.history(period='1d')
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
        
        shares = holding['shares']
        entry_price = holding['avg_cost']
        
        position_value = shares * current_price
        position_cost = shares * entry_price
        pnl_dollar = position_value - position_cost
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        return {
            'ticker': ticker,
            'shares': shares,
            'entry_price': entry_price,
            'current_price': current_price,
            'position_value': position_value,
            'position_cost': position_cost,
            'pnl_dollar': pnl_dollar,
            'pnl_pct': pnl_pct
        }
        
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    print(get_portfolio_status())
    
    print("\nSingle position test:")
    print(get_position_pnl('IBRX'))
