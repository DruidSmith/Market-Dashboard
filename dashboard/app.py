"""
Market Health Dashboard - Enhanced with Early Warning System
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import re

# Page config
st.set_page_config(
    page_title="Market Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better styling
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #0e1117;
    }
    
    /* Indicator badges */
    .indicator-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 10px 0;
    }
    .indicator-badge {
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    .indicator-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Status colors */
    .bullish {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border: 2px solid #28a745;
    }
    .bearish {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border: 2px solid #dc3545;
    }
    .neutral {
        background: linear-gradient(135deg, #e2e3e5 0%, #d6d8db 100%);
        color: #383d41;
        border: 2px solid #6c757d;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e2530 0%, #2d3748 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #4a5568;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .good-metric {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 6px solid #28a745;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(40,167,69,0.2);
    }
    .warning-metric {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 6px solid #ffc107;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(255,193,7,0.2);
    }
    .bad-metric {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 6px solid #dc3545;
        padding: 16px;
        border-radius: 8px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(220,53,69,0.2);
    }
    
    /* Alert box */
    .alert-critical {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        margin: 20px 0;
        border: 3px solid #bd2130;
        box-shadow: 0 4px 12px rgba(220,53,69,0.4);
    }
    .alert-warning {
        background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
        color: #212529;
        padding: 20px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        margin: 20px 0;
        border: 3px solid #d39e00;
        box-shadow: 0 4px 12px rgba(255,193,7,0.4);
    }
    .alert-normal {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        margin: 20px 0;
        border: 3px solid #1e7e34;
        box-shadow: 0 4px 12px rgba(40,167,69,0.4);
    }
    
    /* Signal indicators */
    .signal-bull {
        color: #28a745;
        font-weight: bold;
    }
    .signal-bear {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Dividers */
    hr {
        margin: 30px 0;
        border: none;
        border-top: 2px solid #4a5568;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_latest_values():
    """Load the latest values aggregate."""
    file_path = Path("data/analytics/aggregated/latest_values.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


@st.cache_data(ttl=300)
def load_performance_rankings():
    """Load performance rankings."""
    file_path = Path("data/analytics/aggregated/performance_rankings.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


@st.cache_data(ttl=300)
def load_active_signals():
    """Load active trading signals."""
    file_path = Path("data/analytics/aggregated/active_signals.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


@st.cache_data(ttl=300)
def load_category_summary():
    """Load category-based summary."""
    file_path = Path("data/analytics/aggregated/by_category.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


@st.cache_data(ttl=300)
def load_market_health():
    """Load market health assessment."""
    file_path = Path("data/analytics/market_health/market_health.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


def load_symbol_technical(symbol):
    """Load full technical data for a symbol."""
    safe_symbol = symbol.replace("-", "_").replace("^", "")
    file_path = Path(f"data/analytics/technical/{safe_symbol}.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


def load_symbol_fundamentals(symbol):
    """Load fundamental data for a symbol."""
    safe_symbol = symbol.replace("-", "_").replace("^", "")
    file_path = Path(f"data/analytics/fundamentals/{safe_symbol}.json")
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


def get_health_color(rsi, volatility):
    """Determine health color based on indicators."""
    if rsi and rsi > 70:
        return "🔴", "Overbought", "bad-metric"
    elif rsi and rsi < 30:
        return "🟡", "Oversold", "warning-metric"
    elif volatility and volatility > 3:
        return "🟡", "High Volatility", "warning-metric"
    else:
        return "🟢", "Healthy", "good-metric"


def parse_cron_from_workflow(workflow_path: Path) -> str:
    """Parse the cron schedule from a GitHub Actions workflow YAML file."""
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
            
            # Try to parse as YAML first
            try:
                workflow = yaml.safe_load(content)
                if 'on' in workflow and 'schedule' in workflow['on']:
                    schedules = workflow['on']['schedule']
                    if schedules and len(schedules) > 0:
                        return schedules[0].get('cron')
            except:
                pass
            
            # Fallback: regex search for cron pattern
            cron_pattern = r"cron:\s*['\"]([^'\"]+)['\"]"
            match = re.search(cron_pattern, content)
            if match:
                return match.group(1)
            
        return None
    except Exception as e:
        print(f"Error parsing workflow: {e}")
        return None


def get_cron_description(cron_expr: str) -> str:
    """Convert cron expression to human-readable description."""
    parts = cron_expr.split()
    if len(parts) != 5:
        return "Custom schedule"
    
    minute, hour, day, month, day_of_week = parts
    
    # Every N minutes
    if minute.startswith('*/'):
        interval = int(minute[2:])
        return f"Every {interval} minutes"
    
    # Every N hours
    if hour.startswith('*/'):
        interval = int(hour[2:])
        return f"Every {interval} hours"
    
    # Every hour
    if minute == '0' and hour == '*':
        return "Every hour"
    
    # Daily at specific time
    if minute.isdigit() and hour.isdigit():
        return f"Daily at {hour.zfill(2)}:{minute.zfill(2)} UTC"
    
    return "Custom schedule"


def calculate_next_cron_run(cron_schedule: str) -> datetime:
    """Calculate next run time based on cron schedule."""
    if not cron_schedule:
        return None
    
    parts = cron_schedule.split()
    
    if len(parts) != 5:
        return None
    
    minute, hour, day, month, day_of_week = parts
    
    now = datetime.utcnow()
    
    # Handle */N pattern for minutes
    if minute.startswith('*/'):
        interval = int(minute[2:])
        current_minute = now.minute
        next_minute = ((current_minute // interval) + 1) * interval
        
        if next_minute >= 60:
            next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        else:
            next_run = now.replace(minute=next_minute, second=0, microsecond=0)
        
        return next_run
    
    # Handle */N pattern for hours
    if hour.startswith('*/'):
        interval = int(hour[2:])
        current_hour = now.hour
        next_hour = ((current_hour // interval) + 1) * interval
        
        if next_hour >= 24:
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            next_run = now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        
        return next_run
    
    # Handle * pattern (every hour)
    if hour == '*' and minute == '0':
        next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        return next_run
    
    # Handle specific time
    if minute.isdigit() and hour.isdigit():
        target_hour = int(hour)
        target_minute = int(minute)
        
        next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return next_run
    
    return None


def display_comprehensive_indicators(symbol):
    """Display all indicators for a symbol in a formatted way."""
    tech_data = load_symbol_technical(symbol)
    fund_data = load_symbol_fundamentals(symbol)
    
    if not tech_data:
        st.warning(f"No technical data for {symbol}")
        return
    
    # Get latest data point
    latest = tech_data['data'][-1]
    
    # === PERFORMANCE SECTION ===
    st.markdown("### 📈 Performance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        roc_20d = latest.get('roc_20d', 0)
        st.metric("1 Month", f"{roc_20d:.2f}%", 
                 delta=None,
                 delta_color="normal" if roc_20d >= 0 else "inverse")
    
    with col2:
        # Approximate 3 months (60 days)
        if len(tech_data['data']) > 60:
            price_60d_ago = tech_data['data'][-60]['close']
            price_now = latest['close']
            roc_60d = ((price_now - price_60d_ago) / price_60d_ago) * 100
            st.metric("3 Months", f"{roc_60d:.2f}%",
                     delta=None,
                     delta_color="normal" if roc_60d >= 0 else "inverse")
        else:
            st.metric("3 Months", "N/A")
    
    with col3:
        # 1 year if available
        if len(tech_data['data']) > 250:
            price_1y_ago = tech_data['data'][-250]['close']
            price_now = latest['close']
            roc_1y = ((price_now - price_1y_ago) / price_1y_ago) * 100
            st.metric("1 Year", f"{roc_1y:.2f}%",
                     delta=None,
                     delta_color="normal" if roc_1y >= 0 else "inverse")
        else:
            st.metric("1 Year", "N/A")
    
    st.divider()
    
    # === TECHNICAL INDICATORS ===
    st.markdown("### 🔧 Technical Indicators")
    
    indicators_html = '<div class="indicator-row">'
    
    # RSI
    rsi = latest.get('rsi_14')
    if rsi:
        if rsi > 70:
            rsi_badge = f'<span class="indicator-badge bearish">RSI: {rsi:.1f} (Overbought 📉 BEARISH)</span>'
        elif rsi < 30:
            rsi_badge = f'<span class="indicator-badge bullish">RSI: {rsi:.1f} (Oversold 📈 BULLISH)</span>'
        else:
            rsi_badge = f'<span class="indicator-badge neutral">RSI: {rsi:.1f} (Neutral ↔)</span>'
        indicators_html += rsi_badge
    
    # SMA Cross
    sma_position = latest.get('sma_position', 'neutral')
    if sma_position == 'golden':
        sma_badge = '<span class="indicator-badge bullish">SMA: Golden Cross 📈 BULLISH</span>'
    elif sma_position == 'death':
        sma_badge = '<span class="indicator-badge bearish">SMA: Death Cross 📉 BEARISH</span>'
    else:
        sma_badge = '<span class="indicator-badge neutral">SMA: Neutral ↔</span>'
    indicators_html += sma_badge
    
    # EMA Trend
    ema_trend = latest.get('ema_trend', 'neutral')
    if ema_trend == 'bullish':
        ema_badge = '<span class="indicator-badge bullish">EMA: Bullish 📈</span>'
    elif ema_trend == 'bearish':
        ema_badge = '<span class="indicator-badge bearish">EMA: Bearish 📉</span>'
    else:
        ema_badge = '<span class="indicator-badge neutral">EMA: Neutral ↔</span>'
    indicators_html += ema_badge
    
    # MACD
    macd = latest.get('macd')
    macd_signal = latest.get('macd_signal')
    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            macd_badge = '<span class="indicator-badge bullish">MACD: Bullish 📈</span>'
        else:
            macd_badge = '<span class="indicator-badge bearish">MACD: Bearish 📉</span>'
        indicators_html += macd_badge
    
    indicators_html += '</div>'
    st.markdown(indicators_html, unsafe_allow_html=True)
    
    st.divider()
    
    # === FUNDAMENTALS ===
    if fund_data:
        st.markdown("### 💼 Fundamental Analysis")
        
        # Valuation Metrics
        st.markdown("#### 📊 Valuation")
        valuation = fund_data.get('valuation', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fwd_pe = valuation.get('forward_pe')
            if fwd_pe:
                st.metric("Forward PE", f"{fwd_pe:.2f}")
            else:
                st.metric("Forward PE", "N/A")
        
        with col2:
            trail_pe = valuation.get('trailing_pe')
            if trail_pe:
                st.metric("Trailing PE", f"{trail_pe:.2f}")
            else:
                st.metric("Trailing PE", "N/A")
        
        with col3:
            peg = valuation.get('peg_ratio')
            if peg:
                if peg < 1:
                    st.metric("PEG Ratio", f"{peg:.2f}", delta="Undervalued 📈", delta_color="normal")
                elif peg > 2:
                    st.metric("PEG Ratio", f"{peg:.2f}", delta="Overvalued 📉", delta_color="inverse")
                else:
                    st.metric("PEG Ratio", f"{peg:.2f}")
            else:
                st.metric("PEG Ratio", "N/A")
        
        with col4:
            ev_ebitda = valuation.get('ev_to_ebitda')
            if ev_ebitda:
                st.metric("EV/EBITDA", f"{ev_ebitda:.2f}")
            else:
                st.metric("EV/EBITDA", "N/A")
        
        st.divider()
        
        # Profitability Metrics
        st.markdown("#### 💰 Profitability")
        profitability = fund_data.get('profitability', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            gross_margin = profitability.get('gross_margin')
            if gross_margin:
                st.metric("Gross Margin", f"{gross_margin * 100:.1f}%")
            else:
                st.metric("Gross Margin", "N/A")
        
        with col2:
            profit_margin = profitability.get('profit_margin')
            if profit_margin:
                st.metric("Profit Margin", f"{profit_margin * 100:.1f}%")
            else:
                st.metric("Profit Margin", "N/A")
        
        with col3:
            roe = profitability.get('roe')
            if roe:
                roe_pct = roe * 100
                if roe_pct > 15:
                    st.metric("ROE", f"{roe_pct:.1f}%", delta="Strong 📈", delta_color="normal")
                elif roe_pct < 5:
                    st.metric("ROE", f"{roe_pct:.1f}%", delta="Weak 📉", delta_color="inverse")
                else:
                    st.metric("ROE", f"{roe_pct:.1f}%")
            else:
                st.metric("ROE", "N/A")
        
        with col4:
            roic = profitability.get('roic')
            if roic:
                if roic > 15:
                    st.metric("ROIC", f"{roic:.1f}%", delta="Strong 📈", delta_color="normal")
                elif roic < 5:
                    st.metric("ROIC", f"{roic:.1f}%", delta="Weak 📉", delta_color="inverse")
                else:
                    st.metric("ROIC", f"{roic:.1f}%")
            else:
                st.metric("ROIC", "N/A")
        
        st.divider()
        
        # Cash Flow & CapEx
        st.markdown("#### 💵 Cash Flow & Capital Expenditure")
        cash_flow = fund_data.get('cash_flow', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fcf = cash_flow.get('free_cashflow')
            if fcf:
                fcf_billions = fcf / 1e9
                st.metric("Free Cash Flow", f"${fcf_billions:.2f}B")
            else:
                st.metric("Free Cash Flow", "N/A")
        
        with col2:
            fcf_margin = cash_flow.get('fcf_margin')
            if fcf_margin:
                st.metric("FCF Margin", f"{fcf_margin:.1f}%")
            else:
                st.metric("FCF Margin", "N/A")
        
        with col3:
            capex = cash_flow.get('capex')
            if capex:
                capex_billions = capex / 1e9
                st.metric("CapEx", f"${capex_billions:.2f}B")
            else:
                st.metric("CapEx", "N/A")
        
        with col4:
            capex_pct = cash_flow.get('capex_as_pct_revenue')
            if capex_pct:
                st.metric("CapEx % Revenue", f"{capex_pct:.1f}%")
            else:
                st.metric("CapEx % Revenue", "N/A")
        
        # CapEx Trend Indicator
        capex_trend = cash_flow.get('capex_trend')
        capex_cagr = cash_flow.get('capex_3yr_cagr')
        
        if capex_trend or capex_cagr:
            st.markdown("**CapEx Trend:**")
            trend_html = '<div class="indicator-row">'
            
            if capex_trend == 'increasing':
                trend_html += '<span class="indicator-badge bearish">📈 Increasing CapEx (AI bubble concern) 📉 BEARISH</span>'
            elif capex_trend == 'decreasing':
                trend_html += '<span class="indicator-badge bullish">📉 Decreasing CapEx (positive signal) 📈 BULLISH</span>'
            else:
                trend_html += '<span class="indicator-badge neutral">➡️ Stable CapEx</span>'
            
            if capex_cagr:
                if capex_cagr > 20:
                    trend_html += f'<span class="indicator-badge bearish">3Y CAGR: +{capex_cagr:.1f}% 📉 BEARISH</span>'
                elif capex_cagr < -10:
                    trend_html += f'<span class="indicator-badge bullish">3Y CAGR: {capex_cagr:.1f}% 📈 BULLISH</span>'
                else:
                    trend_html += f'<span class="indicator-badge neutral">3Y CAGR: {capex_cagr:.1f}%</span>'
            
            trend_html += '</div>'
            st.markdown(trend_html, unsafe_allow_html=True)
        
        st.divider()
        
        # Financial Health
        st.markdown("#### 🏥 Financial Health")
        financial_health = fund_data.get('financial_health', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            debt_to_equity = financial_health.get('debt_to_equity')
            if debt_to_equity:
                if debt_to_equity < 50:
                    st.metric("Debt/Equity", f"{debt_to_equity:.1f}", delta="Low 📈", delta_color="normal")
                elif debt_to_equity > 150:
                    st.metric("Debt/Equity", f"{debt_to_equity:.1f}", delta="High 📉", delta_color="inverse")
                else:
                    st.metric("Debt/Equity", f"{debt_to_equity:.1f}")
            else:
                st.metric("Debt/Equity", "N/A")
        
        with col2:
            current_ratio = financial_health.get('current_ratio')
            if current_ratio:
                if current_ratio > 2:
                    st.metric("Current Ratio", f"{current_ratio:.2f}", delta="Strong 📈", delta_color="normal")
                elif current_ratio < 1:
                    st.metric("Current Ratio", f"{current_ratio:.2f}", delta="Weak 📉", delta_color="inverse")
                else:
                    st.metric("Current Ratio", f"{current_ratio:.2f}")
            else:
                st.metric("Current Ratio", "N/A")
        
        with col3:
            interest_coverage = financial_health.get('interest_coverage')
            if interest_coverage:
                if interest_coverage > 5:
                    st.metric("Interest Coverage", f"{interest_coverage:.1f}x", delta="Safe 📈", delta_color="normal")
                elif interest_coverage < 2:
                    st.metric("Interest Coverage", f"{interest_coverage:.1f}x", delta="Risk 📉", delta_color="inverse")
                else:
                    st.metric("Interest Coverage", f"{interest_coverage:.1f}x")
            else:
                st.metric("Interest Coverage", "N/A")
        
        with col4:
            total_cash = financial_health.get('total_cash')
            if total_cash:
                cash_billions = total_cash / 1e9
                st.metric("Total Cash", f"${cash_billions:.2f}B")
            else:
                st.metric("Total Cash", "N/A")
        
        st.divider()
        
        # Growth Metrics
        st.markdown("#### 📈 Growth")
        growth = fund_data.get('growth', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue_growth = growth.get('revenue_growth')
            if revenue_growth:
                st.metric("Revenue Growth", f"{revenue_growth * 100:.1f}%")
            else:
                st.metric("Revenue Growth", "N/A")
        
        with col2:
            earnings_growth = growth.get('earnings_growth')
            if earnings_growth:
                st.metric("Earnings Growth", f"{earnings_growth * 100:.1f}%")
            else:
                st.metric("Earnings Growth", "N/A")
        
        with col3:
            qtr_growth = growth.get('earnings_quarterly_growth')
            if qtr_growth:
                st.metric("Quarterly Growth", f"{qtr_growth * 100:.1f}%")
            else:
                st.metric("Quarterly Growth", "N/A")


def create_price_chart(symbol_data):
    """Create comprehensive price chart."""
    df = pd.DataFrame(symbol_data['data'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.tail(60)  # Last 60 days
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=('Price & Moving Averages', 'RSI', 'MACD')
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # SMAs
    if 'sma_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['sma_20'], name='SMA 20', 
                      line=dict(color='blue', width=1)),
            row=1, col=1
        )
    if 'sma_50' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['sma_50'], name='SMA 50',
                      line=dict(color='orange', width=1)),
            row=1, col=1
        )
    if 'sma_200' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['sma_200'], name='SMA 200',
                      line=dict(color='red', width=1)),
            row=1, col=1
        )
    
    # RSI
    if 'rsi_14' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['rsi_14'], name='RSI',
                      line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    if 'macd' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['macd'], name='MACD',
                      line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['macd_signal'], name='Signal',
                      line=dict(color='red')),
            row=3, col=1
        )
        if 'macd_histogram' in df.columns:
            fig.add_trace(
                go.Bar(x=df['date'], y=df['macd_histogram'], name='Histogram',
                      marker_color='gray'),
                row=3, col=1
            )
    
    fig.update_layout(
        title=f"{symbol_data['symbol']} - Technical Analysis",
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        template="plotly_dark"
    )
    
    return fig


def filter_symbols_by_signals(symbols_list, filter_options):
    """Filter symbols based on selected signal criteria."""
    if not filter_options or "All Symbols" in filter_options:
        return symbols_list
    
    filtered = []
    
    for symbol in symbols_list:
        signals = symbol.get('signals', {})
        
        # Check each filter
        matches = False
        
        if "Golden Cross" in filter_options and signals.get('golden_cross'):
            matches = True
        if "Death Cross" in filter_options and signals.get('death_cross'):
            matches = True
        if "RSI Overbought (>70)" in filter_options and signals.get('rsi_overbought'):
            matches = True
        if "RSI Oversold (<30)" in filter_options and signals.get('rsi_oversold'):
            matches = True
        if "MACD Bullish Cross" in filter_options and signals.get('macd_bullish_cross'):
            matches = True
        if "MACD Bearish Cross" in filter_options and signals.get('macd_bearish_cross'):
            matches = True
        if "High Volatility" in filter_options and signals.get('high_volatility'):
            matches = True
        if "Low Volatility" in filter_options and signals.get('low_volatility'):
            matches = True
        if "Above SMA 200" in filter_options and signals.get('price_above_sma_200'):
            matches = True
        if "Below SMA 200" in filter_options and not signals.get('price_above_sma_200'):
            matches = True
        
        if matches:
            filtered.append(symbol)
    
    return filtered


# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    st.title("📊 Market Health Dashboard")
    st.caption("Early Warning System for Market Turning Points")
    
    # Load data
    latest_values = load_latest_values()
    rankings = load_performance_rankings()
    signals = load_active_signals()
    categories = load_category_summary()
    market_health = load_market_health()
    
    # Load cron schedules from actual workflow files
    fetch_workflow_path = Path(".github/workflows/fetch-data.yml")
    analytics_workflow_path = Path(".github/workflows/calculate-analytics.yml")
    
    fetch_cron = parse_cron_from_workflow(fetch_workflow_path) if fetch_workflow_path.exists() else None
    analytics_cron = parse_cron_from_workflow(analytics_workflow_path) if analytics_workflow_path.exists() else None
    
    if not latest_values:
        st.error("⚠️ No data available. Please run: python run_analytics.py")
        return
    
    # === MARKET HEALTH WARNING BANNER ===
    if market_health:
        risk_score = market_health.get('risk_score', 0)
        status = market_health.get('overall_status', 'UNKNOWN')
        recommendation = market_health.get('recommendation', '')
        
        if status == "DANGER":
            st.markdown(f'<div class="alert-critical">🚨 MARKET HEALTH: {status} (Risk: {risk_score}/10)<br>{recommendation}</div>', unsafe_allow_html=True)
        elif status == "WARNING":
            st.markdown(f'<div class="alert-warning">⚠️ MARKET HEALTH: {status} (Risk: {risk_score}/10)<br>{recommendation}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-normal">✅ MARKET HEALTH: {status} (Risk: {risk_score}/10)<br>{recommendation}</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select View",
        ["🏥 Market Health", "🌍 Market Overview", "🤖 AI Bubble Watch", "📈 Individual Symbols", "⚙️ System Status"]
    )
    
    # Data Status in Sidebar
    st.sidebar.divider()
    st.sidebar.subheader("📊 Data Status")
    
    if latest_values:
        generated_time = datetime.fromisoformat(latest_values['generated_at'].replace('Z', ''))
        age = datetime.utcnow() - generated_time
        
        age_minutes = int(age.total_seconds() / 60)
        age_hours = int(age.total_seconds() / 3600)
        
        # Color code based on age
        if age_minutes < 60:
            age_str = f"{age_minutes} min ago"
            status_emoji = "🟢"
            status_text = "Fresh"
        elif age_hours < 3:
            age_str = f"{age_hours}h ago"
            status_emoji = "🟡"
            status_text = "Recent"
        else:
            age_str = f"{age_hours}h ago"
            status_emoji = "🔴"
            status_text = "Stale"
        
        st.sidebar.metric("Last Updated", age_str, delta=f"{status_emoji} {status_text}")
        
        if st.sidebar.button("🔄 Refresh Data", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        st.sidebar.caption("💡 Tip: Run `git pull` first to get latest data")
        
        # Show actual schedule from workflow file
        if fetch_cron:
            schedule_desc = get_cron_description(fetch_cron)
            st.sidebar.caption(f"⚙️ Updates: {schedule_desc}")
        else:
            st.sidebar.caption("⚙️ Auto-updates via GitHub Actions")
    
    # ==============================================================================
    # TAB 0: MARKET HEALTH (NEW)
    # ==============================================================================
    if page == "🏥 Market Health":
        st.header("Market Health - Early Warning System")
        st.markdown("*Monitor critical indicators for market turning points*")
        
        if not market_health:
            st.warning("⚠️ Market health data not available. Run `python run_analytics.py` to generate.")
            return
        
        # Overall Status
        risk_score = market_health.get('risk_score', 0)
        status = market_health.get('overall_status', 'UNKNOWN')
        recommendation = market_health.get('recommendation', '')
        alerts = market_health.get('alerts', [])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Score", f"{risk_score}/10", delta=f"{status}")
        
        with col2:
            if status == "DANGER":
                st.metric("Market Status", "🔴 DANGER", delta="High Risk")
            elif status == "WARNING":
                st.metric("Market Status", "🟡 WARNING", delta="Elevated Risk")
            else:
                st.metric("Market Status", "🟢 NORMAL", delta="Low Risk")
        
        with col3:
            st.metric("Active Alerts", len(alerts))
        
        st.divider()
        
        # Recommendation Box
        if status == "DANGER":
            st.markdown(f'<div class="alert-critical">📋 RECOMMENDATION:<br>{recommendation}</div>', unsafe_allow_html=True)
        elif status == "WARNING":
            st.markdown(f'<div class="alert-warning">📋 RECOMMENDATION:<br>{recommendation}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-normal">📋 RECOMMENDATION:<br>{recommendation}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Individual Indicators
        st.subheader("📊 Critical Market Indicators")
        
        indicators = market_health.get('indicators', {})
        
        # S&P 500 P/E Ratio
        sp500_pe = indicators.get('sp500_pe')
        if sp500_pe:
            st.markdown("### 1. S&P 500 P/E Ratio")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                pe_val = sp500_pe['value']
                st.metric("Current P/E", f"{pe_val:.1f}")
            
            with col2:
                # Create gauge chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = pe_val,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "P/E Ratio (Crash Threshold: 30)"},
                    delta = {'reference': 30},
                    gauge = {
                        'axis': {'range': [None, 40]},
                        'bar': {'color': "darkblue"},
                        'steps' : [
                            {'range': [0, 20], 'color': "lightgreen"},
                            {'range': [20, 25], 'color': "yellow"},
                            {'range': [25, 30], 'color': "orange"},
                            {'range': [30, 40], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 30
                        }
                    }
                ))
                fig.update_layout(height=300, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                st.metric("Threshold", "30.0")
                if sp500_pe['status'] == 'danger':
                    st.error("🔴 CRITICAL")
                elif sp500_pe['status'] == 'warning':
                    st.warning("🟡 WARNING")
                else:
                    st.success("🟢 NORMAL")
            
            if sp500_pe['status'] == 'danger':
                st.markdown(f'<div class="bad-metric">⚠️ {sp500_pe["interpretation"]}<br><strong>Action:</strong> {sp500_pe["signal"]}</div>', unsafe_allow_html=True)
            elif sp500_pe['status'] == 'warning':
                st.markdown(f'<div class="warning-metric">⚠️ {sp500_pe["interpretation"]}<br><strong>Action:</strong> {sp500_pe["signal"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="good-metric">✅ {sp500_pe["interpretation"]}</div>', unsafe_allow_html=True)
            
            st.divider()
        
        # 30-Year Treasury Yield
        treasury_30y = indicators.get('treasury_30y')
        if treasury_30y:
            st.markdown("### 2. 30-Year Treasury Yield")
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                yield_val = treasury_30y['value']
                st.metric("Current Yield", f"{yield_val:.2f}%")
            
            with col2:
                # Create gauge chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = yield_val,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "30Y Yield (Alert Threshold: 4.5%)"},
                    delta = {'reference': 4.5},
                    gauge = {
                        'axis': {'range': [None, 6]},
                        'bar': {'color': "darkblue"},
                        'steps' : [
                            {'range': [0, 3.5], 'color': "lightgreen"},
                            {'range': [3.5, 4.0], 'color': "yellow"},
                            {'range': [4.0, 4.5], 'color': "orange"},
                            {'range': [4.5, 6], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 4.5
                        }
                    }
                ))
                fig.update_layout(height=300, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            
            with col3:
                st.metric("Threshold", "4.5%")
                if treasury_30y['status'] == 'danger':
                    st.error("🔴 CRITICAL")
                elif treasury_30y['status'] == 'warning':
                    st.warning("🟡 WARNING")
                else:
                    st.success("🟢 NORMAL")
            
            if treasury_30y['status'] == 'danger':
                st.markdown(f'<div class="bad-metric">⚠️ {treasury_30y["interpretation"]}<br><strong>Action:</strong> {treasury_30y["signal"]}</div>', unsafe_allow_html=True)
            elif treasury_30y['status'] == 'warning':
                st.markdown(f'<div class="warning-metric">⚠️ {treasury_30y["interpretation"]}<br><strong>Action:</strong> {treasury_30y["signal"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="good-metric">✅ {treasury_30y["interpretation"]}</div>', unsafe_allow_html=True)
            
            st.divider()
        
        # NYSE New Highs (placeholder for future data)
        nyse_highs = indicators.get('nyse_new_highs')
        if nyse_highs:
            st.markdown("### 3. NYSE New Highs (4-Week Moving Total)")
            st.info(nyse_highs['interpretation'])
            st.caption("💡 Consider adding Barchart or Bloomberg API for real-time breadth data")
        
        # Active Alerts Summary
        if alerts:
            st.divider()
            st.subheader("🚨 Active Alerts")
            for alert in alerts:
                if "CRITICAL" in alert:
                    st.error(alert)
                elif "WARNING" in alert:
                    st.warning(alert)
                else:
                    st.info(alert)
    
    # ==============================================================================
    # TAB 1: MARKET OVERVIEW
    # ==============================================================================
    elif page == "🌍 Market Overview":
        st.header("Market Health Overview")
        st.markdown("*Quick snapshot of overall market conditions*")
        
        # Get key market indicators
        vix_data = next((s for s in latest_values['symbols'] if s['symbol'] == '^VIX'), None)
        spy_data = next((s for s in latest_values['symbols'] if s['symbol'] == 'SPY'), None)
        qqq_data = next((s for s in latest_values['symbols'] if s['symbol'] == 'QQQ'), None)
        nq_data = next((s for s in latest_values['symbols'] if s['symbol'] == 'NQ=F'), None)
        
        # VIX Fear Gauge
        st.subheader("📉 VIX Fear Gauge")
        if vix_data:
            vix_close = vix_data['price']['close']
            
            if vix_close < 15:
                vix_status = "🟢 Low Fear - Market Calm"
                vix_class = "good-metric"
                vix_advice = "Markets are stable. Normal trading conditions."
            elif vix_close < 25:
                vix_status = "🟡 Moderate - Normal Volatility"
                vix_class = "warning-metric"
                vix_advice = "Markets showing typical volatility. Stay alert."
            else:
                vix_status = "🔴 High Fear - Elevated Risk"
                vix_class = "bad-metric"
                vix_advice = "⚠️ Markets are stressed. Consider defensive positioning."
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("VIX Level", f"{vix_close:.2f}", 
                         delta=f"{vix_data['performance']['roc_1d']:.2f}%")
            with col2:
                st.markdown(f'<div class="{vix_class}">{vix_status}</div>', unsafe_allow_html=True)
            with col3:
                st.info("VIX < 15 = Calm | 15-25 = Normal | >25 = Fear")
            
            st.caption(f"💡 {vix_advice}")
        
        st.divider()
        
        # Market Indices & Futures
        st.subheader("📊 Major Indices & Futures")
        cols = st.columns(3)
        
        with cols[0]:
            if spy_data:
                st.markdown("### SPY")
                st.caption("S&P 500 ETF")
                st.metric("Price", f"${spy_data['price']['close']:.2f}",
                         delta=f"{spy_data['performance']['roc_1d']:.2f}%")
                
                emoji, status, css_class = get_health_color(
                    spy_data['momentum']['rsi_14'],
                    spy_data['volatility']['volatility_20d']
                )
                st.markdown(f'<div class="{css_class}">{emoji} {status}</div>', unsafe_allow_html=True)
        
        with cols[1]:
            if qqq_data:
                st.markdown("### QQQ")
                st.caption("Nasdaq-100 ETF")
                st.metric("Price", f"${qqq_data['price']['close']:.2f}",
                         delta=f"{qqq_data['performance']['roc_1d']:.2f}%")
                
                emoji, status, css_class = get_health_color(
                    qqq_data['momentum']['rsi_14'],
                    qqq_data['volatility']['volatility_20d']
                )
                st.markdown(f'<div class="{css_class}">{emoji} {status}</div>', unsafe_allow_html=True)
        
        with cols[2]:
            if nq_data:
                st.markdown("### NQ")
                st.caption("Nasdaq-100 Futures")
                st.metric("Price", f"${nq_data['price']['close']:.2f}",
                         delta=f"{nq_data['performance']['roc_1d']:.2f}%")
                
                emoji, status, css_class = get_health_color(
                    nq_data['momentum']['rsi_14'],
                    nq_data['volatility']['volatility_20d']
                )
                st.markdown(f'<div class="{css_class}">{emoji} {status}</div>', unsafe_allow_html=True)
            else:
                st.markdown("### NQ")
                st.caption("Nasdaq-100 Futures")
                st.info("Data not yet available")
        
        # Futures vs ETF comparison (if both available)
        if nq_data and qqq_data:
            st.markdown("##### 📊 Futures vs ETF")
            nq_close = nq_data['price']['close']
            qqq_close = qqq_data['price']['close']
            
            # Normalize for comparison (NQ trades at ~20x QQQ price)
            nq_normalized = nq_close / 20
            spread = ((nq_normalized - qqq_close) / qqq_close) * 100
            
            if abs(spread) < 0.5:
                st.success(f"✅ Futures aligned with ETF (spread: {spread:.2f}%)")
            elif spread > 0.5:
                st.warning(f"⚠️ Futures trading higher - bullish pre-market sentiment (spread: +{spread:.2f}%)")
            else:
                st.error(f"⚠️ Futures trading lower - bearish pre-market sentiment (spread: {spread:.2f}%)")
        
        st.divider()
        
        # Overall Market Sentiment Score
        st.subheader("🎯 Overall Market Sentiment")
        
        sentiment_score = 0
        sentiment_factors = []
        
        # Factor 1: VIX
        if vix_data:
            vix_close = vix_data['price']['close']
            if vix_close < 15:
                sentiment_score += 2
                sentiment_factors.append("✅ Low volatility (VIX < 15)")
            elif vix_close < 25:
                sentiment_score += 0
                sentiment_factors.append("⚠️ Normal volatility (VIX 15-25)")
            else:
                sentiment_score -= 2
                sentiment_factors.append("🔴 High volatility (VIX > 25)")
        
        # Factor 2: SPY trend
        if spy_data:
            if spy_data['signals'].get('price_above_sma_200'):
                sentiment_score += 1
                sentiment_factors.append("✅ SPY above 200-day SMA")
            else:
                sentiment_score -= 1
                sentiment_factors.append("🔴 SPY below 200-day SMA")
        
        # Factor 3: QQQ trend
        if qqq_data:
            if qqq_data['signals'].get('price_above_sma_200'):
                sentiment_score += 1
                sentiment_factors.append("✅ QQQ above 200-day SMA")
            else:
                sentiment_score -= 1
                sentiment_factors.append("🔴 QQQ below 200-day SMA")
        
        # Display sentiment
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if sentiment_score >= 2:
                st.markdown('<div class="good-metric"><h2>🟢 BULLISH</h2><p>Market conditions favorable</p></div>', 
                           unsafe_allow_html=True)
            elif sentiment_score >= 0:
                st.markdown('<div class="warning-metric"><h2>🟡 NEUTRAL</h2><p>Mixed signals, stay cautious</p></div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="bad-metric"><h2>🔴 BEARISH</h2><p>Defensive positioning advised</p></div>', 
                           unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Factors:**")
            for factor in sentiment_factors:
                st.markdown(f"- {factor}")
        
        st.divider()
        
        # Top movers - CHANGED TO 5
        if rankings:
            st.subheader("🔥 Today's Top Movers")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top 5 Gainers (1D)**")
                for item in rankings['top_gainers_1d'][:5]:  # Changed from 3 to 5
                    st.success(f"**{item['symbol']}**: +{item['roc_1d']:.2f}% 📈 BULLISH")
            
            with col2:
                st.markdown("**Top 5 Losers (1D)**")
                for item in rankings['top_losers_1d'][:5]:  # Changed from 3 to 5
                    st.error(f"**{item['symbol']}**: {item['roc_1d']:.2f}% 📉 BEARISH")
        
        st.divider()
        
        # === MACRO ECONOMIC INDICATORS ===
        st.subheader("🏛️ Economic Indicators (FRED)")
        
        # Load FRED data
        fred_path = Path("data/fred/indicators.json")
        if fred_path.exists():
            try:
                with open(fred_path, 'r') as f:
                    fred_data = json.load(f)
                
                indicators = fred_data.get('data', {})
                
                # Key Metrics Row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    treasury_10y = indicators.get('treasury_10y')
                    if treasury_10y:
                        val = treasury_10y['latest_value']
                        change = treasury_10y['changes'].get('1m', 0)
                        st.metric("10Y Treasury", f"{val:.2f}%", 
                                 delta=f"{change:+.2f}% (1M)")
                
                with col2:
                    unemployment = indicators.get('unemployment')
                    if unemployment:
                        val = unemployment['latest_value']
                        change = unemployment['changes'].get('1m', 0)
                        st.metric("Unemployment", f"{val:.1f}%",
                                 delta=f"{change:+.1f}% (1M)",
                                 delta_color="inverse")
                
                with col3:
                    yield_curve = indicators.get('yield_curve_spread')
                    if yield_curve:
                        val = yield_curve['latest_value']
                        if val < 0:
                            st.metric("Yield Curve", f"{val:.2f}%",
                                     delta="⚠️ Inverted 📉 BEARISH",
                                     delta_color="inverse")
                        else:
                            st.metric("Yield Curve", f"{val:.2f}%",
                                     delta="✅ Normal 📈 BULLISH",
                                     delta_color="normal")
                
                with col4:
                    fed_funds = indicators.get('fed_funds_rate')
                    if fed_funds:
                        val = fed_funds['latest_value']
                        change = fed_funds['changes'].get('1m', 0)
                        st.metric("Fed Funds Rate", f"{val:.2f}%",
                                 delta=f"{change:+.2f}% (1M)")
                
                # Yield Curve Chart
                st.markdown("#### 📈 Yield Curve Trend (10Y-2Y Spread)")
                
                treasury_10y_data = indicators.get('treasury_10y', {}).get('data', [])
                treasury_2y_data = indicators.get('treasury_2y', {}).get('data', [])
                
                if treasury_10y_data and treasury_2y_data:
                    # Calculate spread over time
                    df_10y = pd.DataFrame(treasury_10y_data)
                    df_2y = pd.DataFrame(treasury_2y_data)
                    
                    # Merge on date
                    df_spread = pd.merge(df_10y, df_2y, on='date', suffixes=('_10y', '_2y'))
                    df_spread['spread'] = df_spread['value_10y'] - df_spread['value_2y']
                    df_spread['date'] = pd.to_datetime(df_spread['date'])
                    
                    # Last 90 days
                    df_spread = df_spread.tail(90)
                    
                    # Create chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df_spread['date'],
                        y=df_spread['spread'],
                        mode='lines',
                        name='Yield Curve Spread',
                        line=dict(color='#1f77b4', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(31, 119, 180, 0.2)'
                    ))
                    
                    # Add zero line
                    fig.add_hline(y=0, line_dash="dash", line_color="red",
                                 annotation_text="Inversion Line")
                    
                    fig.update_layout(
                        title="Yield Curve Spread - Last 90 Days (Inverted = Recession Risk)",
                        xaxis_title="Date",
                        yaxis_title="Spread (%)",
                        height=300,
                        hovermode='x unified',
                        template="plotly_dark"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Interpretation
                    current_spread = df_spread['spread'].iloc[-1]
                    if current_spread < 0:
                        st.error("🔴 **Yield curve is inverted** - Historically precedes recessions 📉 BEARISH")
                    elif current_spread < 0.5:
                        st.warning("🟡 **Yield curve is flattening** - Monitor for inversion")
                    else:
                        st.success("🟢 **Normal yield curve** - Healthy economic conditions 📈 BULLISH")
                
                # Additional Economic Charts in Tabs
                tab1, tab2, tab3 = st.tabs(["📊 Interest Rates", "💼 Employment", "📈 Inflation"])
                
                with tab1:
                    # Interest Rates Chart
                    st.markdown("##### Treasury Yields")
                    
                    if treasury_10y_data and treasury_2y_data:
                        df_rates = pd.merge(
                            pd.DataFrame(treasury_10y_data).tail(180),
                            pd.DataFrame(treasury_2y_data).tail(180),
                            on='date',
                            suffixes=('_10y', '_2y')
                        )
                        df_rates['date'] = pd.to_datetime(df_rates['date'])
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df_rates['date'],
                            y=df_rates['value_10y'],
                            name='10-Year',
                            line=dict(color='#2ca02c', width=2)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=df_rates['date'],
                            y=df_rates['value_2y'],
                            name='2-Year',
                            line=dict(color='#ff7f0e', width=2)
                        ))
                        
                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Yield (%)",
                            height=300,
                            hovermode='x unified',
                            template="plotly_dark"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Unemployment Chart
                    st.markdown("##### Unemployment Rate")
                    
                    unemployment_data = indicators.get('unemployment', {}).get('data', [])
                    if unemployment_data:
                        df_unemp = pd.DataFrame(unemployment_data).tail(180)
                        df_unemp['date'] = pd.to_datetime(df_unemp['date'])
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df_unemp['date'],
                            y=df_unemp['value'],
                            mode='lines',
                            name='Unemployment Rate',
                            line=dict(color='#d62728', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(214, 39, 40, 0.2)'
                        ))
                        
                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Unemployment Rate (%)",
                            height=300,
                            hovermode='x unified',
                            template="plotly_dark"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    # CPI Chart
                    st.markdown("##### Consumer Price Index (Inflation)")
                    
                    cpi_data = indicators.get('cpi', {}).get('data', [])
                    if cpi_data:
                        df_cpi = pd.DataFrame(cpi_data).tail(180)
                        df_cpi['date'] = pd.to_datetime(df_cpi['date'])
                        
                        # Calculate YoY change
                        df_cpi['yoy_change'] = df_cpi['value'].pct_change(12) * 100
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df_cpi['date'],
                            y=df_cpi['yoy_change'],
                            mode='lines',
                            name='YoY Inflation',
                            line=dict(color='#9467bd', width=2),
                            fill='tozeroy',
                            fillcolor='rgba(148, 103, 189, 0.2)'
                        ))
                        
                        # Add 2% target line
                        fig.add_hline(y=2, line_dash="dash", line_color="green",
                                     annotation_text="Fed 2% Target")
                        
                        fig.update_layout(
                            xaxis_title="Date",
                            yaxis_title="YoY Change (%)",
                            height=300,
                            hovermode='x unified',
                            template="plotly_dark"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Last update time
                last_update = fred_data.get('last_updated', 'Unknown')
                st.caption(f"📅 FRED data last updated: {last_update}")
                
            except Exception as e:
                st.error(f"⚠️ Error loading FRED data: {e}")
        else:
            st.info("💡 **FRED economic data not yet available**")
            st.markdown("""
            To enable macro indicators:
            1. Get a free API key at [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
            2. Add `FRED_API_KEY` to your `.env` file
            3. Run `python run_fred.py`
            """)


# ==============================================================================
    # TAB 2: AI BUBBLE WATCH
    # ==============================================================================
    elif page == "🤖 AI Bubble Watch":
        st.header("AI Bubble Outlook")
        st.markdown("*Monitoring key AI stocks for overvaluation signals*")
        
        # Get AI category data
        ai_category = None
        if categories:
            available_categories = [c['category'] for c in categories.get('categories', [])]
            st.caption(f"Available categories: {', '.join(available_categories)}")
            
            # Try exact match first
            ai_category = next((c for c in categories.get('categories', []) if c['category'] == 'AI bubble indicator'), None)
            
            # Try partial match if exact fails
            if not ai_category:
                ai_category = next((c for c in categories.get('categories', []) if 'AI' in c['category']), None)
        
        if not ai_category:
            st.warning("⚠️ No AI bubble indicator category found. Please check your data.")
            st.info("**Troubleshooting:**")
            st.write("1. Verify symbols in `config/tickers.csv` have `category=AI bubble indicator`")
            st.write("2. Run `python run_analytics.py` to regenerate aggregates")
            st.write("3. Check that symbols have technical data")
            
            # Show all available data as fallback
            if latest_values and latest_values.get('symbols'):
                st.markdown("### 📊 All Available Symbols")
                for symbol_data in latest_values['symbols'][:10]:  # Show first 10
                    st.write(f"- **{symbol_data['symbol']}** ({symbol_data.get('category', 'Unknown')})")
        else:
            st.subheader("📊 AI Stocks Dashboard")
            st.caption(f"Monitoring {len(ai_category['symbols'])} AI-related symbols")
            
            # Create metrics grid
            ai_symbols = ai_category['symbols']
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_rsi = sum(s.get('rsi_14', 0) for s in ai_symbols if s.get('rsi_14')) / len([s for s in ai_symbols if s.get('rsi_14')])
                st.metric("Average RSI", f"{avg_rsi:.1f}")
            
            with col2:
                overbought_count = len([s for s in ai_symbols if s.get('rsi_14', 0) > 70])
                st.metric("Overbought Stocks", overbought_count)
                if overbought_count > 0:
                    st.caption("📉 BEARISH signal")
            
            with col3:
                avg_1d = sum(s.get('roc_1d', 0) for s in ai_symbols if s.get('roc_1d')) / len([s for s in ai_symbols if s.get('roc_1d')])
                st.metric("Avg 1D Change", f"{avg_1d:.2f}%")
            
            with col4:
                above_sma200 = len([s for s in ai_symbols if s.get('price_above_sma_200', False)])
                st.metric("Above SMA 200", f"{above_sma200}/{len(ai_symbols)}")
            
            st.divider()
            
            # Individual symbol analysis
            for symbol_info in ai_symbols:
                # Get full symbol data from latest_values
                symbol_data = next((s for s in latest_values['symbols'] if s['symbol'] == symbol_info['symbol']), None)
                if not symbol_data:
                    continue
                
                with st.expander(f"**{symbol_data['symbol']}** - ${symbol_data['price']['close']:.2f}", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        change_1d = symbol_data['performance']['roc_1d']
                        st.metric("1D Change", f"{change_1d:.2f}%")
                        if change_1d > 0:
                            st.caption("📈 BULLISH")
                        else:
                            st.caption("📉 BEARISH")
                    
                    with col2:
                        change_5d = symbol_data['performance']['roc_5d']
                        st.metric("5D Change", f"{change_5d:.2f}%")
                        if change_5d > 0:
                            st.caption("📈 BULLISH")
                        else:
                            st.caption("📉 BEARISH")
                    
                    with col3:
                        change_20d = symbol_data['performance']['roc_20d']
                        st.metric("20D Change", f"{change_20d:.2f}%")
                        if change_20d > 0:
                            st.caption("📈 BULLISH")
                        else:
                            st.caption("📉 BEARISH")
                    
                    with col4:
                        rsi = symbol_data['momentum']['rsi_14']
                        if rsi > 70:
                            st.error(f"RSI: {rsi:.1f} (Overbought 📉 BEARISH)")
                        elif rsi < 30:
                            st.success(f"RSI: {rsi:.1f} (Oversold 📈 BULLISH)")
                        else:
                            st.info(f"RSI: {rsi:.1f} (Neutral)")
                    
                    # Full indicators display
                    display_comprehensive_indicators(symbol_data['symbol'])
                    
                    # Load and show chart
                    full_data = load_symbol_technical(symbol_data['symbol'])
                    if full_data:
                        fig = create_price_chart(full_data)
                        st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Bubble warnings
            st.subheader("⚠️ Bubble Warning Signals")
            
            overbought = [s for s in ai_symbols if s.get('rsi_14', 0) > 70]
            if overbought:
                st.warning(f"**{len(overbought)} AI stocks are overbought (RSI > 70) - 📉 BEARISH:**")
                for s in overbought:
                    st.markdown(f"- **{s['symbol']}**: RSI {s['rsi_14']:.1f}")
            else:
                st.success("✅ No overbought signals in AI stocks - 📈 BULLISH")
            
            # CapEx warnings (if fundamentals available)
            st.markdown("### 💰 CapEx Trends (AI Bubble Indicator)")
            
            capex_concerns = []
            for symbol_info in ai_symbols:
                fund_data = load_symbol_fundamentals(symbol_info['symbol'])
                if fund_data:
                    cash_flow = fund_data.get('cash_flow', {})
                    capex_trend = cash_flow.get('capex_trend')
                    capex_cagr = cash_flow.get('capex_3yr_cagr')
                    
                    if capex_trend == 'increasing' or (capex_cagr and capex_cagr > 20):
                        capex_concerns.append({
                            'symbol': symbol_info['symbol'],
                            'trend': capex_trend,
                            'cagr': capex_cagr
                        })
            
            if capex_concerns:
                st.warning(f"**{len(capex_concerns)} companies showing aggressive CapEx growth - 📉 BEARISH:**")
                for concern in capex_concerns:
                    cagr_str = f", 3Y CAGR: +{concern['cagr']:.1f}%" if concern['cagr'] else ""
                    st.markdown(f"- **{concern['symbol']}**: {concern['trend']}{cagr_str}")
                st.info("💡 High CapEx growth in AI companies may indicate overinvestment bubble")
            else:
                st.success("✅ No extreme CapEx growth patterns detected - 📈 BULLISH")
            
            # Valuation concerns
            st.markdown("### 📊 Valuation Metrics")
            
            high_pe_stocks = []
            for symbol_info in ai_symbols:
                fund_data = load_symbol_fundamentals(symbol_info['symbol'])
                if fund_data:
                    valuation = fund_data.get('valuation', {})
                    fwd_pe = valuation.get('forward_pe')
                    peg = valuation.get('peg_ratio')
                    
                    if (fwd_pe and fwd_pe > 50) or (peg and peg > 2.5):
                        high_pe_stocks.append({
                            'symbol': symbol_info['symbol'],
                            'fwd_pe': fwd_pe,
                            'peg': peg
                        })
            
            if high_pe_stocks:
                st.warning(f"**{len(high_pe_stocks)} stocks showing elevated valuations - 📉 BEARISH:**")
                for stock in high_pe_stocks:
                    pe_str = f"Forward PE: {stock['fwd_pe']:.1f}" if stock['fwd_pe'] else ""
                    peg_str = f", PEG: {stock['peg']:.2f}" if stock['peg'] else ""
                    st.markdown(f"- **{stock['symbol']}**: {pe_str}{peg_str}")
            else:
                st.success("✅ Valuations appear reasonable - 📈 BULLISH")
    
    # ==============================================================================
    # TAB 3: INDIVIDUAL SYMBOLS
    # ==============================================================================
    elif page == "📈 Individual Symbols":
        st.header("Individual Symbol Analysis")
        
        # Create searchable table
        symbols_list = latest_values['symbols']
        
        # DEFAULT SORT: Highest to Lowest Performing
        symbols_list = sorted(symbols_list, key=lambda x: x['performance'].get('roc_1d', -999), reverse=True)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search = st.text_input("🔍 Search Symbol", "")
        
        with col2:
            category_filter = st.multiselect(
                "Filter by Category",
                options=list(set(s['category'] for s in symbols_list)),
                default=[]
            )
        
        with col3:
            signal_filter = st.multiselect(
                "Filter by Signals",
                options=[
                    "All Symbols",
                    "Golden Cross",
                    "Death Cross",
                    "RSI Overbought (>70)",
                    "RSI Oversold (<30)",
                    "MACD Bullish Cross",
                    "MACD Bearish Cross",
                    "High Volatility",
                    "Low Volatility",
                    "Above SMA 200",
                    "Below SMA 200",
                    "Bullish Trend (EMA)",
                    "Bearish Trend (EMA)"
                ],
                default=["All Symbols"]
            )
        
        # Filter symbols
        filtered = symbols_list
        
        # Apply search filter
        if search:
            filtered = [s for s in filtered if search.upper() in s['symbol'].upper()]
        
        # Apply category filter
        if category_filter:
            filtered = [s for s in filtered if s['category'] in category_filter]
        
        # Apply signal filter
        if signal_filter and "All Symbols" not in signal_filter:
            # Add EMA trend filters
            filtered_temp = []
            for symbol in filtered:
                tech_data = load_symbol_technical(symbol['symbol'])
                if tech_data:
                    latest = tech_data['data'][-1]
                    ema_trend = latest.get('ema_trend', 'neutral')
                    
                    # Check EMA filters
                    if "Bullish Trend (EMA)" in signal_filter and ema_trend == 'bullish':
                        filtered_temp.append(symbol)
                        continue
                    if "Bearish Trend (EMA)" in signal_filter and ema_trend == 'bearish':
                        filtered_temp.append(symbol)
                        continue
                
                # Check other filters
                if filter_symbols_by_signals([symbol], signal_filter):
                    filtered_temp.append(symbol)
            
            filtered = filtered_temp
        
        # Show count
        st.caption(f"Showing {len(filtered)} of {len(symbols_list)} symbols (sorted by 1D performance)")
        
        # Display as cards with full indicators
        for symbol in filtered:
            with st.expander(f"**{symbol['symbol']}** - {symbol['category']}", expanded=False):
                # Load technical data to get timestamps and ATR
                tech_data = load_symbol_technical(symbol['symbol'])
                
                # Header with last update timestamp
                if tech_data:
                    last_calc = tech_data.get('last_calculated', 'Unknown')
                    try:
                        calc_time = datetime.fromisoformat(last_calc.replace('Z', ''))
                        time_ago = datetime.utcnow() - calc_time
                        if time_ago.total_seconds() < 3600:
                            time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
                        else:
                            time_str = f"{int(time_ago.total_seconds() / 3600)} hours ago"
                        st.caption(f"🕐 Last updated: {time_str}")
                    except:
                        st.caption(f"🕐 Last updated: {last_calc}")
                
                # Quick metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Price", f"${symbol['price']['close']:.2f}")
                
                with col2:
                    change_1d = symbol['performance']['roc_1d']
                    st.metric("1D", f"{change_1d:.2f}%")
                    if change_1d > 0:
                        st.caption("📈 BULLISH")
                    else:
                        st.caption("📉 BEARISH")
                
                with col3:
                    change_5d = symbol['performance']['roc_5d']
                    st.metric("5D", f"{change_5d:.2f}%")
                    if change_5d > 0:
                        st.caption("📈 BULLISH")
                    else:
                        st.caption("📉 BEARISH")
                
                with col4:
                    rsi = symbol['momentum']['rsi_14']
                    st.metric("RSI", f"{rsi:.1f}")
                    if rsi > 70:
                        st.caption("📉 BEARISH")
                    elif rsi < 30:
                        st.caption("📈 BULLISH")
                
                with col5:
                    emoji, status, _ = get_health_color(
                        symbol['momentum']['rsi_14'],
                        symbol['volatility']['volatility_20d']
                    )
                    st.markdown(f"### {emoji}")
                    st.caption(status)
                
                st.divider()
                
                # ATR and Stop Loss Section
                if tech_data:
                    latest = tech_data['data'][-1]
                    atr = latest.get('atr_14')
                    current_price = latest.get('close')
                    
                    if atr and current_price:
                        st.markdown("### 🛡️ Risk Management (ATR-Based)")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("ATR (14)", f"${atr:.2f}")
                            st.caption("Average True Range")
                        
                        # Calculate stop losses at different ATR multipliers
                        with col2:
                            stop_1x = current_price - (atr * 1)
                            st.metric("Conservative Stop", f"${stop_1x:.2f}")
                            st.caption("1x ATR (tight)")
                        
                        with col3:
                            stop_2x = current_price - (atr * 2)
                            st.metric("Moderate Stop", f"${stop_2x:.2f}")
                            st.caption("2x ATR (recommended)")
                        
                        with col4:
                            stop_3x = current_price - (atr * 3)
                            st.metric("Wide Stop", f"${stop_3x:.2f}")
                            st.caption("3x ATR (swing trade)")
                        
                        # Show percentage risk
                        risk_2x = ((current_price - stop_2x) / current_price) * 100
                        st.info(f"💡 **Recommended Strategy:** Use 2x ATR stop at **${stop_2x:.2f}** "
                               f"(Risk: {risk_2x:.1f}% from current price)")
                        
                        st.divider()
                
                # Full indicators
                display_comprehensive_indicators(symbol['symbol'])
                
                # Detailed chart
                full_data = load_symbol_technical(symbol['symbol'])
                if full_data:
                    fig = create_price_chart(full_data)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # ==============================================================================
    # TAB 4: SYSTEM STATUS
    # ==============================================================================
    elif page == "⚙️ System Status":
        st.header("System Health & Status")
        
        # Data freshness
        st.subheader("📅 Data Freshness")
        
        if latest_values:
            generated_time = datetime.fromisoformat(latest_values['generated_at'].replace('Z', ''))
            age = datetime.utcnow() - generated_time
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Analytics Age", f"{age.seconds // 60} min" if age.total_seconds() < 3600 else f"{age.seconds // 3600}h")
                
                if age.total_seconds() < 7200:  # Less than 2 hours
                    st.success("✅ Fresh")
                elif age.total_seconds() < 14400:  # Less than 4 hours
                    st.warning("⚠️ Slightly stale")
                else:
                    st.error("🔴 Stale")
            
            with col2:
                st.metric("Last Analytics Run", generated_time.strftime("%Y-%m-%d %H:%M UTC"))
            
            with col3:
                # Calculate next run based on ACTUAL cron schedule from workflow file
                if fetch_cron:
                    next_run = calculate_next_cron_run(fetch_cron)
                    
                    if next_run:
                        time_until_next = next_run - datetime.utcnow()
                        hours_until = time_until_next.total_seconds() / 3600
                        
                        if hours_until < 1:
                            time_str = f"{int(time_until_next.total_seconds() / 60)}m"
                        else:
                            time_str = f"{hours_until:.1f}h"
                        
                        st.metric("Next Scheduled Run", time_str)
                        st.caption(f"At {next_run.strftime('%H:%M')} UTC")
                    else:
                        st.metric("Next Run", "Unknown")
                else:
                    st.metric("Next Run", "Unknown")
                    st.caption("Cannot read workflow file")
        
        st.divider()
        
        # Pipeline Status - Check each component
        st.subheader("🔧 Pipeline Component Status")
        
        # Check raw data
        raw_data_path = Path("data/raw")
        raw_files = list(raw_data_path.glob("*.json")) if raw_data_path.exists() else []
        
        # Check technical analytics
        tech_path = Path("data/analytics/technical")
        tech_files = list(tech_path.glob("*.json")) if tech_path.exists() else []
        
        # Check fundamentals
        fund_path = Path("data/analytics/fundamentals")
        fund_files = list(fund_path.glob("*.json")) if fund_path.exists() else []
        
        # Check aggregates
        agg_path = Path("data/analytics/aggregated")
        agg_files = list(agg_path.glob("*.json")) if agg_path.exists() else []
        
        # Check market health
        health_path = Path("data/analytics/market_health")
        health_files = list(health_path.glob("*.json")) if health_path.exists() else []
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Data Collection")
            
            # Raw data status
            if raw_files:
                # Get oldest and newest file times
                file_times = []
                for f in raw_files:
                    try:
                        with open(f, 'r') as file:
                            data = json.load(file)
                            last_updated = data.get('last_updated')
                            if last_updated:
                                file_times.append(datetime.fromisoformat(last_updated.replace('Z', '')))
                    except:
                        pass
                
                if file_times:
                    oldest = min(file_times)
                    newest = max(file_times)
                    age_oldest = datetime.utcnow() - oldest
                    age_newest = datetime.utcnow() - newest
                    
                    st.success(f"✅ **Raw Data:** {len(raw_files)} files")
                    st.caption(f"Newest: {age_newest.seconds // 60}m ago | Oldest: {age_oldest.seconds // 3600}h ago")
                else:
                    st.success(f"✅ **Raw Data:** {len(raw_files)} files")
            else:
                st.error("❌ **Raw Data:** No files found")
            
            # Technical indicators status
            if tech_files:
                # Check a sample file for timestamp
                try:
                    with open(tech_files[0], 'r') as f:
                        sample = json.load(f)
                        last_calc = sample.get('last_calculated')
                        if last_calc:
                            calc_time = datetime.fromisoformat(last_calc.replace('Z', ''))
                            calc_age = datetime.utcnow() - calc_time
                            st.success(f"✅ **Technical Indicators:** {len(tech_files)} files")
                            st.caption(f"Last calculated: {calc_age.seconds // 60}m ago")
                        else:
                            st.success(f"✅ **Technical Indicators:** {len(tech_files)} files")
                except:
                    st.success(f"✅ **Technical Indicators:** {len(tech_files)} files")
            else:
                st.error("❌ **Technical Indicators:** No files found")
        
        with col2:
            st.markdown("#### Analytics & Aggregation")
            
            # Fundamentals status
            if fund_files:
                try:
                    with open(fund_files[0], 'r') as f:
                        sample = json.load(f)
                        last_updated = sample.get('last_updated')
                        if last_updated:
                            update_time = datetime.fromisoformat(last_updated.replace('Z', ''))
                            update_age = datetime.utcnow() - update_time
                            st.success(f"✅ **Fundamentals:** {len(fund_files)} files")
                            st.caption(f"Last updated: {update_age.seconds // 3600}h ago")
                        else:
                            st.success(f"✅ **Fundamentals:** {len(fund_files)} files")
                except:
                    st.success(f"✅ **Fundamentals:** {len(fund_files)} files")
            else:
                st.warning("⚠️ **Fundamentals:** No files (expected for indices/crypto)")
            
            # Aggregates status
            if len(agg_files) >= 4:
                st.success(f"✅ **Aggregates:** {len(agg_files)}/4 files")
                
                # Check which aggregates exist
                expected = ['latest_values.json', 'by_category.json', 'performance_rankings.json', 'active_signals.json']
                existing = [f.name for f in agg_files]
                
                all_exist = all(exp in existing for exp in expected)
                if all_exist:
                    st.caption("All aggregate views present")
                else:
                    missing = [exp for exp in expected if exp not in existing]
                    st.caption(f"Missing: {', '.join(missing)}")
            else:
                st.error(f"❌ **Aggregates:** {len(agg_files)}/4 files")
            
            # Market health status
            if health_files:
                st.success(f"✅ **Market Health:** {len(health_files)} file(s)")
            else:
                st.warning("⚠️ **Market Health:** Not generated")
        
        st.divider()
        
        # GitHub Actions Status
        st.subheader("⚙️ Automation Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Fetch Workflow**")
            if raw_files:
                # Estimate last successful fetch from newest raw file
                newest_raw = max(raw_files, key=lambda f: f.stat().st_mtime)
                last_fetch = datetime.fromtimestamp(newest_raw.stat().st_mtime)
                fetch_age = datetime.utcnow() - last_fetch
                
                st.info(f"Last run: {fetch_age.seconds // 3600}h {(fetch_age.seconds % 3600) // 60}m ago")
                
                if fetch_cron:
                    schedule_desc = get_cron_description(fetch_cron)
                    st.caption(f"Schedule: `{fetch_cron}`")
                    st.caption(f"({schedule_desc})")
                    
                    # Calculate next run
                    next_fetch = calculate_next_cron_run(fetch_cron)
                    if next_fetch:
                        st.caption(f"Next run: {next_fetch.strftime('%H:%M UTC')}")
                    
                    # Determine if on schedule based on actual interval
                    if '*/30' in fetch_cron:  # Every 30 minutes
                        threshold = 3600  # 1 hour
                    elif '*/6' in fetch_cron:  # Every 6 hours
                        threshold = 25200  # 7 hours
                    elif '*/' in fetch_cron:  # Every N hours/minutes
                        # Try to extract interval
                        if 'hour' in schedule_desc.lower():
                            try:
                                interval = int(schedule_desc.split()[1])
                                threshold = (interval + 1) * 3600
                            except:
                                threshold = 7200
                        else:
                            threshold = 7200
                    else:
                        threshold = 7200  # Default 2 hours
                    
                    if fetch_age.total_seconds() < threshold:
                        st.success("✅ Running on schedule")
                    else:
                        st.error("🔴 May have failed - check GitHub Actions")
                else:
                    st.caption("Schedule: Unknown (cannot read workflow)")
                    st.warning("⚠️ Unable to determine status")
            else:
                st.warning("⚠️ Unable to determine status")
        
        with col2:
            st.markdown("**Analytics Workflow**")
            if tech_files:
                newest_tech = max(tech_files, key=lambda f: f.stat().st_mtime)
                last_analytics = datetime.fromtimestamp(newest_tech.stat().st_mtime)
                analytics_age = datetime.utcnow() - last_analytics
                
                st.info(f"Last run: {analytics_age.seconds // 3600}h {(analytics_age.seconds % 3600) // 60}m ago")
                st.caption("Triggered after fetch completion")
                
                if analytics_age.total_seconds() < 7200:  # 2 hours
                    st.success("✅ Running on schedule")
                else:
                    st.error("🔴 May have failed - check GitHub Actions")
            else:
                st.warning("⚠️ Unable to determine status")
        
        st.divider()
        
        # Symbol coverage
        st.subheader("📊 Symbol Coverage")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Symbols", len(latest_values['symbols']))
        with col2:
            st.metric("Categories", len(set(s['category'] for s in latest_values['symbols'])))
        
        # Symbols by category
        category_counts = {}
        for symbol in latest_values['symbols']:
            cat = symbol['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        st.markdown("**Symbols by Category:**")
        for cat, count in category_counts.items():
            st.markdown(f"- {cat}: {count} symbols")
        
        st.divider()
        
        # Active signals
        if signals:
            st.subheader("🔔 Active Signals Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Golden Crosses", len(signals.get('golden_crosses', [])))
                st.metric("Death Crosses", len(signals.get('death_crosses', [])))
            
            with col2:
                st.metric("RSI Overbought", len(signals.get('rsi_overbought', [])))
                st.metric("RSI Oversold", len(signals.get('rsi_oversold', [])))
            
            with col3:
                st.metric("High Volatility", len(signals.get('high_volatility', [])))
                st.metric("Low Volatility", len(signals.get('low_volatility', [])))
        
        st.divider()
        
        # Backend info
        st.subheader("🔧 Backend Information")
        st.info("Data is automatically updated via GitHub Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Data Pipeline:**")
            st.markdown("1. ✅ Fetch raw OHLCV data")
            st.markdown("2. ✅ Calculate technical indicators")
            st.markdown("3. ✅ Fetch fundamentals (stocks only)")
            st.markdown("4. ✅ Generate aggregated views")
            st.markdown("5. ✅ Analyze market health")
            st.markdown("6. ✅ Commit to Git")
        
        with col2:
            st.markdown("**Data Sources:**")
            st.markdown("- Yahoo Finance (all symbols)")
            st.markdown("- FRED (macro indicators)")
            st.markdown("- 45+ calculated indicators")
            st.markdown("- Market health scoring")
            st.markdown("- 4 aggregate summary files")
        
        # Workflow file status
        st.divider()
        st.subheader("📄 Workflow Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if fetch_workflow_path.exists():
                st.success("✅ **fetch-data.yml** found")
                if fetch_cron:
                    st.code(f"schedule: {fetch_cron}", language="yaml")
                    st.caption(get_cron_description(fetch_cron))
                else:
                    st.warning("⚠️ Could not parse cron schedule")
            else:
                st.error("❌ **fetch-data.yml** not found")
        
        with col2:
            if analytics_workflow_path.exists():
                st.success("✅ **calculate-analytics.yml** found")
                st.caption("Triggered by fetch-data workflow")
            else:
                st.error("❌ **calculate-analytics.yml** not found")
        
        # Quick actions
        st.divider()
        st.subheader("🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**View Logs:**")
            st.markdown("[GitHub Actions →](https://github.com/DruidSmith/Market-Dashboard/actions)")
        
        with col2:
            st.markdown("**Manual Trigger:**")
            st.markdown("Use 'Run workflow' in Actions tab")
        
        with col3:
            st.markdown("**Repository:**")
            st.markdown("[View Code →](https://github.com/DruidSmith/Market-Dashboard)")
        
        # NEW: Export section
        st.divider()
        st.subheader("📥 Export for AI Analysis")
        
        st.markdown("""
        Generate a comprehensive report with all market data, indicators, and fundamentals.
        Perfect for pasting into ChatGPT, Claude, or other AI assistants for personalized
        trading recommendations.
        """)
        
        if st.button("🤖 Generate AI-Ready Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive export..."):
                try:
                    # Add project root to path
                    import sys
                    
                    project_root = Path(__file__).parent.parent
                    if str(project_root) not in sys.path:
                        sys.path.insert(0, str(project_root))
                    
                    from src.export_generator import ExportGenerator
                    
                    generator = ExportGenerator()
                    output_path = generator.export_to_file()
                    
                    # Present the file for download
                    with open(output_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    st.success(f"✅ Report generated! ({output_path.stat().st_size:,} bytes)")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=report_content,
                        file_name=output_path.name,
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    # Show preview
                    with st.expander("📄 Preview Report (First 2000 characters)"):
                        st.text(report_content[:2000] + "\n\n... (truncated)")
                    
                    st.info("""
                    **Next Steps:**
                    1. Download the report
                    2. Open in your preferred AI assistant (ChatGPT, Claude, etc.)
                    3. Paste the entire content
                    4. Ask for specific recommendations based on your goals
                    
                    **Example prompts:**
                    - "Based on this data, what are your top 3 buy recommendations?"
                    - "Should I reduce my NVDA position given the AI bubble indicators?"
                    - "What's the recession probability based on macro indicators?"
                    - "Recommend stop loss levels for my current positions"
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error generating report: {e}")
                    import traceback
                    st.code(traceback.format_exc())


if __name__ == "__main__":
    main()