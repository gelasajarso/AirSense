"""Pandas-based ETL pipeline when Spark/Java is unavailable."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


def generate_synthetic_data(n_hours: int = 720) -> pd.DataFrame:
    """Generate realistic synthetic air quality data (n_hours rows)."""
    rng = np.random.default_rng(42)
    base = datetime(2024, 11, 1, 0, 0, 0)
    dates = [base + timedelta(hours=i) for i in range(n_hours)]

    hours = np.array([d.hour for d in dates])

    rush = (
        np.sin((hours - 8) * np.pi / 6) ** 2 + np.sin((hours - 18) * np.pi / 6) ** 2
    )

    pm25_base = 60 + 25 * rush + rng.normal(0, 5, n_hours)
    pm10_base = 100 + 40 * rush + rng.normal(0, 8, n_hours)
    no2_base = 45 + 20 * rush + rng.normal(0, 4, n_hours)
    so2_base = 20 + 10 * rush + rng.normal(0, 2, n_hours)
    co_base = 1.5 + 0.8 * rush + rng.normal(0, 0.15, n_hours)
    o3_base = 60 - 15 * rush + rng.normal(0, 5, n_hours)
    temp_base = 15 + 8 * np.sin((hours - 6) * np.pi / 12) + rng.normal(0, 1.5, n_hours)
    hum_base = 65 - 10 * np.sin((hours - 6) * np.pi / 12) + rng.normal(0, 3, n_hours)
    pres_base = 1015 + 3 * np.sin(hours * np.pi / 12) + rng.normal(0, 0.5, n_hours)
    ws_base = 2.5 + 1.5 * np.sin((hours - 12) * np.pi / 12) + np.abs(rng.normal(0, 0.5, n_hours))
    wd_base = (180 + 10 * hours + rng.normal(0, 15, n_hours)) % 360

    return pd.DataFrame(
        {
            "datetime": dates,
            "PM2.5": np.clip(pm25_base, 0, None).round(1),
            "PM10": np.clip(pm10_base, 0, None).round(1),
            "NO2": np.clip(no2_base, 0, None).round(1),
            "SO2": np.clip(so2_base, 0, None).round(1),
            "CO": np.clip(co_base, 0, None).round(2),
            "O3": np.clip(o3_base, 0, None).round(1),
            "temperature": temp_base.round(1),
            "humidity": np.clip(hum_base, 0, 100).round(1),
            "pressure": pres_base.round(1),
            "wind_speed": ws_base.round(1),
            "wind_direction": wd_base.round(0),
        }
    )


def run_pandas_pipeline(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Load CSV from ``input_path`` if present; otherwise build synthetic data.
    Writes parquet to ``output_path``. Mirrors ``process_data_simple.py`` behavior.
    """
    settings = get_settings()
    settings.setup_directories()

    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Starting pandas pipeline", input=str(input_file), output=str(output_file))

    if input_file.exists():
        df = pd.read_csv(input_file)
        logger.info("Loaded CSV", rows=len(df), columns=len(df.columns))
        if len(df) < 200:
            logger.warning(
                "CSV too small for robust analysis; replacing with synthetic 30-day hourly data",
                rows=len(df),
            )
            df = generate_synthetic_data(720)
    else:
        logger.warning("Input file not found; generating synthetic dataset", path=str(input_file))
        df = generate_synthetic_data(720)

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
    elif "date" in df.columns:
        df["datetime"] = pd.to_datetime(df["date"])
    else:
        logger.warning("No datetime column; synthesizing hourly index")
        df["datetime"] = pd.date_range("2024-11-01", periods=len(df), freq="h")

    df = df.ffill().bfill()

    df["hour"] = df["datetime"].dt.hour
    df["day_of_week"] = df["datetime"].dt.dayofweek
    df["month"] = df["datetime"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    if all(c in df.columns for c in ["PM2.5", "PM10", "NO2", "SO2"]):
        df["AQI"] = (
            df["PM2.5"] * 0.4 + df["PM10"] * 0.3 + df["NO2"] * 0.2 + df["SO2"] * 0.1
        ).round(2)

    pollutants = settings.pollutant_columns
    for pollutant in pollutants:
        if pollutant in df.columns:
            df[f"{pollutant}_lag1"] = df[pollutant].shift(1)

    core_cols = [p for p in pollutants if p in df.columns]
    df = df.dropna(subset=core_cols)
    df = df.ffill().bfill()

    df.to_parquet(output_file, compression="snappy", index=False)

    summary = {
        "basic_stats": {
            "record_count": len(df),
            "column_count": len(df.columns),
            "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024),
        },
        "date_range": {
            "start": df["datetime"].min().isoformat(),
            "end": df["datetime"].max().isoformat(),
        },
    }

    result = {
        "status": "success",
        "output_path": str(output_file),
        "record_count": len(df),
        "feature_count": len(df.columns),
        "summary": summary,
    }
    logger.info("Pandas pipeline completed", **{k: v for k, v in result.items() if k != "summary"})
    return result
