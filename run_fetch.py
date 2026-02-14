"""
Main entry point for fetching market data.
Run this script locally or via GitHub Actions.
"""

import sys
import argparse
from src.fetcher import MarketDataFetcher

def main():
    """Run the market data fetcher."""
    parser = argparse.ArgumentParser(description="Fetch market data")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Maximum number of symbols to fetch in this run (default: 5)"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Market Data Fetcher - Phase 1 (Smart Resume)")
    print("="*60)
    
    try:
        fetcher = MarketDataFetcher()
        fetcher.fetch_batch(max_symbols=args.batch_size)
        
        print("\n✅ Fetch completed successfully!")
        return 0
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())