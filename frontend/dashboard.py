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

# Modern Custom CSS with improved typography and design
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');

:root {
  --primary: #3B82F6;
  --primary-dark: #2563EB;
  --primary-light: #60A5FA;
  --secondary: #8B5CF6;
  --secondary-dark: #7C3AED;
  --accent: #10B981;
  --accent-orange: #F59E0B;
  --accent-red: #EF4444;
  --bg-primary: #F8FAFC;
  --bg-secondary: #F1F5F9;
  --card-bg: #FFFFFF;
  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-muted: #94A3B8;
  --border: #E2E8F0;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-blue: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
  --gradient-green: linear-gradient(135deg, #10B981 0%, #059669 100%);
  --gradient-orange: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
}

/* Global Styles */
* {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.main {
  background: var(--bg-primary);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

p, span, div {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Main Header with Modern Design */
.main-header {
  background: var(--gradient-blue);
  color: white;
  padding: 2.5rem 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.main-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translate(30%, -30%);
}

.main-header h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.03em;
  position: relative;
  z-index: 1;
}

.main-header p {
  margin: 0.75rem 0 0 0;
  font-size: 1.125rem;
  opacity: 0.95;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 400;
  position: relative;
  z-index: 1;
}

/* Logo Styling */
.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.logo-icon {
  font-size: 2.5rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.logo-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.02em;
}

/* Modern Metric Cards */
.metric-card {
  background: var(--card-bg);
  border-radius: 16px;
  padding: 1.75rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--gradient-blue);
}

/* AQI Card Variants */
.aqi-good::before { background: var(--gradient-green); }
.aqi-moderate::before { background: var(--gradient-orange); }
.aqi-unhealthy::before { background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); }

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 0.375rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.025em;
  text-transform: uppercase;
}

.status-good { 
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  color: #065F46;
}

.status-moderate { 
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  color: #92400E;
}

.status-unhealthy { 
  background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
  color: #991B1B;
}

/* Info Box */
.info-box {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border-left: 4px solid var(--primary);
  padding: 1.25rem;
  border-radius: 12px;
  margin: 1rem 0;
  font-size: 0.95rem;
}

.info-box strong {
  color: var(--primary-dark);
  font-weight: 600;
}

/* Buttons */
.stButton>button {
  background: var(--gradient-blue);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  letter-spacing: 0.025em;
  transition: all 0.3s ease;
  box-shadow: var(--shadow);
  font-family: 'Inter', sans-serif;
}

.stButton>button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  background: var(--gradient-primary);
}

/* Sidebar Styling */
.css-1d391kg, [data-testid="stSidebar"] {
  background: var(--card-bg);
  border-right: 1px solid var(--border);
}

.css-1d391kg h3, [data-testid="stSidebar"] h3 {
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1.125rem;
}

/* Radio Buttons */
.stRadio > label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.stRadio > div {
  gap: 0.75rem;
}

.stRadio > div > label {
  background: var(--bg-secondary);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.stRadio > div > label:hover {
  background: var(--primary-light);
  color: white;
  border-color: var(--primary);
}

/* Select Boxes */
.stSelectbox > label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.95rem;
}

/* Multiselect */
.stMultiSelect > label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.95rem;
}

/* Metrics */
.stMetric {
  background: var(--card-bg);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.stMetric label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stMetric [data-testid="stMetricValue"] {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary);
  font-family: 'Poppins', sans-serif;
}

/* Expander */
.streamlit-expanderHeader {
  background: var(--bg-secondary);
  border-radius: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 0.5rem;
  background: var(--bg-secondary);
  padding: 0.5rem;
  border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
  background: var(--gradient-blue);
  color: white;
}

/* Success/Error/Warning Messages */
.stSuccess {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  padding: 1rem;
  color: #065F46;
}

.stError {
  background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
  border-left: 4px solid var(--accent-red);
  border-radius: 8px;
  padding: 1rem;
  color: #991B1B;
}

.stWarning {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-left: 4px solid var(--accent-orange);
  border-radius: 8px;
  padding: 1rem;
  color: #92400E;
}

.stInfo {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border-left: 4px solid var(--primary);
  border-radius: 8px;
  padding: 1rem;
  color: #1E40AF;
}

/* Dataframe */
.stDataFrame {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
}

