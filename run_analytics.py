"""
Run analytics calculations on fetched market data.
"""

from src.analytics.calculator import AnalyticsCalculator
from src.analytics.aggregator import AnalyticsAggregator
from src.analytics.market_health import MarketHealthAnalyzer


def main():
    """Main execution function."""
    print("="*70)
    print("🚀 MARKET ANALYTICS CALCULATOR")
    print("="*70)
    
    try:
        # Step 1: Calculate technical indicators for all symbols
        print("\n📊 Step 1: Calculating Technical Indicators")
        print("-"*70)
        
        calculator = AnalyticsCalculator()
        calc_results = calculator.calculate_all(include_fundamentals=True)
        
        print("\n✅ Technical indicator calculation complete!")
        print(f"   Successful: {calc_results['successful']}")
        print(f"   Failed: {calc_results['failed']}")
        
        # Step 2: Create aggregated views
        print("\n📊 Step 2: Creating Aggregated Views")
        print("-"*70)
        
        aggregator = AnalyticsAggregator()
        aggregator.create_all()
        
        print("\n✅ Aggregated views created!")
        
        # Step 3: Analyze market health
        print("\n🏥 Step 3: Analyzing Market Health")
        print("-"*70)
        
        health_analyzer = MarketHealthAnalyzer()
        health_analyzer.analyze_and_save()
        
        # Summary
        print("\n" + "="*70)
        print("✅ ANALYTICS CALCULATION COMPLETE")
        print("="*70)
        print(f"Total symbols processed: {calc_results['successful'] + calc_results['failed']}")
        print(f"Success rate: {calc_results['successful']}/{calc_results['successful'] + calc_results['failed']}")
        print("\n💡 Next steps:")
        print("   - Run the dashboard: streamlit run dashboard/app.py")
        print("   - Or commit to GitHub to trigger automated updates")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        print("="*70)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print("="*70)


if __name__ == "__main__":
    main()