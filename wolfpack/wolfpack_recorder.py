#!/usr/bin/env python3
"""
Wolf Pack Daily Recorder
Captures EVERYTHING. Technical indicators, move classification, ALL data.
"""

import sqlite3
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

from config import ALL_TICKERS, TICKER_TO_SECTOR, DB_PATH, RATE_LIMIT_DELAY
from config import BIG_MOVE_THRESHOLD, MEDIUM_MOVE_THRESHOLD
from wolfpack_db import init_database

def calculate_technicals(hist):
    """Calculate technical indicators from history"""
    
    try:
        close = hist['Close']
        
        # Simple Moving Averages
        sma_20 = close.rolling(window=20).mean().iloc[-1] if len(close) >= 20 else None
        sma_50 = close.rolling(window=50).mean().iloc[-1] if len(close) >= 50 else None
        sma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
        
        # RSI (14-period)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_14 = rsi.iloc[-1] if len(rsi) > 0 else None
        
        current_price = close.iloc[-1]
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'rsi_14': rsi_14,
            'above_sma_20': current_price > sma_20 if sma_20 else None,
            'above_sma_50': current_price > sma_50 if sma_50 else None,
            'above_sma_200': current_price > sma_200 if sma_200 else None
        }
    
    except Exception as e:
        return {
            'sma_20': None, 'sma_50': None, 'sma_200': None,
            'rsi_14': None, 'above_sma_20': None, 'above_sma_50': None,
            'above_sma_200': None
        }

def calculate_consecutive_days(ticker, current_return):
    """Calculate consecutive green/red days by looking at history"""
    
    try:
        # Get last 30 days of history
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1mo')
        
        if len(hist) < 2:
            return 0, 0
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        if len(returns) == 0:
            return 0, 0
        
        # Count consecutive days of same sign (not including today)
        consecutive_green = 0
        consecutive_red = 0
        
        # Start from most recent and go backwards
        for ret in reversed(returns.values[:-1]):  # Exclude today
            if current_return > 0:  # Today is green
                if ret > 0:
                    consecutive_green += 1
                else:
                    break
            else:  # Today is red
                if ret < 0:
                    consecutive_red += 1
                else:
                    break
        
        return consecutive_green, consecutive_red
    
    except:
        return 0, 0

