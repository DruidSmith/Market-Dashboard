"""
Main calculator that orchestrates all analytics computations.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional

from src.utils.data_helpers import (
    load_symbol_raw_data, 
    get_all_symbols, 
    save_analytics
)
from src.analytics.technical_indicators import TechnicalIndicators
from src.analytics.fundamentals import FundamentalsCalculator


class AnalyticsCalculator:
    """Orchestrates calculation of all analytics for market data."""
    
    def __init__(self):
        self.technical = TechnicalIndicators()
        self.fundamentals = FundamentalsCalculator()
    
    def calculate_for_symbol(self, symbol: str, include_fundamentals: bool = True, verbose: bool = True) -> bool:
        """
        Calculate all analytics for a single symbol.
        
        Args:
            symbol: Ticker symbol
            include_fundamentals: Whether to fetch fundamental data
            verbose: Print progress messages
        
        Returns:
            True if successful, False otherwise
        """
        if verbose:
            print(f"\n📊 Calculating analytics for {symbol}...")
        
        try:
            # Load raw data
            df = load_symbol_raw_data(symbol)
            
            if df is None or df.empty:
                print(f"  ⚠️  No raw data found for {symbol}")
                return False
            
            if len(df) < 50:
                print(f"  ⚠️  Insufficient data for {symbol} ({len(df)} days, need 50+)")
                return False
            
            # Calculate technical indicators
            df_with_indicators = self.technical.calculate_all(df)
            
            # Calculate custom signals
            df_with_signals = self.technical.calculate_custom_signals(df_with_indicators)
            
            # Calculate momentum metrics
            df_complete = self.technical.calculate_momentum_metrics(df_with_signals)
            
            # Save to analytics directory
            save_analytics(symbol, 'technical', df_complete)
            
            if verbose:
                print(f"  ✅ Calculated {len(df_complete.columns)} indicators for {symbol}")
                print(f"  📈 Data points: {len(df_complete)}")
            
            # Fetch fundamentals (only for stocks, not indices or crypto)
            if include_fundamentals:
                # Skip fundamentals for indices and crypto
                skip_symbols = ['^VIX', '^GSPC', '^DJI', '^IXIC']
                if symbol not in skip_symbols and not symbol.endswith('-USD'):
                    self.fundamentals.calculate_for_symbol(symbol, verbose=verbose)
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error calculating analytics for {symbol}: {e}")
            return False
    
    def calculate_all(self, symbols: Optional[List[str]] = None, include_fundamentals: bool = True) -> Dict[str, int]:
        """
        Calculate analytics for all symbols (or specified list).
        
        Args:
            symbols: Optional list of symbols to process. If None, process all.
            include_fundamentals: Whether to fetch fundamental data
        
        Returns:
            Dictionary with counts: {'successful': N, 'failed': M}
        """
        if symbols is None:
            symbols = get_all_symbols()
        
        print(f"🚀 Starting analytics calculation for {len(symbols)} symbols...")
        
        successful = 0
        failed = 0
        
        for symbol in symbols:
            if self.calculate_for_symbol(symbol, include_fundamentals=include_fundamentals):
                successful += 1
            else:
                failed += 1
        
        # Summary
        print("\n" + "="*60)
        print("📈 Analytics Calculation Summary:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print("="*60)
        
        return {
            'successful': successful,
            'failed': failed
        }