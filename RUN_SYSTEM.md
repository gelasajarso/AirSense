# How to Run the Complete AirSense System

## Prerequisites

1. **Python 3.9+** installed and accessible via `python` or `py` command
2. **pip** package manager (should come with Python)
3. **Java 11+** (required for Apache Spark)
4. **Git** (for cloning if needed)

## Important: Python Setup

**Before running the system**, ensure Python is properly installed:

```powershell
# Check Python version (should be 3.9 or higher)
python --version

# Check pip is available
python -m pip --version

# If 'python' doesn't work, try 'py' launcher:
py --version
py -m pip --version
```

If these commands don't work, you need to:

1. Install Python 3.9+ from <https://python.org>
2. During installation, **check "Add Python to PATH"**
3. Restart your terminal/PowerShell after installation

## Quick Start - Automated Startup Scripts

### Windows - Using PowerShell (Recommended)

```powershell
# Navigate to project directory
cd AirSense

# Run the system using PowerShell script
.\run_system_powershell.ps1
```

### Windows - Using Batch Script

```cmd
# Navigate to project directory
cd AirSense

# Run the system using batch script
.\run_system.bat
```

**What the scripts do:**

- Automatically detect a valid Python installation with pip
- Install all required dependencies
- Start the complete AirSense system (pipeline + API + dashboard)
- Open your browser to the dashboard

## Manual Setup (Alternative)

If you prefer manual control:

```powershell
# Navigate to project directory
cd AirSense

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run the complete system (pipeline + API + dashboard)
python -m src.main all
```

**Note:** Use `python -m src.main all` (not `python src/main.py all`) to avoid module import errors.

### Run Components Individually

If you want to run components separately:

```powershell
# 1. Run data processing pipeline first
python -m src.main pipeline

# 2. In a new terminal, start the API server
python -m src.main api

# 3. In another terminal, start the dashboard
python -m src.main dashboard
```

## Access Points

Once running, you can access:

- **Dashboard**: <http://localhost:8501>
- **API Documentation**: <http://localhost:8000/docs>
- **API Health Check**: <http://localhost:8000/health>

## Stopping the System

**If running via startup scripts:**

- Press `Ctrl+C` in the terminal to stop all components

**If running components individually:**

- Press `Ctrl+C` in each terminal window

**If using Docker:**

```powershell
docker-compose down
```

## Next Steps

Once the system is running successfully:

