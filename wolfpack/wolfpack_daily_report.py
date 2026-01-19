#!/usr/bin/env python3
"""
Wolf Pack Daily Report
Comprehensive EOD summary: portfolio, market, sectors, investigations, alerts
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

from config import DB_PATH, PORTFOLIO, BIG_MOVE_THRESHOLD
from wolfpack_db import get_sector_performance

def generate_daily_report(save_to_file=True):
    """Generate comprehensive daily report"""
    
    print("\n" + "🐺"*30)
    print("WOLF PACK DAILY REPORT")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🐺"*30 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get today's date (most recent in database)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(date) FROM daily_records')
    today = cursor.fetchone()[0]
    
    if not today:
        print("❌ No data in database yet. Run wolfpack_recorder.py first.\n")
        conn.close()
        return
    
    yesterday = (datetime.strptime(today, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    
    output = []
    output.append("="*80)
    output.append(f"WOLF PACK DAILY REPORT - {today}")
    output.append("="*80)
    output.append("")
    
    # =============================================================================
    # PORTFOLIO SUMMARY
    # =============================================================================
    
    output.append("💼 PORTFOLIO SUMMARY")
    output.append("-"*80)
    
    portfolio_value = 0
    portfolio_day_change = 0
    best_performer = None
    worst_performer = None
    
    for ticker, position in PORTFOLIO.items():
        cursor.execute('''
        SELECT close, daily_return_pct
        FROM daily_records
        WHERE ticker = ? AND date = ?
        ''', (ticker, today))
        
        result = cursor.fetchone()
        
        if result:
            close, daily_return = result
            shares = position['shares']
            avg_cost = position['avg_cost']
            
            position_value = shares * close
            position_return = ((close - avg_cost) / avg_cost) * 100
            day_change = shares * close * (daily_return / 100)
            
            portfolio_value += position_value
            portfolio_day_change += day_change
            
            output.append(f"{ticker:6} | {shares:3} shares @ ${avg_cost:>7.2f} | Now: ${close:>7.2f} | "
                         f"Today: {daily_return:>+6.1f}% | Total: {position_return:>+6.1f}% | Tier: {position['tier']}")
            
            if best_performer is None or daily_return > best_performer[1]:
                best_performer = (ticker, daily_return)
            
            if worst_performer is None or daily_return < worst_performer[1]:
                worst_performer = (ticker, daily_return)
    
    output.append("-"*80)
    output.append(f"Total Value: ${portfolio_value:.2f} | Day Change: ${portfolio_day_change:+.2f} ({(portfolio_day_change/portfolio_value)*100:+.1f}%)")
    if best_performer:
        output.append(f"Best: {best_performer[0]} {best_performer[1]:+.1f}% | Worst: {worst_performer[0]} {worst_performer[1]:+.1f}%")
    output.append("")
    
    # =============================================================================
    # TODAY'S BIG MOVES + INVESTIGATIONS
    # =============================================================================
    
    output.append("📈 BIG MOVES + INVESTIGATIONS")
    output.append("-"*80)
    
    query = f'''
    SELECT r.ticker, r.sector, r.close, r.daily_return_pct, r.volume_ratio, r.return_60d,
           i.catalyst_type, i.catalyst_confidence, i.sector_correlation, i.volume_confirmed
    FROM daily_records r
    LEFT JOIN investigations i ON r.ticker = i.ticker AND r.date = i.date
    WHERE r.date = ? AND r.is_big_move = 1
    ORDER BY ABS(r.daily_return_pct) DESC
    '''
    
    big_movers = pd.read_sql_query(query, conn, params=(today,))
    
    if len(big_movers) > 0:
        output.append(f"{'Ticker':<8} {'Sector':<12} {'Price':<10} {'Today%':<10} {'Vol':<8} {'Catalyst':<20} {'Confidence':<12}")
        output.append("-"*80)
        
        for _, row in big_movers.iterrows():
            catalyst = row['catalyst_type'] or 'unknown'
            confidence = f"{row['catalyst_confidence']*100:.0f}%" if row['catalyst_confidence'] else "N/A"
            sector_flag = "📊" if row['sector_correlation'] else ""
            volume_flag = "🔊" if row['volume_confirmed'] else ""
            
            output.append(f"{row['ticker']:<8} {row['sector']:<12} ${row['close']:<9.2f} "
                         f"{row['daily_return_pct']:>+8.1f}% {row['volume_ratio']:>6.1f}x "
                         f"{catalyst:<20} {confidence:<12} {sector_flag}{volume_flag}")
    else:
        output.append("  No big moves today")
    
    output.append("")
    
    # =============================================================================
    # DAY 2 CONFIRMATIONS
    # =============================================================================
    
    output.append("🔥 DAY 2 CONFIRMATIONS (Yesterday 5%+, Today green)")
    output.append("-"*80)
    
    query = f'''
    SELECT t.ticker, t.sector, y.daily_return_pct as yesterday_pct, 
           t.daily_return_pct as today_pct, t.return_60d, t.volume_ratio
    FROM daily_records t
    JOIN daily_records y ON t.ticker = y.ticker AND y.date = ?
    WHERE t.date = ? 
    AND ABS(y.daily_return_pct) >= ?
    AND t.daily_return_pct > 0
    ORDER BY t.daily_return_pct DESC
    '''
    
    confirmations = pd.read_sql_query(query, conn, params=(yesterday, today, BIG_MOVE_THRESHOLD))
    
    if len(confirmations) > 0:
        output.append(f"{'Ticker':<8} {'Sector':<12} {'Yest%':<10} {'Today%':<10} {'2-Day%':<10} {'Vol':<8} {'Valid?':<10}")
        output.append("-"*80)
        
        for _, row in confirmations.iterrows():
            two_day = row['yesterday_pct'] + row['today_pct']
            valid = "YES ✅" if row['return_60d'] < 30 else "NO (ext)"
            output.append(f"{row['ticker']:<8} {row['sector']:<12} "
                         f"{row['yesterday_pct']:>+8.1f}% {row['today_pct']:>+8.1f}% {two_day:>+8.1f}% "
                         f"{row['volume_ratio']:>6.1f}x {valid:<10}")
    else:
        output.append("  No Day 2 confirmations")
    
    output.append("")
    
    # =============================================================================
    # SECTOR MOMENTUM
    # =============================================================================
    
    output.append("🎯 SECTOR MOMENTUM")
    output.append("-"*80)
    
    sectors = get_sector_performance(conn, today)
    
    if sectors:
        output.append(f"{'Sector':<15} {'Avg Return':<12} {'Avg Vol Ratio':<15} {'Count':<10}")
        output.append("-"*80)
        
        for sector, avg_ret, avg_vol, count in sectors:
            momentum_icon = "🚀" if avg_ret > 3 else "📈" if avg_ret > 1 else "📉" if avg_ret < -1 else "➡️"
            output.append(f"{momentum_icon} {sector:<13} {avg_ret:>+10.1f}% {avg_vol:>13.1f}x {count:>8}")
    
    output.append("")
    
    # =============================================================================
    # ALERTS SUMMARY
    # =============================================================================
    
    output.append("🚨 ALERTS TODAY")
    output.append("-"*80)
    
    cursor.execute('''
    SELECT priority, alert_type, ticker, message
    FROM alerts
    WHERE DATE(timestamp) = ?
    AND dismissed = 0
    ORDER BY 
        CASE priority 
            WHEN 'high' THEN 1
            WHEN 'medium' THEN 2
            ELSE 3
        END
    ''', (today,))
    
    alerts = cursor.fetchall()
    
    if alerts:
        for priority, alert_type, ticker, message in alerts:
            icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "⚪"
            ticker_str = f"{ticker} - " if ticker else ""
            output.append(f"{icon} [{priority.upper():6}] {ticker_str}{message}")
    else:
        output.append("  ✅ No alerts - all quiet")
    
    output.append("")
    output.append("="*80)
    output.append("🐺 LLHR - Long Live the Hunt, Rise")
    output.append("="*80)
    
    # Print to console
    report_text = "\n".join(output)
    print(report_text)
    
    # Save to file
    if save_to_file:
        import os
        os.makedirs('reports', exist_ok=True)
        filename = f"reports/daily_{today.replace('-', '')}.txt"
        with open(filename, 'w') as f:
            f.write(report_text)
        print(f"\n💾 Report saved to: {filename}\n")
    
    conn.close()

if __name__ == '__main__':
    generate_daily_report()
