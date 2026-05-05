# AirSense Dashboard Guide

## Overview

The AirSense Dashboard is a production-ready, interactive web application built with Streamlit that provides real-time air quality monitoring, analysis, and forecasting capabilities. It integrates seamlessly with the AirSense API to deliver comprehensive environmental data insights.

---

## Features

### 🏠 Dashboard Page

**Real-Time Monitoring:**
- Current Air Quality Index (AQI) with health recommendations
- Live pollutant levels for PM2.5, PM10, NO2, SO2, CO, O3
- Statistical summaries (mean, std, min, max, median)
- Interactive time series charts
- Multi-pollutant comparison

**Key Metrics:**
- Current AQI with color-coded health status
- Latest pollutant concentrations
- Comparison with historical averages
- Health impact assessments
- Actionable recommendations

### 🔬 Analysis Page

**Time-Based Pattern Analysis:**
- Daily patterns (hourly analysis)
- Weekly patterns (day-of-week trends)
- Monthly patterns (seasonal variations)
- Yearly trends (long-term changes)
- Comprehensive multi-scale analysis

**Correlation Analysis:**
- Pollutant-to-pollutant correlations
- Weather-to-pollutant correlations
- Correlation strength classification
- Interactive correlation heatmaps
- Strong correlation identification

### 🔮 Forecasting Page

**Forecasting Methods:**
- Moving Average
- Weighted Moving Average
- Seasonal Naive
- Exponential Smoothing
- Ensemble (combines all methods)

**Forecast Features:**
- Configurable forecast horizon (6-168 hours)
- Method-specific parameter tuning
- Confidence intervals
- Interactive forecast visualization
- Forecast value tables

---

## Getting Started

### Prerequisites

1. **API Server Running:**
   ```bash
   python -m src.main api
   ```
   The API should be accessible at `http://localhost:8000`

2. **Data Processed:**
   Ensure the data processing pipeline has been run:
   ```bash
   python -m src.main pipeline
   ```

### Starting the Dashboard

**Method 1: Direct Command**
```bash
streamlit run frontend/dashboard.py
```

**Method 2: Via Main Script**
```bash
python -m src.main dashboard
```

**Method 3: Complete System**
```bash
python -m src.main all
```

The dashboard will be available at: `http://localhost:8501`

---

## Dashboard Navigation

### Sidebar

**Navigation Menu:**
- Dashboard - Main overview and real-time monitoring
- Analysis - Time patterns and correlation analysis
- Forecasting - Generate predictions

**Settings:**
- API connection status indicator
- API URL display
- Refresh data button
- Quick links to resources

**API Status:**
- ✅ Green: API connected and healthy
- ❌ Red: API offline or error

---

## Using the Dashboard

### 1. Dashboard Page

**Viewing Current AQI:**
1. Navigate to the Dashboard page
2. View the AQI card at the top
3. Check the color-coded health status:
   - Green: Good (0-50)
   - Yellow: Moderate (51-100)
   - Red: Unhealthy (101+)
4. Read health recommendations

**Monitoring Pollutants:**
1. View current levels in the statistics cards
2. Click "📊 Details" to see full statistics
3. Compare current values with averages

**Analyzing Trends:**
1. Select pollutants from the multiselect dropdown
2. View interactive time series chart
3. Hover over lines for detailed values
4. Zoom and pan using chart controls

**Viewing Raw Data:**
1. Click "📋 View Raw Data" expander
2. Browse the data table
3. Sort by clicking column headers

### 2. Analysis Page

**Time Pattern Analysis:**
1. Go to the "⏰ Time Patterns" tab
2. Select a pollutant (PM2.5, PM10, NO2, etc.)
3. Choose analysis type:
   - Daily: Hourly patterns throughout the day
   - Weekly: Day-of-week patterns
   - Monthly: Seasonal patterns
   - Yearly: Long-term trends
   - Comprehensive: All analyses combined
4. Click "🔍 Analyze Patterns"
5. View the pattern visualization
6. Expand "📊 Detailed Results" for full data

