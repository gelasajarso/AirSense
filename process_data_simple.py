"""Simple data processor without Spark — for systems without Java.

Generates processed parquet from the raw CSV, or creates a realistic
30-day synthetic dataset when the CSV is missing or too small (< 200 rows).
"""

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def process_data_simple():
    """Process data using pandas instead of Spark."""

    print("=" * 60)
    print("AirSense Simple Data Processor ")
    print("=" * 60)
    print()

    from src.data.pandas_processor import run_pandas_pipeline

    input_file = ROOT / "data" / "raw" / "beijing_demo.csv"
    output_dir = ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"processed_{timestamp}.parquet"

    print(f"Input file : {input_file}")
    print(f"Output file: {output_file}")
    print()

    result = run_pandas_pipeline(str(input_file), str(output_file))

    print()
    print("=" * 60)
    print("Data processing completed successfully.")
    print("=" * 60)
    print()
    print("You can now run:")
    print("  API      : python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
    print("  Dashboard: python -m streamlit run frontend/dashboard.py --server.port 8501")
    print()

    return result.get("status") == "success"


if __name__ == "__main__":
    success = process_data_simple()
    sys.exit(0 if success else 1)
