"""
Helper functions for loading and processing market data.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict


def load_symbol_raw_data(symbol: str, data_dir: str = "data/raw") -> Optional[pd.DataFrame]:
    """
    Load raw OHLCV data for a symbol and convert to pandas DataFrame.
    
    Args:
        symbol: Ticker symbol
        data_dir: Directory containing raw data files
    
    Returns:
        DataFrame with columns: date, open, high, low, close, volume
        Returns None if file doesn't exist
    """
    data_path = Path(data_dir)
    
    # Sanitize symbol for filename (same logic as storage.py)
    safe_symbol = symbol.replace("-", "_").replace("^", "")
    file_path = data_path / f"{safe_symbol}.json"
    
    if not file_path.exists():
        return None
    
    # Load JSON
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Convert data array to DataFrame
    if not data.get('data'):
        return None
    
    df = pd.DataFrame(data['data'])
    
    # Convert date to datetime and set as index
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    
    # Sort by date ascending (oldest first) for time series calculations
    df = df.sort_index()
    
    # Ensure numeric types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def get_all_symbols(data_dir: str = "data/raw") -> List[str]:
    """
    Get list of all symbols that have raw data files.
    
    Returns:
        List of symbol strings
    """
    data_path = Path(data_dir)
    symbols = []
    
    for file_path in data_path.glob("*.json"):
        # Read the symbol from the JSON file itself
        with open(file_path, 'r') as f:
            data = json.load(f)
            symbol = data.get('symbol')
            if symbol:
                symbols.append(symbol)
    
    return sorted(symbols)


def save_analytics(symbol: str, analytics_type: str, data: pd.DataFrame, 
                   output_dir: str = "data/analytics") -> None:
    """
    Save calculated analytics to JSON file.
    
    Args:
        symbol: Ticker symbol
        analytics_type: Subdirectory (e.g., 'technical', 'aggregated')
        data: DataFrame with calculated indicators
        output_dir: Base analytics directory
    """
    output_path = Path(output_dir) / analytics_type
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Sanitize symbol for filename
    safe_symbol = symbol.replace("-", "_").replace("^", "")
    file_path = output_path / f"{safe_symbol}.json"
    
    # Reset index to include date in output
    df_output = data.reset_index()
    
    # Convert DataFrame to records format
    records = df_output.to_dict(orient='records')
    
    # Create output structure
    output = {
        "symbol": symbol,
        "analytics_type": analytics_type,
        "last_calculated": pd.Timestamp.utcnow().isoformat() + "Z",
        "data_points": len(records),
        "data": records
    }
    
    # Write to file
    with open(file_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)