/* Plotly Charts */
.js-plotly-plot {
  border-radius: 12px;
  overflow: hidden;
}

/* Spinner */
.stSpinner > div {
  border-top-color: var(--primary) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--primary-light);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary);
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-header h1 {
    font-size: 1.75rem;
  }
  
  .main-header p {
    font-size: 1rem;
  }
  
  .metric-card {
    padding: 1.25rem;
  }
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.metric-card, .main-header {
  animation: fadeIn 0.5s ease-out;
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
    pollutant_data = get_pollutant_correlation_result(corr_data)
    if pollutant_data:
        corr_matrix = pollutant_data.get("correlation_matrix", {})
        
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

def get_pollutant_correlation_result(corr_data: Dict) -> Optional[Dict]:
    """Extract pollutant correlation results from direct or comprehensive responses."""
    result = corr_data.get("result", {})
    if "pollutant_correlations" in result:
        return result["pollutant_correlations"]

    comprehensive = result.get("comprehensive_analysis", {})
    if "pollutant_correlations" in comprehensive:
        return comprehensive["pollutant_correlations"]

    if result.get("analysis_type") == "pollutant_correlations":
        return result

    return None

def plot_daily_patterns(pattern_data: Dict):
    """Plot daily patterns."""
    if "result" in pattern_data:
        result = pattern_data["result"]
        
        # Handle comprehensive analysis format (nested structure)
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
        
        # Handle direct daily analysis format (pandas analyzer)
        elif isinstance(result, dict) and "hourly_stats" in result:
            daily_stats = result.get("hourly_stats", [])
            pollutant = pattern_data.get("pollutant", "Unknown")
            
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

def plot_weekly_patterns(pattern_data: Dict):
    """Plot weekly patterns."""
    if "result" in pattern_data:
        result = pattern_data["result"]
        pollutant = pattern_data.get("pollutant", "Unknown")
        
        # Handle comprehensive format
        if isinstance(result, dict) and "individual_analyses" in result:
            for poll, analysis in result["individual_analyses"].items():
                if "weekly" in analysis:
                    weekly_stats = analysis["weekly"].get("daily_stats", [])
                    if weekly_stats:
                        df = pd.DataFrame(weekly_stats)
                        pollutant = poll
                        break
        # Handle direct format
        elif isinstance(result, dict) and "daily_stats" in result:
            weekly_stats = result.get("daily_stats", [])
            df = pd.DataFrame(weekly_stats)
        else:
            return None
        
        if not df.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df['day_name'],
                y=df['mean'],
                name='Average',
                marker_color='#2575fc',
                error_y=dict(
                    type='data',
                    array=df['std'],
                    visible=True
                )
            ))
            
            fig.update_layout(
                title=f"Weekly Pattern - {pollutant}",
                xaxis_title="Day of Week",
                yaxis_title="Concentration (µg/m³)",
                template='plotly_white',
                height=400
            )
            
            return fig
    
    return None

def plot_monthly_patterns(pattern_data: Dict):
    """Plot monthly patterns."""
    if "result" in pattern_data:
        result = pattern_data["result"]
        pollutant = pattern_data.get("pollutant", "Unknown")
        
        # Handle comprehensive format
        if isinstance(result, dict) and "individual_analyses" in result:
            for poll, analysis in result["individual_analyses"].items():
                if "monthly" in analysis:
                    monthly_stats = analysis["monthly"].get("monthly_stats", [])
                    if monthly_stats:
                        df = pd.DataFrame(monthly_stats)
                        pollutant = poll
                        break
        # Handle direct format
        elif isinstance(result, dict) and "monthly_stats" in result:
            monthly_stats = result.get("monthly_stats", [])
            df = pd.DataFrame(monthly_stats)
        else:
            return None
        
        if not df.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['month_name'],
                y=df['mean'],
                mode='lines+markers',
                name='Average',
                line=dict(color='#2575fc', width=3),
                marker=dict(size=10),
                error_y=dict(
                    type='data',
                    array=df['std'],
                    visible=True
                )
            ))
            
            fig.update_layout(
                title=f"Monthly Pattern - {pollutant}",
                xaxis_title="Month",
                yaxis_title="Concentration (µg/m³)",
                template='plotly_white',
                height=400
            )
            
            return fig
    
    return None

