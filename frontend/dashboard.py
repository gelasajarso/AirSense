"""
AirSense Dashboard - Integrated with API
Production-ready dashboard with real data from API
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional
import json

# Page configuration
st.set_page_config(
    page_title="AirSense - Air Quality Monitoring",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

# Custom CSS
CSS = """
<style>
:root {
  --primary: #2575fc;
  --secondary: #6a11cb;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --text: #1e293b;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.main-header {
  background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: var(--shadow);
}

.main-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
}

.main-header p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
}

.metric-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--shadow);
  border-left: 4px solid var(--primary);
}

.aqi-good { border-left-color: var(--success); }
.aqi-moderate { border-left-color: var(--warning); }
.aqi-unhealthy { border-left-color: var(--danger); }

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-good { background: #d1fae5; color: #065f46; }
.status-moderate { background: #fef3c7; color: #92400e; }
.status-unhealthy { background: #fee2e2; color: #991b1b; }

.info-box {
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.stButton>button {
  background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  transition: transform 0.2s;
}

.stButton>button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ==================== API Functions ====================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_api_data(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Fetch data from API with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to API at {API_BASE_URL}. Please ensure the API server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ API request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def post_api_data(endpoint: str, data: Dict) -> Optional[Dict]:
    """Post data to API with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

@st.cache_data(ttl=300)
def get_air_quality_data(limit: int = 1000) -> Optional[pd.DataFrame]:
    """Get air quality data from API."""
    data = fetch_api_data("/data", params={"limit": limit})
    if data and "data" in data:
        df = pd.DataFrame(data["data"])
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    return None

@st.cache_data(ttl=300)
def get_statistics() -> Optional[Dict]:
    """Get statistical summary from API."""
    return fetch_api_data("/stats")

@st.cache_data(ttl=300)
def get_aqi() -> Optional[Dict]:
    """Get current AQI from API."""
    return fetch_api_data("/aqi")

@st.cache_data(ttl=600)
def get_time_patterns(pollutant: str, analysis_type: str = "comprehensive") -> Optional[Dict]:
    """Get time-based pattern analysis from API."""
    return fetch_api_data("/analysis/time-patterns", params={
        "pollutant": pollutant,
        "analysis_type": analysis_type
    })

@st.cache_data(ttl=600)
def get_correlations(analysis_type: str = "comprehensive") -> Optional[Dict]:
    """Get correlation analysis from API."""
    return fetch_api_data("/analysis/correlations", params={
        "analysis_type": analysis_type
    })

def generate_forecast(pollutant: str, method: str, steps: int = 24, **kwargs) -> Optional[Dict]:
    """Generate forecast using API."""
    data = {
        "pollutant": pollutant,
        "method": method,
        "forecast_steps": steps,
        **kwargs
    }
    return post_api_data("/forecast/simple", data)

# ==================== Visualization Functions ====================

def plot_time_series_multi(df: pd.DataFrame, pollutants: List[str]):
    """Plot multiple pollutants over time."""
    fig = go.Figure()
    
    colors = ['#2575fc', '#6a11cb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    for i, pollutant in enumerate(pollutants):
        if pollutant in df.columns:
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df[pollutant],
                mode='lines',
                name=pollutant,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
    
    fig.update_layout(
        title="Pollutant Levels Over Time",
        xaxis_title="Date",
        yaxis_title="Concentration (µg/m³)",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig

def plot_forecast_with_confidence(forecast_data: Dict):
    """Plot forecast with confidence intervals."""
    fig = go.Figure()
    
    forecast = forecast_data.get("forecast", [])
    
    if isinstance(forecast, dict) and "forecast" in forecast:
        # Extract forecast values
        values = forecast["forecast"]
        x = list(range(len(values)))
        
        # Add forecast line
        fig.add_trace(go.Scatter(
            x=x,
            y=values,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#2575fc', width=3)
        ))
        
        # Add confidence intervals if available
        if "confidence_lower" in forecast and "confidence_upper" in forecast:
            fig.add_trace(go.Scatter(
                x=x + x[::-1],
                y=forecast["confidence_upper"] + forecast["confidence_lower"][::-1],
                fill='toself',
                fillcolor='rgba(37, 117, 252, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence',
                showlegend=True
            ))
    
    fig.update_layout(
        title="Forecast with Confidence Intervals",
        xaxis_title="Hours Ahead",
        yaxis_title="Predicted Value (µg/m³)",
        template='plotly_white',
        height=400
    )
    
    return fig

def plot_correlation_heatmap(corr_data: Dict):
    """Plot correlation heatmap."""
    if "result" in corr_data and "pollutant_correlations" in corr_data["result"]:
        corr_matrix = corr_data["result"]["pollutant_correlations"].get("correlation_matrix", {})
        
        if corr_matrix:
            # Convert to DataFrame
            df_corr = pd.DataFrame(corr_matrix)
            
            fig = px.imshow(
                df_corr,
                text_auto='.2f',
                aspect="auto",
                color_continuous_scale='RdBu_r',
                color_continuous_midpoint=0,
                title="Pollutant Correlation Matrix"
            )
            
            fig.update_layout(
                template='plotly_white',
                height=500
            )
            
            return fig
    
    return None

def plot_daily_patterns(pattern_data: Dict):
    """Plot daily patterns."""
    if "result" in pattern_data:
        result = pattern_data["result"]
        
        if isinstance(result, dict) and "individual_analyses" in result:
            # Get first pollutant's daily analysis
            for pollutant, analysis in result["individual_analyses"].items():
                if "daily" in analysis:
                    daily_stats = analysis["daily"].get("hourly_stats", [])
                    
                    if daily_stats:
                        df = pd.DataFrame(daily_stats)
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df['hour'],
                            y=df['mean'],
                            mode='lines+markers',
                            name='Average',
                            line=dict(color='#2575fc', width=3),
                            error_y=dict(
                                type='data',
                                array=df['std'],
                                visible=True
                            )
                        ))
                        
                        fig.update_layout(
                            title=f"Daily Pattern - {pollutant}",
                            xaxis_title="Hour of Day",
                            yaxis_title="Concentration (µg/m³)",
                            template='plotly_white',
                            height=400
                        )
                        
                        return fig
    
    return None

# ==================== Page Components ====================

def render_header():
    """Render main header."""
    st.markdown("""
        <div class="main-header">
            <h1>🌤️ AirSense - Air Quality Monitoring System</h1>
            <p>Real-time air quality analysis, forecasting, and environmental monitoring</p>
        </div>
    """, unsafe_allow_html=True)

def render_aqi_card():
    """Render current AQI card."""
    aqi_data = get_aqi()
    
    if aqi_data:
        aqi = aqi_data.get("aqi", 0)
        level = aqi_data.get("level", "Unknown")
        health_impact = aqi_data.get("health_impact", "")
        recommendations = aqi_data.get("recommendations", "")
        
        # Determine AQI class
        if aqi <= 50:
            aqi_class = "aqi-good"
            status_class = "status-good"
        elif aqi <= 100:
            aqi_class = "aqi-moderate"
            status_class = "status-moderate"
        else:
            aqi_class = "aqi-unhealthy"
            status_class = "status-unhealthy"
        
        st.markdown(f"""
            <div class="metric-card {aqi_class}">
                <h3 style="margin-top:0;">Current Air Quality Index</h3>
                <div style="display:flex;align-items:center;gap:1rem;margin:1rem 0;">
                    <div style="font-size:3rem;font-weight:700;color:var(--primary);">{aqi}</div>
                    <div>
                        <span class="status-badge {status_class}">{level}</span>
                        <p style="margin:0.5rem 0 0 0;color:var(--text-muted);">{health_impact}</p>
                    </div>
                </div>
                <div class="info-box">
                    <strong>💡 Recommendation:</strong> {recommendations}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Unable to fetch current AQI. Please check API connection.")

def render_statistics_cards():
    """Render statistics cards."""
    stats = get_statistics()
    
    if stats and "statistics" in stats:
        pollutant_stats = stats["statistics"]
        
        cols = st.columns(len(pollutant_stats))
        
        for i, (pollutant, data) in enumerate(pollutant_stats.items()):
            with cols[i]:
                st.metric(
                    label=pollutant,
                    value=f"{data.get('latest', 0):.1f} µg/m³",
                    delta=f"{data.get('latest', 0) - data.get('mean', 0):.1f} vs avg"
                )
                
                with st.expander("📊 Details"):
                    st.write(f"**Mean:** {data.get('mean', 0):.2f}")
                    st.write(f"**Std Dev:** {data.get('std', 0):.2f}")
                    st.write(f"**Min:** {data.get('min', 0):.2f}")
                    st.write(f"**Max:** {data.get('max', 0):.2f}")
                    st.write(f"**Median:** {data.get('median', 0):.2f}")

# ==================== Main Pages ====================

def page_dashboard():
    """Main dashboard page."""
    render_header()
    
    # AQI Card
    render_aqi_card()
    
    st.markdown("---")
    
    # Statistics Cards
    st.subheader("📈 Current Pollutant Levels")
    render_statistics_cards()
    
    st.markdown("---")
    
    # Time Series Plot
    st.subheader("📊 Pollutant Trends")
    
    df = get_air_quality_data(limit=500)
    
    if df is not None and not df.empty:
        # Select pollutants to display
        available_pollutants = [col for col in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'] if col in df.columns]
        
        selected_pollutants = st.multiselect(
            "Select pollutants to display:",
            options=available_pollutants,
            default=available_pollutants[:3] if len(available_pollutants) >= 3 else available_pollutants
        )
        
        if selected_pollutants:
            fig = plot_time_series_multi(df, selected_pollutants)
            st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        with st.expander("📋 View Raw Data"):
            st.dataframe(df.tail(100), use_container_width=True)
    else:
        st.info("ℹ️ No data available. Please run the data processing pipeline first.")

def page_analysis():
    """Analysis page with time patterns and correlations."""
    st.title("🔬 Data Analysis")
    
    tab1, tab2 = st.tabs(["⏰ Time Patterns", "🔗 Correlations"])
    
    with tab1:
        st.subheader("Time-Based Pattern Analysis")
        
        pollutant = st.selectbox(
            "Select pollutant:",
            options=['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'],
            key="time_pollutant"
        )
        
        analysis_type = st.radio(
            "Analysis type:",
            options=['daily', 'weekly', 'monthly', 'yearly', 'comprehensive'],
            horizontal=True
        )
        
        if st.button("🔍 Analyze Patterns"):
            with st.spinner("Analyzing patterns..."):
                pattern_data = get_time_patterns(pollutant, analysis_type)
                
                if pattern_data:
                    if analysis_type == 'daily' or analysis_type == 'comprehensive':
                        fig = plot_daily_patterns(pattern_data)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Display results
                    with st.expander("📊 Detailed Results"):
                        st.json(pattern_data)
                else:
                    st.error("Failed to fetch pattern analysis.")
    
    with tab2:
        st.subheader("Correlation Analysis")
        
        analysis_type = st.radio(
            "Analysis type:",
            options=['pollutants', 'weather', 'comprehensive'],
            horizontal=True,
            key="corr_type"
        )
        
        if st.button("🔍 Analyze Correlations"):
            with st.spinner("Analyzing correlations..."):
                corr_data = get_correlations(analysis_type)
                
                if corr_data:
                    # Plot heatmap
                    fig = plot_correlation_heatmap(corr_data)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Display strong correlations
                    if "result" in corr_data:
                        result = corr_data["result"]
                        
                        if "pollutant_correlations" in result:
                            strong_corr = result["pollutant_correlations"].get("strong_correlations", [])
                            
                            if strong_corr:
                                st.subheader("🔗 Strong Correlations Found")
                                
                                for corr in strong_corr[:10]:  # Top 10
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    
                                    with col1:
                                        st.write(f"**{corr['pollutant1']}** ↔ **{corr['pollutant2']}**")
                                    with col2:
                                        st.write(f"{corr['correlation']:.3f}")
                                    with col3:
                                        st.write(f"{corr['strength']} {corr['direction']}")
                    
                    # Detailed results
                    with st.expander("📊 Detailed Results"):
                        st.json(corr_data)
                else:
                    st.error("Failed to fetch correlation analysis.")

def page_forecasting():
    """Forecasting page."""
    st.title("🔮 Air Quality Forecasting")
    
    st.markdown("""
        Generate forecasts using various methods including simple statistical methods 
        and advanced machine learning models.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Forecast Configuration")
        
        pollutant = st.selectbox(
            "Select pollutant:",
            options=['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
        )
        
        method = st.selectbox(
            "Forecasting method:",
            options=[
                'moving_average',
                'weighted_moving_average',
                'seasonal_naive',
                'exponential_smoothing',
                'ensemble'
            ],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        steps = st.slider("Forecast horizon (hours):", min_value=6, max_value=168, value=24, step=6)
        
        # Method-specific parameters
        if method == 'moving_average' or method == 'weighted_moving_average':
            window_size = st.slider("Window size:", min_value=6, max_value=72, value=24, step=6)
        else:
            window_size = 24
        
        if method == 'exponential_smoothing':
            alpha = st.slider("Smoothing factor (alpha):", min_value=0.1, max_value=0.9, value=0.3, step=0.1)
        else:
            alpha = 0.3
        
        if st.button("🚀 Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                forecast_data = generate_forecast(
                    pollutant=pollutant,
                    method=method,
                    steps=steps,
                    window_size=window_size,
                    alpha=alpha
                )
                
                if forecast_data:
                    st.success("✅ Forecast generated successfully!")
                    
                    # Plot forecast
                    fig = plot_forecast_with_confidence(forecast_data)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display forecast values
                    with st.expander("📋 Forecast Values"):
                        if "forecast" in forecast_data:
                            forecast_values = forecast_data["forecast"]
                            if isinstance(forecast_values, dict) and "forecast" in forecast_values:
                                values = forecast_values["forecast"]
                                df_forecast = pd.DataFrame({
                                    'Hour': range(1, len(values) + 1),
                                    'Predicted Value': values
                                })
                                st.dataframe(df_forecast, use_container_width=True)
                else:
                    st.error("❌ Failed to generate forecast. Please check API connection.")
    
    with col2:
        st.subheader("ℹ️ Method Info")
        
        method_info = {
            'moving_average': "Simple moving average of recent values. Good for stable trends.",
            'weighted_moving_average': "Recent values have more weight. Better for changing trends.",
            'seasonal_naive': "Uses values from the same time in previous periods. Good for seasonal data.",
            'exponential_smoothing': "Exponentially weighted moving average. Balances recent and historical data.",
            'ensemble': "Combines multiple methods for improved accuracy."
        }
        
        st.info(method_info.get(method, "Select a method to see information."))
        
        st.markdown("---")
        
        st.subheader("📊 Model Performance")
        st.write("Forecast accuracy metrics will be displayed here after generating predictions.")

# ==================== Main App ====================

def main():
    """Main application."""
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/2575fc/ffffff?text=AirSense", use_container_width=True)
        
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "",
            options=["Dashboard", "Analysis", "Forecasting"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Settings")
        
        # API status check
        try:
            health = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if health.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ API Offline")
        
        st.markdown(f"**API URL:** `{API_BASE_URL}`")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📚 Resources")
        st.markdown("- [API Docs](http://localhost:8000/docs)")
        st.markdown("- [GitHub](https://github.com)")
        st.markdown("- [Documentation](./docs)")
    
    # Route to pages
    if page == "Dashboard":
        page_dashboard()
    elif page == "Analysis":
        page_analysis()
    elif page == "Forecasting":
        page_forecasting()

if __name__ == "__main__":
    main()
