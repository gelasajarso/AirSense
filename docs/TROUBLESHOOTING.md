# AirSense Troubleshooting Guide

## Common Issues and Solutions

---

## Installation Issues

### Issue: Python version incompatibility

**Symptoms:**
```
ERROR: Package requires Python >=3.9
```

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.9+ if needed
# Ubuntu/Debian:
sudo apt-get install python3.9

# macOS:
brew install python@3.9

# Windows: Download from python.org
```

---

### Issue: Java not found for Spark

**Symptoms:**
```
JAVA_HOME is not set
Exception: Java gateway process exited before sending its port number
```

**Solution:**
```bash
# Check Java installation
java -version

# Install Java 11+
# Ubuntu/Debian:
sudo apt-get install openjdk-11-jre-headless

# macOS:
brew install openjdk@11

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Linux
export JAVA_HOME=/usr/local/opt/openjdk@11  # macOS

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
```

---

### Issue: Dependency installation fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement
```

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# If specific package fails, install separately
pip install pyspark==3.4.0

# For TensorFlow issues on Apple Silicon
pip install tensorflow-macos tensorflow-metal
```

---

## Runtime Issues

### Issue: Spark session fails to start

**Symptoms:**
```
Exception: Java gateway process exited
Py4JNetworkError: An error occurred while trying to connect to the Java server
```

**Solutions:**

1. **Check Java installation:**
```bash
java -version
echo $JAVA_HOME
```

2. **Reduce Spark memory:**
```bash
export SPARK_DRIVER_MEMORY=2g
export SPARK_EXECUTOR_MEMORY=2g
```

3. **Check for port conflicts:**
```bash
# Check if port 4040 is in use
lsof -i :4040
netstat -an | grep 4040

# Kill conflicting process
kill -9 <PID>
```

4. **Clear Spark temporary files:**
```bash
rm -rf /tmp/spark-*
```

---

### Issue: Out of memory errors

**Symptoms:**
```
java.lang.OutOfMemoryError: Java heap space
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Increase Spark memory:**
```python
# In src/core/config.py
spark_config = {
    "spark.driver.memory": "4g",
    "spark.executor.memory": "4g",
    "spark.driver.maxResultSize": "2g"
}
```

2. **Reduce data batch size:**
```python
# Process data in smaller chunks
chunk_size = 10000
for chunk in pd.read_csv(file, chunksize=chunk_size):
    process(chunk)
```

3. **Increase Docker memory:**
```yaml
# In docker-compose.yml
services:
  airsense-api:
    deploy:
      resources:
        limits:
          memory: 8G
```

---

### Issue: Port already in use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
ERROR: for airsense-api  Cannot start service
```

**Solutions:**

1. **Find and kill process:**
```bash
# Linux/macOS
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

2. **Change port in configuration:**
```bash
# In .env
API_PORT=8001
```

3. **Stop Docker containers:**
```bash
docker-compose down
docker ps -a
docker rm -f <container_id>
```

---

### Issue: Data file not found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/beijing_demo.csv'
```

**Solutions:**

1. **Check file location:**
```bash
ls -la data/raw/
find . -name "beijing_demo.csv"
```

2. **Create directories:**
```bash
mkdir -p data/raw data/processed
```

3. **Download sample data:**
```bash
# Place your data file in data/raw/
cp /path/to/your/data.csv data/raw/beijing_demo.csv
```

---

## Model Training Issues

### Issue: ARIMA training fails

**Symptoms:**
```
ValueError: The computed initial AR coefficients are not stationary
LinAlgError: SVD did not converge
```

**Solutions:**

1. **Check data quality:**
```python
# Remove NaN values
data = data.dropna()

# Check for constant values
if data.std() == 0:
    print("Data has no variation")
```

2. **Adjust ARIMA parameters:**
```python
# Use simpler model
model = ARIMAModel()
model.train(data, order=(1, 1, 1), auto_params=False)
```

3. **Increase data size:**
```python
# ARIMA needs at least 100 data points
if len(data) < 100:
    print("Insufficient data for ARIMA")
