#!/usr/bin/env python3
"""
Wolf Pack Alert Engine
Monitors portfolio, watchlist, and sectors for actionable situations
"""

import sqlite3
from datetime import datetime
import json

from config import DB_PATH, PORTFOLIO, BIG_MOVE_THRESHOLD, PORTFOLIO_STOP_LOSS_PCT
from config import WATCHLIST_DIP_BUY_PCT, SECTOR_BREAKOUT_PCT, VOLUME_SPIKE_THRESHOLD

def check_portfolio_alerts(date):
    """Check alerts for stocks we hold"""
    
    alerts = []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for ticker, position in PORTFOLIO.items():
        cursor.execute('''
        SELECT daily_return_pct, close, volume_ratio, is_big_move, dist_52w_high_pct
        FROM daily_records
        WHERE ticker = ? AND date = ?
        ''', (ticker, date))
        
        result = cursor.fetchone()
        
        if not result:
            continue
        
        daily_return, close, volume_ratio, is_big_move, dist_52w_high = result
        avg_cost = position['avg_cost']
        shares = position['shares']
        position_return = ((close - avg_cost) / avg_cost) * 100
        
        # BIG MOVE ALERT
        if is_big_move:
            alerts.append({
                'timestamp': datetime.now().isoformat(),
                'priority': 'high',
                'alert_type': 'portfolio_big_move',
                'ticker': ticker,
                'message': f"{ticker} moved {daily_return:+.1f}% today",
                'data': {
                    'daily_return': daily_return,
                    'position_return': position_return,
                    'close': close,
                    'volume_ratio': volume_ratio
                },
                'suggested_action': 'Review position - investigate catalyst'
            })
        
        # VOLUME SPIKE ALERT
        if volume_ratio and volume_ratio >= VOLUME_SPIKE_THRESHOLD:
            alerts.append({
                'timestamp': datetime.now().isoformat(),
                'priority': 'medium',
                'alert_type': 'volume_spike',
                'ticker': ticker,
                'message': f"{ticker} volume spike {volume_ratio:.1f}x average",
                'data': {
                    'volume_ratio': volume_ratio,
                    'daily_return': daily_return
                },
                'suggested_action': 'Watch for breakout/breakdown'
            })
        
        # STOP LOSS WARNING
        if position_return <= PORTFOLIO_STOP_LOSS_PCT:
            alerts.append({
                'timestamp': datetime.now().isoformat(),
                'priority': 'high',
                'alert_type': 'approaching_stop_loss',
                'ticker': ticker,
                'message': f"{ticker} down {position_return:.1f}% from entry",
                'data': {
                    'position_return': position_return,
                    'avg_cost': avg_cost,
                    'current_price': close
                },
                'suggested_action': 'Consider stop loss - review thesis'
            })
        
        # NEW HIGH ALERT
        if dist_52w_high and dist_52w_high > -2.0:
            alerts.append({
                'timestamp': datetime.now().isoformat(),
                'priority': 'medium',
                'alert_type': 'approaching_52w_high',
                'ticker': ticker,
                'message': f"{ticker} within 2% of 52-week high",
                'data': {
                    'dist_52w_high': dist_52w_high,
                    'close': close
                },
                'suggested_action': 'Consider taking profits or trailing stop'
            })
    
    conn.close()
    return alerts

def check_sector_alerts(date):
    """Check for sector-wide moves"""
    
    alerts = []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get sector average performance
    cursor.execute('''
    SELECT sector, AVG(daily_return_pct) as avg_return, COUNT(*) as count
    FROM daily_records
    WHERE date = ?
    GROUP BY sector
    HAVING ABS(avg_return) >= ?
    ORDER BY ABS(avg_return) DESC
    ''', (date, SECTOR_BREAKOUT_PCT))
    
    sectors = cursor.fetchall()
    
    for sector, avg_return, count in sectors:
        alerts.append({
            'timestamp': datetime.now().isoformat(),
            'priority': 'medium',
            'alert_type': 'sector_breakout' if avg_return > 0 else 'sector_breakdown',
            'ticker': None,
            'message': f"{sector} sector moved {avg_return:+.1f}% avg today",
            'data': {
                'sector': sector,
                'avg_return': avg_return,
                'stock_count': count
            },
            'suggested_action': f"Review {sector} positions - sector rotation detected"
        })
    
    conn.close()
    return alerts