1. **Explore the Dashboard** (<http://localhost:8501>)
   - View real-time air quality metrics
   - Generate forecasts with different models
   - Analyze patterns and correlations

2. **Test the API** (<http://localhost:8000/docs>)
   - Try different endpoints
   - Generate forecasts programmatically
   - Integrate with your applications

3. **Use Your Own Data**
   - Place your CSV file in `data/raw/`
   - Update `.env` file if needed
   - Run the pipeline again

4. **Experiment with Models**
   - Try ARIMA vs LSTM forecasting
   - Compare simple vs advanced methods
   - Evaluate model performance

5. **Analyze Patterns**
   - Daily, weekly, monthly patterns
   - Pollutant correlations
   - Weather impact analysis

## Additional Resources

- **API Documentation**: Full endpoint reference at `/docs`
- **Project README**: `README.md` for architecture details
- **Configuration**: `.env` file for customization
- **Logs**: Check `logs/` directory for detailed execution logs

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review console output for error messages
3. Check log files in `logs/` directory
4. Ensure all prerequisites are installed correctly
5. Verify Python version is 3.9+ with pip available

## Performance Notes

**Expected execution times:**

- Pipeline processing: 2-5 minutes (for demo dataset)
- ARIMA model training: 30-60 seconds
- LSTM model training: 1-3 minutes
- API response time: <100ms for most endpoints

**System requirements:**

- RAM: 4GB minimum, 8GB recommended
- Disk: 2GB free space for data and models
- CPU: Multi-core recommended for Spark processing

---

**Built with ❤️ for environmental monitoring and air quality analysis**


## Troubleshooting

### Common Issues

#### 1. "Python not recognized" or "command not found"

**Problem:** Python is not in your system PATH.

**Solution:**

```powershell
# Try using the py launcher instead
py -m src.main all

# Or find where Python is installed
where python
where py
```

If neither works, reinstall Python from <https://python.org> and check "Add Python to PATH" during installation.

#### 2. "No module named pip"

**Problem:** The Python installation lacks pip (common with bundled Python from Nmap, PostgreSQL).

**Solution:** The startup scripts will automatically skip these installations. Ensure you have a proper Python installation from python.org.

#### 3. "ModuleNotFoundError: No module named 'src'"

**Problem:** Using incorrect module invocation method.

**Solution:** Always use `python -m src.main all` (not `python src/main.py all`).

#### 4. Java/Spark Issues

**Problem:** Spark requires Java 11+.

**Solution:**

```powershell
# Check Java version
java -version

# If not installed, download from:
# https://adoptium.net/ (recommended)
# or https://www.oracle.com/java/technologies/downloads/

# Set JAVA_HOME (if needed)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-11"
```

#### 5. Port Already in Use

**Problem:** Ports 8000 or 8501 are already occupied.

**Solution:**

```powershell
# Find what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Kill the process or use different ports (modify .env file)
```

#### 6. Dependencies Installation Fails

**Problem:** Network issues or package conflicts.

**Solution:**

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output to see errors
python -m pip install -r requirements.txt -v

# Try installing key packages individually
python -m pip install pyspark pandas fastapi streamlit plotly
```

### Verify Your Environment

Run these commands to check your setup:

```powershell
# Check Python version (should be 3.9+)
python --version

# Check pip
python -m pip --version

# Check Java (should be 11+)
java -version

# Check installed packages
python -m pip list | Select-String -Pattern "pyspark|fastapi|streamlit"
```

## Docker Deployment (Alternative)

If you prefer Docker:

```powershell
# Build and run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop the system
docker-compose down
```

## Data Requirements

The system expects air quality data in CSV format with these columns:

**Required:**

- `datetime` - Timestamp in format: YYYY-MM-DD HH:MM:SS

**Pollutants (at least one required):**

- `PM2.5`, `PM10`, `NO2`, `SO2`, `CO`, `O3`

**Weather data (optional but recommended):**

- `temperature`, `humidity`, `pressure`, `wind_speed`, `wind_direction`

**Sample data:** `data/raw/beijing_demo.csv`

## System Architecture

When running, the system consists of:

1. **Data Processing Pipeline**: Spark-based data cleaning and feature engineering
2. **API Server**: FastAPI backend with RESTful endpoints (port 8000)
3. **Dashboard**: Streamlit frontend for visualization (port 8501)
4. **Storage**: Processed data saved in Parquet format (`data/processed/`)
5. **Models**: Trained models saved in `models/` directory

## What Happens When You Run the System

1. **Pipeline Phase** (~2-5 minutes):
   - Loads raw data from `data/raw/beijing_demo.csv`
   - Cleans and validates data
   - Engineers features for ML models
   - Saves processed data to `data/processed/`

2. **API Phase**:
   - Starts FastAPI server on port 8000
   - Loads processed data
   - Initializes forecasting models
   - Provides REST endpoints

3. **Dashboard Phase**:
   - Starts Streamlit dashboard on port 8501
   - Connects to API
   - Opens browser automatically
   - Displays real-time visualizations

## Testing the System

### 1. Test API Endpoints

```powershell
# Health check
curl http://localhost:8000/health

# Get latest data
curl "http://localhost:8000/data?limit=10"

# Get statistics
curl http://localhost:8000/stats

# Get current AQI
curl http://localhost:8000/aqi

# Simple moving average forecast
curl -X POST http://localhost:8000/forecast/simple `
  -H "Content-Type: application/json" `
  -d '{\"pollutant\": \"PM2.5\", \"method\": \"moving_average\", \"forecast_steps\": 24}'

# Advanced ARIMA forecast
curl -X POST http://localhost:8000/forecast `
  -H "Content-Type: application/json" `
  -d '{\"target_pollutant\": \"PM2.5\", \"model_type\": \"arima\", \"steps\": 24, \"retrain\": false}'

# Time pattern analysis
curl "http://localhost:8000/analysis/time-patterns?pollutant=PM2.5&analysis_type=daily"

# Correlation analysis
curl "http://localhost:8000/analysis/correlations?analysis_type=comprehensive"
```

### 2. Explore the Dashboard

Open <http://localhost:8501> in your browser and explore:

- **Dashboard Tab**: Real-time KPI metrics, trends, distributions
- **Predictions Tab**: Interactive forecasting with multiple models
- **Insights Tab**: Feature importance, correlations, seasonal patterns

### 3. View API Documentation

Open <http://localhost:8000/docs> for interactive API documentation (Swagger UI).

## Monitoring and Logs

**Console Output:**

- Pipeline progress and statistics
- API request logs
- Dashboard status messages

**Log Files:**

- Application logs: `logs/airsense_YYYYMMDD.log`
- Structured JSON logging for production monitoring

**Data Files:**

- Processed data: `data/processed/processed_YYYYMMDD_HHMMSS.parquet`
- Trained models: `models/*.joblib` or `models/*.h5`