```

---

### Issue: LSTM training fails

**Symptoms:**
```
ImportError: No module named 'tensorflow'
ValueError: Input 0 of layer sequential is incompatible with the layer
```

**Solutions:**

1. **Install TensorFlow:**
```bash
pip install tensorflow>=2.13.0

# For Apple Silicon
pip install tensorflow-macos tensorflow-metal
```

2. **Check data shape:**
```python
# Ensure data has enough samples
if len(data) < sequence_length + 50:
    print("Insufficient data for LSTM")
```

3. **Reduce model complexity:**
```python
# Use smaller LSTM units
model = LSTMModel(sequence_length=12, lstm_units=25)
```

---

### Issue: Model predictions are unrealistic

**Symptoms:**
- Negative values for pollutants
- Extremely high values
- Constant predictions

**Solutions:**

1. **Check data preprocessing:**
```python
# Verify data scaling
print(f"Data range: {data.min()} to {data.max()}")
print(f"Data mean: {data.mean()}, std: {data.std()}")
```

2. **Retrain model:**
```python
# Force model retraining
forecast_request = {
    "target_pollutant": "PM2.5",
    "model_type": "arima",
    "steps": 24,
    "retrain": True  # Force retrain
}
```

3. **Use ensemble methods:**
```python
# Try simple forecasting methods
result = forecaster.ensemble_forecast(data, steps=24)
```

---

## API Issues

### Issue: API returns 503 Service Unavailable

**Symptoms:**
```json
{
  "detail": "Forecaster not initialized"
}
```

**Solutions:**

1. **Check API startup:**
```bash
# View API logs
tail -f logs/airsense_*.log

# Check if all components initialized
curl http://localhost:8000/health
```

2. **Restart API:**
```bash
# Kill existing process
pkill -f "uvicorn"

# Restart
python src/main.py api
```

---

### Issue: API returns 404 for data endpoints

**Symptoms:**
```json
{
  "detail": "No processed data available"
}
```

**Solutions:**

1. **Run data pipeline:**
```bash
# Process data first
python src/main.py pipeline

# Or via API
curl -X POST http://localhost:8000/pipeline/run
```

2. **Check processed data:**
```bash
ls -la data/processed/
```

---

### Issue: Slow API responses

**Symptoms:**
- Requests take >10 seconds
- Timeout errors

**Solutions:**

1. **Enable caching:**
```python
# In .env
REDIS_URL=redis://localhost:6379/0
```

2. **Reduce data size:**
```bash
# Use limit parameter
curl "http://localhost:8000/data?limit=100"
```

3. **Optimize Spark:**
```python
# Reduce shuffle partitions
spark_config = {
    "spark.sql.shuffle.partitions": "50"
}
```

---

## Dashboard Issues

### Issue: Dashboard won't start

**Symptoms:**
```
streamlit.errors.StreamlitError: Port 8501 is already in use
```

**Solutions:**

1. **Change port:**
```bash
streamlit run frontend/dashboard.py --server.port=8502
```

2. **Kill existing process:**
```bash
lsof -i :8501
kill -9 <PID>
```

---

### Issue: Dashboard shows no data

**Symptoms:**
- Empty charts
- "No data available" messages

**Solutions:**

1. **Check API connection:**
```python
# In dashboard, verify API_URL
import os
api_url = os.getenv("API_URL", "http://localhost:8000")
print(f"API URL: {api_url}")
```

2. **Test API manually:**
```bash
curl http://localhost:8000/data?limit=10
```

3. **Run pipeline:**
```bash
python src/main.py pipeline
```

---

## Docker Issues

### Issue: Docker build fails

**Symptoms:**
```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Solutions:**

1. **Check Dockerfile:**
```bash
# Validate Dockerfile syntax
docker build --no-cache -t airsense:latest .
```

2. **Increase Docker resources:**
- Docker Desktop → Settings → Resources
- Increase CPU and Memory

3. **Clean Docker cache:**
```bash
docker system prune -a
docker builder prune
```

---

### Issue: Container exits immediately

**Symptoms:**
```
Container airsense-api exited with code 1
```

**Solutions:**

1. **Check container logs:**
```bash
docker logs airsense-api
docker-compose logs airsense-api
```

