"""Main entry point for AirSense system."""

import argparse
import shutil
import sys
from pathlib import Path

# Add project root to path so `from src.x import ...` works
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.main import create_app
from src.core.config import get_settings
from src.core.logging import get_logger
from src.data.processor import SPARK_AVAILABLE, SparkDataProcessor


def _spark_runtime_ready() -> bool:
    """PySpark needs a Java executable on PATH; otherwise skip Spark and use pandas."""
    if not SPARK_AVAILABLE:
        return False
    return shutil.which("java") is not None


def run_pipeline():
    """Run data processing pipeline (Spark when available, else pandas)."""
    from datetime import datetime

    logger = get_logger(__name__)
    settings = get_settings()

    logger.info("Starting AirSense data pipeline")

    input_file = Path(settings.raw_data_dir) / "beijing_demo.csv"
    if not input_file.exists():
        alt_input_file = Path(settings.data_dir) / "beijing_demo.csv"
        if alt_input_file.exists():
            input_file = alt_input_file

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(settings.processed_data_dir) / f"processed_{timestamp}.parquet"

    if input_file.exists() and SPARK_AVAILABLE and shutil.which("java") is None:
        logger.info("Skipping Spark: Java not found on PATH; using pandas pipeline.")

    if _spark_runtime_ready() and input_file.exists():
        processor = None
        try:
            processor = SparkDataProcessor()
            result = processor.process_pipeline(str(input_file), str(output_path))
            ok = result.get("status") == "success"
            if ok:
                logger.info("Spark pipeline completed successfully", **result)
            else:
                logger.error("Spark pipeline failed", **result)
            return ok
        except Exception as e:
            logger.warning("Spark pipeline unavailable or failed; using pandas fallback.", error=str(e))
        finally:
            if processor is not None:
                processor.stop()

    from src.data.pandas_processor import run_pandas_pipeline

    try:
        result = run_pandas_pipeline(str(input_file), str(output_path))
        ok = result.get("status") == "success"
        if ok:
            logger.info("Pandas pipeline completed successfully", **result)
        else:
            logger.error("Pandas pipeline failed", **result)
        return ok
    except Exception as e:
        logger.error(f"Pandas pipeline execution failed: {e}")
        return False


def run_api():
    """Run API server."""
    import uvicorn
    
    logger = get_logger(__name__)
    settings = get_settings()
    
    logger.info("Starting AirSense API server")
    
    try:
        uvicorn.run(
            create_app(),
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.api_reload,
            workers=1 if settings.api_reload else settings.api_workers
        )
    except Exception as e:
        logger.error(f"API server failed: {e}")
        return False


def run_dashboard():
    """Run Streamlit dashboard."""
    import subprocess
    import sys
    
    logger = get_logger(__name__)
    
    logger.info("Starting AirSense dashboard")
    
    try:
        dashboard_path = Path(__file__).parent.parent / "frontend" / "dashboard.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path), "--server.port", "8501"
        ])
    except Exception as e:
        logger.error(f"Dashboard failed: {e}")
        return False


def run_all():
    """Run complete system."""
    import threading
    import time
    import webbrowser
    
    logger = get_logger(__name__)
    
    logger.info("Starting complete AirSense system")
    
    # Run pipeline first
    if not run_pipeline():
        logger.warning("Pipeline failed, continuing without data processing")
        # return False  # Commented out to allow running without Java
    
    # Start API in background thread
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Wait for API to start
    time.sleep(5)
    
    # Start dashboard in background thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Wait for dashboard to start
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:8501")
        logger.info("Dashboard opened in browser")
    except Exception as e:
        logger.warning(f"Could not open browser: {e}")
    
    logger.info("AirSense system is running")
    logger.info("Dashboard: http://localhost:8501")
    logger.info("API: http://localhost:8000")
    logger.info("API Docs: http://localhost:8000/docs")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down AirSense system")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AirSense - Enterprise Air Quality Analysis System")
    parser.add_argument(
        "command",
        choices=["pipeline", "api", "dashboard", "all"],
        help="Command to run"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Configuration file path"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Override settings if needed
    if args.debug:
        import os
        os.environ["DEBUG"] = "true"
    
    # Run command
    if args.command == "pipeline":
        success = run_pipeline()
    elif args.command == "api":
        success = run_api()
    elif args.command == "dashboard":
        success = run_dashboard()
    elif args.command == "all":
        success = run_all()
    else:
        print(f"Unknown command: {args.command}")
        success = False
    
    # Exit with appropriate code
    sys.exit(0 if success is not False else 1)


if __name__ == "__main__":
    main()
