"""
Market data fetcher supporting multiple free APIs.
Phase 1: Alpha Vantage + Yahoo Finance implementation.
"""

import os
import time
import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from src.config_loader import ConfigLoader, TickerConfig
from src.storage import DataStorage


class RateLimitError(Exception):
    """Raised when API rate limit is hit."""
    pass


class AlphaVantageAPI:
    """Fetcher for Alpha Vantage API with multi-asset support."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    RATE_LIMIT_DELAY = 12  # seconds between requests (5 per minute = 12 sec spacing)
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - elapsed
            print(f"  ⏳ Waiting {wait_time:.1f}s for rate limit...")
            time.sleep(wait_time)
    
    def _make_request(self, params: Dict) -> Dict:
        """Make API request with error handling."""
        self._wait_for_rate_limit()
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            self.last_request_time = time.time()
            
            data = response.json()
            
            # Check for errors
            if "Error Message" in data:
                raise Exception(f"API Error: {data['Error Message']}")
            
            if "Note" in data:
                raise RateLimitError(f"Rate limit hit: {data['Note']}")
            
            if "Information" in data:
                raise RateLimitError(f"Rate limit hit: {data['Information']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def fetch_stock_data(self, symbol: str, outputsize: str = "compact") -> List[Dict]:
        """
        Fetch daily time series data for stocks/ETFs.
        
        Args:
            symbol: Ticker symbol (e.g., 'NVDA')
            outputsize: 'compact' (100 days) or 'full' (20+ years)
        
        Returns:
            List of daily data points with date, OHLCV
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key
        }
        
        print(f"  📡 Fetching {symbol} (stock/ETF) from Alpha Vantage...")
        
        data = self._make_request(params)
        time_series = data.get("Time Series (Daily)", {})
        
        if not time_series:
            raise Exception(f"No data returned for {symbol}")
        
        # Convert to our format
        parsed_data = []
        for date_str, values in time_series.items():
            parsed_data.append({
                "date": date_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"])
            })
        
        print(f"  ✓ Fetched {len(parsed_data)} days of data for {symbol}")
        return parsed_data
    
    def fetch_crypto_data(self, symbol: str, market: str = "USD") -> List[Dict]:
        """
        Fetch daily crypto data.
        
        Args:
            symbol: Crypto symbol without market (e.g., 'BTC' from 'BTC-USD')
            market: Market currency (default: 'USD')
        
        Returns:
            List of daily data points
        """
        params = {
            "function": "DIGITAL_CURRENCY_DAILY",
            "symbol": symbol,
            "market": market,
            "apikey": self.api_key
        }
        
        print(f"  📡 Fetching {symbol}-{market} (crypto) from Alpha Vantage...")
        
        data = self._make_request(params)
        time_series = data.get("Time Series (Digital Currency Daily)", {})
        
        if not time_series:
            raise Exception(f"No crypto data returned for {symbol}-{market}")
        
        # Convert to our format
        parsed_data = []
        for date_str, values in time_series.items():
            # Alpha Vantage crypto data has different keys
            parsed_data.append({
                "date": date_str,
                "open": float(values["1a. open (USD)"]),
                "high": float(values["2a. high (USD)"]),
                "low": float(values["3a. low (USD)"]),
                "close": float(values["4a. close (USD)"]),
                "volume": float(values["5. volume"])
            })
        
        print(f"  ✓ Fetched {len(parsed_data)} days of data for {symbol}-{market}")
        return parsed_data
    
    def fetch_data(self, symbol: str, asset_type: str) -> List[Dict]:
        """
        Fetch data based on asset type.
        
        Args:
            symbol: Ticker symbol
            asset_type: 'stock', 'etf', 'crypto', 'index', 'indicator'
        
        Returns:
            List of daily data points
        """
        if asset_type in ['stock', 'etf']:
            return self.fetch_stock_data(symbol)
        
        elif asset_type == 'crypto':
            # Parse crypto symbol (e.g., 'BTC-USD' -> 'BTC', 'USD')
            if '-' in symbol:
                crypto_symbol, market = symbol.split('-', 1)
                return self.fetch_crypto_data(crypto_symbol, market)
            else:
                raise Exception(f"Crypto symbol {symbol} must be in format XXX-YYY (e.g., BTC-USD)")
        
        else:
            raise Exception(f"Asset type {asset_type} not supported by Alpha Vantage")


