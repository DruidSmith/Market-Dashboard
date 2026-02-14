"""
Create aggregated views of analytics for dashboard consumption.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from src.config_loader import ConfigLoader
from src.utils.data_helpers import get_all_symbols


class AnalyticsAggregator:
    """Create aggregated summary views for dashboards."""
    
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.analytics_dir = Path("data/analytics/technical")
        self.output_dir = Path("data/analytics/aggregated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_symbol_analytics(self, symbol: str) -> Optional[Dict]:
        """Load analytics for a symbol."""
        safe_symbol = symbol.replace("-", "_").replace("^", "")
        file_path = self.analytics_dir / f"{safe_symbol}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def create_latest_values_summary(self) -> Dict:
        """
        Create summary of latest indicator values for all symbols.
        
        Returns:
            Dictionary with latest values for all symbols
        """
        print("\n📊 Creating latest values summary...")
        
        tickers = self.config_loader.load_tickers()
        summary = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "symbols": []
        }
        
        for ticker in tickers:
            analytics = self._load_symbol_analytics(ticker.symbol)
            
            if not analytics or not analytics.get('data'):
                continue
            
            # Get latest data point
            latest = analytics['data'][-1]
            
            symbol_summary = {
                "symbol": ticker.symbol,
                "type": ticker.type,
                "category": ticker.category,
                "date": latest.get('date'),
                "price": {
                    "close": latest.get('close'),
                    "open": latest.get('open'),
                    "high": latest.get('high'),
                    "low": latest.get('low'),
                    "volume": latest.get('volume')
                },
                "moving_averages": {
                    "sma_20": latest.get('sma_20'),
                    "sma_50": latest.get('sma_50'),
                    "sma_200": latest.get('sma_200'),
                    "ema_12": latest.get('ema_12'),
                    "ema_26": latest.get('ema_26')
                },
                "momentum": {
                    "rsi_14": latest.get('rsi_14'),
                    "macd": latest.get('macd'),
                    "macd_signal": latest.get('macd_signal'),
                    "macd_histogram": latest.get('macd_histogram')
                },
                "volatility": {
                    "atr_14": latest.get('atr_14'),
                    "bb_upper": latest.get('bb_upper'),
                    "bb_middle": latest.get('bb_middle'),
                    "bb_lower": latest.get('bb_lower'),
                    "volatility_20d": latest.get('volatility_20d')
                },
                "trend": {
                    "adx": latest.get('adx'),
                    "adx_pos": latest.get('adx_pos'),
                    "adx_neg": latest.get('adx_neg')
                },
                "performance": {
                    "roc_1d": latest.get('roc_1d'),
                    "roc_5d": latest.get('roc_5d'),
                    "roc_20d": latest.get('roc_20d')
                },
                "signals": {
                    "price_above_sma_20": latest.get('price_above_sma_20'),
                    "price_above_sma_50": latest.get('price_above_sma_50'),
                    "price_above_sma_200": latest.get('price_above_sma_200'),
                    "rsi_overbought": latest.get('rsi_overbought'),
                    "rsi_oversold": latest.get('rsi_oversold'),
                    "macd_bullish_cross": latest.get('macd_bullish_cross'),
                    "macd_bearish_cross": latest.get('macd_bearish_cross'),
                    "golden_cross": latest.get('golden_cross'),
                    "death_cross": latest.get('death_cross'),
                    "high_volatility": latest.get('high_volatility'),
                    "low_volatility": latest.get('low_volatility')
                }
            }
            
            summary["symbols"].append(symbol_summary)
        
        # Save to file
        output_file = self.output_dir / "latest_values.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  ✅ Created latest_values.json with {len(summary['symbols'])} symbols")
        return summary
    
    def create_category_summary(self) -> Dict:
        """
        Create summary grouped by category.
        
        Returns:
            Dictionary with data grouped by category
        """
        print("\n📊 Creating category summary...")
        
        tickers = self.config_loader.load_tickers()
        categories = {}
        
        for ticker in tickers:
            analytics = self._load_symbol_analytics(ticker.symbol)
            
            if not analytics or not analytics.get('data'):
                continue
            
            latest = analytics['data'][-1]
            
            # Initialize category if needed
            if ticker.category not in categories:
                categories[ticker.category] = {
                    "category": ticker.category,
                    "symbols": []
                }
            
            # Add symbol to category
            categories[ticker.category]["symbols"].append({
                "symbol": ticker.symbol,
                "close": latest.get('close'),
                "rsi_14": latest.get('rsi_14'),
                "roc_1d": latest.get('roc_1d'),
                "roc_5d": latest.get('roc_5d'),
                "roc_20d": latest.get('roc_20d'),
                "volatility_20d": latest.get('volatility_20d'),
                "price_above_sma_200": latest.get('price_above_sma_200')
            })
        
        summary = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "categories": list(categories.values())
        }
        
        # Save to file
        output_file = self.output_dir / "by_category.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  ✅ Created by_category.json with {len(categories)} categories")
        return summary
    
    def create_performance_rankings(self) -> Dict:
        """
        Create performance rankings for different time periods.
        
        Returns:
            Dictionary with ranked symbols
        """
        print("\n📊 Creating performance rankings...")
        
        tickers = self.config_loader.load_tickers()
        symbols_data = []
        
        for ticker in tickers:
            analytics = self._load_symbol_analytics(ticker.symbol)
            
            if not analytics or not analytics.get('data'):
                continue
            
            latest = analytics['data'][-1]
            
            symbols_data.append({
                "symbol": ticker.symbol,
                "category": ticker.category,
                "roc_1d": latest.get('roc_1d', 0),
                "roc_5d": latest.get('roc_5d', 0),
                "roc_20d": latest.get('roc_20d', 0),
                "rsi_14": latest.get('rsi_14', 50),
                "volatility_20d": latest.get('volatility_20d', 0)
            })
        
        # Create rankings
        rankings = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "top_gainers_1d": sorted(symbols_data, key=lambda x: x['roc_1d'], reverse=True)[:5],
            "top_losers_1d": sorted(symbols_data, key=lambda x: x['roc_1d'])[:5],
            "top_gainers_5d": sorted(symbols_data, key=lambda x: x['roc_5d'], reverse=True)[:5],
            "top_losers_5d": sorted(symbols_data, key=lambda x: x['roc_5d'])[:5],
            "top_gainers_20d": sorted(symbols_data, key=lambda x: x['roc_20d'], reverse=True)[:5],
            "top_losers_20d": sorted(symbols_data, key=lambda x: x['roc_20d'])[:5],
            "most_overbought": sorted(symbols_data, key=lambda x: x['rsi_14'], reverse=True)[:5],
            "most_oversold": sorted(symbols_data, key=lambda x: x['rsi_14'])[:5],
            "highest_volatility": sorted(symbols_data, key=lambda x: x['volatility_20d'], reverse=True)[:5]
        }
        
        # Save to file
        output_file = self.output_dir / "performance_rankings.json"
        with open(output_file, 'w') as f:
            json.dump(rankings, f, indent=2)
        
        print(f"  ✅ Created performance_rankings.json")
        return rankings
    
    def create_signals_summary(self) -> Dict:
        """
        Create summary of active signals across all symbols.
        
        Returns:
            Dictionary with active signals
        """
        print("\n📊 Creating signals summary...")
        
        tickers = self.config_loader.load_tickers()
        signals = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "golden_crosses": [],
            "death_crosses": [],
            "macd_bullish_crosses": [],
            "macd_bearish_crosses": [],
            "rsi_overbought": [],
            "rsi_oversold": [],
            "high_volatility": [],
            "low_volatility": []
        }
        
        for ticker in tickers:
            analytics = self._load_symbol_analytics(ticker.symbol)
            
            if not analytics or not analytics.get('data'):
                continue
            
            latest = analytics['data'][-1]
            
            # Collect active signals
            if latest.get('golden_cross'):
                signals['golden_crosses'].append({
                    "symbol": ticker.symbol,
                    "date": latest.get('date')
                })
            
            if latest.get('death_cross'):
                signals['death_crosses'].append({
                    "symbol": ticker.symbol,
                    "date": latest.get('date')
                })
            
            if latest.get('macd_bullish_cross'):
                signals['macd_bullish_crosses'].append({
                    "symbol": ticker.symbol,
                    "date": latest.get('date')
                })
            
            if latest.get('macd_bearish_cross'):
                signals['macd_bearish_crosses'].append({
                    "symbol": ticker.symbol,
                    "date": latest.get('date')
                })
            
            if latest.get('rsi_overbought'):
                signals['rsi_overbought'].append({
                    "symbol": ticker.symbol,
                    "rsi": latest.get('rsi_14')
                })
            
            if latest.get('rsi_oversold'):
                signals['rsi_oversold'].append({
                    "symbol": ticker.symbol,
                    "rsi": latest.get('rsi_14')
                })
            
            if latest.get('high_volatility'):
                signals['high_volatility'].append({
                    "symbol": ticker.symbol,
                    "volatility": latest.get('volatility_20d')
                })
            
            if latest.get('low_volatility'):
                signals['low_volatility'].append({
                    "symbol": ticker.symbol,
                    "volatility": latest.get('volatility_20d')
                })
        
        # Save to file
        output_file = self.output_dir / "active_signals.json"
        with open(output_file, 'w') as f:
            json.dump(signals, f, indent=2)
        
        print(f"  ✅ Created active_signals.json")
        return signals
    
    def create_all_aggregates(self) -> Dict[str, bool]:
        """
        Create all aggregate views.
        
        Returns:
            Dictionary with success status for each aggregate
        """
        results = {}
        
        try:
            self.create_latest_values_summary()
            results['latest_values'] = True
        except Exception as e:
            print(f"  ❌ Error creating latest_values: {e}")
            results['latest_values'] = False
        
        try:
            self.create_category_summary()
            results['category_summary'] = True
        except Exception as e:
            print(f"  ❌ Error creating category_summary: {e}")
            results['category_summary'] = False
        
        try:
            self.create_performance_rankings()
            results['performance_rankings'] = True
        except Exception as e:
            print(f"  ❌ Error creating performance_rankings: {e}")
            results['performance_rankings'] = False
        
        try:
            self.create_signals_summary()
            results['signals_summary'] = True
        except Exception as e:
            print(f"  ❌ Error creating signals_summary: {e}")
            results['signals_summary'] = False
        
        return results