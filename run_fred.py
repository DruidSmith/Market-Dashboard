"""
Fetch FRED economic indicators.
"""

from dotenv import load_dotenv  # Add this import
from src.fred_fetcher import FREDFetcher
import os

load_dotenv()  # Load environment variables from .env file

def main():
    """Main execution function."""
    print("="*70)
    print("🏛️ FRED ECONOMIC INDICATORS FETCHER")
    print("="*70)
    
    # Check for API key
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        print("\n❌ FRED_API_KEY not found in environment variables")
        print("\n📝 To get a free FRED API key:")
        print("   1. Go to: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("   2. Create a free account")
        print("   3. Get your API key")
        print("   4. Add to .env file: FRED_API_KEY=your_key_here")
        print("\n" + "="*70)
        return
    
    try:
        fetcher = FREDFetcher()
        success = fetcher.fetch_and_save(days_back=365)
        
        if success:
            print("\n" + "="*70)
            print("✅ FRED DATA FETCH COMPLETE")
            print("="*70)
            print("💡 Next steps:")
            print("   - View in dashboard: streamlit run dashboard/app.py")
            print("   - Or commit to GitHub for automated updates")
            print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("="*70)


if __name__ == "__main__":
    main()