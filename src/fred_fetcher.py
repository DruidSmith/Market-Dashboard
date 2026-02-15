"""
Fetch economic indicators from FRED (Federal Reserve Economic Data).
"""

import os
from fredapi import Fred
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv  # Add this line

#load fred API key from .env file
load_dotenv()


class FREDFetcher:
    """Fetch economic indicators from FRED API."""
    
    # FRED Series IDs for key indicators
    SERIES = {
        # Interest Rates & Yields
        "treasury_10y": "DGS10",           # 10-Year Treasury Constant Maturity Rate
        "treasury_2y": "DGS2",             # 2-Year Treasury Constant Maturity Rate
        "fed_funds_rate": "FEDFUNDS",      # Federal Funds Effective Rate
        
        # Inflation
        "cpi": "CPIAUCSL",                 # Consumer Price Index for All Urban Consumers
        "pce": "PCEPI",                    # Personal Consumption Expenditures Price Index
        
        # Employment
        "unemployment": "UNRATE",          # Unemployment Rate
        "initial_claims": "ICSA",          # Initial Jobless Claims
        
        # Economic Activity
        "gdp": "GDP",                      # Gross Domestic Product
        "industrial_production": "INDPRO", # Industrial Production Index
        
        # Credit & Risk
        "high_yield_spread": "BAMLH0A0HYM2", # ICE BofA US High Yield Option-Adjusted Spread
        
        # Sentiment
        "consumer_sentiment": "UMCSENT"    # University of Michigan Consumer Sentiment
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED fetcher.
        
        Args:
            api_key: FRED API key (or set FRED_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "FRED API key not found. Set FRED_API_KEY environment variable "
                "or pass api_key parameter. Get a free key at: "
                "https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        
        self.fred = Fred(api_key=self.api_key)
        self.output_dir = Path("data/fred")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_series(self, series_id: str, name: str, days_back: int = 365) -> Optional[Dict]:
        """
        Fetch a single FRED series.
        
        Args:
            series_id: FRED series ID
            name: Human-readable name
            days_back: Number of days of historical data
        
        Returns:
            Dictionary with series data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Fetch data
            series = self.fred.get_series(
                series_id,
                observation_start=start_date.strftime('%Y-%m-%d'),
                observation_end=end_date.strftime('%Y-%m-%d')
            )
            
            if series is None or series.empty:
                print(f"  ⚠️  No data returned for {name}")
                return None
            
            # Convert to list of dicts
            data_points = []
            for date, value in series.items():
                if pd.notna(value):
                    data_points.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "value": float(value)
                    })
            
            # Get latest value
            latest = data_points[-1] if data_points else None
            
            # Calculate change metrics
            changes = {}
            if len(data_points) > 1:
                changes['1d'] = data_points[-1]['value'] - data_points[-2]['value']
            if len(data_points) > 7:
                changes['1w'] = data_points[-1]['value'] - data_points[-8]['value']
            if len(data_points) > 30:
                changes['1m'] = data_points[-1]['value'] - data_points[-31]['value']
            if len(data_points) > 90:
                changes['3m'] = data_points[-1]['value'] - data_points[-91]['value']
            
            return {
                "series_id": series_id,
                "name": name,
                "latest_value": latest['value'] if latest else None,
                "latest_date": latest['date'] if latest else None,
                "changes": changes,
                "data": data_points
            }
            
        except Exception as e:
            print(f"  ⚠️  Error fetching {name}: {e}")
            return None
    
    def calculate_yield_curve(self, data: Dict) -> Optional[float]:
        """
        Calculate yield curve spread (10Y - 2Y).
        Negative values indicate inverted yield curve (recession warning).
        
        Args:
            data: Dictionary containing treasury_10y and treasury_2y
        
        Returns:
            Yield curve spread in basis points
        """
        treasury_10y = data.get('treasury_10y')
        treasury_2y = data.get('treasury_2y')
        
        if treasury_10y and treasury_2y:
            latest_10y = treasury_10y.get('latest_value')
            latest_2y = treasury_2y.get('latest_value')
            
            if latest_10y is not None and latest_2y is not None:
                return latest_10y - latest_2y
        
        return None
    
    def fetch_all_indicators(self, days_back: int = 365) -> Dict:
        """
        Fetch all economic indicators.
        
        Args:
            days_back: Number of days of historical data
        
        Returns:
            Dictionary with all indicators
        """
        print("\n📊 Fetching FRED Economic Indicators...")
        print(f"   Retrieving last {days_back} days of data")
        
        indicators = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "data": {}
        }
        
        for key, series_id in self.SERIES.items():
            print(f"  📈 Fetching {key}...")
            data = self.fetch_series(series_id, key, days_back)
            if data:
                indicators['data'][key] = data
                print(f"  ✅ {key}: {data['latest_value']:.2f} (as of {data['latest_date']})")
        
        # Calculate derived metrics
        yield_curve = self.calculate_yield_curve(indicators['data'])
        if yield_curve is not None:
            indicators['data']['yield_curve_spread'] = {
                "name": "Yield Curve Spread (10Y-2Y)",
                "latest_value": yield_curve,
                "latest_date": indicators['data']['treasury_10y']['latest_date'],
                "interpretation": "Inverted (Recession Warning)" if yield_curve < 0 else "Normal"
            }
            print(f"  ✅ Yield Curve Spread: {yield_curve:.2f}% ({indicators['data']['yield_curve_spread']['interpretation']})")
        
        return indicators
    
    def save_indicators(self, indicators: Dict):
        """Save indicators to JSON file with atomic write."""
        file_path = self.output_dir / "indicators.json"
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w') as f:
                json.dump(indicators, f, indent=2, default=str)
            temp_path.replace(file_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def fetch_and_save(self, days_back: int = 365) -> bool:
        """
        Fetch all indicators and save to file.
        
        Args:
            days_back: Number of days of historical data
        
        Returns:
            True if successful
        """
        try:
            indicators = self.fetch_all_indicators(days_back)
            self.save_indicators(indicators)
            
            print("\n✅ FRED indicators saved successfully")
            return True
            
        except Exception as e:
            print(f"\n❌ Error fetching FRED indicators: {e}")
            return False


def main():
    """Test function."""
    import sys
    
    # Check for API key
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        print("❌ FRED_API_KEY not found in environment variables")
        print("Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("Then set it with: export FRED_API_KEY='your_key_here'")
        sys.exit(1)
    
    fetcher = FREDFetcher()
    fetcher.fetch_and_save(days_back=365)


if __name__ == "__main__":
    main()