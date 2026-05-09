"""API routes for AirSense."""

# Standard library imports
import os
from datetime import datetime, timedelta
from typing import List, Optional

# Third-party imports
import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, UploadFile, File

# Local imports
from ..core.config import get_settings
from ..core.exceptions import ModelError, ValidationError
from ..core.logging import get_logger
from ..data.schemas import (
    AQIResponse,
    DataQueryRequest,
    ForecastRequest,
    ForecastResponse,
    PipelineStatus,
)
from ..data.validator import DataValidator
from ..models.simple_forecasting import SimpleForecaster

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Create router
router = APIRouter()

# Dependency to get app state
async def get_forecaster(request: Request):
    """Get forecaster from app state."""
    app = request.app
    
    if not hasattr(app.state, "forecaster") or app.state.forecaster is None:
        raise HTTPException(status_code=503, detail="Forecaster not initialized")
    
    return app.state.forecaster

async def get_data_processor(request: Request):
    """Get data processor from app state."""
    app = request.app
    
    if not hasattr(app.state, "data_processor") or app.state.data_processor is None:
        raise HTTPException(
            status_code=503,
            detail="Data processor not initialized (requires PySpark and Java)",
        )
    
    return app.state.data_processor

async def get_validator(request: Request):
    """Get data validator from app state."""
    app = request.app
    
    if not hasattr(app.state, 'validator'):
        # Initialize validator if not present
        app.state.validator = DataValidator()
    
    return app.state.validator


async def get_optional_data_processor(request: Request):
    """Get data processor from app state when Spark is available."""
    return getattr(request.app.state, "data_processor", None)


def _get_latest_processed_dataframe() -> tuple[pd.DataFrame, str]:
    """Load the latest processed parquet file."""
    processed_dir = settings.processed_data_dir

    if not os.path.exists(processed_dir):
        raise HTTPException(status_code=404, detail="No processed data available")

    parquet_files = [f for f in os.listdir(processed_dir) if f.endswith(".parquet")]
    if not parquet_files:
        raise HTTPException(status_code=404, detail="No processed data available")

    latest_file = sorted(parquet_files)[-1]
    return pd.read_parquet(os.path.join(processed_dir, latest_file)), latest_file


def _correlation_strength(value: float, strong_threshold: float) -> str:
    return "strong" if abs(value) > strong_threshold else "moderate"


def _pandas_pollutant_correlations(df: pd.DataFrame) -> dict:
    """Calculate pollutant correlations without Spark."""
    available_pollutants = [col for col in settings.pollutant_columns if col in df.columns]

    if len(available_pollutants) < 2:
        return {"message": "Need at least 2 pollutants for correlation analysis"}

    corr_df = df[available_pollutants].apply(pd.to_numeric, errors="coerce").corr()
    correlations = {
        row: {
            col: float(value)
            for col, value in values.items()
            if pd.notna(value)
        }
        for row, values in corr_df.to_dict(orient="index").items()
    }

    strong_correlations = []
    for i, pollutant1 in enumerate(available_pollutants):
        for pollutant2 in available_pollutants[i + 1:]:
            corr_value = corr_df.loc[pollutant1, pollutant2]
            if pd.notna(corr_value) and abs(corr_value) > 0.3:
                corr_value = float(corr_value)
                strong_correlations.append({
                    "pollutant1": pollutant1,
                    "pollutant2": pollutant2,
                    "correlation": corr_value,
                    "strength": _correlation_strength(corr_value, 0.7),
                    "direction": "positive" if corr_value > 0 else "negative",
                })

    strong_correlations.sort(key=lambda item: abs(item["correlation"]), reverse=True)

    return {
        "analysis_type": "pollutant_correlations",
        "pollutants_analyzed": available_pollutants,
        "correlation_matrix": correlations,
        "strong_correlations": strong_correlations,
        "summary": {
            "total_pairs": len(strong_correlations),
            "positive_correlations": len([c for c in strong_correlations if c["correlation"] > 0]),
            "negative_correlations": len([c for c in strong_correlations if c["correlation"] < 0]),
            "strongest_correlation": strong_correlations[0] if strong_correlations else None,
        },
    }