class YahooFinanceAPI:
    """Fetcher for Yahoo Finance using yfinance library."""
    
    RATE_LIMIT_DELAY = 1  # Yahoo is more lenient, but still be respectful
    
    def __init__(self):
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Ensure we don't hammer Yahoo Finance."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - elapsed
            time.sleep(wait_time)
    
    def fetch_data(self, symbol: str, period: str = "3mo") -> List[Dict]:
        """
        Fetch daily data from Yahoo Finance.
        
        Args:
            symbol: Ticker symbol (e.g., '^VIX', 'SPY')
            period: Period to fetch ('1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
        
        Returns:
            List of daily data points with date, OHLCV
        """
        self._wait_for_rate_limit()
        
        print(f"  📡 Fetching {symbol} from Yahoo Finance...")
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                raise Exception(f"No data returned from Yahoo Finance for {symbol}")
            
            self.last_request_time = time.time()
            
            # Convert to our format
            parsed_data = []
            for date, row in hist.iterrows():
                parsed_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']) if row['Volume'] > 0 else 0
                })
            
            # Sort by date descending (newest first)
            parsed_data.sort(key=lambda x: x['date'], reverse=True)
            
            print(f"  ✓ Fetched {len(parsed_data)} days of data for {symbol}")
            return parsed_data
            
        except Exception as e:
            raise Exception(f"Yahoo Finance error for {symbol}: {str(e)}")


