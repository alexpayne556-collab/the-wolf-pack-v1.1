# 🐺 FENRIR V2 - RISK MANAGER
# Track exposure, concentration, PDT usage

from datetime import datetime, timedelta
from typing import Dict, List
import config
import database

class RiskManager:
    """Monitor portfolio risk and PDT limits"""
    
    def __init__(self):
        self.pdt_limit = 3  # 3 day trades per 5 days
        self.max_position_pct = 0.35  # Max 35% in one position
        self.max_sector_pct = 0.50  # Max 50% in one sector
    
    def get_day_trades_used(self) -> int:
        """Count day trades in last 5 trading days"""
        conn = database.get_connection()
        cursor = conn.cursor()
        
        five_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # Find same-day buy+sell or sell+buy
        cursor.execute('''
            SELECT COUNT(*) FROM trades
            WHERE DATE(timestamp) >= DATE(?)
            AND ticker IN (
                SELECT ticker FROM trades
                WHERE DATE(timestamp) >= DATE(?)
                GROUP BY DATE(timestamp), ticker
                HAVING COUNT(*) > 1
            )
        ''', (five_days_ago, five_days_ago))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        # Rough estimate - actual logic needs buy+sell same day detection
        return min(count // 2, self.pdt_limit)
    
    def get_portfolio_stats(self, holdings: Dict) -> Dict:
        """Calculate portfolio concentration and risk"""
        
        import yfinance as yf
        
        # Get current prices for all positions
        position_values = {}
        for ticker, data in holdings.items():
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose', 0)
                
                if current_price == 0:
                    hist = stock.history(period='1d')
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                
                if current_price == 0:
                    current_price = data['avg_cost']  # Fallback
                
                position_values[ticker] = data['shares'] * current_price
            except:
                position_values[ticker] = data['shares'] * data['avg_cost']
        
        total_value = sum(position_values.values())
        total_value += config.TOTAL_CASH
        
        # Position concentration
        positions = []
        for ticker, value in position_values.items():
            pct = (value / total_value) * 100
            positions.append({
                'ticker': ticker,
                'value': value,
                'pct': pct,
            })
        
        # Sort by size
        positions.sort(key=lambda x: x['value'], reverse=True)
        
        # Sector concentration
        sectors = {}
        for ticker, value in position_values.items():
            # Find sector from watchlist
            sector = 'unknown'
            for s, tickers in config.WATCHLIST.items():
                if ticker in tickers:
                    sector = s
                    break
            
            sectors[sector] = sectors.get(sector, 0) + value
        
        sector_pcts = {s: (v / total_value) * 100 for s, v in sectors.items()}
        
        return {
            'total_value': total_value,
            'cash': config.TOTAL_CASH,
            'cash_pct': (config.TOTAL_CASH / total_value) * 100,
            'positions': positions,
            'sectors': sector_pcts,
            'largest_position_pct': positions[0]['pct'] if positions else 0,
            'largest_sector_pct': max(sector_pcts.values()) if sector_pcts else 0,
        }
    
    def check_risks(self, holdings: Dict) -> List[str]:
        """Return list of risk warnings"""
        
        warnings = []
        
        # PDT check
        day_trades_used = self.get_day_trades_used()
        remaining = self.pdt_limit - day_trades_used
        
        if remaining == 0:
            warnings.append(f"🚨 NO DAY TRADES LEFT (used {day_trades_used}/{self.pdt_limit})")
        elif remaining == 1:
            warnings.append(f"⚠️  Only {remaining} day trade left this week")
        
        # Position concentration
        stats = self.get_portfolio_stats(holdings)
        
        if stats['largest_position_pct'] > self.max_position_pct * 100:
            largest = stats['positions'][0]
            warnings.append(f"⚠️  {largest['ticker']} is {largest['pct']:.1f}% of portfolio (max {self.max_position_pct*100}%)")
        
        # Sector concentration
        if stats['largest_sector_pct'] > self.max_sector_pct * 100:
            largest_sector = max(stats['sectors'].items(), key=lambda x: x[1])
            warnings.append(f"⚠️  {largest_sector[0]} sector is {largest_sector[1]:.1f}% of portfolio")
        
        # Low cash
        if stats['cash_pct'] < 10:
            warnings.append(f"⚠️  Low cash: ${stats['cash']:.2f} ({stats['cash_pct']:.1f}%)")
        
        return warnings
    
    def calculate_position_size(self, ticker: str, price: float, 
                               risk_pct: float = 2.0) -> Dict:
        """
        Calculate position size based on risk tolerance
        
        Args:
            ticker: Stock symbol
            price: Entry price
            risk_pct: Max % of portfolio to risk (default 2%)
        
        Returns:
            Dict with shares, cost, stop_loss, etc.
        """
        
        stats = self.get_portfolio_stats(config.HOLDINGS)
        portfolio_value = stats['total_value']
        
        # Max $ to risk on this trade
        risk_dollars = portfolio_value * (risk_pct / 100)
        
        # Assume 5% stop loss
        stop_loss_pct = 5.0
        stop_loss_price = price * (1 - stop_loss_pct / 100)
        
        # Shares = risk / (entry - stop)
        risk_per_share = price - stop_loss_price
        shares = risk_dollars / risk_per_share if risk_per_share > 0 else 0
        
        # Round down to avoid overspending
        shares = int(shares)
        
        # Total cost
        cost = shares * price
        
        # Check if we have cash
        if cost > config.TOTAL_CASH:
            shares = int(config.TOTAL_CASH / price)
            cost = shares * price
        
        # Position as % of portfolio
        position_pct = (cost / portfolio_value) * 100
        
        return {
            'ticker': ticker,
            'price': price,
            'shares': shares,
            'cost': cost,
            'stop_loss': stop_loss_price,
            'risk_dollars': risk_dollars,
            'position_pct': position_pct,
            'warning': 'TOO LARGE' if position_pct > self.max_position_pct * 100 else None,
        }


def format_risk_report(holdings: Dict) -> str:
    """Generate risk report"""
    
    rm = RiskManager()
    stats = rm.get_portfolio_stats(holdings)
    warnings = rm.check_risks(holdings)
    
    output = "\n" + "=" * 60 + "\n"
    output += "🐺 RISK REPORT\n"
    output += "=" * 60 + "\n\n"
    
    # Portfolio overview
    output += f"Portfolio Value: ${stats['total_value']:.2f}\n"
    output += f"Cash: ${stats['cash']:.2f} ({stats['cash_pct']:.1f}%)\n"
    output += f"Invested: ${stats['total_value'] - stats['cash']:.2f}\n\n"
    
    # PDT status
    dt_used = rm.get_day_trades_used()
    dt_remaining = rm.pdt_limit - dt_used
    output += f"Day Trades: {dt_used}/{rm.pdt_limit} used ({dt_remaining} remaining)\n\n"
    
    # Position concentration
    output += "POSITION SIZES:\n"
    for pos in stats['positions']:
        emoji = "🚨" if pos['pct'] > rm.max_position_pct * 100 else "✅"
        output += f"  {emoji} {pos['ticker']}: ${pos['value']:.2f} ({pos['pct']:.1f}%)\n"
    output += "\n"
    
    # Sector concentration
    output += "SECTOR EXPOSURE:\n"
    for sector, pct in sorted(stats['sectors'].items(), key=lambda x: x[1], reverse=True):
        emoji = "🚨" if pct > rm.max_sector_pct * 100 else "✅"
        output += f"  {emoji} {sector}: {pct:.1f}%\n"
    output += "\n"
    
    # Warnings
    if warnings:
        output += "⚠️  WARNINGS:\n"
        for w in warnings:
            output += f"  {w}\n"
    else:
        output += "✅ No risk warnings\n"
    
    output += "\n" + "=" * 60 + "\n"
    
    return output


# Test
if __name__ == '__main__':
    print("\n🐺 Testing Risk Manager\n")
    
    rm = RiskManager()
    
    # Mock current prices
    mock_holdings = config.HOLDINGS.copy()
    mock_holdings['IBRX']['current_price'] = 5.52
    mock_holdings['KTOS']['current_price'] = 130.72
    mock_holdings['MU']['current_price'] = 362.75
    
    print(format_risk_report(mock_holdings))
    
    # Test position sizing
    print("\n🐺 Position Size Calculator\n")
    print("If buying TSLA at $250:")
    size = rm.calculate_position_size('TSLA', 250.0, risk_pct=2.0)
    print(f"  Shares: {size['shares']}")
    print(f"  Cost: ${size['cost']:.2f}")
    print(f"  Stop Loss: ${size['stop_loss']:.2f}")
    print(f"  Position Size: {size['position_pct']:.1f}% of portfolio")
    if size['warning']:
        print(f"  ⚠️  {size['warning']}")