def _pandas_weather_pollutant_correlations(df: pd.DataFrame) -> dict:
    """Calculate weather-pollutant correlations without Spark."""
    available_weather = [col for col in settings.weather_columns if col in df.columns]
    available_pollutants = [col for col in settings.pollutant_columns if col in df.columns]

    if not available_weather or not available_pollutants:
        return {"message": "Insufficient weather or pollutant data for correlation analysis"}

    numeric_df = df[available_pollutants + available_weather].apply(pd.to_numeric, errors="coerce")
    correlations = {}
    significant_correlations = []

    for pollutant in available_pollutants:
        correlations[pollutant] = {}
        for weather_var in available_weather:
            corr_value = numeric_df[pollutant].corr(numeric_df[weather_var])
            if pd.notna(corr_value):
                corr_value = float(corr_value)
                correlations[pollutant][weather_var] = corr_value
                if abs(corr_value) > 0.2:
                    significant_correlations.append({
                        "pollutant": pollutant,
                        "weather_variable": weather_var,
                        "correlation": corr_value,
                        "strength": _correlation_strength(corr_value, 0.5),
                        "direction": "positive" if corr_value > 0 else "negative",
                    })

    significant_correlations.sort(key=lambda item: abs(item["correlation"]), reverse=True)

    weather_insights = {}
    for weather_var in available_weather:
        weather_corrs = [
            corr for corr in significant_correlations
            if corr["weather_variable"] == weather_var
        ]
        if weather_corrs:
            weather_insights[weather_var] = {
                "most_affected_pollutant": max(weather_corrs, key=lambda item: abs(item["correlation"])),
                "correlation_count": len(weather_corrs),
                "positive_correlations": len([c for c in weather_corrs if c["correlation"] > 0]),
                "negative_correlations": len([c for c in weather_corrs if c["correlation"] < 0]),
            }

    return {
        "analysis_type": "weather_pollutant_correlations",
        "weather_variables": available_weather,
        "pollutants": available_pollutants,
        "correlation_matrix": correlations,
        "significant_correlations": significant_correlations,
        "weather_insights": weather_insights,
        "summary": {
            "total_correlations": len(significant_correlations),
            "strong_correlations": len([
                c for c in significant_correlations
                if c["strength"] == "strong"
            ]),
            "most_influential_weather": max(
                weather_insights.items(),
                key=lambda item: item[1]["correlation_count"],
            )[0] if weather_insights else None,
        },
    }


def _pandas_comprehensive_correlations(df: pd.DataFrame) -> dict:
    pollutant_correlations = _pandas_pollutant_correlations(df)
    weather_correlations = _pandas_weather_pollutant_correlations(df)

    key_findings = []
    strongest = pollutant_correlations.get("summary", {}).get("strongest_correlation")
    if strongest:
        key_findings.append(
            f"Strongest correlation: {strongest['pollutant1']} and {strongest['pollutant2']} "
            f"({strongest['correlation']:.3f}, {strongest['strength']} {strongest['direction']})"
        )

    most_influential = weather_correlations.get("summary", {}).get("most_influential_weather")
    if most_influential:
        key_findings.append(f"Most influential weather factor: {most_influential}")

    return {
        "analysis_timestamp": pd.Timestamp.now().isoformat(),
        "pollutant_correlations": pollutant_correlations,
        "weather_pollutant_correlations": weather_correlations,
        "summary_insights": {"key_findings": key_findings},
    }