**Correlation Analysis:**
1. Go to the "🔗 Correlations" tab
2. Choose analysis type:
   - Pollutants: Inter-pollutant correlations
   - Weather: Weather-pollutant correlations
   - Comprehensive: All correlations
3. Click "🔍 Analyze Correlations"
4. View the correlation heatmap
5. Review strong correlations list
6. Expand "📊 Detailed Results" for full data

### 3. Forecasting Page

**Generating Forecasts:**
1. Navigate to the Forecasting page
2. Select a pollutant to forecast
3. Choose a forecasting method:
   - **Moving Average**: Good for stable trends
   - **Weighted Moving Average**: Better for changing trends
   - **Seasonal Naive**: Good for seasonal data
   - **Exponential Smoothing**: Balances recent and historical
   - **Ensemble**: Combines all methods
4. Set forecast horizon (6-168 hours)
5. Adjust method-specific parameters:
   - Window size (for moving averages)
   - Alpha (for exponential smoothing)
6. Click "🚀 Generate Forecast"
7. View the forecast chart with confidence intervals
8. Expand "📋 Forecast Values" to see the data table

**Understanding Forecasts:**
- Blue line: Predicted values
- Shaded area: 95% confidence interval
- X-axis: Hours ahead
- Y-axis: Predicted concentration (µg/m³)

---

## API Integration

The dashboard integrates with the following API endpoints:

### Data Endpoints
- `GET /data` - Retrieve air quality data
- `GET /stats` - Get statistical summaries
- `GET /aqi` - Get current AQI

### Analysis Endpoints
- `GET /analysis/time-patterns` - Time-based pattern analysis
- `GET /analysis/correlations` - Correlation analysis

### Forecasting Endpoints
- `POST /forecast/simple` - Generate simple forecasts

### Configuration
- Default API URL: `http://localhost:8000`
- Request timeout: 30 seconds
- Data cache TTL: 5 minutes (300 seconds)
- Analysis cache TTL: 10 minutes (600 seconds)

---

## Troubleshooting

### Dashboard Won't Start

**Error: "Address already in use"**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use a different port
streamlit run frontend/dashboard.py --server.port 8502
```

**Error: "Module not found"**
```bash
# Install Streamlit
pip install streamlit plotly requests

# Or install all requirements
pip install -r requirements.txt
```

### API Connection Issues

**"Cannot connect to API"**
1. Check if API is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. Start the API if not running:
   ```bash
   python -m src.main api
   ```
3. Check firewall settings
4. Verify API_BASE_URL in dashboard code

**"API request timed out"**
1. Check API server logs
2. Ensure data processing is complete
3. Increase timeout in dashboard code
4. Check system resources

### No Data Available

**"No data available. Please run the data processing pipeline first."**
1. Run the pipeline:
   ```bash
   python -m src.main pipeline
   ```
2. Wait for processing to complete
3. Refresh the dashboard
4. Check `data/processed/` directory for output files

### Slow Performance

**Dashboard is slow or unresponsive:**
1. Reduce data limit in API calls
2. Clear cache: Click "🔄 Refresh Data" in sidebar
3. Restart the dashboard
4. Check system resources (RAM, CPU)
5. Reduce forecast horizon

---

## Customization

### Changing API URL

Edit `frontend/dashboard.py`:
```python
# Change this line
API_BASE_URL = "http://localhost:8000"

# To your API URL
API_BASE_URL = "http://your-api-server:8000"
```

### Adjusting Cache Duration

```python
# Change TTL (time-to-live) in seconds
@st.cache_data(ttl=300)  # 5 minutes
def get_air_quality_data(limit: int = 1000):
    ...

# Increase for less frequent updates
@st.cache_data(ttl=600)  # 10 minutes

# Decrease for more frequent updates
@st.cache_data(ttl=60)   # 1 minute
```

### Modifying Colors

Edit the CSS section in `frontend/dashboard.py`:
```python
CSS = """
<style>
:root {
  --primary: #2575fc;      /* Primary color */
  --secondary: #6a11cb;    /* Secondary color */
  --success: #10b981;      /* Success/Good */
  --warning: #f59e0b;      /* Warning/Moderate */
  --danger: #ef4444;       /* Danger/Unhealthy */
  ...
}
</style>
"""
```

### Adding New Pages

1. Create a new page function:
```python
def page_my_new_page():
    st.title("My New Page")
    # Your page content here