class MarketDataFetcher:
    """Main fetcher orchestrator with smart resume logic."""
    
    def __init__(self, config_path: str = "config/tickers.csv"):
        self.config_loader = ConfigLoader(config_path)
        self.storage = DataStorage()
        
        # Load API keys from environment
        load_dotenv()
        alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        
        # Alpha Vantage is optional if all symbols use Yahoo Finance
        if alpha_vantage_key:
            self.alpha_vantage = AlphaVantageAPI(alpha_vantage_key)
        else:
            self.alpha_vantage = None
            print("⚠️  No ALPHA_VANTAGE_API_KEY found - only Yahoo Finance will be used")
        
        # Yahoo Finance doesn't need an API key
        self.yahoo_finance = YahooFinanceAPI()
    
    def _get_symbol_priority(self, ticker: TickerConfig) -> Tuple[int, datetime]:
        """
        Calculate priority for fetching a symbol.
        Returns (priority_level, last_updated_time).
        
        Priority levels:
        0 = Never fetched (highest priority)
        1 = Failed last time
        2 = Normal (by staleness)
        """
        metadata = self.storage.get_metadata()
        symbol_meta = metadata.get(ticker.symbol)
        
        if not symbol_meta:
            # Never fetched - highest priority
            return (0, datetime.min)
        
        last_updated_str = symbol_meta.get("last_updated")
        last_status = symbol_meta.get("last_fetch_status", "")
        
        # Parse last updated time
        if last_updated_str:
            # Remove 'Z' and parse
            last_updated = datetime.fromisoformat(last_updated_str.replace('Z', ''))
        else:
            last_updated = datetime.min
        
        # Failed symbols get medium-high priority
        if "failed" in last_status.lower():
            return (1, last_updated)
        
        # Normal priority based on staleness
        return (2, last_updated)
    
    def _get_prioritized_tickers(self, tickers: List[TickerConfig]) -> List[TickerConfig]:
        """
        Sort tickers by priority (never fetched first, then oldest first).
        """
        # Calculate priorities
        ticker_priorities = []
        for ticker in tickers:
            priority_level, last_updated = self._get_symbol_priority(ticker)
            ticker_priorities.append((ticker, priority_level, last_updated))
        
        # Sort by priority level (ascending), then by last_updated (ascending = oldest first)
        ticker_priorities.sort(key=lambda x: (x[1], x[2]))
        
        return [t[0] for t in ticker_priorities]
    
    def fetch_symbol(self, ticker: TickerConfig) -> bool:
        """Fetch data for a single symbol."""
        # Get last update info
        metadata = self.storage.get_metadata()
        symbol_meta = metadata.get(ticker.symbol)
        
        if symbol_meta:
            last_updated_str = symbol_meta.get("last_updated", "never")
            last_status = symbol_meta.get("last_fetch_status", "unknown")
            print(f"\n📊 Processing {ticker.symbol} ({ticker.category})")
            print(f"  📅 Last updated: {last_updated_str}")
            print(f"  📝 Last status: {last_status}")
        else:
            print(f"\n📊 Processing {ticker.symbol} ({ticker.category}) [FIRST TIME]")
        
        try:
            # Route to appropriate API
            if ticker.api_source == "yahoo_finance":
                data = self.yahoo_finance.fetch_data(ticker.symbol)
            elif ticker.api_source == "alpha_vantage":
                if not self.alpha_vantage:
                    raise Exception("Alpha Vantage API key not configured")
                data = self.alpha_vantage.fetch_data(ticker.symbol, ticker.type)
            else:
                print(f"  ⚠️  Unknown API source: {ticker.api_source}")
                return False
            
            # Save to storage
            self.storage.save_symbol_data(
                symbol=ticker.symbol,
                symbol_type=ticker.type,
                category=ticker.category,
                api_source=ticker.api_source,
                data=data
            )
            
            print(f"  ✅ Successfully saved {ticker.symbol}")
            return True
            
        except RateLimitError as e:
            print(f"  🛑 Rate limit hit for {ticker.symbol}: {e}")
            self.storage.mark_symbol_failed(ticker.symbol, "rate_limit")
            raise
            
        except Exception as e:
            print(f"  ❌ Error fetching {ticker.symbol}: {e}")
            self.storage.mark_symbol_failed(ticker.symbol, str(e))
            return False
    
    def fetch_batch(self, max_symbols: int = 5):
        """
        Fetch data for a batch of symbols, prioritizing stale data.
        
        Args:
            max_symbols: Maximum number of symbols to fetch in this run
        """
        tickers = self.config_loader.load_tickers()
        
        print(f"🚀 Starting fetch for up to {max_symbols} symbols (total enabled: {len(tickers)})...")
        
        # Prioritize tickers
        prioritized = self._get_prioritized_tickers(tickers)
        batch = prioritized[:max_symbols]
        
        print(f"\n📋 Batch order (by priority):")
        for i, ticker in enumerate(batch, 1):
            priority_level, last_updated = self._get_symbol_priority(ticker)
            priority_names = {0: "NEVER FETCHED", 1: "FAILED", 2: "STALE"}
            print(f"  {i}. {ticker.symbol} ({ticker.type}) [{ticker.api_source}] - {priority_names.get(priority_level, 'NORMAL')}")
        
        successful = 0
        failed = 0
        rate_limited = False
        
        for ticker in batch:
            try:
                if self.fetch_symbol(ticker):
                    successful += 1
                else:
                    failed += 1
            except RateLimitError:
                rate_limited = True
                print("\n⚠️  Rate limit reached. Stopping for now.")
                print("💡 Next run will resume with remaining symbols.")
                break
        
        # Summary
        print("\n" + "="*60)
        print("📈 Fetch Summary:")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📊 Remaining in queue: {len(tickers) - (successful + failed)}")
        if rate_limited:
            print(f"  🛑 Stopped due to rate limit")
        print("="*60)
        
        # Show what needs updating
        self._print_status_overview()
    
    def _print_status_overview(self):
        """Print overview of all symbols and their update status."""
        tickers = self.config_loader.load_tickers()
        metadata = self.storage.get_metadata()
        
        print("\n📊 Overall Status:")
        
        never_fetched = []
        failed = []
        stale = []
        fresh = []
        
        now = datetime.utcnow()
        
        for ticker in tickers:
            symbol_meta = metadata.get(ticker.symbol)
            
            if not symbol_meta:
                never_fetched.append(ticker.symbol)
            else:
                last_status = symbol_meta.get("last_fetch_status", "")
                last_updated_str = symbol_meta.get("last_updated")
                
                if "failed" in last_status.lower() or "rate_limit" in last_status.lower():
                    failed.append(f"{ticker.symbol} ({last_status})")
                elif last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str.replace('Z', ''))
                    age_hours = (now - last_updated).total_seconds() / 3600
                    
                    if age_hours > 24:
                        stale.append(f"{ticker.symbol} ({age_hours:.0f}h old)")
                    else:
                        fresh.append(f"{ticker.symbol} ({age_hours:.0f}h old)")
        
        if never_fetched:
            print(f"  🆕 Never fetched ({len(never_fetched)}): {', '.join(never_fetched)}")
        if failed:
            print(f"  ❌ Failed/Rate Limited ({len(failed)}): {', '.join(failed[:5])}")  # Show first 5
        if stale:
            print(f"  ⏰ Stale >24h ({len(stale)}): {', '.join(stale[:5])}")
        if fresh:
            print(f"  ✅ Fresh <24h ({len(fresh)}): {', '.join(fresh[:5])}")