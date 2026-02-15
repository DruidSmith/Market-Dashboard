"""
Create aggregated views of analytics data for dashboard consumption.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class AnalyticsAggregator:
    """Generate aggregated views from calculated analytics."""
    
    def __init__(self):
        self.technical_dir = Path("data/analytics/technical")
        self.output_dir = Path("data/analytics/aggregated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _save_atomic(self, file_path: Path, data: Dict):
        """Save JSON with atomic write to prevent corruption."""
        temp_path = file_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(file_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def load_technical_data(self, symbol: str) -> Optional[Dict]:
        """Load technical analysis data for a symbol."""
        safe_symbol = symbol.replace("-", "_").replace("^", "")
        file_path = self.technical_dir / f"{safe_symbol}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def get_all_symbols(self) -> List[str]:
        """Get list of all symbols with technical data."""
        symbols = []
        for file_path in self.technical_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    symbols.append(data.get('symbol', file_path.stem))
            except:
                continue
        return symbols
    
    def create_latest_values_summary(self):
        """Create summary of latest values for all symbols."""
        print("\n📊 Creating latest values summary...")
        
        symbols = self.get_all_symbols()
        
        if not symbols:
            print("  ⚠️  No symbols found with technical data")
            return
        
        summary = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "symbol_count": len(symbols),
            "symbols": []
        }
        
        for symbol in symbols:
            tech_data = self.load_technical_data(symbol)
            
            if not tech_data or not tech_data.get('data'):
                continue
            
            # Get latest data point
            latest = tech_data['data'][-1]
            
            symbol_summary = {
                "symbol": symbol,
                "category": tech_data.get('analytics_type', 'Unknown'),
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
                    "macd_histogram": latest.get('macd_histogram'),
                    "stochastic_k": latest.get('stochastic_k'),
                    "stochastic_d": latest.get('stochastic_d')
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
                    "plus_di": latest.get('plus_di'),
                    "minus_di": latest.get('minus_di')
                },
                "performance": {
                    "roc_1d": latest.get('roc_1d'),
                    "roc_5d": latest.get('roc_5d'),
                    "roc_20d": latest.get('roc_20d'),
                    "momentum_10": latest.get('momentum_10')
                },
                "signals": {
                    "golden_cross": latest.get('golden_cross', False),
                    "death_cross": latest.get('death_cross', False),
                    "macd_bullish_cross": latest.get('macd_bullish_cross', False),
                    "macd_bearish_cross": latest.get('macd_bearish_cross', False),
                    "rsi_overbought": latest.get('rsi_overbought', False),
                    "rsi_oversold": latest.get('rsi_oversold', False),
                    "price_above_sma_200": latest.get('price_above_sma_200', False),
                    "high_volatility": latest.get('high_volatility', False),
                    "low_volatility": latest.get('low_volatility', False)
                }
            }
            
            summary['symbols'].append(symbol_summary)
        
        # Save to file using atomic write
        output_file = self.output_dir / "latest_values.json"
        self._save_atomic(output_file, summary)
        
        print(f"  ✅ Latest values summary saved ({len(summary['symbols'])} symbols)")
    
    def create_category_summary(self):
        """Create summary grouped by category."""
        print("\n📂 Creating category summary...")
        
        # Load latest values
        latest_file = self.output_dir / "latest_values.json"
        if not latest_file.exists():
            print("  ⚠️  Latest values not found, creating it first...")
            self.create_latest_values_summary()
        
        with open(latest_file, 'r') as f:
            latest_data = json.load(f)
        
        # Group by category
        categories = {}
        for symbol in latest_data['symbols']:
            category = symbol.get('category', 'Unknown')
            
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "symbol": symbol['symbol'],
                "close": symbol['price']['close'],
                "rsi_14": symbol['momentum']['rsi_14'],
                "roc_1d": symbol['performance']['roc_1d'],
                "roc_5d": symbol['performance']['roc_5d'],
                "roc_20d": symbol['performance']['roc_20d'],
                "volatility_20d": symbol['volatility']['volatility_20d'],
                "price_above_sma_200": symbol['signals']['price_above_sma_200']
            })
        
        summary = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "category_count": len(categories),
            "categories": [
                {"category": cat, "symbol_count": len(symbols), "symbols": symbols}
                for cat, symbols in categories.items()
            ]
        }
        
        # Save to file using atomic write
        output_file = self.output_dir / "by_category.json"
        self._save_atomic(output_file, summary)
        
        print(f"  ✅ Category summary saved ({len(categories)} categories)")
    
    def create_performance_rankings(self):
        """Create rankings of top/bottom performers."""
        print("\n🏆 Creating performance rankings...")
        
        # Load latest values
        latest_file = self.output_dir / "latest_values.json"
        if not latest_file.exists():
            print("  ⚠️  Latest values not found, creating it first...")
            self.create_latest_values_summary()
        
        with open(latest_file, 'r') as f:
            latest_data = json.load(f)
        
        symbols = latest_data['symbols']
        
        # Sort by different metrics
        by_roc_1d = sorted(symbols, key=lambda x: x['performance']['roc_1d'] or -999, reverse=True)
        by_roc_5d = sorted(symbols, key=lambda x: x['performance']['roc_5d'] or -999, reverse=True)
        by_roc_20d = sorted(symbols, key=lambda x: x['performance']['roc_20d'] or -999, reverse=True)
        by_rsi = sorted(symbols, key=lambda x: x['momentum']['rsi_14'] or 0, reverse=True)
        by_volatility = sorted(symbols, key=lambda x: x['volatility']['volatility_20d'] or 0, reverse=True)
        
        rankings = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "top_gainers_1d": [
                {"symbol": s['symbol'], "roc_1d": s['performance']['roc_1d']}
                for s in by_roc_1d[:5]
            ],
            "top_losers_1d": [
                {"symbol": s['symbol'], "roc_1d": s['performance']['roc_1d']}
                for s in by_roc_1d[-5:][::-1]
            ],
            "top_gainers_5d": [
                {"symbol": s['symbol'], "roc_5d": s['performance']['roc_5d']}
                for s in by_roc_5d[:5]
            ],
            "top_gainers_20d": [
                {"symbol": s['symbol'], "roc_20d": s['performance']['roc_20d']}
                for s in by_roc_20d[:5]
            ],
            "most_overbought": [
                {"symbol": s['symbol'], "rsi_14": s['momentum']['rsi_14']}
                for s in by_rsi[:5]
            ],
            "most_oversold": [
                {"symbol": s['symbol'], "rsi_14": s['momentum']['rsi_14']}
                for s in by_rsi[-5:][::-1]
            ],
            "highest_volatility": [
                {"symbol": s['symbol'], "volatility_20d": s['volatility']['volatility_20d']}
                for s in by_volatility[:5]
            ]
        }
        
        # Save to file using atomic write
        output_file = self.output_dir / "performance_rankings.json"
        self._save_atomic(output_file, rankings)
        
        print(f"  ✅ Performance rankings saved")
    
    def create_active_signals_summary(self):
        """Create summary of active trading signals."""
        print("\n🔔 Creating active signals summary...")
        
        # Load latest values
        latest_file = self.output_dir / "latest_values.json"
        if not latest_file.exists():
            print("  ⚠️  Latest values not found, creating it first...")
            self.create_latest_values_summary()
        
        with open(latest_file, 'r') as f:
            latest_data = json.load(f)
        
        symbols = latest_data['symbols']
        
        # Collect active signals
        signals_summary = {
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
        
        for symbol in symbols:
            signals = symbol['signals']
            sym = symbol['symbol']
            
            if signals.get('golden_cross'):
                signals_summary['golden_crosses'].append({
                    "symbol": sym,
                    "date": latest_data['generated_at']
                })
            
            if signals.get('death_cross'):
                signals_summary['death_crosses'].append({
                    "symbol": sym,
                    "date": latest_data['generated_at']
                })
            
            if signals.get('macd_bullish_cross'):
                signals_summary['macd_bullish_crosses'].append({
                    "symbol": sym,
                    "macd": symbol['momentum']['macd']
                })
            
            if signals.get('macd_bearish_cross'):
                signals_summary['macd_bearish_crosses'].append({
                    "symbol": sym,
                    "macd": symbol['momentum']['macd']
                })
            
            if signals.get('rsi_overbought'):
                signals_summary['rsi_overbought'].append({
                    "symbol": sym,
                    "rsi": symbol['momentum']['rsi_14']
                })
            
            if signals.get('rsi_oversold'):
                signals_summary['rsi_oversold'].append({
                    "symbol": sym,
                    "rsi": symbol['momentum']['rsi_14']
                })
            
            if signals.get('high_volatility'):
                signals_summary['high_volatility'].append({
                    "symbol": sym,
                    "volatility": symbol['volatility']['volatility_20d']
                })
            
            if signals.get('low_volatility'):
                signals_summary['low_volatility'].append({
                    "symbol": sym,
                    "volatility": symbol['volatility']['volatility_20d']
                })
        
        # Save to file using atomic write
        output_file = self.output_dir / "active_signals.json"
        self._save_atomic(output_file, signals_summary)
        
        print(f"  ✅ Active signals summary saved")
    
    def create_all(self):
        """Create all aggregated views."""
        print("\n" + "="*60)
        print("📊 Creating Aggregated Views")
        print("="*60)
        
        self.create_latest_values_summary()
        self.create_category_summary()
        self.create_performance_rankings()
        self.create_active_signals_summary()
        
        print("\n" + "="*60)
        print("✅ All aggregated views created successfully")
        print("="*60)