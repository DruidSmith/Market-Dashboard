# Market Tracking Dashboard - Backend

## Overview
This is a scheduled data-fetching system that runs on GitHub Actions to collect market data from free APIs.

**Current Phase: Phase 1 - Data Collection Layer**

## Project Structure
```
market-dashboard/
├── .github/workflows/    # GitHub Actions automation
├── config/              # Ticker registry and configuration
├── data/                # Stored market data
│   ├── raw/            # Daily price data, volume, etc.
│   └── metadata/       # Update timestamps and status
├── src/                 # Python modules
└── run_fetch.py        # Main execution script
```

## Ticker Registry

The `config/tickers.csv` file defines which symbols to track, organized by category:
- **AI bubble indicators**: NVDA, AMD, INTC, SOXX
- **Market volatility**: VIX, SPY
- **Crypto**: BTC-USD

## Data Storage

Phase 1 uses a simple file-based approach (to be determined in Step 3).

## Local Development

### Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Fetcher Locally
```bash
python run_fetch.py
```

### Check Results
- Raw data: `data/raw/`
- Update status: `data/metadata/update_status.json`

## GitHub Actions

The workflow runs automatically on a schedule. You can also trigger it manually:
1. Go to the "Actions" tab in your GitHub repo
2. Select "Fetch Market Data"
3. Click "Run workflow"

## API Keys

Some APIs require free API keys. Store them as GitHub Secrets:
- `ALPHA_VANTAGE_API_KEY`
- `FINNHUB_API_KEY`

## Roadmap

- **Phase 1** (Current): Data fetching and storage
- **Phase 2**: Calculate technical indicators (RSI, MACD, etc.)
- **Phase 3**: Build dashboard frontend
```

### **.gitignore Content**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Data (we'll commit the structure but not the data files)
data/raw/*
!data/raw/.gitkeep
data/metadata/update_status.json

# API keys and secrets
.env
secrets.txt

# OS
.DS_Store
Thumbs.db