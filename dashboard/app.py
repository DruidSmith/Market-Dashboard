"""
Market Health Dashboard - Enhanced with Full Indicators
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Market Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .indicator-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 10px 0;
    }
    .indicator-badge {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .bullish {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .bearish {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .neutral {
        background-color: #e2e3e5;
        color: #383d41;
        border: 1px solid #d6d8db;
    }
    .good-metric {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 10px;
        border-radius: 5px;
    }
    .warning-metric {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        border-radius: 5px;
    }
    .bad-metric {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 10px;
        border-radius: 5px;
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


def display_comprehensive_indicators(symbol):
    """Display all indicators for a symbol in a formatted way."""
    tech_data = load_symbol_technical(symbol)
    fund_data = load_symbol_fundamentals(symbol)
    
    if not tech_data:
        st.warning(f"No technical data for {symbol}")
        return
    
    # Get latest data point
    latest = tech_data['data'][-1]
    
    # === YIELDS SECTION ===
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
            rsi_badge = f'<span class="indicator-badge bearish">RSI: {rsi:.1f} (Overbought ↓)</span>'
        elif rsi < 30:
            rsi_badge = f'<span class="indicator-badge bullish">RSI: {rsi:.1f} (Oversold ↑)</span>'
        else:
            rsi_badge = f'<span class="indicator-badge neutral">RSI: {rsi:.1f} (Neutral ↔)</span>'
        indicators_html += rsi_badge
    
    # SMA Cross
    sma_position = latest.get('sma_position', 'neutral')
    if sma_position == 'golden':
        sma_badge = '<span class="indicator-badge bullish">SMA: Golden Cross (↑)</span>'
    elif sma_position == 'death':
        sma_badge = '<span class="indicator-badge bearish">SMA: Death Cross (↓)</span>'
    else:
        sma_badge = '<span class="indicator-badge neutral">SMA: Neutral (↔)</span>'
    indicators_html += sma_badge
    
    # EMA Trend
    ema_trend = latest.get('ema_trend', 'neutral')
    if ema_trend == 'bullish':
        ema_badge = '<span class="indicator-badge bullish">EMA: Bullish (↑)</span>'
    elif ema_trend == 'bearish':
        ema_badge = '<span class="indicator-badge bearish">EMA: Bearish (↓)</span>'
    else:
        ema_badge = '<span class="indicator-badge neutral">EMA: Neutral (↔)</span>'
    indicators_html += ema_badge
    
    # MACD
    macd = latest.get('macd')
    macd_signal = latest.get('macd_signal')
    if macd is not None and macd_signal is not None:
        if macd > macd_signal:
            macd_badge = '<span class="indicator-badge bullish">MACD: Bullish (↑)</span>'
        else:
            macd_badge = '<span class="indicator-badge bearish">MACD: Bearish (↓)</span>'
        indicators_html += macd_badge
    
    indicators_html += '</div>'
    st.markdown(indicators_html, unsafe_allow_html=True)
    
    st.divider()
    
    # === FUNDAMENTALS ===
    if fund_data:
        st.markdown("### 💼 Fundamental Metrics")
        
        valuation = fund_data.get('valuation', {})
        
        fund_html = '<div class="indicator-row">'
        
        # Forward PE
        fwd_pe = valuation.get('forward_pe')
        if fwd_pe:
            fund_html += f'<span class="indicator-badge neutral">Forward PE: {fwd_pe:.2f}</span>'
        else:
            fund_html += '<span class="indicator-badge neutral">Forward PE: N/A</span>'
        
        # Trailing PE
        trail_pe = valuation.get('trailing_pe')
        if trail_pe:
            fund_html += f'<span class="indicator-badge neutral">Trailing PE: {trail_pe:.2f}</span>'
        else:
            fund_html += '<span class="indicator-badge neutral">Trailing PE: N/A</span>'
        
        # PEG Ratio
        peg = valuation.get('peg_ratio')
        if peg:
            if peg < 1:
                peg_badge = f'<span class="indicator-badge bullish">PEG: {peg:.2f} (Undervalued)</span>'
            elif peg > 2:
                peg_badge = f'<span class="indicator-badge bearish">PEG: {peg:.2f} (Overvalued)</span>'
            else:
                peg_badge = f'<span class="indicator-badge neutral">PEG: {peg:.2f}</span>'
            fund_html += peg_badge
        
        # Price to Book
        pb = valuation.get('price_to_book')
        if pb:
            fund_html += f'<span class="indicator-badge neutral">P/B: {pb:.2f}</span>'
        
        fund_html += '</div>'
        st.markdown(fund_html, unsafe_allow_html=True)
        
        # Profitability
        profitability = fund_data.get('profitability', {})
        if any(profitability.values()):
            st.markdown("**Profitability:**")
            prof_html = '<div class="indicator-row">'
            
            if profitability.get('profit_margin'):
                margin = profitability['profit_margin'] * 100
                prof_html += f'<span class="indicator-badge neutral">Profit Margin: {margin:.1f}%</span>'
            
            if profitability.get('roe'):
                roe = profitability['roe'] * 100
                if roe > 15:
                    prof_html += f'<span class="indicator-badge bullish">ROE: {roe:.1f}%</span>'
                elif roe < 5:
                    prof_html += f'<span class="indicator-badge bearish">ROE: {roe:.1f}%</span>'
                else:
                    prof_html += f'<span class="indicator-badge neutral">ROE: {roe:.1f}%</span>'
            
            prof_html += '</div>'
            st.markdown(prof_html, unsafe_allow_html=True)


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
        showlegend=True
    )
    
    return fig


# ==============================================================================
# MAIN APP
# ==============================================================================

def main():
    st.title("📊 Market Health Dashboard")
    
    # Load data
    latest_values = load_latest_values()
    rankings = load_performance_rankings()
    signals = load_active_signals()
    categories = load_category_summary()
    
    if not latest_values:
        st.error("⚠️ No data available. Please run: python run_analytics.py")
        return
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select View",
        ["🌍 Market Overview", "🤖 AI Bubble Watch", "📈 Individual Tickers", "⚙️ System Status"]
    )
    
    # Display last update time
    last_update = latest_values.get('generated_at', 'Unknown')
    st.sidebar.info(f"📅 Last Updated: {last_update}")
    
    # ==============================================================================
    # TAB 1: MARKET OVERVIEW
    # ==============================================================================
    if page == "🌍 Market Overview":
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
        
        # Top movers
        if rankings:
            st.subheader("🔥 Today's Movers")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top Gainers (1D)**")
                for item in rankings['top_gainers_1d'][:3]:
                    st.success(f"**{item['symbol']}**: +{item['roc_1d']:.2f}%")
            
            with col2:
                st.markdown("**Top Losers (1D)**")
                for item in rankings['top_losers_1d'][:3]:
                    st.error(f"**{item['symbol']}**: {item['roc_1d']:.2f}%")
    
    # ==============================================================================
    # TAB 2: AI BUBBLE WATCH
    # ==============================================================================
    elif page == "🤖 AI Bubble Watch":
        st.header("AI Bubble Outlook")
        st.markdown("*Monitoring key AI stocks for overvaluation signals*")
        
        # Get AI category data
        ai_category = None
        if categories:
            ai_category = next((c for c in categories['categories'] if 'AI' in c['category']), None)
        
        if ai_category:
            st.subheader("📊 AI Stocks Dashboard")
            
            # Create metrics grid
            ai_symbols = ai_category['symbols']
            
            for symbol_info in ai_symbols:
                # Get full symbol data from latest_values
                symbol_data = next((s for s in latest_values['symbols'] if s['symbol'] == symbol_info['symbol']), None)
                if not symbol_data:
                    continue
                
                with st.expander(f"**{symbol_data['symbol']}** - ${symbol_data['price']['close']:.2f}"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("1D Change", f"{symbol_data['performance']['roc_1d']:.2f}%")
                    with col2:
                        st.metric("5D Change", f"{symbol_data['performance']['roc_5d']:.2f}%")
                    with col3:
                        st.metric("20D Change", f"{symbol_data['performance']['roc_20d']:.2f}%")
                    with col4:
                        rsi = symbol_data['momentum']['rsi_14']
                        if rsi > 70:
                            st.error(f"RSI: {rsi:.1f} (Overbought)")
                        elif rsi < 30:
                            st.success(f"RSI: {rsi:.1f} (Oversold)")
                        else:
                            st.info(f"RSI: {rsi:.1f} (Neutral)")
                    
                    # Full indicators display
                    display_comprehensive_indicators(symbol_data['symbol'])
                    
                    # Load and show chart
                    full_data = load_symbol_technical(symbol_data['symbol'])
                    if full_data:
                        fig = create_price_chart(full_data)
                        st.plotly_chart(fig, width="stretch")
            
            st.divider()
            
            # Bubble warnings
            st.subheader("⚠️ Bubble Warning Signals")
            
            overbought = [s for s in ai_symbols if s.get('rsi_14', 0) > 70]
            if overbought:
                st.warning(f"**{len(overbought)} AI stocks are overbought:**")
                for s in overbought:
                    st.markdown(f"- **{s['symbol']}**: RSI {s['rsi_14']:.1f}")
            else:
                st.success("✅ No overbought signals in AI stocks")
    
    # ==============================================================================
    # TAB 3: INDIVIDUAL TICKERS
    # ==============================================================================
    elif page == "📈 Individual Tickers":
        st.header("Individual Ticker Analysis")
        
        # Create searchable table
        symbols_list = latest_values['symbols']
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("🔍 Search Symbol", "")
        with col2:
            category_filter = st.multiselect(
                "Filter by Category",
                options=list(set(s['category'] for s in symbols_list)),
                default=[]
            )
        
        # Filter symbols
        filtered = symbols_list
        if search:
            filtered = [s for s in filtered if search.upper() in s['symbol'].upper()]
        if category_filter:
            filtered = [s for s in filtered if s['category'] in category_filter]
        
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
                    st.metric("1D", f"{symbol['performance']['roc_1d']:.2f}%")
                with col3:
                    st.metric("5D", f"{symbol['performance']['roc_5d']:.2f}%")
                with col4:
                    st.metric("RSI", f"{symbol['momentum']['rsi_14']:.1f}")
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
                    st.plotly_chart(fig, width="stretch")
    
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
                # Calculate expected next run (6 hour intervals)
                hours_since = age.total_seconds() / 3600
                hours_until_next = 6 - (hours_since % 6)
                st.metric("Next Run In", f"~{hours_until_next:.1f}h")
        
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
        
        st.divider()
        
        # GitHub Actions Status (if we can detect it from file timestamps)
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
                st.caption("Schedule: Every 6 hours")
                
                if fetch_age.total_seconds() < 25200:  # Less than 7 hours
                    st.success("✅ Running on schedule")
                else:
                    st.error("🔴 May have failed - check GitHub Actions")
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
                
                if analytics_age.total_seconds() < 25200:
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
        st.info("Data is automatically updated every 6 hours via GitHub Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Data Pipeline:**")
            st.markdown("1. ✅ Fetch raw OHLCV data")
            st.markdown("2. ✅ Calculate technical indicators")
            st.markdown("3. ✅ Fetch fundamentals (stocks only)")
            st.markdown("4. ✅ Generate aggregated views")
            st.markdown("5. ✅ Commit to Git")
        
        with col2:
            st.markdown("**Data Sources:**")
            st.markdown("- Alpha Vantage (stocks, crypto)")
            st.markdown("- Yahoo Finance (indices, fundamentals)")
            st.markdown("- 45+ calculated indicators")
            st.markdown("- 4 aggregate summary files")
        
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


if __name__ == "__main__":
    main()