2. **Run interactively:**
```bash
docker run -it airsense:latest /bin/bash
```

3. **Check environment variables:**
```bash
docker exec airsense-api env
```

---

## Data Quality Issues

### Issue: Validation reports critical issues

**Symptoms:**
```json
{
  "has_critical_issues": true,
  "issues": ["Missing required columns", "Invalid data ranges"]
}
```

**Solutions:**

1. **Check data schema:**
```python
# Verify required columns
required = ["datetime", "PM2.5", "PM10", "NO2"]
missing = set(required) - set(df.columns)
print(f"Missing columns: {missing}")
```

2. **Clean data:**
```python
# Remove outliers
df = df[(df['PM2.5'] >= 0) & (df['PM2.5'] <= 500)]

# Fill missing values
df = df.fillna(method='ffill').fillna(method='bfill')
```

3. **Validate before processing:**
```bash
curl -X POST "http://localhost:8000/validate"
```

---

## Performance Issues

### Issue: Pipeline takes too long

**Symptoms:**
- Processing takes >10 minutes
- High CPU/memory usage

**Solutions:**

1. **Optimize Spark configuration:**
```python
spark_config = {
    "spark.sql.shuffle.partitions": "50",
    "spark.default.parallelism": "50",
    "spark.sql.adaptive.enabled": "true"
}
```

2. **Process in batches:**
```python
# Split large files
chunk_size = 100000
for chunk in pd.read_csv(file, chunksize=chunk_size):
    process_chunk(chunk)
```

3. **Use parquet format:**
```python
# Parquet is faster than CSV
df.to_parquet("output.parquet", compression="snappy")
```

---

## Logging Issues

### Issue: No logs generated

**Symptoms:**
- Empty logs directory
- No log files created

**Solutions:**

1. **Check log directory:**
```bash
mkdir -p logs
chmod 755 logs
```

2. **Verify logging configuration:**
```python
# In src/core/logging.py
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
```

3. **Check log level:**
```bash
# In .env
LOG_LEVEL=INFO  # Not ERROR or CRITICAL
```

---

## Testing Issues

### Issue: Tests fail to run

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
```

**Solutions:**

1. **Install in development mode:**
```bash
pip install -e .
```

2. **Set PYTHONPATH:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

3. **Use pytest from project root:**
```bash
cd /path/to/AirSense
pytest tests/
```

---

## Getting Help

If you're still experiencing issues:

1. **Check logs:**
   ```bash
   tail -f logs/airsense_*.log
   ```

2. **Enable debug logging:**
   ```bash
   # In .env
   LOG_LEVEL=DEBUG
   ```

3. **Run diagnostics:**
   ```bash
   python -c "import sys; print(sys.version)"
   java -version
   docker --version
   ```

4. **Create GitHub issue:**
   - Include error messages
   - Include system information
   - Include steps to reproduce

5. **Community support:**
   - GitHub Discussions
   - Stack Overflow (tag: airsense)
   - Project documentation

---

## Preventive Measures

### Regular Maintenance

1. **Update dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

2. **Clean temporary files:**
   ```bash
   rm -rf /tmp/spark-*
   rm -rf __pycache__
   find . -name "*.pyc" -delete
   ```

3. **Monitor disk space:**
   ```bash
   df -h
   du -sh data/processed/
   ```

4. **Backup data:**
   ```bash
   tar -czf backup_$(date +%Y%m%d).tar.gz data/ models/
   ```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Data availability
curl http://localhost:8000/data?limit=1

# Model status
curl http://localhost:8000/models
```

---

## Quick Reference

### Common Commands

```bash
# Start system
python src/main.py all

# Run pipeline only
python src/main.py pipeline

# Run API only
python src/main.py api

# Run dashboard only
python src/main.py dashboard

# Docker commands
docker-compose up -d
docker-compose logs -f
docker-compose down

# Check status
curl http://localhost:8000/health
curl http://localhost:8000/models
```

### Environment Variables

```bash
# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000

# Spark
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=4g
```

### Log Locations

- Application logs: `logs/airsense_*.log`
- Docker logs: `docker logs <container_name>`
- Spark logs: `/tmp/spark-*/`