def plot_yearly_trends(pattern_data: Dict):
    """Plot yearly trends."""
    if "result" in pattern_data:
        result = pattern_data["result"]
        pollutant = pattern_data.get("pollutant", "Unknown")
        
        # Handle comprehensive format
        if isinstance(result, dict) and "individual_analyses" in result:
            for poll, analysis in result["individual_analyses"].items():
                if "yearly" in analysis:
                    yearly_stats = analysis["yearly"].get("yearly_stats", [])
                    if yearly_stats:
                        df = pd.DataFrame(yearly_stats)
                        pollutant = poll
                        break
        # Handle direct format
        elif isinstance(result, dict) and "yearly_stats" in result:
            yearly_stats = result.get("yearly_stats", [])
            df = pd.DataFrame(yearly_stats)
        else:
            return None
        
        if not df.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['year'],
                y=df['mean'],
                mode='lines+markers',
                name='Average',
                line=dict(color='#2575fc', width=3),
                marker=dict(size=12),
                fill='tonexty',
                fillcolor='rgba(37, 117, 252, 0.1)'
            ))
            
            fig.update_layout(
                title=f"Yearly Trend - {pollutant}",
                xaxis_title="Year",
                yaxis_title="Concentration (µg/m³)",
                template='plotly_white',
                height=400
            )
            
            return fig
    
    return None

def plot_comprehensive_patterns(pattern_data: Dict):
    """Plot comprehensive patterns (all time scales)."""
    if "result" in pattern_data:
        result = pattern_data["result"]
        pollutant = pattern_data.get("pollutant", "Unknown")
        
        if isinstance(result, dict) and "individual_analyses" in result:
            for poll, analysis in result["individual_analyses"].items():
                pollutant = poll
                
                # Create subplots for all patterns
                from plotly.subplots import make_subplots
                
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=("Daily Pattern", "Weekly Pattern", "Monthly Pattern", "Yearly Trend"),
                    vertical_spacing=0.12,
                    horizontal_spacing=0.1
                )
                
                # Daily pattern
                if "daily" in analysis:
                    daily_stats = analysis["daily"].get("hourly_stats", [])
                    if daily_stats:
                        df_daily = pd.DataFrame(daily_stats)
                        fig.add_trace(
                            go.Scatter(x=df_daily['hour'], y=df_daily['mean'], 
                                     mode='lines+markers', name='Daily',
                                     line=dict(color='#2575fc', width=2)),
                            row=1, col=1
                        )
                
                # Weekly pattern
                if "weekly" in analysis:
                    weekly_stats = analysis["weekly"].get("daily_stats", [])
                    if weekly_stats:
                        df_weekly = pd.DataFrame(weekly_stats)
                        fig.add_trace(
                            go.Bar(x=df_weekly['day_name'], y=df_weekly['mean'],
                                 name='Weekly', marker_color='#6a11cb'),
                            row=1, col=2
                        )
                
                # Monthly pattern
                if "monthly" in analysis:
                    monthly_stats = analysis["monthly"].get("monthly_stats", [])
                    if monthly_stats:
                        df_monthly = pd.DataFrame(monthly_stats)
                        fig.add_trace(
                            go.Scatter(x=df_monthly['month_name'], y=df_monthly['mean'],
                                     mode='lines+markers', name='Monthly',
                                     line=dict(color='#10b981', width=2)),
                            row=2, col=1
                        )
                
                # Yearly trend
                if "yearly" in analysis:
                    yearly_stats = analysis["yearly"].get("yearly_stats", [])
                    if yearly_stats:
                        df_yearly = pd.DataFrame(yearly_stats)
                        fig.add_trace(
                            go.Scatter(x=df_yearly['year'], y=df_yearly['mean'],
                                     mode='lines+markers', name='Yearly',
                                     line=dict(color='#f59e0b', width=2)),
                            row=2, col=2
                        )
                
                fig.update_xaxes(title_text="Hour", row=1, col=1)
                fig.update_xaxes(title_text="Day", row=1, col=2)
                fig.update_xaxes(title_text="Month", row=2, col=1)
                fig.update_xaxes(title_text="Year", row=2, col=2)
                
                fig.update_yaxes(title_text="µg/m³", row=1, col=1)
                fig.update_yaxes(title_text="µg/m³", row=1, col=2)
                fig.update_yaxes(title_text="µg/m³", row=2, col=1)
                fig.update_yaxes(title_text="µg/m³", row=2, col=2)
                
                fig.update_layout(
                    title_text=f"Comprehensive Time Analysis - {pollutant}",
                    showlegend=False,
                    height=700,
                    template='plotly_white'
                )
                
                return fig
    
    return None

