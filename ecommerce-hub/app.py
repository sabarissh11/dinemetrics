import os
import io
import csv
import tempfile
import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Intelligence Hub",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2234;
    --accent: #6366f1;
    --accent2: #22d3ee;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: #1e293b;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headers */
h1, h2, h3 { color: var(--text) !important; }

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.2);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #e2e8f0, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-label {
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 8px;
}
.kpi-delta {
    font-size: 0.8rem;
    margin-top: 6px;
    font-weight: 600;
}
.delta-up { color: var(--success); }
.delta-down { color: var(--danger); }

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}
.section-header h2 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
}
.section-badge {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}

/* AI Chat */
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    min-height: 300px;
    max-height: 500px;
    overflow-y: auto;
}
.chat-msg-user {
    background: linear-gradient(135deg, var(--accent), #4f46e5);
    color: white;
    padding: 12px 16px;
    border-radius: 16px 16px 4px 16px;
    margin: 8px 0 8px 40px;
    font-size: 0.9rem;
}
.chat-msg-ai {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;
    margin: 8px 40px 8px 0;
    font-size: 0.9rem;
    line-height: 1.6;
}
.chat-msg-label {
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), #4f46e5) !important;
    color: white !important;
}

/* Inputs */
.stTextInput > div > div, .stTextArea > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
.stButton button {
    background: linear-gradient(135deg, var(--accent), #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: opacity 0.2s;
}
.stButton button:hover { opacity: 0.85 !important; }

/* DataFrames */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Metric */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* Plotly bg fix */
.js-plotly-plot { border-radius: 12px; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 16px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Title area */
.hero-title {
    background: linear-gradient(135deg, #e2e8f0 0%, #6366f1 50%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.2;
}
.hero-sub {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Space Grotesk', color='#e2e8f0', size=12),
    colorway=['#6366f1','#22d3ee','#10b981','#f59e0b','#ef4444','#a78bfa','#34d399','#fbbf24'],
    xaxis=dict(gridcolor='#1e293b', linecolor='#1e293b', tickcolor='#64748b'),
    yaxis=dict(gridcolor='#1e293b', linecolor='#1e293b', tickcolor='#64748b'),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1e293b'),
    margin=dict(t=40, b=40, l=40, r=20),
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_THEME)
    return fig

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file_bytes=None, file_name=None):
    if file_bytes:
        if file_name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        df = pd.read_csv('ecommerce_data.csv')
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.strftime('%b')
    df['quarter'] = df['order_date'].dt.quarter
    df['year'] = df['order_date'].dt.year
    df['week'] = df['order_date'].dt.isocalendar().week.astype(int)
    return df

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛒 E-Commerce Hub")
    st.markdown("---")

    # API Key
    st.markdown("**🔑 Anthropic API Key**")
    api_key = st.text_input("", type="password",
                             value=st.session_state.get("anthropic_key", os.getenv("ANTHROPIC_API_KEY", "")),
                             placeholder="sk-ant-...")
    if api_key:
        st.session_state.anthropic_key = api_key
        st.success("✓ API key set")
    
    st.markdown("---")

    # File Upload
    st.markdown("**📁 Data Source**")
    uploaded = st.file_uploader("Upload CSV / Excel", type=["csv", "xlsx"])
    use_sample = st.checkbox("Use built-in sample data", value=True)

    st.markdown("---")

    # Load data
    if uploaded:
        df_raw = load_data(uploaded.getvalue(), uploaded.name)
        st.success(f"✓ Loaded {len(df_raw):,} rows")
    else:
        df_raw = load_data()
        if use_sample:
            st.info(f"📊 Sample: {len(df_raw):,} orders")

    # Filters
    st.markdown("**🔧 Filters**")
    years = sorted(df_raw['year'].unique())
    sel_years = st.multiselect("Year", years, default=years)
    
    categories = sorted(df_raw['category'].unique())
    sel_cats = st.multiselect("Category", categories, default=categories)
    
    regions = sorted(df_raw['region'].unique())
    sel_regions = st.multiselect("Region", regions, default=regions)
    
    channels = sorted(df_raw['channel'].unique())
    sel_channels = st.multiselect("Channel", channels, default=channels)

    st.markdown("---")
    st.markdown("<small style='color:#64748b'>Built with Streamlit + Claude</small>", unsafe_allow_html=True)

# ─── FILTER DATA ──────────────────────────────────────────────────────────────
df = df_raw.copy()
if sel_years:   df = df[df['year'].isin(sel_years)]
if sel_cats:    df = df[df['category'].isin(sel_cats)]
if sel_regions: df = df[df['region'].isin(sel_regions)]
if sel_channels: df = df[df['channel'].isin(sel_channels)]

if df.empty:
    st.warning("No data matches your filters. Please broaden the selection.")
    st.stop()

# ─── HEADER ───────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="hero-title">E-Commerce Intelligence Hub</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Full EDA · Power BI Dashboard · AI-Powered Insights</p>', unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align:right;padding-top:20px'><span style='color:#64748b;font-size:0.8rem'>TOTAL RECORDS</span><br><span style='font-size:1.5rem;font-weight:700;color:#6366f1'>{len(df):,}</span></div>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔬 Full EDA", "📈 Advanced Analytics", "🤖 AI Analyst"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: POWER BI-STYLE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # ── KPIs ──
    total_revenue = df['revenue'].sum()
    total_orders = len(df)
    total_profit = df['profit'].sum()
    avg_order_val = df['revenue'].mean()
    return_rate = df['return_flag'].mean() * 100
    avg_rating = df['rating'].mean()
    unique_customers = df['customer_id'].nunique()

    # YoY comparison if multi-year
    yoy_rev = None
    if len(sel_years) >= 2:
        max_yr = max(sel_years)
        prev_yr = max_yr - 1
        if prev_yr in sel_years:
            r1 = df[df['year']==max_yr]['revenue'].sum()
            r2 = df[df['year']==prev_yr]['revenue'].sum()
            yoy_rev = ((r1 - r2) / r2 * 100) if r2 else None

    kpis = [
        ("💰 Total Revenue", f"₹{total_revenue/1e6:.2f}M", yoy_rev, "YoY"),
        ("📦 Total Orders", f"{total_orders:,}", None, ""),
        ("📈 Gross Profit", f"₹{total_profit/1e6:.2f}M", None, ""),
        ("🛍️ Avg Order Value", f"₹{avg_order_val:,.0f}", None, ""),
        ("👥 Unique Customers", f"{unique_customers:,}", None, ""),
        ("⭐ Avg Rating", f"{avg_rating:.2f}", None, ""),
        ("↩️ Return Rate", f"{return_rate:.1f}%", None, ""),
        ("💳 Profit Margin", f"{(total_profit/total_revenue*100):.1f}%", None, ""),
    ]

    cols = st.columns(4)
    for i, (label, value, delta, delta_label) in enumerate(kpis):
        with cols[i % 4]:
            delta_html = ""
            if delta is not None:
                arrow = "↑" if delta >= 0 else "↓"
                cls = "delta-up" if delta >= 0 else "delta-down"
                delta_html = f'<div class="kpi-delta {cls}">{arrow} {abs(delta):.1f}% {delta_label}</div>'
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 1: Revenue Trend + Category Sales ──
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-header"><h2>Revenue Trend</h2><span class="section-badge">Monthly</span></div>', unsafe_allow_html=True)
        monthly = df.groupby(['year','month','month_name'])['revenue'].sum().reset_index()
        monthly = monthly.sort_values(['year','month'])
        monthly['period'] = monthly['month_name'] + ' ' + monthly['year'].astype(str)
        fig = px.area(monthly, x='period', y='revenue', color='year',
                      color_discrete_sequence=['#6366f1','#22d3ee','#10b981'])
        fig.update_traces(mode='lines+markers', line_width=2.5, marker_size=5)
        fig.update_layout(**PLOTLY_THEME, height=300, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header"><h2>Revenue by Category</h2></div>', unsafe_allow_html=True)
        cat_rev = df.groupby('category')['revenue'].sum().sort_values(ascending=True).reset_index()
        fig = px.bar(cat_rev, x='revenue', y='category', orientation='h',
                     color='revenue', color_continuous_scale='Viridis')
        fig.update_layout(**PLOTLY_THEME, height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── ROW 2: Region Map + Channel + Segment ──
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown('<div class="section-header"><h2>Region Performance</h2></div>', unsafe_allow_html=True)
        region_data = df.groupby('region').agg(revenue=('revenue','sum'), orders=('order_id','count')).reset_index()
        fig = px.pie(region_data, names='region', values='revenue',
                     hole=0.55, color_discrete_sequence=['#6366f1','#22d3ee','#10b981','#f59e0b','#ef4444'])
        fig.update_layout(**PLOTLY_THEME, height=280, showlegend=True,
                          legend=dict(orientation='v', x=1.0))
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header"><h2>Channel Mix</h2></div>', unsafe_allow_html=True)
        ch_data = df.groupby('channel')['revenue'].sum().reset_index()
        fig = px.bar(ch_data, x='channel', y='revenue',
                     color='channel', color_discrete_sequence=['#6366f1','#22d3ee','#10b981','#f59e0b'])
        fig.update_layout(**PLOTLY_THEME, height=280, showlegend=False, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    with col5:
        st.markdown('<div class="section-header"><h2>Customer Segments</h2></div>', unsafe_allow_html=True)
        seg_data = df.groupby('customer_segment')['revenue'].sum().reset_index()
        fig = px.pie(seg_data, names='customer_segment', values='revenue',
                     color_discrete_sequence=['#6366f1','#22d3ee','#10b981','#f59e0b'])
        fig.update_layout(**PLOTLY_THEME, height=280)
        st.plotly_chart(fig, use_container_width=True)

    # ── ROW 3: Payment Methods + Shipping Status + Weekly Heatmap ──
    col6, col7 = st.columns([1, 2])

    with col6:
        st.markdown('<div class="section-header"><h2>Payment Methods</h2></div>', unsafe_allow_html=True)
        pay_data = df.groupby('payment_method')['revenue'].sum().sort_values(ascending=False).reset_index()
        fig = px.funnel(pay_data, x='revenue', y='payment_method',
                        color_discrete_sequence=['#6366f1'])
        fig.update_layout(**PLOTLY_THEME, height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col7:
        st.markdown('<div class="section-header"><h2>Weekly Revenue Heatmap</h2></div>', unsafe_allow_html=True)
        df['dow'] = df['order_date'].dt.day_name()
        pivot_data = df.groupby(['week', 'dow'])['revenue'].sum().reset_index()
        pivot = pivot_data.pivot(index='dow', columns='week', values='revenue').fillna(0)
        day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        pivot = pivot.reindex([d for d in day_order if d in pivot.index])
        fig = px.imshow(pivot, color_continuous_scale='Purples', aspect='auto')
        fig.update_layout(**PLOTLY_THEME, height=300)
        st.plotly_chart(fig, use_container_width=True)

    # ── ROW 4: Top Products Table ──
    st.markdown('<div class="section-header"><h2>Top Products Performance</h2><span class="section-badge">Live</span></div>', unsafe_allow_html=True)
    top_prod = df.groupby(['product_name','category']).agg(
        revenue=('revenue','sum'),
        orders=('order_id','count'),
        avg_rating=('rating','mean'),
        profit=('profit','sum')
    ).reset_index().sort_values('revenue', ascending=False).head(15)
    top_prod['revenue'] = top_prod['revenue'].round(0).astype(int)
    top_prod['profit'] = top_prod['profit'].round(0).astype(int)
    top_prod['avg_rating'] = top_prod['avg_rating'].round(2)
    st.dataframe(top_prod, use_container_width=True, height=350,
                 column_config={
                     "revenue": st.column_config.NumberColumn("Revenue (₹)", format="₹%d"),
                     "profit": st.column_config.NumberColumn("Profit (₹)", format="₹%d"),
                     "avg_rating": st.column_config.ProgressColumn("Avg Rating", min_value=1, max_value=5),
                     "orders": st.column_config.NumberColumn("Orders"),
                 })

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: FULL EDA
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🔬 Exploratory Data Analysis")
    
    # Dataset Overview
    st.markdown("### 📋 Dataset Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{df.shape[0]:,}")
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", df.isnull().sum().sum())
    c4.metric("Duplicates", df.duplicated().sum())

    with st.expander("📄 Raw Data Preview (First 100 rows)"):
        st.dataframe(df.head(100), use_container_width=True)

    with st.expander("📊 Descriptive Statistics"):
        st.dataframe(df.describe().T.round(3), use_container_width=True)

    with st.expander("🔍 Data Types & Missing Values"):
        dtype_df = pd.DataFrame({
            'Column': df.columns,
            'DType': df.dtypes.astype(str).values,
            'Non-Null': df.notnull().sum().values,
            'Null Count': df.isnull().sum().values,
            'Null %': (df.isnull().sum() / len(df) * 100).round(2).values,
            'Unique Values': df.nunique().values
        })
        st.dataframe(dtype_df, use_container_width=True)

    # Univariate Analysis
    st.markdown("### 📊 Univariate Analysis")
    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Numerical distributions
    st.markdown("**Numerical Distributions**")
    sel_num = st.selectbox("Select numerical column", num_cols)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df, x=sel_num, nbins=40, color_discrete_sequence=['#6366f1'],
                           marginal='box', title=f'Distribution of {sel_num}')
        fig.update_layout(**PLOTLY_THEME, height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.violin(df, y=sel_num, color_discrete_sequence=['#22d3ee'],
                        box=True, points='outliers', title=f'Violin Plot: {sel_num}')
        fig.update_layout(**PLOTLY_THEME, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Categorical distributions
    st.markdown("**Categorical Distributions**")
    sel_cat = st.selectbox("Select categorical column", cat_cols)
    cat_counts = df[sel_cat].value_counts().reset_index()
    cat_counts.columns = [sel_cat, 'count']
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cat_counts, x=sel_cat, y='count', color='count',
                     color_continuous_scale='Viridis', title=f'Count: {sel_cat}')
        fig.update_layout(**PLOTLY_THEME, height=350, coloraxis_showscale=False, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(cat_counts, names=sel_cat, values='count', hole=0.4,
                     title=f'Share: {sel_cat}')
        fig.update_layout(**PLOTLY_THEME, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Bivariate Analysis
    st.markdown("### 🔗 Bivariate Analysis")
    c1, c2 = st.columns(2)
    with c1:
        x_col = st.selectbox("X axis", num_cols, key="biv_x")
    with c2:
        y_col = st.selectbox("Y axis", num_cols, index=1, key="biv_y")

    color_col = st.selectbox("Color by", ['None'] + cat_cols, key="biv_c")
    fig = px.scatter(df.sample(min(1000, len(df))),
                     x=x_col, y=y_col,
                     color=None if color_col == 'None' else color_col,
                     trendline='ols' if color_col == 'None' else None,
                     opacity=0.6, title=f'{x_col} vs {y_col}',
                     color_discrete_sequence=['#6366f1','#22d3ee','#10b981','#f59e0b','#ef4444'])
    fig.update_layout(**PLOTLY_THEME, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Box plots by category
    st.markdown("**Revenue Distribution by Category**")
    fig = px.box(df, x='category', y='revenue', color='category',
                 color_discrete_sequence=['#6366f1','#22d3ee','#10b981','#f59e0b','#ef4444','#a78bfa','#34d399','#fbbf24'],
                 title='Revenue Box Plot by Category', points='outliers')
    fig.update_layout(**PLOTLY_THEME, height=400, showlegend=False, xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

    # Correlation Heatmap
    st.markdown("### 🌡️ Correlation Heatmap")
    corr_cols = [c for c in num_cols if c not in ['month','quarter','year','week']]
    corr = df[corr_cols].corr()
    fig = px.imshow(corr, text_auto='.2f', color_continuous_scale='RdBu_r',
                    aspect='auto', title='Feature Correlation Matrix',
                    zmin=-1, zmax=1)
    fig.update_layout(**PLOTLY_THEME, height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Outlier Detection
    st.markdown("### 🚨 Outlier Detection (IQR Method)")
    outlier_col = st.selectbox("Detect outliers in", num_cols, key='out_col')
    Q1 = df[outlier_col].quantile(0.25)
    Q3 = df[outlier_col].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df[(df[outlier_col] < Q1 - 1.5*IQR) | (df[outlier_col] > Q3 + 1.5*IQR)]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Outliers", len(outliers))
    c2.metric("Outlier %", f"{len(outliers)/len(df)*100:.2f}%")
    c3.metric("IQR Range", f"{Q1:.1f} - {Q3:.1f}")
    
    fig = go.Figure()
    fig.add_trace(go.Box(y=df[outlier_col], name=outlier_col,
                          marker_color='#6366f1', boxpoints='outliers',
                          jitter=0.3, pointpos=-1.8))
    fig.update_layout(**PLOTLY_THEME, height=350, title=f'Box Plot with Outliers: {outlier_col}')
    st.plotly_chart(fig, use_container_width=True)

    # Time Series Decomposition
    st.markdown("### 📅 Time Series Analysis")
    ts_metric = st.selectbox("Time series metric", ['revenue', 'profit', 'quantity'], key='ts_m')
    ts = df.groupby('order_date')[ts_metric].sum().reset_index()
    ts_weekly = ts.set_index('order_date').resample('W').sum().reset_index()
    fig = px.line(ts_weekly, x='order_date', y=ts_metric,
                  title=f'Weekly {ts_metric.title()} Trend',
                  color_discrete_sequence=['#6366f1'])
    fig.update_traces(line_width=2)
    fig.add_traces(go.Scatter(x=ts_weekly['order_date'],
                               y=ts_weekly[ts_metric].rolling(4).mean(),
                               mode='lines', name='4-week MA',
                               line=dict(color='#22d3ee', width=2, dash='dot')))
    fig.update_layout(**PLOTLY_THEME, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: ADVANCED ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📈 Advanced Analytics")

    # Cohort Analysis (simplified)
    st.markdown("### 🧩 Category × Region Revenue Matrix")
    pivot_cat_region = df.pivot_table(values='revenue', index='category',
                                       columns='region', aggfunc='sum').fillna(0)
    fig = px.imshow(pivot_cat_region.round(0), text_auto='.2s',
                    color_continuous_scale='Blues', aspect='auto',
                    title='Revenue Heatmap: Category × Region')
    fig.update_layout(**PLOTLY_THEME, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # RFM Segmentation
    st.markdown("### 🎯 RFM Customer Segmentation")
    snapshot_date = df['order_date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_id').agg(
        recency=('order_date', lambda x: (snapshot_date - x.max()).days),
        frequency=('order_id', 'count'),
        monetary=('revenue', 'sum')
    ).reset_index()
    rfm['r_score'] = pd.qcut(rfm['recency'], q=4, labels=[4,3,2,1], duplicates='drop')
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=4, labels=[1,2,3,4], duplicates='drop')
    rfm['m_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1,2,3,4], duplicates='drop')
    rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)
    rfm['segment'] = pd.cut(rfm['rfm_score'], bins=[2,5,8,12],
                             labels=['At Risk','Regular','Champions'])

    c1, c2 = st.columns(2)
    with c1:
        seg_counts = rfm['segment'].value_counts().reset_index()
        seg_counts.columns = ['segment', 'count']
        fig = px.pie(seg_counts, names='segment', values='count', hole=0.5,
                     color_discrete_sequence=['#ef4444','#f59e0b','#10b981'],
                     title='Customer Segments')
        fig.update_layout(**PLOTLY_THEME, height=320)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.scatter(rfm.sample(min(500, len(rfm))),
                         x='frequency', y='monetary', size='recency',
                         color='segment', opacity=0.7,
                         color_discrete_sequence=['#ef4444','#f59e0b','#10b981'],
                         title='RFM Scatter: Frequency vs Monetary',
                         size_max=15)
        fig.update_layout(**PLOTLY_THEME, height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Quarter-over-Quarter
    st.markdown("### 📊 Quarter-over-Quarter Growth")
    qoq = df.groupby(['year','quarter'])['revenue'].sum().reset_index()
    qoq['label'] = 'Q' + qoq['quarter'].astype(str) + ' ' + qoq['year'].astype(str)
    qoq['growth'] = qoq['revenue'].pct_change() * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=qoq['label'], y=qoq['revenue'],
                          name='Revenue', marker_color='#6366f1'), secondary_y=False)
    fig.add_trace(go.Scatter(x=qoq['label'], y=qoq['growth'],
                              mode='lines+markers', name='QoQ Growth %',
                              line=dict(color='#22d3ee', width=2.5),
                              marker=dict(size=7)), secondary_y=True)
    fig.update_layout(**PLOTLY_THEME, height=380, title='QoQ Revenue & Growth Rate')
    fig.update_yaxes(title_text="Revenue", secondary_y=False)
    fig.update_yaxes(title_text="Growth %", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    # Discount Impact Analysis
    st.markdown("### 💸 Discount Impact on Revenue & Returns")
    disc_impact = df.groupby('discount_pct').agg(
        avg_revenue=('revenue','mean'),
        return_rate=('return_flag','mean'),
        order_count=('order_id','count')
    ).reset_index()
    disc_impact['return_rate'] *= 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=disc_impact['discount_pct'], y=disc_impact['avg_revenue'],
                          name='Avg Revenue', marker_color='#10b981'), secondary_y=False)
    fig.add_trace(go.Scatter(x=disc_impact['discount_pct'], y=disc_impact['return_rate'],
                              mode='lines+markers', name='Return Rate %',
                              line=dict(color='#ef4444', width=2.5)), secondary_y=True)
    fig.update_layout(**PLOTLY_THEME, height=350, title='Discount % vs Avg Revenue & Return Rate',
                      xaxis_title='Discount %')
    st.plotly_chart(fig, use_container_width=True)

    # Category Profitability
    st.markdown("### 💰 Category Profitability Analysis")
    cat_prof = df.groupby('category').agg(
        revenue=('revenue','sum'),
        profit=('profit','sum'),
        orders=('order_id','count'),
        avg_rating=('rating','mean')
    ).reset_index()
    cat_prof['margin'] = cat_prof['profit'] / cat_prof['revenue'] * 100
    fig = px.scatter(cat_prof, x='revenue', y='profit', size='orders',
                     color='margin', text='category',
                     color_continuous_scale='RdYlGn',
                     size_max=40, title='Revenue vs Profit (bubble=orders, color=margin%)')
    fig.update_traces(textposition='top center', textfont_size=10)
    fig.update_layout(**PLOTLY_THEME, height=420)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: AI ANALYST (Claude)
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 🤖 AI Data Analyst — Powered by Claude")
    st.markdown("Ask anything about your e-commerce data. Claude will analyze it in real-time.")

    # Prepare data summary for context
    @st.cache_data
    def build_context(df_hash):
        summary = {
            "total_orders": len(df),
            "date_range": f"{df['order_date'].min().date()} to {df['order_date'].max().date()}",
            "total_revenue": round(df['revenue'].sum(), 2),
            "total_profit": round(df['profit'].sum(), 2),
            "avg_order_value": round(df['revenue'].mean(), 2),
            "unique_customers": df['customer_id'].nunique(),
            "categories": df['category'].unique().tolist(),
            "regions": df['region'].unique().tolist(),
            "channels": df['channel'].unique().tolist(),
            "top_category": df.groupby('category')['revenue'].sum().idxmax(),
            "top_region": df.groupby('region')['revenue'].sum().idxmax(),
            "avg_discount": round(df['discount_pct'].mean(), 2),
            "return_rate_pct": round(df['return_flag'].mean() * 100, 2),
            "avg_rating": round(df['rating'].mean(), 2),
            "columns": df.columns.tolist(),
            "sample_rows": df.head(5).to_dict(orient='records'),
            "category_revenue": df.groupby('category')['revenue'].sum().to_dict(),
            "region_revenue": df.groupby('region')['revenue'].sum().to_dict(),
            "channel_revenue": df.groupby('channel')['revenue'].sum().to_dict(),
            "monthly_revenue": df.groupby(['year','month'])['revenue'].sum().to_dict(),
        }
        return summary
    
    # Use a simple hash to cache context
    ctx = build_context(len(df))

    SYSTEM_PROMPT = f"""You are an expert e-commerce data analyst. You have access to a dataset with {ctx['total_orders']:,} orders.

DATASET SUMMARY:
- Date Range: {ctx['date_range']}
- Total Revenue: ₹{ctx['total_revenue']:,.2f}
- Total Profit: ₹{ctx['total_profit']:,.2f}
- Avg Order Value: ₹{ctx['avg_order_value']:,.2f}
- Unique Customers: {ctx['unique_customers']:,}
- Categories: {', '.join(ctx['categories'])}
- Regions: {', '.join(ctx['regions'])}
- Channels: {', '.join(ctx['channels'])}
- Top Category: {ctx['top_category']}
- Top Region: {ctx['top_region']}
- Avg Discount: {ctx['avg_discount']}%
- Return Rate: {ctx['return_rate_pct']}%
- Avg Rating: {ctx['avg_rating']}

CATEGORY REVENUE: {ctx['category_revenue']}
REGION REVENUE: {ctx['region_revenue']}
CHANNEL REVENUE: {ctx['channel_revenue']}

Respond with clear, structured insights. Use bullet points, numbers, and percentages where relevant.
Be concise but insightful. If asked for recommendations, provide actionable ones.
When showing numbers, use ₹ for currency and format large numbers clearly."""

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Quick questions
    st.markdown("**💡 Quick Questions:**")
    quick_qs = [
        "What are the top 3 revenue-driving categories?",
        "Which region needs attention and why?",
        "How is the discount strategy affecting profitability?",
        "What's the customer retention story?",
        "Give me an executive summary of the business",
    ]
    q_cols = st.columns(3)
    for i, q in enumerate(quick_qs[:3]):
        if q_cols[i].button(q, key=f"quick_{i}", use_container_width=True):
            st.session_state.pending_query = q

    q_cols2 = st.columns(2)
    for i, q in enumerate(quick_qs[3:]):
        if q_cols2[i].button(q, key=f"quick2_{i}", use_container_width=True):
            st.session_state.pending_query = q

    st.markdown("---")

    # Chat display
    chat_placeholder = st.container()
    with chat_placeholder:
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""
                    <div style='margin: 12px 0'>
                        <div class='chat-msg-label'>YOU</div>
                        <div class='chat-msg-user'>{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='margin: 12px 0'>
                        <div class='chat-msg-label'>CLAUDE</div>
                        <div class='chat-msg-ai'>{msg['content']}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align:center;padding:40px;color:#64748b;'>
                <div style='font-size:2rem;margin-bottom:12px'>🤖</div>
                <div>Ask Claude anything about your data above</div>
            </div>""", unsafe_allow_html=True)

    # Input
    user_input = st.text_area("💬 Your question:", height=80,
                               value=st.session_state.pop("pending_query", ""),
                               placeholder="e.g. Which product category has the best profit margin?")

    col_a, col_b, col_c = st.columns([2, 1, 1])
    send_btn = col_a.button("🚀 Ask Claude", use_container_width=True)
    clear_btn = col_b.button("🗑️ Clear Chat", use_container_width=True)
    export_btn = col_c.button("📋 Export Chat", use_container_width=True)

    if clear_btn:
        st.session_state.chat_history = []
        st.rerun()

    if export_btn and st.session_state.chat_history:
        chat_text = "\n\n".join([f"{'USER' if m['role']=='user' else 'CLAUDE'}: {m['content']}"
                                  for m in st.session_state.chat_history])
        st.download_button("⬇️ Download", chat_text, "chat_export.txt", "text/plain")

    if send_btn and user_input.strip():
        if "anthropic_key" not in st.session_state or not st.session_state.anthropic_key:
            st.error("⚠️ Please enter your Anthropic API key in the sidebar.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
            
            with st.spinner("Claude is analyzing your data..."):
                try:
                    client = anthropic.Anthropic(api_key=st.session_state.anthropic_key)
                    messages = [{"role": m["role"], "content": m["content"]}
                                for m in st.session_state.chat_history]
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=1500,
                        system=SYSTEM_PROMPT,
                        messages=messages
                    )
                    answer = response.content[0].text
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()
                except anthropic.AuthenticationError:
                    st.error("❌ Invalid API key. Please check your Anthropic API key.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
