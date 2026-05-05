"""FastAPI main application for AirSense."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime
import psutil
import os

from ..core.config import get_settings
from ..core.logging import get_logger
from ..core.exceptions import AirSenseError
from .routes import router

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Global variables for startup/shutdown
startup_time = None
latest_data = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global startup_time, latest_data
    
    startup_time = time.time()
    logger.info("AirSense API starting up", version=settings.app_version)

    try:
        await initialize_components(app)
        logger.info("AirSense API startup completed")
    except Exception as e:
        logger.error("Failed to initialize AirSense API", error=str(e))
        raise

    try:
        yield
    finally:
        logger.info("AirSense API shutting down")


async def initialize_components(app: FastAPI):
    """Initialize application components."""
    global latest_data
    
    try:
        # Load latest processed data if available
        processed_dir = settings.processed_data_dir
        if os.path.exists(processed_dir):
            import pandas as pd
            
            # Find latest parquet file
            parquet_files = [f for f in os.listdir(processed_dir) if f.endswith('.parquet')]
            if parquet_files:
                latest_file = sorted(parquet_files)[-1]
                latest_data = pd.read_parquet(os.path.join(processed_dir, latest_file))
                logger.info("Loaded latest data", file=latest_file, records=len(latest_data))
        
        # Initialize model registry / forecaster
        try:
            from ..models import TimeSeriesForecaster
            app.state.forecaster = TimeSeriesForecaster()
            logger.info("TimeSeriesForecaster initialized")
        except Exception as e:
            app.state.forecaster = None
            logger.warning("TimeSeriesForecaster unavailable", error=str(e))

        # Initialize data processor (requires Java/Spark)
        try:
            from ..data import SparkDataProcessor
            app.state.data_processor = SparkDataProcessor()
            logger.info("SparkDataProcessor initialized")
        except Exception as e:
            app.state.data_processor = None
            logger.warning(
                "SparkDataProcessor unavailable (Java/Spark not found); "
                "data-processing endpoints will return 503",
                error=str(e),
            )

        logger.info("Components initialized successfully")
        
    except Exception as e:
        logger.error("Component initialization failed", error=str(e))
        raise


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="AirSense API",
        description="Enterprise Air Quality Analysis & Forecasting API",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=process_time
            )
            raise
    
    # Exception handlers
    @app.exception_handler(AirSenseError)
    async def airsense_exception_handler(request: Request, exc: AirSenseError):
        logger.error("AirSense error", error=str(exc), type=type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={
                "error": type(exc).__name__,
                "message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning("HTTP error", status_code=exc.status_code, detail=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPException",
                "message": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", error=str(exc), type=type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Include routes (no prefix so dashboard /data /stats /aqi calls resolve directly)
    app.include_router(router)

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Comprehensive health check."""
        try:
            uptime = time.time() - startup_time if startup_time else 0
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            dp = getattr(app.state, "data_processor", None)
            fc = getattr(app.state, "forecaster", None)
            components = {
                "data_processor": dp is not None,
                "forecaster": fc is not None,
                "data_available": latest_data is not None,
            }

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": settings.app_version,
                "uptime_seconds": uptime,
                "memory_usage_mb": memory_usage,
                "components": components,
                "settings": {
                    "debug": settings.debug,
                    "api_host": settings.api_host,
                    "api_port": settings.api_port,
                },
            }

        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "AirSense API",
            "version": settings.app_version,
            "description": "Enterprise Air Quality Analysis & Forecasting API",
            "docs_url": "/docs",
            "health_url": "/health",
            "timestamp": datetime.now().isoformat(),
        }

    return app


# Application instance for `uvicorn src.api.main:app`
app = create_app()
