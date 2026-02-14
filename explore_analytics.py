"""
Quick script to explore calculated analytics.
"""

import json
from pathlib import Path

def explore_symbol(symbol: str):
    """Display latest indicators for a symbol."""
    # Sanitize symbol for filename
    safe_symbol = symbol.replace("-", "_").replace("^", "")
    file_path = Path(f"data/analytics/technical/{safe_symbol}.json")
    
    if not file_path.exists():
        print(f"❌ No analytics found for {symbol}")
        return
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Get the most recent data point
    latest = data['data'][-1]
    
    print(f"\n{'='*60}")
    print(f"📊 {symbol} - Latest Technical Indicators")
    print(f"{'='*60}")
    print(f"Date: {latest['date']}")
    print(f"\n💰 Price:")
    print(f"  Close: ${latest['close']:.2f}")
    print(f"  20-day SMA: ${latest.get('sma_20', 0):.2f}")
    print(f"  50-day SMA: ${latest.get('sma_50', 0):.2f}")
    print(f"  200-day SMA: ${latest.get('sma_200', 0):.2f}")
    
    print(f"\n📈 Momentum:")
    print(f"  RSI(14): {latest.get('rsi_14', 0):.2f}")
    print(f"  MACD: {latest.get('macd', 0):.4f}")
    print(f"  MACD Signal: {latest.get('macd_signal', 0):.4f}")
    
    print(f"\n📊 Volatility:")
    print(f"  ATR(14): ${latest.get('atr_14', 0):.2f}")
    print(f"  20-day Volatility: {latest.get('volatility_20d', 0):.2f}%")
    
    print(f"\n🎯 Signals:")
    print(f"  Price above SMA(20): {latest.get('price_above_sma_20', False)}")
    print(f"  Price above SMA(50): {latest.get('price_above_sma_50', False)}")
    print(f"  Price above SMA(200): {latest.get('price_above_sma_200', False)}")
    print(f"  RSI Overbought (>70): {latest.get('rsi_overbought', False)}")
    print(f"  RSI Oversold (<30): {latest.get('rsi_oversold', False)}")
    
    print(f"\n📉 Recent Performance:")
    print(f"  1-day change: {latest.get('roc_1d', 0):.2f}%")
    print(f"  5-day change: {latest.get('roc_5d', 0):.2f}%")
    print(f"  20-day change: {latest.get('roc_20d', 0):.2f}%")

if __name__ == "__main__":
    # Explore a few symbols
    symbols = ["NVDA", "AMD", "BTC-USD", "^VIX"]
    
    for symbol in symbols:
        explore_symbol(symbol)
    
    print(f"\n{'='*60}")
    print("✅ Exploration complete!")