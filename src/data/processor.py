"""Data processor facade: full Spark implementation when PySpark is available."""

from __future__ import annotations

from ..core.exceptions import SparkError

try:
    from .spark_processor import SparkDataProcessor

    SPARK_AVAILABLE = True
except ImportError:

    SPARK_AVAILABLE = False

    class SparkDataProcessor:
        """Placeholder when PySpark is not installed."""

        def __init__(self, spark_session=None):
            raise SparkError(
                "PySpark is not installed or failed to import. "
                "Install Java and run `pip install pyspark`, or use the pandas pipeline: "
                "`python process_data_simple.py` or `python -m src.main pipeline` "
                "(which falls back automatically)."
            )

        def stop(self) -> None:
            pass
