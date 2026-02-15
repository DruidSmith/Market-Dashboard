"""
Technical indicator calculations using ta library.
"""

import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator


class TechnicalIndicators:
    """Calculate technical indicators for market data."""
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for a symbol.
        
        Args:
            df: DataFrame with OHLCV data (indexed by date)
        
        Returns:
            DataFrame with original data plus all indicators
        """
        # Create a copy to avoid modifying original
        result = df.copy()
        
        # Moving Averages
        result['sma_20'] = SMAIndicator(close=result['close'], window=20).sma_indicator()
        result['sma_50'] = SMAIndicator(close=result['close'], window=50).sma_indicator()
        result['sma_200'] = SMAIndicator(close=result['close'], window=200).sma_indicator()
        result['ema_12'] = EMAIndicator(close=result['close'], window=12).ema_indicator()
        result['ema_26'] = EMAIndicator(close=result['close'], window=26).ema_indicator()
        
        # RSI (Relative Strength Index)
        result['rsi_14'] = RSIIndicator(close=result['close'], window=14).rsi()
        
        # MACD (Moving Average Convergence Divergence)
        macd = MACD(close=result['close'], window_slow=26, window_fast=12, window_sign=9)
        result['macd'] = macd.macd()
        result['macd_signal'] = macd.macd_signal()
        result['macd_histogram'] = macd.macd_diff()
        
        # Bollinger Bands
        bbands = BollingerBands(close=result['close'], window=20, window_dev=2)
        result['bb_upper'] = bbands.bollinger_hband()
        result['bb_middle'] = bbands.bollinger_mavg()
        result['bb_lower'] = bbands.bollinger_lband()
        result['bb_bandwidth'] = bbands.bollinger_wband()
        
        # ATR (Average True Range) - Volatility
        result['atr_14'] = AverageTrueRange(
            high=result['high'], 
            low=result['low'], 
            close=result['close'], 
            window=14
        ).average_true_range()
        
        # Volume indicators
        result['volume_sma_20'] = SMAIndicator(close=result['volume'], window=20).sma_indicator()
        
        # On-Balance Volume
        result['obv'] = OnBalanceVolumeIndicator(
            close=result['close'], 
            volume=result['volume']
        ).on_balance_volume()
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(
            high=result['high'],
            low=result['low'],
            close=result['close'],
            window=14,
            smooth_window=3
        )
        result['stoch_k'] = stoch.stoch()
        result['stoch_d'] = stoch.stoch_signal()
        
        # ADX (Average Directional Index) - Trend Strength
        adx = ADXIndicator(
            high=result['high'],
            low=result['low'],
            close=result['close'],
            window=14
        )
        result['adx'] = adx.adx()
        result['adx_pos'] = adx.adx_pos()
        result['adx_neg'] = adx.adx_neg()
        
        # Add crossover detection at the end, before return
        result = TechnicalIndicators.detect_crossovers(result)
        
        return result
    
    @staticmethod
    def calculate_custom_signals(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate custom trading signals and patterns.
        
        Args:
            df: DataFrame with OHLCV and technical indicators
        
        Returns:
            DataFrame with additional signal columns
        """
        result = df.copy()
        
        # Golden Cross / Death Cross signals
        if 'sma_50' in result.columns and 'sma_200' in result.columns:
            result['golden_cross'] = (
                (result['sma_50'] > result['sma_200']) & 
                (result['sma_50'].shift(1) <= result['sma_200'].shift(1))
            )
            result['death_cross'] = (
                (result['sma_50'] < result['sma_200']) & 
                (result['sma_50'].shift(1) >= result['sma_200'].shift(1))
            )
        
        # RSI Overbought/Oversold
        if 'rsi_14' in result.columns:
            result['rsi_overbought'] = result['rsi_14'] > 70
            result['rsi_oversold'] = result['rsi_14'] < 30
        
        # MACD Crossovers
        if 'macd' in result.columns and 'macd_signal' in result.columns:
            result['macd_bullish_cross'] = (
                (result['macd'] > result['macd_signal']) & 
                (result['macd'].shift(1) <= result['macd_signal'].shift(1))
            )
            result['macd_bearish_cross'] = (
                (result['macd'] < result['macd_signal']) & 
                (result['macd'].shift(1) >= result['macd_signal'].shift(1))
            )
        
        # Price vs Moving Averages
        if 'sma_20' in result.columns:
            result['price_above_sma_20'] = result['close'] > result['sma_20']
        if 'sma_50' in result.columns:
            result['price_above_sma_50'] = result['close'] > result['sma_50']
        if 'sma_200' in result.columns:
            result['price_above_sma_200'] = result['close'] > result['sma_200']
        
        # Volatility regime (using ATR)
        if 'atr_14' in result.columns:
            atr_percentile = result['atr_14'].rolling(window=50).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1] if len(x) > 0 else np.nan
            )
            result['high_volatility'] = atr_percentile > 0.75
            result['low_volatility'] = atr_percentile < 0.25
        
        return result
    
    @staticmethod
    def calculate_momentum_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate momentum and rate of change metrics.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with momentum metrics
        """
        result = df.copy()
        
        # Rate of Change (ROC)
        result['roc_1d'] = result['close'].pct_change(periods=1) * 100
        result['roc_5d'] = result['close'].pct_change(periods=5) * 100
        result['roc_20d'] = result['close'].pct_change(periods=20) * 100
        
        # Momentum (absolute price change)
        result['momentum_10'] = result['close'] - result['close'].shift(10)
        
        # Rolling volatility (standard deviation of returns)
        result['volatility_20d'] = result['roc_1d'].rolling(window=20).std()
        
        return result
    
    @staticmethod
    def detect_crossovers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect and classify SMA/EMA crossovers.
        
        Args:
            df: DataFrame with moving averages
        
        Returns:
            DataFrame with crossover status columns
        """
        result = df.copy()
        
        # SMA Cross (50 vs 200)
        if 'sma_50' in result.columns and 'sma_200' in result.columns:
            # Current position
            result['sma_position'] = 'neutral'
            result.loc[result['sma_50'] > result['sma_200'], 'sma_position'] = 'golden'
            result.loc[result['sma_50'] < result['sma_200'], 'sma_position'] = 'death'
            
            # Recent cross detection (within last 5 days)
            sma_50_above = result['sma_50'] > result['sma_200']
            sma_50_was_below = result['sma_50'].shift(5) <= result['sma_200'].shift(5)
            result['recent_golden_cross'] = sma_50_above & sma_50_was_below
            
            sma_50_below = result['sma_50'] < result['sma_200']
            sma_50_was_above = result['sma_50'].shift(5) >= result['sma_200'].shift(5)
            result['recent_death_cross'] = sma_50_below & sma_50_was_above
        
        # EMA Trend (12 vs 26)
        if 'ema_12' in result.columns and 'ema_26' in result.columns:
            result['ema_trend'] = 'neutral'
            result.loc[result['ema_12'] > result['ema_26'], 'ema_trend'] = 'bullish'
            result.loc[result['ema_12'] < result['ema_26'], 'ema_trend'] = 'bearish'
        
        return result