def display_pattern_summary(pattern_data: Dict, analysis_type: str):
    """Display summary statistics for pattern analysis."""
    if "result" not in pattern_data:
        return
    
    result = pattern_data["result"]
    pollutant = pattern_data.get("pollutant", "Unknown")
    
    # Extract summary based on format
    if isinstance(result, dict):
        if "individual_analyses" in result:
            # Comprehensive format
            for poll, analysis in result["individual_analyses"].items():
                if analysis_type in analysis:
                    data = analysis[analysis_type]
                    _display_summary_cards(data, analysis_type, poll)
                    break
        else:
            # Direct format
            _display_summary_cards(result, analysis_type, pollutant)

def _display_summary_cards(data: Dict, analysis_type: str, pollutant: str):
    """Display summary cards for analysis results."""
    cols = st.columns(3)
    
    if analysis_type == "daily":
        with cols[0]:
            st.metric("Peak Hour", f"{data.get('peak_hour', 'N/A')}:00")
        with cols[1]:
            st.metric("Lowest Hour", f"{data.get('lowest_hour', 'N/A')}:00")
        with cols[2]:
            st.metric("Overall Mean", f"{data.get('overall_mean', 0):.2f} µg/m³")
    
    elif analysis_type == "weekly":
        with cols[0]:
            st.metric("Peak Day", data.get('peak_day', 'N/A'))
        with cols[1]:
            st.metric("Lowest Day", data.get('lowest_day', 'N/A'))
        with cols[2]:
            st.metric("Pollutant", pollutant)
    
    elif analysis_type == "monthly":
        with cols[0]:
            st.metric("Peak Month", data.get('peak_month', 'N/A'))
        with cols[1]:
            st.metric("Lowest Month", data.get('lowest_month', 'N/A'))
        with cols[2]:
            st.metric("Pollutant", pollutant)
    
    elif analysis_type == "yearly":
        with cols[0]:
            st.metric("Trend", data.get('trend', 'N/A').title())
        with cols[1]:
            st.metric("Pollutant", pollutant)
        with cols[2]:
            yearly_stats = data.get('yearly_stats', [])
            if yearly_stats:
                st.metric("Years Analyzed", len(yearly_stats))

