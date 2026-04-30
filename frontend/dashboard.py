"""name=app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AirSense Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------
# Custom CSS (embedded)
# -----------------------
CSS = """
:root{
  --bg: #f6f8fb;
  --card-bg: #ffffff;
  --muted: #6b7280;
  --accent: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
  --shadow: 0 6px 18px rgba(28, 32, 38, 0.08);
  --radius: 12px;
  --glass: rgba(255,255,255,0.6);
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  :root{
    --bg: #0b1020;
    --card-bg: #0f1724;
    --muted: #9aa4b2;
    --shadow: 0 6px 18px rgba(2,6,23,0.6);
    --glass: rgba(255,255,255,0.02);
  }
}

[data-testid="stSidebar"] > div:first-child {
  padding-top: 1rem;
}

/* Page background and container */
.css-1lcbmhc {  /* main app container class can vary; we set body background generically */
  background: var(--bg) !important;
}

/* Cards */
.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}

/* KPI small card */
.kpi {
  padding: 14px;
  border-radius: calc(var(--radius) - 4px);
  background: linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.4));
  text-align: left;
}

/* Title / header */
.header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header h1 {
  margin: 0;
  font-size: 1.35rem;
}

/* Gradient button */
.stButton>button {
  background: var(--accent);
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  box-shadow: none;
}
.stButton>button:hover {
  filter: brightness(1.02);
  transform: translateY(-1px);
}

/* Small muted text */
.muted {
  color: var(--muted);
  font-size: 0.9rem;
}

/* Card title */
.card-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 6px;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .card { padding: 12px; }
  .header h1 { font-size: 1.1rem; }
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# -----------------------
# Sample / placeholder data generation
# -----------------------
@st.cache_data(show_spinner=False)
def load_sample_data(days: int = 90):
    """Generates sample time-series air quality data."""
    rng = pd.date_range(end=datetime.now(), periods=days, freq="D")
    np.random.seed(42)
    base_pm = np.clip(35 + np.random.randn(days).cumsum() * 0.5, 5, 200)
    temp = 20 + 4 * np.sin(np.linspace(0, 3.14, days)) + np.random.randn(days) * 0.6
    humidity = np.clip(60 + 5 * np.cos(np.linspace(0, 3.14, days)) + np.random.randn(days) * 2, 10, 100)
    df = pd.DataFrame({
        "timestamp": rng,
        "pm25": base_pm,
        "temperature": temp,
        "humidity": humidity,
    })
    # a mock "predicted" column for demo
    df["pm25_pred"] = df["pm25"].shift(1).fillna(df["pm25"].mean()) + np.random.randn(days) * 1.5
    return df

data = load_sample_data(120)


# -----------------------
# Utility components
# -----------------------
def format_kpi_label(label: str, value, delta=None, unit=""):
    delta_str = f"{delta:+.1f}" if delta is not None else ""
    return f"<div class='kpi'><div style='display:flex;justify-content:space-between;align-items:center'>\
                <div style='font-size:0.9rem;color:var(--muted)'>{label}</div>\
                <div style='font-weight:600;font-size:1.05rem'>{value}{unit}</div></div>\
                {'<div class=muted style=\"margin-top:6px\">Change: '+delta_str+'</div>' if delta is not None else ''}</div>"

def plot_time_series(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pm25'], mode='lines', name='PM2.5', line=dict(color='#2575fc')))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pm25_pred'], mode='lines', name='Predicted PM2.5', line=dict(color='#6a11cb', dash='dash')))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        template='plotly_white'
    )
    return fig

def plot_distribution(df: pd.DataFrame):
    fig = px.histogram(df, x="pm25", nbins=30, title="PM2.5 Distribution", color_discrete_sequence=['#2575fc'])
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), template='plotly_white')
    return fig

def plot_corr_heatmap(df: pd.DataFrame):
    corr = df[["pm25", "temperature", "humidity", "pm25_pred"]].corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r', origin='lower')
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), template='plotly_white')
    return fig

def feature_importance_mock():
    features = ["temperature", "humidity", "wind_speed", "traffic_index", "industrial_index"]
    importance = [0.35, 0.25, 0.15, 0.15, 0.10]
    fig = px.bar(x=importance, y=features, orientation='h', labels={'x':'Importance','y':'Feature'}, title="Feature importance (mock)")
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), template='plotly_white')
    return fig

