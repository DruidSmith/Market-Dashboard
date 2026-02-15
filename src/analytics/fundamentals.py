"""
Fetch and calculate comprehensive fundamental metrics including FCF, CapEx, ROIC, etc.
"""

import yfinance as yf
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class FundamentalsCalculator:
    """Fetch comprehensive fundamental data for symbols."""
    
    def __init__(self):
        self.output_dir = Path("data/analytics/fundamentals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_roic(self, info: Dict) -> Optional[float]:
        """
        Calculate Return on Invested Capital.
        ROIC = NOPAT / Invested Capital
        Approximation: ROIC ≈ (Net Income) / (Total Assets - Current Liabilities)
        """
        try:
            net_income = info.get('netIncomeToCommon')
            total_assets = info.get('totalAssets')
            current_liabilities = info.get('totalCurrentLiabilities')
            
            if net_income and total_assets and current_liabilities:
                invested_capital = total_assets - current_liabilities
                if invested_capital > 0:
                    return (net_income / invested_capital) * 100
        except:
            pass
        return None
    
    def calculate_interest_coverage(self, info: Dict) -> Optional[float]:
        """
        Calculate Interest Coverage Ratio.
        Interest Coverage = EBIT / Interest Expense
        """
        try:
            ebit = info.get('ebit')
            interest_expense = info.get('interestExpense')
            
            if ebit and interest_expense and interest_expense != 0:
                return ebit / abs(interest_expense)
        except:
            pass
        return None
    
    def calculate_fcf_margin(self, info: Dict) -> Optional[float]:
        """
        Calculate Free Cash Flow Margin.
        FCF Margin = FCF / Revenue
        """
        try:
            fcf = info.get('freeCashflow')
            revenue = info.get('totalRevenue')
            
            if fcf and revenue and revenue != 0:
                return (fcf / revenue) * 100
        except:
            pass
        return None
    
    def calculate_capex_metrics(self, ticker_obj) -> Dict:
        """
        Calculate CapEx-related metrics and trends.
        """
        metrics = {
            "capex_latest": None,
            "capex_as_pct_revenue": None,
            "capex_trend": None,  # "increasing", "decreasing", "stable"
            "capex_3yr_cagr": None
        }
        
        try:
            # Get cashflow statement
            cashflow = ticker_obj.cashflow
            
            if cashflow is not None and not cashflow.empty:
                # Capital Expenditure (usually negative in cashflow)
                if 'Capital Expenditure' in cashflow.index:
                    capex_row = cashflow.loc['Capital Expenditure']
                    
                    # Latest CapEx (make positive)
                    latest_capex = abs(capex_row.iloc[0]) if len(capex_row) > 0 else None
                    metrics['capex_latest'] = latest_capex
                    
                    # CapEx as % of Revenue
                    income = ticker_obj.financials
                    if income is not None and not income.empty and 'Total Revenue' in income.index:
                        revenue_row = income.loc['Total Revenue']
                        latest_revenue = revenue_row.iloc[0] if len(revenue_row) > 0 else None
                        
                        if latest_capex and latest_revenue and latest_revenue != 0:
                            metrics['capex_as_pct_revenue'] = (latest_capex / latest_revenue) * 100
                    
                    # CapEx Trend (compare last 3 years if available)
                    if len(capex_row) >= 3:
                        capex_values = [abs(x) for x in capex_row.iloc[:3].values]
                        
                        # Check trend
                        if capex_values[0] > capex_values[1] * 1.1:
                            metrics['capex_trend'] = "increasing"
                        elif capex_values[0] < capex_values[1] * 0.9:
                            metrics['capex_trend'] = "decreasing"
                        else:
                            metrics['capex_trend'] = "stable"
                        
                        # 3-year CAGR
                        if len(capex_values) >= 3 and capex_values[2] > 0:
                            years = 2
                            cagr = ((capex_values[0] / capex_values[2]) ** (1/years) - 1) * 100
                            metrics['capex_3yr_cagr'] = cagr
        except Exception as e:
            print(f"    ⚠️  Error calculating CapEx metrics: {e}")
        
        return metrics
    
    def fetch_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Fetch comprehensive fundamental data for a symbol.
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Dictionary with fundamental metrics
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Calculate derived metrics
            roic = self.calculate_roic(info)
            interest_coverage = self.calculate_interest_coverage(info)
            fcf_margin = self.calculate_fcf_margin(info)
            capex_metrics = self.calculate_capex_metrics(ticker)
            
            fundamentals = {
                "symbol": symbol,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                
                # Valuation Metrics
                "valuation": {
                    "forward_pe": info.get('forwardPE'),
                    "trailing_pe": info.get('trailingPE'),
                    "peg_ratio": info.get('pegRatio'),
                    "price_to_book": info.get('priceToBook'),
                    "price_to_sales": info.get('priceToSalesTrailing12Months'),
                    "enterprise_value": info.get('enterpriseValue'),
                    "ev_to_revenue": info.get('enterpriseToRevenue'),
                    "ev_to_ebitda": info.get('enterpriseToEbitda'),
                    "market_cap": info.get('marketCap')
                },
                
                # Profitability Metrics
                "profitability": {
                    "profit_margin": info.get('profitMargins'),
                    "operating_margin": info.get('operatingMargins'),
                    "gross_margin": info.get('grossMargins'),
                    "roe": info.get('returnOnEquity'),
                    "roa": info.get('returnOnAssets'),
                    "roic": roic
                },
                
                # Growth Metrics
                "growth": {
                    "revenue_growth": info.get('revenueGrowth'),
                    "earnings_growth": info.get('earningsGrowth'),
                    "earnings_quarterly_growth": info.get('earningsQuarterlyGrowth')
                },
                
                # Financial Health
                "financial_health": {
                    "current_ratio": info.get('currentRatio'),
                    "quick_ratio": info.get('quickRatio'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "total_cash": info.get('totalCash'),
                    "total_debt": info.get('totalDebt'),
                    "interest_coverage": interest_coverage
                },
                
                # Cash Flow Metrics
                "cash_flow": {
                    "operating_cashflow": info.get('operatingCashflow'),
                    "free_cashflow": info.get('freeCashflow'),
                    "fcf_margin": fcf_margin,
                    "capex": capex_metrics.get('capex_latest'),
                    "capex_as_pct_revenue": capex_metrics.get('capex_as_pct_revenue'),
                    "capex_trend": capex_metrics.get('capex_trend'),
                    "capex_3yr_cagr": capex_metrics.get('capex_3yr_cagr')
                },
                
                # Company Info
                "company_info": {
                    "sector": info.get('sector'),
                    "industry": info.get('industry'),
                    "full_time_employees": info.get('fullTimeEmployees'),
                    "beta": info.get('beta')
                }
            }
            
            return fundamentals
            
        except Exception as e:
            print(f"  ⚠️  Could not fetch fundamentals for {symbol}: {e}")
            return None
    
    def save_fundamentals(self, symbol: str, data: Dict):
        """Save fundamentals to JSON file with atomic write."""
        safe_symbol = symbol.replace("-", "_").replace("^", "")
        file_path = self.output_dir / f"{safe_symbol}.json"
        
        # Atomic write
        temp_path = file_path.with_suffix('.tmp')
        try:
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(file_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
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