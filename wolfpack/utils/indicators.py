"""
Unified Technical Indicators
Single source of truth for all technical calculations.

Consolidates RSI, volume, SMA calculations from:
- src/wolf_brain/universe_scanner.py
- lightweight_researcher.py  
- wolfpack/wolfpack_recorder.py
- src/wolf_brain/strategy_plugins.py
- src/wolf_brain/autonomous_brain.py
"""

import pandas as pd
import numpy as np
from typing import Union


def calculate_rsi(prices: Union[pd.Series, list], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)
    
    RSI measures momentum on a scale of 0-100:
    - Above 70: Overbought (potential reversal down)
    - Below 30: Oversold (potential reversal up)
    - 50: Neutral
    
    Args:
        prices: Series of closing prices or list of prices
        period: Lookback period (default 14)
        
    Returns:
        float: RSI value (0-100), or 50 if insufficient data
        
    Examples:
        >>> prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113])
        >>> rsi = calculate_rsi(prices)
        >>> print(f"RSI: {rsi:.2f}")
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    if len(prices) < period + 1:
        return 50.0  # Neutral if insufficient data
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Return most recent value, or 50 if NaN
    result = rsi.iloc[-1]
    return float(result) if not pd.isna(result) else 50.0


def calculate_volume_ratio(recent_volume: float, avg_volume: float) -> float:
    """
    Calculate volume ratio (recent vs average)
    
    Volume ratio indicates unusual activity:
    - 2.0+ = High volume spike (unusual activity)
    - 1.0-2.0 = Above average (increased interest)
    - 0.5-1.0 = Below average (low interest)
    - <0.5 = Very low volume (illiquid)
    
    Args:
        recent_volume: Recent volume (e.g., today's volume)
        avg_volume: Average volume (e.g., 20-day average)
        
    Returns:
        float: Volume ratio, or 1.0 if avg_volume is 0
        
    Examples:
        >>> vol_ratio = calculate_volume_ratio(1_000_000, 500_000)
        >>> print(f"Volume is {vol_ratio}x average")  # 2.0x average
    """
    if avg_volume == 0 or avg_volume is None:
        return 1.0
    
    return recent_volume / avg_volume


def calculate_sma(prices: Union[pd.Series, list], period: int) -> float:
    """
    Calculate Simple Moving Average (SMA)
    
    SMA smooths price data to identify trends:
    - Price above SMA: Uptrend
    - Price below SMA: Downtrend
    - Common periods: 20, 50, 200
    
    Args:
        prices: Series of closing prices or list of prices
        period: Lookback period (e.g., 20, 50, 200)
        
    Returns:
        float: SMA value, or None if insufficient data
        
    Examples:
        >>> prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        >>> sma_5 = calculate_sma(prices, 5)
        >>> print(f"5-day SMA: ${sma_5:.2f}")
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    if len(prices) < period:
        return None
    
    sma = prices.rolling(window=period).mean().iloc[-1]
    return float(sma) if not pd.isna(sma) else None


def calculate_price_change_pct(current: float, previous: float) -> float:
    """
    Calculate percentage price change
    
    Args:
        current: Current price
        previous: Previous price
        
    Returns:
        float: Percentage change (e.g., 5.5 for +5.5%)
        
    Examples:
        >>> change = calculate_price_change_pct(105, 100)
        >>> print(f"Price changed {change:+.2f}%")  # +5.00%
    """
    if previous == 0 or previous is None:
        return 0.0
    
    return ((current - previous) / previous) * 100


def calculate_bollinger_bands(prices: Union[pd.Series, list], period: int = 20, std_dev: int = 2):
    """
    Calculate Bollinger Bands (upper, middle, lower)
    
    Bollinger Bands show volatility and potential reversal zones:
    - Price at upper band: Potentially overbought
    - Price at lower band: Potentially oversold
    - Bands tightening: Low volatility (potential breakout coming)
    - Bands widening: High volatility
    
    Args:
        prices: Series of closing prices or list of prices
        period: Lookback period (default 20)
        std_dev: Standard deviations (default 2)
        
    Returns:
        dict: {'upper': float, 'middle': float, 'lower': float}
        
    Examples:
        >>> prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113, 115, 117, 116, 118, 120])
        >>> bands = calculate_bollinger_bands(prices)
        >>> print(f"Price at {bands['middle']:.2f}, range {bands['lower']:.2f} - {bands['upper']:.2f}")
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    if len(prices) < period:
        return {'upper': None, 'middle': None, 'lower': None}
    
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return {
        'upper': float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None,
        'middle': float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
        'lower': float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None
    }


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
    """
    Calculate Average True Range (ATR) - volatility indicator
    
    ATR measures market volatility:
    - High ATR: High volatility (larger price swings)
    - Low ATR: Low volatility (consolidation)
    - Used for stop loss placement (2x ATR common)
    
    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of closing prices
        period: Lookback period (default 14)
        
    Returns:
        float: ATR value, or None if insufficient data
    """
    if len(high) < period + 1:
        return None
    
    # True Range = max of:
    # 1. Current high - current low
    # 2. abs(current high - previous close)
    # 3. abs(current low - previous close)
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    
    return float(atr) if not pd.isna(atr) else None


def calculate_macd(prices: Union[pd.Series, list], fast: int = 12, slow: int = 26, signal: int = 9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    MACD shows momentum and trend changes:
    - MACD line above signal: Bullish
    - MACD line below signal: Bearish
    - Histogram expanding: Momentum increasing
    - Histogram contracting: Momentum decreasing
    
    Args:
        prices: Series of closing prices or list of prices
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)
        
    Returns:
        dict: {'macd': float, 'signal': float, 'histogram': float}
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    if len(prices) < slow + signal:
        return {'macd': None, 'signal': None, 'histogram': None}
    
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
        'signal': float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None,
        'histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
    }


def is_oversold(rsi: float, threshold: float = 30) -> bool:
    """Check if RSI indicates oversold conditions"""
    return rsi < threshold


def is_overbought(rsi: float, threshold: float = 70) -> bool:
    """Check if RSI indicates overbought conditions"""
    return rsi > threshold


def is_volume_spike(volume_ratio: float, threshold: float = 2.0) -> bool:
    """Check if volume represents a significant spike"""
    return volume_ratio >= threshold


def is_price_above_sma(price: float, sma: float) -> bool:
    """Check if price is above moving average (uptrend)"""
    if sma is None:
        return None
    return price > sma


def calculate_volatility(prices: Union[pd.Series, list], period: int = 20) -> float:
    """
    Calculate historical volatility (standard deviation of returns)
    
    Args:
        prices: Series of closing prices
        period: Lookback period
        
    Returns:
        float: Volatility as a percentage
    """
    if isinstance(prices, list):
        prices = pd.Series(prices)
    
    if len(prices) < period:
        return None
    
    returns = prices.pct_change()
    volatility = returns.rolling(window=period).std().iloc[-1] * 100
    
    return float(volatility) if not pd.isna(volatility) else None