def check_watchlist_opportunities(date):
    """Find potential buy opportunities in watchlist"""
    
    alerts = []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Quality dips: stocks down >5% with no obvious bad catalyst
    cursor.execute('''
    SELECT r.ticker, r.sector, r.daily_return_pct, r.close, r.return_60d, 
           i.catalyst_type
    FROM daily_records r
    LEFT JOIN investigations i ON r.ticker = i.ticker AND r.date = i.date
    WHERE r.date = ?
    AND r.daily_return_pct <= ?
    AND r.return_60d < 30
    AND (i.catalyst_type IS NULL OR i.catalyst_type NOT IN ('earnings_miss', 'offering', 'analyst_downgrade'))
    ORDER BY r.daily_return_pct ASC
    LIMIT 10
    ''', (date, WATCHLIST_DIP_BUY_PCT))
    
    dips = cursor.fetchall()
    
    for ticker, sector, daily_return, close, return_60d, catalyst_type in dips:
        alerts.append({
            'timestamp': datetime.now().isoformat(),
            'priority': 'medium',
            'alert_type': 'quality_dip',
            'ticker': ticker,
            'message': f"{ticker} down {daily_return:.1f}%, no bad catalyst found",
            'data': {
                'daily_return': daily_return,
                'close': close,
                'return_60d': return_60d,
                'catalyst_type': catalyst_type or 'unknown'
            },
            'suggested_action': 'Potential buy opportunity if thesis still valid'
        })
    
    conn.close()
    return alerts

def store_alert(alert):
    """Store alert in database"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO alerts (priority, alert_type, ticker, message, data)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            alert['priority'],
            alert['alert_type'],
            alert.get('ticker'),
            alert['message'],
            json.dumps(alert['data'])
        ))
        
        conn.commit()
    
    except Exception as e:
        print(f"  ❌ Error storing alert: {e}")
    
    finally:
        conn.close()

def run_alert_engine(date=None):
    """Run all alert checks"""
    
    print("\n" + "🚨"*30)
    print("WOLF PACK ALERT ENGINE")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚨"*30 + "\n")
    
    # Get latest date if not specified
    if not date:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(date) FROM daily_records')
        date = cursor.fetchone()[0]
        conn.close()
    
    if not date:
        print("❌ No data in database yet.\n")
        return
    
    all_alerts = []
    
    # Check portfolio
    print("📊 Checking portfolio...")
    portfolio_alerts = check_portfolio_alerts(date)
    all_alerts.extend(portfolio_alerts)
    print(f"   Found {len(portfolio_alerts)} portfolio alerts")
    
    # Check sectors
    print("🎯 Checking sectors...")
    sector_alerts = check_sector_alerts(date)
    all_alerts.extend(sector_alerts)
    print(f"   Found {len(sector_alerts)} sector alerts")
    
    # Check watchlist
    print("👀 Checking watchlist opportunities...")
    watchlist_alerts = check_watchlist_opportunities(date)
    all_alerts.extend(watchlist_alerts)
    print(f"   Found {len(watchlist_alerts)} watchlist opportunities")
    
    # Print and store alerts
    if all_alerts:
        print(f"\n{'='*80}")
        print(f"🚨 {len(all_alerts)} TOTAL ALERTS")
        print(f"{'='*80}\n")
        
        for alert in all_alerts:
            priority_icon = "🔴" if alert['priority'] == 'high' else "🟡"
            print(f"{priority_icon} [{alert['priority'].upper()}] {alert['message']}")
            print(f"   Action: {alert['suggested_action']}")
            
            # Store in database
            store_alert(alert)
            print()
    
    else:
        print("\n✅ No alerts - all quiet\n")
    
    print("🚨 Alert engine complete - LLHR\n")

if __name__ == '__main__':
    run_alert_engine()