# -----------------------
# Page renderers
# -----------------------
def render_header():
    st.markdown(
        """
        <div class="header">
          <div>
            <h1>AirSense — Environmental Monitoring</h1>
            <div class="muted">Clean, minimal, and responsive dashboard for air quality</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")


def render_kpis(df: pd.DataFrame):
    latest = df.iloc[-1]
    prev = df.iloc[-8:-1].mean()
    col1, col2, col3, col4 = st.columns([1.5,1.2,1.2,1.2], gap="large")

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Key Metrics</div>", unsafe_allow_html=True)
        kpi_html = format_kpi_label("PM2.5 (current)", f"{latest['pm25']:.1f}", delta=latest['pm25']-prev['pm25'], unit=" µg/m³")
        st.markdown(kpi_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Temperature", f"{latest['temperature']:.1f} °C", delta=f"{latest['temperature'] - prev['temperature']:.1f} °C")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Humidity", f"{latest['humidity']:.0f} %", delta=f"{latest['humidity'] - prev['humidity']:.0f} %")
        st.markdown("</div>", unsafe_allow_html=True)

    with col4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.metric("Predicted PM2.5", f"{latest['pm25_pred']:.1f} µg/m³", delta=f"{latest['pm25_pred']-latest['pm25']:+.1f}")
        st.markdown("</div>", unsafe_allow_html=True)


def render_chart_cards(df: pd.DataFrame):
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Trends")
        st.markdown("Recent measurements and model predictions", unsafe_allow_html=True)
        fig = plot_time_series(df)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader("Distribution")
            st.plotly_chart(plot_distribution(df), use_container_width=True)
        with col2:
            st.subheader("Correlations")
            st.plotly_chart(plot_corr_heatmap(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_dashboard(df: pd.DataFrame):
    render_header()
    render_kpis(df)
    render_chart_cards(df)

    # Additional insights strip
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Quick Insights")
        cols = st.columns([1,1,1], gap="large")
        with cols[0]:
            st.markdown("<div class='card-title'>High pollution days</div>", unsafe_allow_html=True)
            high_days = (df['pm25'] > 75).sum()
            st.markdown(f"<div style='font-weight:700;font-size:1.1rem'>{high_days} days</div>", unsafe_allow_html=True)
            st.markdown("<div class='muted'>Days with PM2.5 &gt; 75 µg/m³ in the period</div>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown("<div class='card-title'>Avg PM2.5</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-weight:700;font-size:1.1rem'>{df['pm25'].mean():.1f} µg/m³</div>", unsafe_allow_html=True)
            st.markdown("<div class='muted'>Mean across selected period</div>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown("<div class='card-title'>Most volatile metric</div>", unsafe_allow_html=True)
            vols = df[["pm25","temperature","humidity"]].std().sort_values(ascending=False)
            top = vols.index[0]
            st.markdown(f"<div style='font-weight:700;font-size:1.1rem'>{top}</div>", unsafe_allow_html=True)
            st.markdown("<div class='muted'>Highest standard deviation</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_predictions(df: pd.DataFrame):
    st.header("Predictions")
    st.markdown("Use a simple interactive form to generate short-term predictions (demo).", unsafe_allow_html=True)

    left, right = st.columns([2,1], gap="large")
    with left:
        # A scenic quick-predict form
        with st.form("predict_form"):
            st.subheader("Model input")
            input_date = st.date_input("Prediction date", value=(datetime.now() + timedelta(days=1)).date())
            pm_now = st.number_input("Current PM2.5", value=float(df['pm25'].iloc[-1]), step=0.1, format="%.1f")
            temp = st.slider("Temperature (°C)", min_value=-10.0, max_value=50.0, value=float(df['temperature'].iloc[-1]))
            humidity = st.slider("Humidity (%)", min_value=0, max_value=100, value=int(df['humidity'].iloc[-1]))
            st.markdown("### Advanced")
            wind = st.slider("Wind speed (m/s)", 0.0, 20.0, 3.2)
            traffic = st.selectbox("Traffic level", ["Low", "Medium", "High"])
            submitted = st.form_submit_button("Run prediction")
            if submitted:
                # simple mock prediction logic for demo (replace with real model)
                traffic_factor = {"Low": -2, "Medium": 0, "High": 3}[traffic]
                pred = pm_now * 0.98 + (temp - 20) * 0.2 + (50 - humidity) * 0.05 + wind * -0.3 + traffic_factor + np.random.randn() * 1.5
                st.success(f"Predicted PM2.5 for {input_date}: {pred:.1f} µg/m³")
                st.info("This is a demo prediction. Plug in your ML model to replace the mock logic.")
    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Model summary (demo)")
        st.markdown("- Lightweight linear model (demo)\n- Features: PM2.5 lag, temp, humidity, wind, traffic\n- Last trained: not trained (stub)")
        st.markdown("</div>", unsafe_allow_html=True)

    # Visualize predictions vs. historical
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Recent actual vs. predicted")
    fig = plot_time_series(df.tail(60))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_insights(df: pd.DataFrame):
    st.header("Insights")
    st.markdown("Actionable insights and feature analyses", unsafe_allow_html=True)
    col1, col2 = st.columns([1,1], gap="large")

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Feature importance")
        st.plotly_chart(feature_importance_mock(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Top correlations")
        corr_df = df[["pm25", "temperature", "humidity"]].corr().unstack().reset_index()
        corr_df.columns = ["feature_a", "feature_b", "corr"]
        corr_df = corr_df[corr_df["feature_a"] != corr_df["feature_b"]].drop_duplicates(subset=["corr"])
        st.dataframe(corr_df.sort_values("corr", ascending=False).head(6).reset_index(drop=True), width=700)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Seasonality & patterns")
        # a small seasonal decomposition-like visualization (mock)
        seasonal = df.copy()
        seasonal['dayofyear'] = seasonal['timestamp'].dt.dayofyear
        fig = px.scatter(seasonal, x='dayofyear', y='pm25', color='temperature', title='Daily seasonality (scatter)')
        fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='card'><div class='card-title'>Suggested actions</div>"
        "<ul><li>Investigate high-pollution clusters on specific dates</li>"
        "<li>Cross-check sensor locations with traffic/industry data</li>"
        "<li>Deploy model retraining pipeline for better forecasts</li></ul></div>",
        unsafe_allow_html=True,
    )


# -----------------------
# Sidebar - Navigation
# -----------------------
with st.sidebar:
    st.markdown("<div style='padding:8px 8px 12px 8px'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0'>Navigation</h3>", unsafe_allow_html=True)
    page = st.radio("", ["Dashboard", "Predictions", "Insights"], index=0)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Display options")
    days = st.slider("Days to show", min_value=14, max_value=365, value=120, step=1)
    st.markdown("### Quick actions")
    if st.button("Refresh data"):
        st.experimental_rerun()

# filter data according to days selection
df = data.tail(days).reset_index(drop=True)

# -----------------------
# Router
# -----------------------
if page == "Dashboard":
    render_dashboard(df)
elif page == "Predictions":
    render_predictions(df)
elif page == "Insights":
    render_insights(df)
else:
    st.write("Unknown page")