def display_formatted_pattern_details(pattern_data: Dict):
    """Display pattern analysis details in a formatted, user-friendly way."""
    if "result" not in pattern_data:
        st.warning("No detailed results available.")
        return
    
    result = pattern_data["result"]
    pollutant = pattern_data.get("pollutant", "Unknown")
    
    st.markdown(f"### 📊 Analysis Details for {pollutant}")
    
    # Handle comprehensive format
    if isinstance(result, dict) and "individual_analyses" in result:
        for poll, analysis in result["individual_analyses"].items():
            st.markdown(f"#### Pollutant: **{poll}**")
            
            # Display each time scale analysis
            for time_scale in ['daily', 'weekly', 'monthly', 'yearly']:
                if time_scale in analysis:
                    data = analysis[time_scale]
                    st.markdown(f"**{time_scale.title()} Analysis:**")
                    
                    # Create a formatted display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if time_scale == 'daily':
                            st.write(f"🔝 Peak Hour: **{data.get('peak_hour', 'N/A')}:00**")
                            st.write(f"🔽 Lowest Hour: **{data.get('lowest_hour', 'N/A')}:00**")
                            st.write(f"📊 Overall Mean: **{data.get('overall_mean', 0):.2f} µg/m³**")
                        elif time_scale == 'weekly':
                            st.write(f"🔝 Peak Day: **{data.get('peak_day', 'N/A')}**")
                            st.write(f"🔽 Lowest Day: **{data.get('lowest_day', 'N/A')}**")
                        elif time_scale == 'monthly':
                            st.write(f"🔝 Peak Month: **{data.get('peak_month', 'N/A')}**")
                            st.write(f"🔽 Lowest Month: **{data.get('lowest_month', 'N/A')}**")
                        elif time_scale == 'yearly':
                            st.write(f"📈 Trend: **{data.get('trend', 'N/A').title()}**")
                            yearly_stats = data.get('yearly_stats', [])
                            if yearly_stats:
                                st.write(f"📅 Years Analyzed: **{len(yearly_stats)}**")
                    
                    with col2:
                        # Display statistics table
                        stats_key = {
                            'daily': 'hourly_stats',
                            'weekly': 'daily_stats',
                            'monthly': 'monthly_stats',
                            'yearly': 'yearly_stats'
                        }.get(time_scale)
                        
                        if stats_key and stats_key in data:
                            stats = data[stats_key]
                            if stats and len(stats) > 0:
                                st.write(f"📋 Data Points: **{len(stats)}**")
                                # Show first few entries
                                if isinstance(stats, list) and len(stats) > 0:
                                    df_stats = pd.DataFrame(stats[:5])
                                    st.dataframe(df_stats, use_container_width=True, height=150)
                    
                    st.markdown("---")
    
    # Handle direct format
    else:
        st.markdown(f"#### Analysis Type: **{result.get('analysis_type', 'Unknown')}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Key Metrics:**")
            if 'peak_hour' in result:
                st.write(f"🔝 Peak Hour: **{result.get('peak_hour', 'N/A')}:00**")
                st.write(f"🔽 Lowest Hour: **{result.get('lowest_hour', 'N/A')}:00**")
                st.write(f"📊 Overall Mean: **{result.get('overall_mean', 0):.2f} µg/m³**")
            elif 'peak_day' in result:
                st.write(f"🔝 Peak Day: **{result.get('peak_day', 'N/A')}**")
                st.write(f"🔽 Lowest Day: **{result.get('lowest_day', 'N/A')}**")
            elif 'peak_month' in result:
                st.write(f"🔝 Peak Month: **{result.get('peak_month', 'N/A')}**")
                st.write(f"🔽 Lowest Month: **{result.get('lowest_month', 'N/A')}**")
            elif 'trend' in result:
                st.write(f"📈 Trend: **{result.get('trend', 'N/A').title()}**")
        
        with col2:
            st.markdown("**Statistical Data:**")
            # Find and display the stats
            for key in ['hourly_stats', 'daily_stats', 'monthly_stats', 'yearly_stats']:
                if key in result:
                    stats = result[key]
                    if stats and len(stats) > 0:
                        st.write(f"📋 Data Points: **{len(stats)}**")
                        df_stats = pd.DataFrame(stats[:5])
                        st.dataframe(df_stats, use_container_width=True, height=150)
                        break

def display_formatted_correlation_details(corr_data: Dict):
    """Display correlation analysis details in a formatted, user-friendly way."""
    if "result" not in corr_data:
        st.warning("No detailed results available.")
        return
    
    result = corr_data["result"]
    
    st.markdown("### 📊 Correlation Analysis Details")
    
    # Get pollutant correlation data
    pollutant_corr = get_pollutant_correlation_result(corr_data)
    
    if pollutant_corr:
        # Display correlation matrix as a table
        corr_matrix = pollutant_corr.get("correlation_matrix", {})
        if corr_matrix:
            st.markdown("#### 📈 Correlation Matrix")
            df_corr = pd.DataFrame(corr_matrix)
            st.dataframe(df_corr.style.background_gradient(cmap='RdBu_r', vmin=-1, vmax=1).format("{:.3f}"), 
                        use_container_width=True)
        
        # Display all correlations in a table
        strong_corr = pollutant_corr.get("strong_correlations", [])
        if strong_corr:
            st.markdown("#### 🔗 All Correlation Pairs")
            
            # Create a DataFrame for better display
            corr_list = []
            for corr in strong_corr:
                corr_list.append({
                    "Pollutant 1": corr.get('pollutant1', 'N/A'),
                    "Pollutant 2": corr.get('pollutant2', 'N/A'),
                    "Correlation": f"{corr.get('correlation', 0):.3f}",
                    "Strength": corr.get('strength', 'N/A'),
                    "Direction": corr.get('direction', 'N/A')
                })
            
            if corr_list:
                df_corr_pairs = pd.DataFrame(corr_list)
                st.dataframe(df_corr_pairs, use_container_width=True, height=400)
        
        # Display summary statistics
        st.markdown("#### 📊 Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Pairs Analyzed", len(strong_corr) if strong_corr else 0)
        
        with col2:
            if strong_corr:
                strong_count = sum(1 for c in strong_corr if c.get('strength') == 'strong')
                st.metric("Strong Correlations", strong_count)
        
        with col3:
            if strong_corr:
                positive_count = sum(1 for c in strong_corr if c.get('direction') == 'positive')
                st.metric("Positive Correlations", positive_count)
    
    # Handle comprehensive analysis
    if "comprehensive_analysis" in result:
        comp = result["comprehensive_analysis"]
        
        st.markdown("---")
        st.markdown("#### 🌐 Comprehensive Analysis")
        
        if "pollutant_correlations" in comp:
            st.write("✅ Pollutant correlations analyzed")
        
        if "weather_correlations" in comp:
            st.write("✅ Weather correlations analyzed")
            weather_corr = comp["weather_correlations"]
            if "strong_correlations" in weather_corr:
                st.write(f"📊 Weather correlation pairs found: **{len(weather_corr['strong_correlations'])}**")

