# AirSense API Documentation

## Overview

The AirSense API provides comprehensive endpoints for air quality data access, forecasting, analysis, and monitoring.

**Base URL:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

Currently, the API does not require authentication. This will be added in future versions.

---

## Endpoints

### Health Check

#### `GET /health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-29T10:00:00",
  "version": "1.0.0"
}
```

---

### Data Endpoints

#### `GET /data`

Retrieve air quality data with optional filtering and validation.

**Query Parameters:**
- `limit` (int, optional): Maximum number of records to return (1-10000, default: 1000)
- `start_date` (datetime, optional): Filter data from this date
- `end_date` (datetime, optional): Filter data until this date
- `pollutants` (list[str], optional): Filter specific pollutants
- `validate` (bool, optional): Run data validation (default: false)

**Example Request:**
```bash
curl "http://localhost:8000/data?limit=100&pollutants=PM2.5&pollutants=NO2&validate=true"
```

**Response:**
```json
{
  "data": [
    {
      "datetime": "2026-04-29T10:00:00",
      "PM2.5": 35.2,
      "NO2": 42.1,
      "temperature": 22.5
    }
  ],
  "count": 100,
  "columns": ["datetime", "PM2.5", "NO2", "temperature"],
  "source_file": "processed_20260429_100000.parquet",
  "validation": {
    "has_critical_issues": false,
    "total_issues": 0
  }
}
```

---

#### `GET /stats`

Get statistical summary of air quality data.

**Response:**
```json
{
  "statistics": {
    "PM2.5": {
      "mean": 35.2,
      "std": 12.4,
      "min": 10.0,
      "max": 150.0,
      "median": 32.5,
      "latest": 38.1
    }
  },
  "data_range": {
    "start": "2026-01-01T00:00:00",
    "end": "2026-04-29T10:00:00",
    "total_records": 10000
  }
}
```

---

#### `POST /validate`

Validate air quality data and get comprehensive report.

**Query Parameters:**
- `file_path` (str, optional): Path to file to validate (uses latest if not provided)

**Response:**
```json
{
  "file_path": "/path/to/data.parquet",
  "validation_report": {
    "has_critical_issues": false,
    "schema_validation": {
      "passed": true,
      "issues": []
    },
    "data_quality": {
      "missing_data_percentage": 2.5,
      "outliers_detected": 15
    }
  },
  "timestamp": "2026-04-29T10:00:00"
}
```

---

### Forecasting Endpoints

#### `POST /forecast`

Generate air quality forecasts using advanced ML models.

**Request Body:**
```json
{
  "target_pollutant": "PM2.5",
  "model_type": "arima",
  "steps": 24,
  "retrain": false
}
```

**Parameters:**
- `target_pollutant` (str): Pollutant to forecast (PM2.5, PM10, NO2, etc.)
- `model_type` (str): Model type ("arima" or "lstm")
- `steps` (int): Number of hours to forecast
- `retrain` (bool): Whether to retrain the model

**Response:**
```json
{
  "forecast": [
    {
      "datetime": "2026-04-29T11:00:00",
      "value": 36.5,
      "target_pollutant": "PM2.5",
      "model_type": "arima"
    }
  ],
  "model_name": "arima_PM2.5_20260429_100000",
  "target_pollutant": "PM2.5",
  "steps": 24,
  "generated_at": "2026-04-29T10:00:00"
}
```

---

#### `POST /forecast/simple`

Generate forecasts using simple statistical methods.

**Request Body:**
```json
{
  "pollutant": "PM2.5",
  "method": "moving_average",
  "forecast_steps": 24,
  "window_size": 24,
  "alpha": 0.3
}
```

**Available Methods:**
- `moving_average`: Simple moving average
- `weighted_moving_average`: Weighted moving average
- `seasonal_naive`: Seasonal naive forecast
- `exponential_smoothing`: Exponential smoothing
- `ensemble`: Ensemble of multiple methods

**Response:**
```json
{
  "pollutant": "PM2.5",
  "method": "moving_average",
  "forecast_steps": 24,
  "data_points_used": 1000,
  "forecast": [35.2, 36.1, 34.8],
  "timestamp": "2026-04-29T10:00:00"
}
```

---

### AQI Endpoints

#### `GET /aqi`

Get current Air Quality Index and health recommendations.

**Response:**
```json
{
  "aqi": 85,
  "level": "Moderate",
  "health_impact": "Acceptable for most people",
  "recommendations": "Unusually sensitive people should reduce prolonged outdoor exertion",
  "timestamp": "2026-04-29T10:00:00",
  "component_aqi": {
    "PM2.5": 85,
    "PM10": 72,
    "NO2": 65
  }
}
```

**AQI Levels:**
- 0-50: Good
- 51-100: Moderate
- 101-150: Unhealthy for Sensitive Groups
- 151+: Unhealthy

---

### Model Management

#### `GET /models`

List all trained models.

**Response:**
```json
{
  "models": {
    "arima_PM2.5_20260429": {
      "type": "ARIMA",
      "trained": true,
      "metadata": {
        "order": [1, 1, 1],
        "aic": 1234.5,
        "training_date": "2026-04-29T09:00:00"
      }
    }
  },
  "total_count": 1
}
```

---

### Pipeline Management

#### `POST /pipeline/run`

Execute the data processing pipeline.

**Query Parameters:**
- `validate_data` (bool, optional): Validate data after processing (default: true)

**Response:**
```json
{
  "status": "running",
  "timestamp": "2026-04-29T10:00:00",
  "processed_files": [],
  "error_count": 0,
  "warning_count": 0
}
```

---

### Analysis Endpoints

#### `GET /analysis/time-patterns`

Analyze time-based patterns in air quality data.

**Query Parameters:**
- `pollutant` (str, required): Pollutant to analyze
- `analysis_type` (str, optional): Type of analysis (default: "comprehensive")
  - `daily`: Daily patterns
  - `weekly`: Weekly patterns
  - `monthly`: Monthly patterns
  - `yearly`: Yearly trends
  - `comprehensive`: All patterns

**Example Request:**
```bash
curl "http://localhost:8000/analysis/time-patterns?pollutant=PM2.5&analysis_type=daily"
```

**Response:**
```json
{
  "pollutant": "PM2.5",
  "analysis_type": "daily",
  "result": {
    "hourly_averages": {
      "0": 28.5,
      "1": 26.3,
      "6": 45.2,
      "12": 38.1
    },
    "peak_hours": [6, 7, 8],
    "low_hours": [1, 2, 3]
  },
  "timestamp": "2026-04-29T10:00:00"
}
```

---

#### `GET /analysis/correlations`

Perform correlation analysis between pollutants and weather factors.

**Query Parameters:**
- `analysis_type` (str, optional): Type of analysis (default: "comprehensive")
  - `pollutants`: Pollutant-to-pollutant correlations
  - `weather`: Weather-to-pollutant correlations
  - `comprehensive`: All correlations

**Response:**
```json
{
  "analysis_type": "comprehensive",
  "result": {
    "pollutant_correlations": {
      "PM2.5_PM10": 0.85,
      "PM2.5_NO2": 0.62
    },
    "weather_correlations": {
      "PM2.5_temperature": -0.35,
      "PM2.5_humidity": 0.42
    }
  },
  "timestamp": "2026-04-29T10:00:00"
}
```

---

#### `GET /analysis/temporal-correlations`

Analyze temporal correlations (autocorrelation) for a pollutant.

**Query Parameters:**
- `pollutant` (str, required): Pollutant to analyze

**Response:**
```json
{
  "pollutant": "PM2.5",
  "result": {
    "lag_1": 0.92,
    "lag_24": 0.78,
    "lag_168": 0.65
  },
  "timestamp": "2026-04-29T10:00:00"
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error
- `503`: Service Unavailable (service not initialized)

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in future versions.

---

## Data Formats

### Datetime Format
All datetime values use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

### Pollutant Units
- PM2.5, PM10, NO2, SO2, CO, O3: μg/m³
- Temperature: °C
- Humidity: %
- Pressure: hPa
- Wind Speed: m/s
- Wind Direction: degrees

---

## Examples

### Python Client Example

```python
import requests

# Get latest data
response = requests.get("http://localhost:8000/data?limit=100")
data = response.json()

# Generate forecast
forecast_request = {
    "target_pollutant": "PM2.5",
    "model_type": "arima",
    "steps": 24,
    "retrain": False
}
response = requests.post("http://localhost:8000/forecast", json=forecast_request)
forecast = response.json()

# Get AQI
response = requests.get("http://localhost:8000/aqi")
aqi = response.json()
print(f"Current AQI: {aqi['aqi']} - {aqi['level']}")
```

### JavaScript Client Example

```javascript
// Get latest data
fetch('http://localhost:8000/data?limit=100')
  .then(response => response.json())
  .then(data => console.log(data));

// Generate forecast
fetch('http://localhost:8000/forecast', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target_pollutant: 'PM2.5',
    model_type: 'arima',
    steps: 24,
    retrain: false
  })
})
  .then(response => response.json())
  .then(forecast => console.log(forecast));
```

---

## Changelog

### Version 1.0.0 (2026-04-29)
- Initial API release
- Data retrieval and filtering
- ARIMA and LSTM forecasting
- Simple forecasting methods
- AQI calculation
- Time-based pattern analysis
- Correlation analysis
- Data validation
- Pipeline management