def get_stock_data(ticker, sector):
    """Pull all metrics for a ticker - enhanced with technicals and move classification"""
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get sufficient history for calculations
        hist = stock.history(period='1y')  # Need more for 200 SMA
        
        if len(hist) < 2:
            return None
        
        # Today's data
        today = hist.iloc[-1]
        yesterday = hist.iloc[-2]
        
        # Calculate metrics
        daily_return = ((today['Close'] - yesterday['Close']) / yesterday['Close']) * 100
        intraday_range = ((today['High'] - today['Low']) / today['Low']) * 100
        close_vs_high = ((today['Close'] - today['Low']) / (today['High'] - today['Low'])) * 100 if today['High'] != today['Low'] else 50.0
        
        # Gap detection
        gap_pct = ((today['Open'] - yesterday['Close']) / yesterday['Close']) * 100
        
        # Volume metrics
        volume = int(today['Volume'])
        avg_volume_20d = int(hist['Volume'].iloc[-21:-1].mean()) if len(hist) >= 21 else int(hist['Volume'].mean())
        volume_ratio = volume / avg_volume_20d if avg_volume_20d > 0 else 0
        dollar_volume = volume * today['Close']
        
        # 52-week high/low
        week_52_high = hist['High'].iloc[-252:].max() if len(hist) >= 252 else hist['High'].max()
        week_52_low = hist['Low'].iloc[-252:].min() if len(hist) >= 252 else hist['Low'].min()
        
        dist_52w_high = ((today['Close'] - week_52_high) / week_52_high) * 100
        dist_52w_low = ((today['Close'] - week_52_low) / week_52_low) * 100
        
        # Multi-day returns
        return_5d = ((today['Close'] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100 if len(hist) >= 6 else 0
        return_20d = ((today['Close'] - hist['Close'].iloc[-21]) / hist['Close'].iloc[-21]) * 100 if len(hist) >= 21 else 0
        return_60d = ((today['Close'] - hist['Close'].iloc[-61]) / hist['Close'].iloc[-61]) * 100 if len(hist) >= 61 else 0
        
        # Consecutive days
        consecutive_green, consecutive_red = calculate_consecutive_days(ticker, daily_return)
        
        # Technical indicators
        technicals = calculate_technicals(hist)
        
        # Move classification
        is_big_move = abs(daily_return) >= BIG_MOVE_THRESHOLD
        move_direction = 'up' if daily_return > 0 else 'down' if daily_return < 0 else 'flat'
        
        if abs(daily_return) < 2:
            move_size = 'small'
        elif abs(daily_return) < 5:
            move_size = 'medium'
        elif abs(daily_return) < 10:
            move_size = 'large'
        else:
            move_size = 'massive'
        
        # Build record
        record = {
            'ticker': ticker,
            'date': today.name.date(),
            'sector': sector,
            'open': today['Open'],
            'high': today['High'],
            'low': today['Low'],
            'close': today['Close'],
            'prev_close': yesterday['Close'],
            'daily_return_pct': daily_return,
            'intraday_range_pct': intraday_range,
            'close_vs_high_pct': close_vs_high,
            'volume': volume,
            'avg_volume_20d': avg_volume_20d,
            'volume_ratio': volume_ratio,
            'dollar_volume': dollar_volume,
            'dist_52w_high_pct': dist_52w_high,
            'dist_52w_low_pct': dist_52w_low,
            'return_5d': return_5d,
            'return_20d': return_20d,
            'return_60d': return_60d,
            'consecutive_green': consecutive_green,
            'consecutive_red': consecutive_red,
            'sma_20': technicals['sma_20'],
            'sma_50': technicals['sma_50'],
            'sma_200': technicals['sma_200'],
            'rsi_14': technicals['rsi_14'],
            'above_sma_20': technicals['above_sma_20'],
            'above_sma_50': technicals['above_sma_50'],
            'above_sma_200': technicals['above_sma_200'],
            'is_big_move': is_big_move,
            'move_direction': move_direction,
            'move_size': move_size,
            'gap_pct': gap_pct
        }
        
        return record
    
    except Exception as e:
        print(f"  ⚠️  Error fetching {ticker}: {e}")
        return None

def insert_daily_record(conn, record):
    """Insert or replace a daily record"""
    
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO daily_records (
            ticker, date, sector,
            open, high, low, close, prev_close,
            daily_return_pct, intraday_range_pct, close_vs_high_pct,
            volume, avg_volume_20d, volume_ratio, dollar_volume,
            dist_52w_high_pct, dist_52w_low_pct,
            return_5d, return_20d, return_60d,
            consecutive_green, consecutive_red,
            sma_20, sma_50, sma_200, rsi_14,
            above_sma_20, above_sma_50, above_sma_200,
            is_big_move, move_direction, move_size, gap_pct
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['ticker'], record['date'], record['sector'],
            record['open'], record['high'], record['low'], record['close'], record['prev_close'],
            record['daily_return_pct'], record['intraday_range_pct'], record['close_vs_high_pct'],
            record['volume'], record['avg_volume_20d'], record['volume_ratio'], record['dollar_volume'],
            record['dist_52w_high_pct'], record['dist_52w_low_pct'],
            record['return_5d'], record['return_20d'], record['return_60d'],
            record['consecutive_green'], record['consecutive_red'],
            record['sma_20'], record['sma_50'], record['sma_200'], record['rsi_14'],
            record['above_sma_20'], record['above_sma_50'], record['above_sma_200'],
            record['is_big_move'], record['move_direction'], record['move_size'], record['gap_pct']
        ))
        
        return True
    
    except Exception as e:
        print(f"  ❌ Error inserting {record['ticker']}: {e}")
        return False

def record_daily_data():
    """Main recording function"""
    
    print("\n" + "🐺"*30)
    print("WOLF PACK DAILY RECORDER")
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🐺"*30 + "\n")
    
    # Initialize database
    init_database()
    
    conn = sqlite3.connect(DB_PATH)
    
    total = len(ALL_TICKERS)
    recorded = 0
    failed = 0
    
    print(f"Recording {total} stocks...\n")
    
    for i, ticker in enumerate(ALL_TICKERS, 1):
        sector = TICKER_TO_SECTOR[ticker]
        
        print(f"[{i}/{total}] {ticker:6} ({sector:10})... ", end='', flush=True)
        
        # Get data
        record = get_stock_data(ticker, sector)
        
        if record:
            # Store in database
            if insert_daily_record(conn, record):
                recorded += 1
                print(f"✅ ${record['close']:.2f} {record['daily_return_pct']:+.1f}% | {record['volume_ratio']:.1f}x vol")
            else:
                failed += 1
                print("❌ Failed to store")
        else:
            failed += 1
            print("❌ No data")
        
        # Rate limit
        time.sleep(RATE_LIMIT_DELAY)
    
    conn.close()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total tickers: {total}")
    print(f"   Recorded: {recorded}")
    print(f"   Failed: {failed}")
    print(f"\n🐺 Recording complete - LLHR\n")

if __name__ == '__main__':
    record_daily_data()
