"""
Advanced market health indicators for early warning system.
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, Optional


class MarketHealthAnalyzer:
    """Calculate advanced market health indicators."""
    
    def __init__(self):
        self.output_dir = Path("data/analytics/market_health")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_sp500_pe_ratio(self) -> Optional[Dict]:
        """
        Get S&P 500 P/E ratio using SPY as proxy.
        Alert threshold: P/E >= 30 (historical crash level)
        """
        try:
            spy = yf.Ticker("SPY")
            info = spy.info
            
            pe_ratio = info.get('trailingPE')
            
            if pe_ratio:
                status = "danger" if pe_ratio >= 30 else "warning" if pe_ratio >= 25 else "normal"
                
                return {
                    "value": pe_ratio,
                    "threshold": 30,
                    "status": status,
                    "signal": "REDUCE EQUITY ALLOCATION" if pe_ratio >= 30 else "MONITOR CLOSELY" if pe_ratio >= 25 else "NORMAL",
                    "interpretation": f"P/E of {pe_ratio:.1f} {'EXCEEDS' if pe_ratio >= 30 else 'approaching' if pe_ratio >= 25 else 'below'} historical crash threshold of 30"
                }
        except Exception as e:
            print(f"Error fetching S&P 500 P/E: {e}")
        
        return None
    
    def get_treasury_30y_yield(self, fred_data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get 30-year Treasury yield.
        Alert threshold: > 4.5%
        
        Args:
            fred_data: Optional FRED data if already loaded
        """
        try:
            # Try to load from FRED data first
            if not fred_data:
                fred_path = Path("data/fred/indicators.json")
                if fred_path.exists():
                    with open(fred_path, 'r') as f:
                        fred_data = json.load(f)
            
            # Get 30Y treasury from yfinance as fallback
            ticker = yf.Ticker("^TYX")  # 30-year Treasury yield
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                latest_yield = hist['Close'].iloc[-1]
                
                status = "danger" if latest_yield > 4.5 else "warning" if latest_yield > 4.0 else "normal"
                
                return {
                    "value": latest_yield,
                    "threshold": 4.5,
                    "status": status,
                    "signal": "SHIFT TO FIXED INCOME" if latest_yield > 4.5 else "MONITOR" if latest_yield > 4.0 else "NORMAL",
                    "interpretation": f"30Y yield at {latest_yield:.2f}% {'EXCEEDS' if latest_yield > 4.5 else 'approaching' if latest_yield > 4.0 else 'below'} threshold of 4.5%"
                }
        except Exception as e:
            print(f"Error fetching 30Y Treasury: {e}")
        
        return None
    
    def get_nyse_new_highs(self) -> Optional[Dict]:
        """
        Calculate NYSE new highs 4-week moving total.
        Alert: Downtrend in 4-week moving total indicates weakening breadth.
        
        Note: This requires specialized data feed. Using approximation with market breadth.
        """
        try:
            # Approximate using advance-decline data
            # In production, you'd use a data feed like Barchart or Alpha Vantage premium
            
            return {
                "value": None,
                "status": "unavailable",
                "signal": "DATA UNAVAILABLE",
                "interpretation": "NYSE new highs data requires premium data feed. Consider adding Barchart API."
            }
        except Exception as e:
            print(f"Error calculating NYSE new highs: {e}")
        
        return None
    
    def calculate_market_health_score(self) -> Dict:
        """
        Calculate overall market health score based on multiple indicators.
        
        Returns:
            Dictionary with health assessment
        """
        indicators = {
            "sp500_pe": self.get_sp500_pe_ratio(),
            "treasury_30y": self.get_treasury_30y_yield(),
            "nyse_new_highs": self.get_nyse_new_highs()
        }
        
        # Calculate risk score (0-10, 10 = highest risk)
        risk_score = 0
        alerts = []
        
        # S&P 500 P/E contribution (0-4 points)
        if indicators['sp500_pe']:
            pe = indicators['sp500_pe']['value']
            if pe >= 30:
                risk_score += 4
                alerts.append("🔴 CRITICAL: S&P 500 P/E at crash threshold")
            elif pe >= 25:
                risk_score += 2
                alerts.append("🟡 WARNING: S&P 500 P/E elevated")
        
        # 30Y Treasury contribution (0-3 points)
        if indicators['treasury_30y']:
            yield_val = indicators['treasury_30y']['value']
            if yield_val > 4.5:
                risk_score += 3
                alerts.append("🔴 CRITICAL: 30Y yield exceeds 4.5%")
            elif yield_val > 4.0:
                risk_score += 1
                alerts.append("🟡 WARNING: 30Y yield rising")
        
        # Overall assessment
        if risk_score >= 6:
            overall_status = "DANGER"
            recommendation = "REDUCE EQUITY EXPOSURE - Consider moving to 50% equities"
        elif risk_score >= 3:
            overall_status = "WARNING"
            recommendation = "MONITOR CLOSELY - Prepare exit strategy"
        else:
            overall_status = "NORMAL"
            recommendation = "MAINTAIN CURRENT ALLOCATION"
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "risk_score": risk_score,
            "max_score": 10,
            "overall_status": overall_status,
            "recommendation": recommendation,
            "alerts": alerts,
            "indicators": indicators
        }
    
    def save_health_assessment(self, assessment: Dict):
        """Save health assessment to file."""
        file_path = self.output_dir / "market_health.json"
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w') as f:
                json.dump(assessment, f, indent=2, default=str)
            temp_path.replace(file_path)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def analyze_and_save(self) -> bool:
        """Run full analysis and save results."""
        try:
            print("\n🏥 Analyzing Market Health Indicators...")
            
            assessment = self.calculate_market_health_score()
            self.save_health_assessment(assessment)
            
            print(f"  Risk Score: {assessment['risk_score']}/10")
            print(f"  Status: {assessment['overall_status']}")
            print(f"  Recommendation: {assessment['recommendation']}")
            
            if assessment['alerts']:
                print("\n  ⚠️  Active Alerts:")
                for alert in assessment['alerts']:
                    print(f"    {alert}")
            
            print("\n✅ Market health assessment saved")
            return True
            
        except Exception as e:
            print(f"\n❌ Error analyzing market health: {e}")
            return False


def main():
    """Test function."""
    analyzer = MarketHealthAnalyzer()
    analyzer.analyze_and_save()


if __name__ == "__main__":
    main()