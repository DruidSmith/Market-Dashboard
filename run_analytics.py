"""
Calculate technical indicators and analytics for all market data.
Run this after fetching new data.
"""

import sys
import argparse
from src.analytics.calculator import AnalyticsCalculator
from src.analytics.aggregator import AnalyticsAggregator


def main():
    """Run analytics calculations."""
    parser = argparse.ArgumentParser(description="Calculate market analytics")
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Specific symbols to calculate (default: all)"
    )
    parser.add_argument(
        "--skip-aggregates",
        action="store_true",
        help="Skip creating aggregate views"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("Market Analytics Calculator - Phase 2")
    print("="*60)
    
    try:
        # Step 1: Calculate technical indicators
        calculator = AnalyticsCalculator()
        calc_results = calculator.calculate_all(symbols=args.symbols)
        
        # Step 2: Create aggregated views
        if not args.skip_aggregates and calc_results['successful'] > 0:
            print("\n" + "="*60)
            print("Creating Aggregated Views")
            print("="*60)
            
            aggregator = AnalyticsAggregator()
            agg_results = aggregator.create_all_aggregates()
            
            successful_aggs = sum(1 for v in agg_results.values() if v)
            print(f"\n✅ Created {successful_aggs}/{len(agg_results)} aggregate views")
        
        if calc_results['failed'] == 0:
            print("\n✅ All calculations completed successfully!")
            return 0
        else:
            print(f"\n⚠️  Completed with {calc_results['failed']} failures")
            return 0 if calc_results['successful'] > 0 else 1
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())