# ==================== Page Components ====================

def render_header():
    """Render main header with modern logo."""
    st.markdown("""
        <div class="main-header">
            <div class="logo-container">
                <span class="logo-icon">🌤️</span>
                <span class="logo-text">AirSense</span>
            </div>
            <h1>Air Quality Monitoring System</h1>
            <p>Real-time analysis, forecasting, and environmental intelligence</p>
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
                    # Display appropriate chart based on analysis type
                    fig = None
                    if analysis_type == 'daily':
                        fig = plot_daily_patterns(pattern_data)
                        display_pattern_summary(pattern_data, 'daily')
                    elif analysis_type == 'weekly':
                        fig = plot_weekly_patterns(pattern_data)
                        display_pattern_summary(pattern_data, 'weekly')
                    elif analysis_type == 'monthly':
                        fig = plot_monthly_patterns(pattern_data)
                        display_pattern_summary(pattern_data, 'monthly')
                    elif analysis_type == 'yearly':
                        fig = plot_yearly_trends(pattern_data)
                        display_pattern_summary(pattern_data, 'yearly')
                    elif analysis_type == 'comprehensive':
                        fig = plot_comprehensive_patterns(pattern_data)
                        st.info("📊 Comprehensive view shows all time patterns in one dashboard")
                    
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("⚠️ Unable to generate chart. Showing raw data below.")
                    
                    # Display detailed results in expandable section
                    with st.expander("📊 Detailed Results"):
                        display_formatted_pattern_details(pattern_data)
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
                        
                        pollutant_corr = get_pollutant_correlation_result(corr_data)
                        if pollutant_corr:
                            strong_corr = pollutant_corr.get("strong_correlations", [])
                            
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
                        display_formatted_correlation_details(corr_data)
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


def page_data_upload():
    """Data upload page."""
    st.title("📤 Upload Air Quality Data")
    
    st.markdown("""
        Upload your own air quality data in CSV format. The file will be validated and processed automatically.
    """)
    
    # Upload section
    st.subheader("📁 Select File")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload air quality data in CSV format with datetime and pollutant columns"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ File selected: **{uploaded_file.name}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        with col2:
            st.metric("File Type", "CSV")
        with col3:
            process_immediately = st.checkbox("Process Immediately", value=True, 
                                             help="Process the file right after upload")
        
        # Preview data
        with st.expander("👁️ Preview Data"):
            try:
                df_preview = pd.read_csv(uploaded_file)
                st.dataframe(df_preview.head(10), use_container_width=True)
                
                st.markdown("**Columns:**")
                st.write(", ".join(df_preview.columns.tolist()))
                
                st.markdown("**Data Info:**")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"📊 Rows: **{len(df_preview)}**")
                with col_b:
                    st.write(f"📋 Columns: **{len(df_preview.columns)}**")
                
                # Reset file pointer for upload
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        
        st.markdown("---")
        
        # Upload button
        if st.button("🚀 Upload and Process", type="primary", use_container_width=True):
            with st.spinner("Uploading file..."):
                try:
                    # Prepare file for upload
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    
                    # Upload to API
                    url = f"{API_BASE_URL}/upload"
                    params = {"process_immediately": process_immediately}
                    
                    response = requests.post(url, files=files, params=params, timeout=60)
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Display result based on status
                    status = result.get("status", "unknown")
                    
                    if status == "uploaded_and_processing":
                        st.success("✅ " + result.get("message", "File uploaded and processing started!"))
                        st.info("🔄 The file is being processed in the background. Refresh the dashboard in a few moments to see the new data.")
                    elif status == "uploaded":
                        st.success("✅ " + result.get("message", "File uploaded successfully!"))
                    elif status == "uploaded_with_warnings":
                        st.warning("⚠️ " + result.get("message", "File uploaded but has validation issues"))
                    elif status == "uploaded_not_processed":
                        st.warning("⚠️ " + result.get("message", "File uploaded but not processed"))
                    else:
                        st.info("ℹ️ " + result.get("message", "File uploaded"))
                    
                    # Display validation results
                    if "validation" in result:
                        validation = result["validation"]
                        
                        with st.expander("📊 Validation Report"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Rows", validation.get("total_rows", 0))
                            with col2:
                                st.metric("Missing Values", validation.get("missing_values_count", 0))
                            with col3:
                                has_issues = validation.get("has_critical_issues", False)
                                st.metric("Status", "⚠️ Issues" if has_issues else "✅ Valid")
                            
                            if validation.get("issues"):
                                st.markdown("**Issues Found:**")
                                for issue in validation["issues"]:
                                    st.write(f"- {issue}")
                    
                    # Display file info
                    with st.expander("📄 Upload Details"):
                        st.json(result)
                    
                    # Clear cache to show new data
                    st.cache_data.clear()
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Upload failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    else:
        # Show instructions when no file is selected
        st.info("👆 Please select a CSV file to upload")
        
        st.markdown("---")
        
        st.subheader("📋 File Requirements")
        
        st.markdown("""
        Your CSV file should contain:
        
        **Required Columns:**
        - `datetime` or `timestamp` - Date and time of measurement
        - At least one pollutant column (PM2.5, PM10, NO2, SO2, CO, O3)
        
        **Optional Columns:**
        - Weather data (TEMP, PRES, DEWP, RAIN, WSPM, etc.)
        - Location information
        
        **Format Guidelines:**
        - ✅ CSV format with comma separator
        - ✅ Header row with column names
        - ✅ Datetime in standard format (YYYY-MM-DD HH:MM:SS)
        - ✅ Numeric values for pollutants and weather
        
        **Example:**
        ```
        datetime,PM2.5,PM10,NO2,SO2,CO,O3,TEMP,PRES
        2024-01-01 00:00:00,35.5,50.2,45.0,10.5,0.8,25.3,5.2,1020.5
        2024-01-01 01:00:00,38.2,52.1,47.5,11.0,0.9,23.1,4.8,1021.0
        ```
        """)
        
        st.markdown("---")
        
        st.subheader("🔍 What Happens After Upload?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **1. Validation** ✅
            - Check data format
            - Verify required columns
            - Identify missing values
            - Detect outliers
            """)
        
        with col2:
            st.markdown("""
            **2. Processing** ⚙️
            - Clean and normalize data
            - Handle missing values
            - Calculate derived metrics
            - Store in database
            """)
        
        st.markdown("""
        **3. Ready to Use** 🎉
        - View in Dashboard
        - Run Analysis
        - Generate Forecasts
        """)

# ==================== Main App ====================

def main():
    """Main application."""
    
    # Sidebar navigation
    with st.sidebar:
        # Modern Logo - Top Left
        st.markdown("""
            <div style="text-align: left; padding: 1rem 0; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="font-size: 2.5rem;">🌤️</div>
                    <div>
                        <div style="font-family: 'Poppins', sans-serif; font-size: 1.5rem; font-weight: 700; 
                                    background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
                                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                                    background-clip: text; line-height: 1.2;">
                            AirSense
                        </div>
                        <div style="font-size: 0.65rem; color: #94A3B8; font-weight: 500; letter-spacing: 0.1em;">
                            AIR QUALITY INTELLIGENCE
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "",
            options=["Dashboard", "Analysis", "Forecasting", "Upload Data"],
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
    elif page == "Upload Data":
        page_data_upload()

if __name__ == "__main__":
    main()
