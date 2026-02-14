"""
Quick test to verify storage and config loading works.
"""

from src.storage import DataStorage
from src.config_loader import ConfigLoader

def test_config_loader():
    """Test loading the ticker registry."""
    print("Testing config loader...")
    loader = ConfigLoader()
    tickers = loader.load_tickers()
    
    print(f"✓ Loaded {len(tickers)} tickers")
    for ticker in tickers[:3]:  # Show first 3
        print(f"  - {ticker.symbol}: {ticker.category}")
    print()

def test_storage():
    """Test storage initialization."""
    print("Testing storage...")
    storage = DataStorage()
    
    # Test saving dummy data
    dummy_data = [
        {"date": "2026-02-14", "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000000}
    ]
    
    storage.save_symbol_data(
        symbol="TEST",
        symbol_type="stock",
        category="test",
        api_source="test",
        data=dummy_data
    )
    
    # Test loading
    loaded = storage.load_symbol_data("TEST")
    print(f"✓ Storage working - saved and loaded test data")
    print(f"  - Symbol: {loaded['symbol']}")
    print(f"  - Data points: {len(loaded['data'])}")
    print()
    
    # Check metadata
    metadata = storage.get_metadata()
    print(f"✓ Metadata tracking working")
    print(f"  - Tracked symbols: {list(metadata.keys())}")
    print()

if __name__ == "__main__":
    test_config_loader()
    test_storage()
    print("✅ All tests passed! Ready for Step 4.")