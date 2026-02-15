"""
Fetch and calculate fundamental metrics (PE ratio, market cap, etc.)
"""

import yfinance as yf
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class FundamentalsCalculator:
    """Fetch fundamental data for symbols."""
    
    def __init__(self):
        self.output_dir = Path("data/analytics/fundamentals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Fetch fundamental data for a symbol.
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Dictionary with fundamental metrics
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            fundamentals = {
                "symbol": symbol,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "valuation": {
                    "forward_pe": info.get('forwardPE'),
                    "trailing_pe": info.get('trailingPE'),
                    "peg_ratio": info.get('pegRatio'),
                    "price_to_book": info.get('priceToBook'),
                    "price_to_sales": info.get('priceToSalesTrailing12Months'),
                    "enterprise_value": info.get('enterpriseValue'),
                    "ev_to_revenue": info.get('enterpriseToRevenue'),
                    "ev_to_ebitda": info.get('enterpriseToEbitda')
                },
                "profitability": {
                    "profit_margin": info.get('profitMargins'),
                    "operating_margin": info.get('operatingMargins'),
                    "roe": info.get('returnOnEquity'),
                    "roa": info.get('returnOnAssets')
                },
                "growth": {
                    "revenue_growth": info.get('revenueGrowth'),
                    "earnings_growth": info.get('earningsGrowth'),
                    "earnings_quarterly_growth": info.get('earningsQuarterlyGrowth')
                },
                "financial_health": {
                    "current_ratio": info.get('currentRatio'),
                    "quick_ratio": info.get('quickRatio'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "total_cash": info.get('totalCash'),
                    "total_debt": info.get('totalDebt'),
                    "free_cashflow": info.get('freeCashflow')
                },
                "company_info": {
                    "market_cap": info.get('marketCap'),
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "full_time_employees": info.get('fullTimeEmployees')
                }
            }
            
            return fundamentals
            
        except Exception as e:
            print(f"  ⚠️  Could not fetch fundamentals for {symbol}: {e}")
            return None
    
    def save_fundamentals(self, symbol: str, data: Dict):
        """Save fundamentals to JSON file."""
        safe_symbol = symbol.replace("-", "_").replace("^", "")
        file_path = self.output_dir / f"{safe_symbol}.json"
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_for_symbol(self, symbol: str, verbose: bool = True) -> bool:
        """Fetch and save fundamentals for a symbol."""
        if verbose:
            print(f"  📊 Fetching fundamentals for {symbol}...")
        
        fundamentals = self.fetch_fundamentals(symbol)
        
        if fundamentals:
            self.save_fundamentals(symbol, fundamentals)
            if verbose:
                print(f"  ✅ Saved fundamentals for {symbol}")
            return True
        
        return False