```

2. Add to sidebar navigation:
```python
page = st.radio(
    "",
    options=["Dashboard", "Analysis", "Forecasting", "My New Page"],
    label_visibility="collapsed"
)
```

3. Add routing:
```python
if page == "My New Page":
    page_my_new_page()
```

---

## Best Practices

### Performance

1. **Use caching effectively:**
   - Cache API calls with appropriate TTL
   - Clear cache when data updates
   - Use `st.cache_data` for data functions

2. **Limit data volume:**
   - Use reasonable data limits (500-1000 records)
   - Implement pagination for large datasets
   - Filter data before visualization

3. **Optimize visualizations:**
   - Limit number of data points in charts
   - Use appropriate chart types
   - Avoid real-time updates for static data

### User Experience

1. **Provide feedback:**
   - Use spinners for long operations
   - Show success/error messages
   - Display loading states

2. **Handle errors gracefully:**
   - Catch API exceptions
   - Show user-friendly error messages
   - Provide troubleshooting hints

3. **Make it intuitive:**
   - Use clear labels and descriptions
   - Provide tooltips and help text
   - Organize content logically

### Security

1. **API Security:**
   - Use HTTPS in production
   - Implement authentication if needed
   - Validate all inputs

2. **Data Privacy:**
   - Don't expose sensitive data
   - Implement access controls
   - Log security events

---

## Advanced Features

### Real-Time Updates

Enable auto-refresh:
```python
import time

# Add to sidebar
auto_refresh = st.checkbox("Auto-refresh (30s)")

if auto_refresh:
    time.sleep(30)
    st.rerun()
```

### Export Data

Add export functionality:
```python
import io

# Convert DataFrame to CSV
csv = df.to_csv(index=False)

# Create download button
st.download_button(
    label="📥 Download Data",
    data=csv,
    file_name="air_quality_data.csv",
    mime="text/csv"
)
```

### Custom Alerts

Implement threshold alerts:
```python
def check_alerts(aqi):
    if aqi > 150:
        st.error("🚨 ALERT: Unhealthy air quality detected!")
    elif aqi > 100:
        st.warning("⚠️ WARNING: Moderate air quality")
    else:
        st.success("✅ Air quality is good")
```

---

## Deployment

### Local Deployment

```bash
# Run on specific port
streamlit run frontend/dashboard.py --server.port 8501

# Run with custom config
streamlit run frontend/dashboard.py --server.headless true
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY frontend/ ./frontend/

EXPOSE 8501

CMD ["streamlit", "run", "frontend/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Cloud Deployment

**Streamlit Cloud:**
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Configure secrets and environment variables
4. Deploy

**Heroku:**
```bash
# Create Procfile
echo "web: streamlit run frontend/dashboard.py --server.port=$PORT" > Procfile

# Deploy
heroku create
git push heroku main
```

---

## Support

### Getting Help

1. **Check logs:**
   - Dashboard logs in terminal
   - API logs in `logs/` directory
   - Browser console for JavaScript errors

2. **Common issues:**
   - See Troubleshooting section above
   - Check API documentation
   - Review system requirements

3. **Resources:**
   - [Streamlit Documentation](https://docs.streamlit.io)
   - [Plotly Documentation](https://plotly.com/python/)
   - [API Documentation](./API_DOCUMENTATION.md)

---

## Changelog

### Version 2.0.0 (Current)
- ✨ Complete API integration
- ✨ Real-time data from API endpoints
- ✨ Time pattern analysis
- ✨ Correlation analysis
- ✨ Multiple forecasting methods
- ✨ Improved UI/UX
- ✨ Better error handling
- ✨ Caching for performance

### Version 1.0.0 (Previous)
- Basic dashboard with mock data
- Simple visualizations
- Limited functionality

---

**Dashboard Version:** 2.0.0  
**Last Updated:** May 1, 2026  
**Maintained By:** AirSense Team
