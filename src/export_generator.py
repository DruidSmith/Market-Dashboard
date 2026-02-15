"""
Generate comprehensive export files for AI analysis.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ExportGenerator:
    """Generate comprehensive export files with all market data and indicators."""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.output_dir = Path("data/exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_latest_values(self) -> Optional[Dict]:
        """Load latest values aggregate."""
        file_path = self.data_dir / "analytics/aggregated/latest_values.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def load_fred_data(self) -> Optional[Dict]:
        """Load FRED economic data."""
        file_path = self.data_dir / "fred/indicators.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def load_symbol_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Load fundamental data for a symbol."""
        safe_symbol = symbol.replace("-", "_").replace("^", "")
        file_path = self.data_dir / f"analytics/fundamentals/{safe_symbol}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def generate_ai_prompt_report(self) -> str:
        """
        Generate a comprehensive text report optimized for AI analysis.
        
        Returns:
            Formatted text report
        """
        report = []
        
        # Header
        report.append("=" * 80)
        report.append("COMPREHENSIVE MARKET ANALYSIS REPORT")
        report.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        report.append("=" * 80)
        report.append("")
        
        # Load data
        latest_values = self.load_latest_values()
        fred_data = self.load_fred_data()
        
        # === SECTION 1: MACRO ECONOMIC CONTEXT ===
        report.append("=" * 80)
        report.append("SECTION 1: MACRO ECONOMIC INDICATORS (FRED)")
        report.append("=" * 80)
        report.append("")
        
        if fred_data:
            indicators = fred_data.get('data', {})
            
            # Interest Rates
            report.append("Interest Rates & Yields:")
            report.append("-" * 40)
            
            treasury_10y = indicators.get('treasury_10y')
            if treasury_10y:
                report.append(f"  10-Year Treasury: {treasury_10y['latest_value']:.2f}%")
                if '1m' in treasury_10y.get('changes', {}):
                    report.append(f"    1-Month Change: {treasury_10y['changes']['1m']:+.2f}%")
            
            treasury_2y = indicators.get('treasury_2y')
            if treasury_2y:
                report.append(f"  2-Year Treasury: {treasury_2y['latest_value']:.2f}%")
            
            yield_curve = indicators.get('yield_curve_spread')
            if yield_curve:
                report.append(f"  Yield Curve Spread (10Y-2Y): {yield_curve['latest_value']:.2f}%")
                report.append(f"    Status: {yield_curve['interpretation']}")
                if yield_curve['latest_value'] < 0:
                    report.append("    ⚠️  WARNING: INVERTED YIELD CURVE - RECESSION RISK")
            
            fed_funds = indicators.get('fed_funds_rate')
            if fed_funds:
                report.append(f"  Fed Funds Rate: {fed_funds['latest_value']:.2f}%")
            
            report.append("")
            
            # Employment
            report.append("Employment:")
            report.append("-" * 40)
            
            unemployment = indicators.get('unemployment')
            if unemployment:
                report.append(f"  Unemployment Rate: {unemployment['latest_value']:.1f}%")
                if '1m' in unemployment.get('changes', {}):
                    report.append(f"    1-Month Change: {unemployment['changes']['1m']:+.1f}%")
            
            initial_claims = indicators.get('initial_claims')
            if initial_claims:
                report.append(f"  Initial Jobless Claims: {initial_claims['latest_value']:,.0f}")
            
            report.append("")
            
            # Inflation
            report.append("Inflation:")
            report.append("-" * 40)
            
            cpi = indicators.get('cpi')
            if cpi:
                report.append(f"  CPI Index: {cpi['latest_value']:.2f}")
            
            report.append("")
        else:
            report.append("⚠️  FRED data not available")
            report.append("")
        
        # === SECTION 2: MARKET INDICES ===
        report.append("=" * 80)
        report.append("SECTION 2: MAJOR MARKET INDICES")
        report.append("=" * 80)
        report.append("")
        
        if latest_values:
            symbols = latest_values.get('symbols', [])
            
            # Key indices
            for symbol_name in ['^VIX', 'SPY', 'QQQ', 'NQ=F']:
                symbol_data = next((s for s in symbols if s['symbol'] == symbol_name), None)
                if symbol_data:
                    report.append(f"{symbol_data['symbol']}:")
                    report.append("-" * 40)
                    report.append(f"  Price: ${symbol_data['price']['close']:.2f}")
                    report.append(f"  1-Day Change: {symbol_data['performance']['roc_1d']:+.2f}%")
                    report.append(f"  5-Day Change: {symbol_data['performance']['roc_5d']:+.2f}%")
                    report.append(f"  20-Day Change: {symbol_data['performance']['roc_20d']:+.2f}%")
                    report.append(f"  RSI(14): {symbol_data['momentum']['rsi_14']:.1f}")
                    
                    if symbol_data['momentum']['rsi_14'] > 70:
                        report.append("    Status: OVERBOUGHT")
                    elif symbol_data['momentum']['rsi_14'] < 30:
                        report.append("    Status: OVERSOLD")
                    else:
                        report.append("    Status: Neutral")
                    
                    report.append(f"  ATR(14): ${symbol_data['volatility']['atr_14']:.2f}")
                    report.append(f"  Volatility (20d): {symbol_data['volatility']['volatility_20d']:.2f}%")
                    
                    # Signals
                    signals = symbol_data.get('signals', {})
                    if signals.get('price_above_sma_200'):
                        report.append("  Trend: ABOVE 200-day SMA (Bullish)")
                    else:
                        report.append("  Trend: BELOW 200-day SMA (Bearish)")
                    
                    report.append("")
        
        # === SECTION 3: AI STOCKS DETAILED ANALYSIS ===
        report.append("=" * 80)
        report.append("SECTION 3: AI BUBBLE INDICATORS - DETAILED ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        if latest_values:
            ai_symbols = [s for s in symbols if 'AI' in s.get('category', '')]
            
            report.append(f"Total AI-related symbols tracked: {len(ai_symbols)}")
            report.append("")
            
            for symbol_data in ai_symbols:
                symbol = symbol_data['symbol']
                report.append(f"{symbol}:")
                report.append("-" * 40)
                
                # Price & Performance
                report.append("Price & Performance:")
                report.append(f"  Current Price: ${symbol_data['price']['close']:.2f}")
                report.append(f"  1-Day: {symbol_data['performance']['roc_1d']:+.2f}%")
                report.append(f"  5-Day: {symbol_data['performance']['roc_5d']:+.2f}%")
                report.append(f"  20-Day: {symbol_data['performance']['roc_20d']:+.2f}%")
                report.append("")
                
                # Technical Indicators
                report.append("Technical Indicators:")
                report.append(f"  RSI(14): {symbol_data['momentum']['rsi_14']:.1f}")
                
                if symbol_data['momentum']['rsi_14'] > 70:
                    report.append("    ⚠️  OVERBOUGHT - Potential correction risk")
                elif symbol_data['momentum']['rsi_14'] < 30:
                    report.append("    💡 OVERSOLD - Potential buying opportunity")
                
                report.append(f"  MACD: {symbol_data['momentum']['macd']:.2f}")
                report.append(f"  MACD Signal: {symbol_data['momentum']['macd_signal']:.2f}")
                
                if symbol_data['momentum']['macd'] > symbol_data['momentum']['macd_signal']:
                    report.append("    MACD: Bullish (above signal)")
                else:
                    report.append("    MACD: Bearish (below signal)")
                
                report.append(f"  ATR(14): ${symbol_data['volatility']['atr_14']:.2f}")
                report.append("")
                
                # Stop Loss Recommendations
                current_price = symbol_data['price']['close']
                atr = symbol_data['volatility']['atr_14']
                
                report.append("Recommended Stop Loss Levels (ATR-based):")
                report.append(f"  Conservative (1x ATR): ${current_price - atr:.2f} (Risk: {((atr/current_price)*100):.1f}%)")
                report.append(f"  Moderate (2x ATR): ${current_price - (atr*2):.2f} (Risk: {((atr*2/current_price)*100):.1f}%) ⭐ RECOMMENDED")
                report.append(f"  Wide (3x ATR): ${current_price - (atr*3):.2f} (Risk: {((atr*3/current_price)*100):.1f}%)")
                report.append("")
                
                # Moving Averages
                report.append("Moving Averages:")
                report.append(f"  SMA(20): ${symbol_data['moving_averages']['sma_20']:.2f}")
                report.append(f"  SMA(50): ${symbol_data['moving_averages']['sma_50']:.2f}")
                report.append(f"  SMA(200): ${symbol_data['moving_averages']['sma_200']:.2f}")
                
                signals = symbol_data.get('signals', {})
                if signals.get('golden_cross'):
                    report.append("    📈 GOLDEN CROSS - Bullish signal")
                elif signals.get('death_cross'):
                    report.append("    📉 DEATH CROSS - Bearish signal")
                
                if signals.get('price_above_sma_200'):
                    report.append("    Trend: ABOVE 200-day SMA (Long-term uptrend)")
                else:
                    report.append("    Trend: BELOW 200-day SMA (Long-term downtrend)")
                
                report.append("")
                
                # Fundamentals (if available)
                fund_data = self.load_symbol_fundamentals(symbol)
                if fund_data:
                    report.append("Fundamental Metrics:")
                    
                    valuation = fund_data.get('valuation', {})
                    if valuation.get('forward_pe'):
                        report.append(f"  Forward P/E: {valuation['forward_pe']:.2f}")
                    if valuation.get('peg_ratio'):
                        peg = valuation['peg_ratio']
                        report.append(f"  PEG Ratio: {peg:.2f}")
                        if peg < 1:
                            report.append("    Status: Potentially undervalued")
                        elif peg > 2:
                            report.append("    ⚠️  Status: Potentially overvalued")
                    
                    if valuation.get('ev_to_ebitda'):
                        report.append(f"  EV/EBITDA: {valuation['ev_to_ebitda']:.2f}")
                    
                    profitability = fund_data.get('profitability', {})
                    if profitability.get('gross_margin'):
                        report.append(f"  Gross Margin: {profitability['gross_margin']*100:.1f}%")
                    if profitability.get('roe'):
                        report.append(f"  ROE: {profitability['roe']*100:.1f}%")
                    if profitability.get('roic'):
                        report.append(f"  ROIC: {profitability['roic']:.1f}%")
                    
                    cash_flow = fund_data.get('cash_flow', {})
                    if cash_flow.get('free_cashflow'):
                        fcf_billions = cash_flow['free_cashflow'] / 1e9
                        report.append(f"  Free Cash Flow: ${fcf_billions:.2f}B")
                    if cash_flow.get('fcf_margin'):
                        report.append(f"  FCF Margin: {cash_flow['fcf_margin']:.1f}%")
                    
                    # CapEx Analysis (AI BUBBLE INDICATOR)
                    if cash_flow.get('capex'):
                        capex_billions = cash_flow['capex'] / 1e9
                        report.append(f"  CapEx: ${capex_billions:.2f}B")
                    
                    if cash_flow.get('capex_as_pct_revenue'):
                        report.append(f"  CapEx % Revenue: {cash_flow['capex_as_pct_revenue']:.1f}%")
                    
                    capex_trend = cash_flow.get('capex_trend')
                    if capex_trend:
                        report.append(f"  CapEx Trend: {capex_trend.upper()}")
                        if capex_trend == 'increasing':
                            report.append("    ⚠️  AI BUBBLE WARNING: Increasing CapEx may indicate overinvestment")
                    
                    if cash_flow.get('capex_3yr_cagr'):
                        cagr = cash_flow['capex_3yr_cagr']
                        report.append(f"  CapEx 3Y CAGR: {cagr:+.1f}%")
                        if cagr > 20:
                            report.append("    ⚠️  AI BUBBLE WARNING: Aggressive CapEx growth")
                    
                    financial_health = fund_data.get('financial_health', {})
                    if financial_health.get('debt_to_equity'):
                        report.append(f"  Debt/Equity: {financial_health['debt_to_equity']:.1f}")
                    if financial_health.get('current_ratio'):
                        report.append(f"  Current Ratio: {financial_health['current_ratio']:.2f}")
                    
                    report.append("")
                
                report.append("")
        
        # === SECTION 4: ALL OTHER SYMBOLS ===
        report.append("=" * 80)
        report.append("SECTION 4: OTHER TRACKED SYMBOLS")
        report.append("=" * 80)
        report.append("")
        
        if latest_values:
            other_symbols = [s for s in symbols if 'AI' not in s.get('category', '') 
                           and s['symbol'] not in ['^VIX', 'SPY', 'QQQ', 'NQ=F']]
            
            for symbol_data in other_symbols:
                symbol = symbol_data['symbol']
                report.append(f"{symbol} ({symbol_data.get('category', 'Unknown')}):")
                report.append(f"  Price: ${symbol_data['price']['close']:.2f} | 1D: {symbol_data['performance']['roc_1d']:+.2f}% | RSI: {symbol_data['momentum']['rsi_14']:.1f}")
                
                # ATR-based stops
                current_price = symbol_data['price']['close']
                atr = symbol_data['volatility']['atr_14']
                report.append(f"  Recommended Stop (2x ATR): ${current_price - (atr*2):.2f}")
                
                report.append("")
        
        # === SECTION 5: ACTIVE SIGNALS SUMMARY ===
        report.append("=" * 80)
        report.append("SECTION 5: ACTIVE TRADING SIGNALS")
        report.append("=" * 80)
        report.append("")
        
        signals_file = self.data_dir / "analytics/aggregated/active_signals.json"
        if signals_file.exists():
            with open(signals_file, 'r') as f:
                signals_data = json.load(f)
            
            if signals_data.get('golden_crosses'):
                report.append("Golden Crosses (Bullish):")
                for signal in signals_data['golden_crosses']:
                    report.append(f"  - {signal['symbol']}")
                report.append("")
            
            if signals_data.get('death_crosses'):
                report.append("Death Crosses (Bearish):")
                for signal in signals_data['death_crosses']:
                    report.append(f"  - {signal['symbol']}")
                report.append("")
            
            if signals_data.get('rsi_overbought'):
                report.append("RSI Overbought (>70 - Potential Correction):")
                for signal in signals_data['rsi_overbought']:
                    report.append(f"  - {signal['symbol']}: RSI {signal['rsi']:.1f}")
                report.append("")
            
            if signals_data.get('rsi_oversold'):
                report.append("RSI Oversold (<30 - Potential Bounce):")
                for signal in signals_data['rsi_oversold']:
                    report.append(f"  - {signal['symbol']}: RSI {signal['rsi']:.1f}")
                report.append("")
        
        # === FOOTER ===
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        report.append("")
        report.append("INSTRUCTIONS FOR AI ANALYSIS:")
        report.append("-" * 80)
        report.append("Based on the above data, please provide:")
        report.append("1. BUY recommendations with reasoning and target entry prices")
        report.append("2. SELL recommendations with reasoning")
        report.append("3. HOLD recommendations with monitoring criteria")
        report.append("4. Specific stop loss levels for each position")
        report.append("5. Overall market risk assessment")
        report.append("6. AI bubble risk level (1-10 scale)")
        report.append("7. Recession probability based on macro indicators")
        report.append("")
        
        return "\n".join(report)
    
    def export_to_file(self, filename: str = None) -> Path:
        """
        Export report to text file.
        
        Args:
            filename: Optional custom filename
        
        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"market_analysis_report_{timestamp}.txt"
        
        report_text = self.generate_ai_prompt_report()
        
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return file_path


def main():
    """Test function."""
    print("="*70)
    print("📊 GENERATING AI-READY MARKET ANALYSIS REPORT")
    print("="*70)
    
    generator = ExportGenerator()
    
    try:
        output_path = generator.export_to_file()
        print(f"\n✅ Report generated successfully!")
        print(f"📄 File: {output_path}")
        print(f"📏 Size: {output_path.stat().st_size:,} bytes")
        print("\n💡 You can now copy this file and paste it into:")
        print("   - ChatGPT")
        print("   - Claude")
        print("   - Gemini")
        print("   - Any other AI assistant")
        print("\n" + "="*70)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("="*70)


if __name__ == "__main__":
    main()