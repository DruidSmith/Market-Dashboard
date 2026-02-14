"""
Load and parse the ticker registry CSV file.
"""

import csv
from pathlib import Path
from typing import List, Dict


class TickerConfig:
    """Represents a single ticker from the registry."""
    
    def __init__(self, symbol: str, ticker_type: str, category: str, 
                 api_source: str, enabled: bool):
        self.symbol = symbol
        self.type = ticker_type
        self.category = category
        self.api_source = api_source
        self.enabled = enabled
    
    def __repr__(self):
        return f"TickerConfig({self.symbol}, {self.type}, {self.category})"


class ConfigLoader:
    """Loads ticker configuration from CSV file."""
    
    def __init__(self, config_path: str = "config/tickers.csv"):
        self.config_path = Path(config_path)
    
    def load_tickers(self) -> List[TickerConfig]:
        """Load all enabled tickers from the CSV file."""
        tickers = []
        
        with open(self.config_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert enabled string to boolean
                enabled = row['enabled'].strip().upper() == 'TRUE'
                
                # Only include enabled tickers
                if enabled:
                    ticker = TickerConfig(
                        symbol=row['symbol'].strip(),
                        ticker_type=row['type'].strip(),
                        category=row['category'].strip(),
                        api_source=row['api_source'].strip(),
                        enabled=enabled
                    )
                    tickers.append(ticker)
        
        return tickers
    
    def get_symbols_by_category(self, category: str) -> List[TickerConfig]:
        """Get all tickers in a specific category."""
        all_tickers = self.load_tickers()
        return [t for t in all_tickers if t.category == category]