@router.get("/data", response_model=dict)
async def get_data(
    limit: int = Query(1000, ge=1, le=10000),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    pollutants: Optional[List[str]] = Query(None),
    validate: bool = Query(False, description="Run data validation"),
    validator=Depends(get_validator)
):
    """Get air quality data with filtering and optional validation."""
    try:
        # Get latest processed data
        processed_dir = settings.processed_data_dir
        import os
        
        if not os.path.exists(processed_dir):
            raise HTTPException(status_code=404, detail="No processed data available")
        
        # Find latest parquet file
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        # Validate data if requested
        validation_report = None
        if validate:
            validation_report = validator.validate_dataframe(df)
            if validation_report["has_critical_issues"]:
                logger.warning("Data validation found critical issues", **validation_report)
        
        # Apply filters
        if start_date:
            df = df[df['datetime'] >= start_date]
        
        if end_date:
            df = df[df['datetime'] <= end_date]
        
        if pollutants:
            available_pollutants = [p for p in pollutants if p in df.columns]
            if available_pollutants:
                columns_to_keep = ['datetime'] + available_pollutants
                df = df[columns_to_keep]
        
        # Limit results
        if limit and len(df) > limit:
            df = df.tail(limit)
        
        # Convert to dict
        response = {
            "data": df.to_dict('records'),
            "count": len(df),
            "columns": list(df.columns),
            "source_file": latest_file
        }
        
        # Add validation report if requested
        if validation_report:
            response["validation"] = validation_report
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /data endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast", response_model=ForecastResponse)
async def create_forecast(
    request: ForecastRequest,
    background_tasks: BackgroundTasks,
    forecaster=Depends(get_forecaster)
):
    """Generate air quality forecast."""
    try:
        # Get data for the target pollutant
        processed_dir = settings.processed_data_dir
        import os
        
        if not os.path.exists(processed_dir):
            raise HTTPException(status_code=404, detail="No processed data available")
        
        # Load latest data
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        if request.target_pollutant not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Pollutant {request.target_pollutant} not found"
            )
        
        # Prepare data
        data = df.set_index('datetime')[request.target_pollutant]
        data = data.ffill().bfill()
        
        # Train or use existing model
        model_name = f"{request.model_type}_{request.target_pollutant}"
        
        if request.retrain or model_name not in forecaster.models:
            logger.info(f"Training {request.model_type} model for {request.target_pollutant}")
            
            # Train model with appropriate parameters
            train_params = {}
            if request.model_type == "arima":
                train_params = {"auto_params": True}
            elif request.model_type == "lstm":
                train_params = {
                    "epochs": 50,
                    "batch_size": 32,
                    "validation_split": 0.2
                }
            
            result = forecaster.train_model(
                request.model_type, 
                data, 
                **train_params
            )
            model_name = result["model_name"]
        
        # Generate forecast
        forecast_values = forecaster.forecast(model_name, request.steps)
        
        # Create forecast dates
        last_date = df['datetime'].max()
        forecast_dates = pd.date_range(
            start=last_date + timedelta(hours=1),
            periods=request.steps,
            freq="h"
        )
        
        # Prepare forecast data
        forecast_data = []
        for date, value in zip(forecast_dates, forecast_values):
            forecast_data.append({
                "datetime": date.isoformat(),
                "value": float(value),
                "target_pollutant": request.target_pollutant,
                "model_type": request.model_type
            })
        
        return ForecastResponse(
            forecast=forecast_data,
            model_name=model_name,
            target_pollutant=request.target_pollutant,
            steps=request.steps,
            generated_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /forecast endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aqi", response_model=AQIResponse)
async def get_aqi():
    """Get current AQI and health recommendations."""
    try:
        # Get latest data
        processed_dir = settings.processed_data_dir
        import os
        
        if not os.path.exists(processed_dir):
            raise HTTPException(status_code=404, detail="No processed data available")
        
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        # Get latest row
        latest_row = df.iloc[-1]
        
        # Calculate AQI components
        pm25_aqi = _calculate_aqi_pm25(latest_row.get('PM2.5', 0))
        pm10_aqi = _calculate_aqi_pm10(latest_row.get('PM10', 0))
        no2_aqi = _calculate_aqi_no2(latest_row.get('NO2', 0))
        
        overall_aqi = max(pm25_aqi, pm10_aqi, no2_aqi)
        
        return AQIResponse(
            aqi=overall_aqi,
            level=_get_aqi_level(overall_aqi),
            health_impact=_get_health_impact(overall_aqi),
            recommendations=_get_recommendations(overall_aqi),
            timestamp=latest_row['datetime'],
            component_aqi={
                "PM2.5": pm25_aqi,
                "PM10": pm10_aqi,
                "NO2": no2_aqi
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /aqi endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """Get data statistics."""
    try:
        # Get latest data
        processed_dir = settings.processed_data_dir
        import os
        
        if not os.path.exists(processed_dir):
            raise HTTPException(status_code=404, detail="No processed data available")
        
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        # Calculate statistics for pollutants
        stats = {}
        for pollutant in settings.pollutant_columns:
            if pollutant in df.columns:
                col_data = df[pollutant].dropna()
                if len(col_data) > 0:
                    stats[pollutant] = {
                        "mean": float(col_data.mean()),
                        "std": float(col_data.std()),
                        "min": float(col_data.min()),
                        "max": float(col_data.max()),
                        "median": float(col_data.median()),
                        "latest": float(col_data.iloc[-1]) if len(col_data) > 0 else None
                    }
        
        return {
            "statistics": stats,
            "data_range": {
                "start": df['datetime'].min().isoformat(),
                "end": df['datetime'].max().isoformat(),
                "total_records": len(df)
            },
            "source_file": latest_file
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models(forecaster=Depends(get_forecaster)):
    """List available trained models."""
    try:
        models = forecaster.list_models()
        return {
            "models": models,
            "total_count": len(models)
        }
        
    except Exception as e:
        logger.error(f"Error in /models endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/run", response_model=PipelineStatus)
async def run_pipeline(
    background_tasks: BackgroundTasks,
    validate_data: bool = Query(True, description="Validate data after processing"),
    processor=Depends(get_data_processor),
    validator=Depends(get_validator)
):
    """Run the data processing pipeline with optional validation."""
    try:
        # Add pipeline execution to background tasks
        background_tasks.add_task(_run_pipeline_task, processor, validator, validate_data)
        
        return PipelineStatus(
            status="running",
            timestamp=datetime.now(),
            processed_files=[],
            error_count=0,
            warning_count=0
        )
        
    except Exception as e:
        logger.error(f"Error starting pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_pipeline_task(processor, validator, validate_data=True):
    """Background task to run pipeline with validation."""
    try:
        logger.info("Starting pipeline execution in background")
        
        # Find input file
        input_file = os.path.join(settings.raw_data_dir, "beijing_demo.csv")
        if not os.path.exists(input_file):
            alt_input_file = os.path.join(settings.data_dir, "beijing_demo.csv")
            if os.path.exists(alt_input_file):
                input_file = alt_input_file
            else:
                logger.error(f"Input file not found: {input_file}")
                return

        # Generate output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(settings.processed_data_dir, f"processed_{timestamp}.parquet")
        
        # Run pipeline
        result = processor.process_pipeline(input_file, output_path)
        
        # Validate processed data if requested
        if validate_data:
            try:
                df = pd.read_parquet(output_path)
                validation_report = validator.validate_dataframe(df)
                
                if validation_report["has_critical_issues"]:
                    logger.warning("Pipeline produced data with critical issues", **validation_report)
                else:
                    logger.info("Pipeline data validation passed", **validation_report)
                    
            except Exception as e:
                logger.error(f"Data validation failed: {e}")
        
        logger.info("Pipeline completed", **result)
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")


# AQI calculation helper functions
def _calculate_aqi_pm25(pm25):
    """Calculate AQI for PM2.5."""
    if pm25 <= 12: return (50 / 12) * pm25
    elif pm25 <= 35.4: return ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1) + 51
    elif pm25 <= 55.4: return ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5) + 101
    else: return 200

def _calculate_aqi_pm10(pm10):
    """Calculate AQI for PM10."""
    if pm10 <= 54: return (50 / 54) * pm10
    elif pm10 <= 154: return ((100 - 51) / (154 - 55)) * (pm10 - 55) + 51
    elif pm10 <= 254: return ((150 - 101) / (254 - 155)) * (pm10 - 155) + 101
    else: return 200

def _calculate_aqi_no2(no2):
    """Calculate AQI for NO2."""
    if no2 <= 53: return (50 / 53) * no2
    elif no2 <= 100: return ((100 - 51) / (100 - 54)) * (no2 - 54) + 51
    elif no2 <= 360: return ((150 - 101) / (360 - 101)) * (no2 - 101) + 101
    else: return 200

def _get_aqi_level(aqi):
    """Get AQI level description."""
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups"
    else: return "Unhealthy"

def _get_health_impact(aqi):
    """Get health impact description."""
    if aqi <= 50: return "Air quality is satisfactory"
    elif aqi <= 100: return "Acceptable for most people"
    elif aqi <= 150: return "Sensitive groups may experience health effects"
    else: return "Everyone may experience health effects"

def _get_recommendations(aqi):
    """Get health recommendations."""
    if aqi <= 50: return "Enjoy outdoor activities"
    elif aqi <= 100: return "Unusually sensitive people should reduce prolonged outdoor exertion"
    elif aqi <= 150: return "Sensitive groups should reduce prolonged outdoor exertion"
    else: return "Everyone should avoid prolonged outdoor exertion"


# Simple forecasting endpoints
@router.post("/forecast/simple")
async def simple_forecast(
    request: dict,
):
    """Generate simple forecast using moving averages and other basic methods."""
    try:
        pollutant = request.get("pollutant", "PM2.5")
        method = request.get("method", "moving_average")
        forecast_steps = request.get("forecast_steps", 24)
        window_size = request.get("window_size", 24)
        
        # Get latest data
        processed_dir = settings.processed_data_dir
        import os

        if not os.path.isdir(processed_dir):
            raise HTTPException(status_code=404, detail="No processed data available")
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        if pollutant not in df.columns:
            raise HTTPException(status_code=400, detail=f"Pollutant {pollutant} not found")
        
        # Get time series data
        ts_data = df[pollutant].dropna()
        
        # Initialize simple forecaster
        forecaster = SimpleForecaster()
        
        # Generate forecast based on method
        if method == "moving_average":
            result = forecaster.moving_average_forecast(ts_data, window_size, forecast_steps)
        elif method == "weighted_moving_average":
            result = forecaster.weighted_moving_average_forecast(ts_data, window_size, forecast_steps)
        elif method == "seasonal_naive":
            result = forecaster.seasonal_naive_forecast(ts_data, 24, forecast_steps)
        elif method == "exponential_smoothing":
            alpha = request.get("alpha", 0.3)
            result = forecaster.exponential_smoothing_forecast(ts_data, alpha, forecast_steps)
        elif method == "ensemble":
            result = forecaster.ensemble_forecast(ts_data, forecast_steps)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown forecasting method: {method}")
        
        return {
            "pollutant": pollutant,
            "method": method,
            "forecast_steps": forecast_steps,
            "data_points_used": len(ts_data),
            "forecast": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Simple forecast failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Time-based analysis endpoints
@router.get("/analysis/time-patterns")
async def time_patterns_analysis(
    pollutant: str = Query(...),
    analysis_type: str = Query("comprehensive"),
    processor=Depends(get_optional_data_processor)
):
    """Analyze time-based patterns for pollutants."""
    try:
        # Get latest data
        processed_dir = settings.processed_data_dir
        import os
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        # Use simple analyzer (pandas-based) if Spark is not available
        if processor is None:
            from ..data.simple_analysis import SimpleAnalyzer
            analyzer = SimpleAnalyzer()
            
            # Perform analysis
            if analysis_type == "daily":
                result = analyzer.daily_patterns(df, pollutant)
            elif analysis_type == "weekly":
                result = analyzer.weekly_patterns(df, pollutant)
            elif analysis_type == "monthly":
                result = analyzer.monthly_patterns(df, pollutant)
            elif analysis_type == "yearly":
                result = analyzer.yearly_trends(df, pollutant)
            elif analysis_type == "comprehensive":
                result = analyzer.comprehensive_time_analysis(df, [pollutant])
            else:
                raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")
        else:
            # Use Spark-based analyzer
            spark_df = processor.spark.createDataFrame(df)
            from ..data.time_analysis import TimeBasedAnalyzer
            analyzer = TimeBasedAnalyzer(processor.spark)
            
            # Perform analysis
            if analysis_type == "daily":
                result = analyzer.daily_patterns(spark_df, pollutant)
            elif analysis_type == "weekly":
                result = analyzer.weekly_patterns(spark_df, pollutant)
            elif analysis_type == "monthly":
                result = analyzer.monthly_patterns(spark_df, pollutant)
            elif analysis_type == "yearly":
                result = analyzer.yearly_trends(spark_df, pollutant)
            elif analysis_type == "comprehensive":
                result = analyzer.comprehensive_time_analysis(spark_df, [pollutant])
            else:
                raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")
        
        return {
            "pollutant": pollutant,
            "analysis_type": analysis_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Time patterns analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Correlation analysis endpoints
@router.get("/analysis/correlations")
async def correlation_analysis(
    analysis_type: str = Query("comprehensive"),
    processor=Depends(get_optional_data_processor)
):
    """Perform correlation analysis."""
    try:
        df, latest_file = _get_latest_processed_dataframe()

        if processor is not None:
            from ..data.correlation_analysis import CorrelationAnalyzer

            spark_df = processor.spark.createDataFrame(df)
            analyzer = CorrelationAnalyzer(processor.spark)

            if analysis_type == "pollutants":
                result = {"pollutant_correlations": analyzer.pollutant_correlations(spark_df)}
            elif analysis_type == "weather":
                result = {"weather_pollutant_correlations": analyzer.weather_pollutant_correlations(spark_df)}
            elif analysis_type == "comprehensive":
                spark_result = analyzer.comprehensive_correlation_analysis(spark_df)
                result = spark_result.get("comprehensive_analysis", spark_result)
                if "summary_insights" in spark_result:
                    result["summary_insights"] = spark_result["summary_insights"]
            else:
                raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")
        else:
            logger.info(
                "SparkDataProcessor unavailable; using pandas correlation analysis",
                analysis_type=analysis_type,
                source_file=latest_file,
            )
            if analysis_type == "pollutants":
                result = {"pollutant_correlations": _pandas_pollutant_correlations(df)}
            elif analysis_type == "weather":
                result = {"weather_pollutant_correlations": _pandas_weather_pollutant_correlations(df)}
            elif analysis_type == "comprehensive":
                result = _pandas_comprehensive_correlations(df)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")
        
        return {
            "analysis_type": analysis_type,
            "result": result,
            "source_file": latest_file,
            "engine": "spark" if processor is not None else "pandas",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/temporal-correlations")
async def temporal_correlations(
    pollutant: str = Query(...),
    processor=Depends(get_optional_data_processor)
):
    """Analyze temporal correlations for a specific pollutant."""
    try:
        # Get latest data
        processed_dir = settings.processed_data_dir
        import os
        parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
        if not parquet_files:
            raise HTTPException(status_code=404, detail="No processed data available")
        
        latest_file = sorted(parquet_files)[-1]
        df = pd.read_parquet(os.path.join(processed_dir, latest_file))
        
        # Use simple analyzer if Spark is not available
        if processor is None:
            # Pandas-based temporal correlation (autocorrelation)
            if pollutant not in df.columns:
                raise HTTPException(status_code=400, detail=f"Pollutant {pollutant} not found")
            
            ts_data = df[pollutant].dropna()
            
            # Calculate autocorrelation for different lags
            lags = [1, 6, 12, 24, 48, 72, 168]  # 1h, 6h, 12h, 1d, 2d, 3d, 1w
            autocorr = {}
            for lag in lags:
                if len(ts_data) > lag:
                    autocorr[f"lag_{lag}h"] = float(ts_data.autocorr(lag=lag))
            
            result = {
                "pollutant": pollutant,
                "autocorrelations": autocorr,
                "data_points": len(ts_data),
                "engine": "pandas"
            }
        else:
            # Use Spark-based analyzer
            spark_df = processor.spark.createDataFrame(df)
            from ..data.correlation_analysis import CorrelationAnalyzer
            analyzer = CorrelationAnalyzer(processor.spark)
            result = analyzer.temporal_correlations(spark_df, pollutant)
            result["engine"] = "spark"
        
        return {
            "pollutant": pollutant,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Temporal correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_data(
    file_path: Optional[str] = Query(None, description="Path to file to validate, or latest if not provided"),
    validator=Depends(get_validator)
):
    """Validate air quality data and return comprehensive report."""
    try:
        # Get file to validate
        if file_path:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            df = pd.read_parquet(file_path) if file_path.endswith('.parquet') else pd.read_csv(file_path)
        else:
            # Use latest processed file
            processed_dir = settings.processed_data_dir
            parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
            if not parquet_files:
                raise HTTPException(status_code=404, detail="No processed data available")
            
            latest_file = sorted(parquet_files)[-1]
            file_path = os.path.join(processed_dir, latest_file)
            df = pd.read_parquet(file_path)
        
        # Run comprehensive validation
        validation_report = validator.validate_dataframe(df)
        
        return {
            "file_path": file_path,
            "validation_report": validation_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    process_immediately: bool = Query(True, description="Process the uploaded file immediately"),
    request: Request = None,
    background_tasks: BackgroundTasks = None,
    validator=Depends(get_validator)
):
    """Upload air quality data file (CSV format)."""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400, 
                detail="Only CSV files are supported. Please upload a .csv file"
            )
        
        # Save uploaded file to raw data directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploaded_{timestamp}.csv"
        file_path = os.path.join(settings.raw_data_dir, filename)
        
        # Ensure raw data directory exists
        os.makedirs(settings.raw_data_dir, exist_ok=True)
        
        # Save file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded successfully: {file_path}")
        
        # Validate uploaded file
        try:
            df = pd.read_csv(file_path)
            validation_report = validator.validate_dataframe(df)
            
            if validation_report["has_critical_issues"]:
                logger.warning("Uploaded file has critical validation issues", **validation_report)
                return {
                    "status": "uploaded_with_warnings",
                    "message": "File uploaded but has validation issues",
                    "file_path": file_path,
                    "filename": filename,
                    "validation": validation_report,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Validation failed for uploaded file: {e}")
            return {
                "status": "uploaded_without_validation",
                "message": "File uploaded but validation failed",
                "file_path": file_path,
                "filename": filename,
                "validation_error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        # Process immediately if requested
        if process_immediately and request:
            # Check if processor is available
            processor = getattr(request.app.state, "data_processor", None)
            
            if processor and background_tasks:
                # Add processing task to background
                background_tasks.add_task(_process_uploaded_file, file_path, processor, validator)
                
                return {
                    "status": "uploaded_and_processing",
                    "message": "File uploaded successfully and processing started",
                    "file_path": file_path,
                    "filename": filename,
                    "validation": validation_report,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning("Data processor not available, file uploaded but not processed")
                return {
                    "status": "uploaded_not_processed",
                    "message": "File uploaded but processor not available (requires PySpark)",
                    "file_path": file_path,
                    "filename": filename,
                    "validation": validation_report,
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "status": "uploaded",
            "message": "File uploaded successfully",
            "file_path": file_path,
            "filename": filename,
            "validation": validation_report,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_uploaded_file(file_path: str, processor, validator):
    """Background task to process uploaded file."""
    try:
        logger.info(f"Processing uploaded file: {file_path}")
        
        # Generate output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(settings.processed_data_dir, f"processed_{timestamp}.parquet")
        
        # Run pipeline
        result = processor.process_pipeline(file_path, output_path)
        
        # Validate processed data
        try:
            df = pd.read_parquet(output_path)
            validation_report = validator.validate_dataframe(df)
            
            if validation_report["has_critical_issues"]:
                logger.warning("Processed uploaded file has critical issues", **validation_report)
            else:
                logger.info("Uploaded file processed and validated successfully", **validation_report)
                
        except Exception as e:
            logger.error(f"Validation of processed file failed: {e}")
        
        logger.info("Uploaded file processing completed", **result)
        
    except Exception as e:
        logger.error(f"Processing uploaded file failed: {e}")
