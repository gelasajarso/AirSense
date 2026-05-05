"""Configuration management for AirSense."""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support.

    Env vars follow pydantic-settings defaults: snake_case fields map to
    SCREAMING_SNAKE_CASE (e.g. ``api_port`` ← ``API_PORT``).
    """

    # Application
    app_name: str = Field(default="AirSense")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    # Data paths
    data_dir: str = Field(default="data")
    raw_data_dir: str = Field(default="data/raw")
    processed_data_dir: str = Field(default="data/processed")
    models_dir: str = Field(default="models")
    logs_dir: str = Field(default="logs")

    # Spark configuration
    spark_app_name: str = Field(default="AirSense")
    spark_master: Optional[str] = Field(default=None)
    spark_executor_memory: str = Field(default="4g")
    spark_driver_memory: str = Field(default="2g")
    spark_executor_cores: int = Field(default=2)

    # API configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=1)
    api_reload: bool = Field(default=False)

    # Database (future)
    database_url: Optional[str] = Field(default=None)

    # Redis
    redis_url: Optional[str] = Field(default=None)

    # ML configuration
    default_forecast_steps: int = Field(default=24)
    model_retrain_interval: int = Field(default=24)  # hours

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Monitoring
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)

    # Security
    secret_key: str = Field(default="your-secret-key-here")
    access_token_expire_minutes: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def setup_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.models_dir,
            self.logs_dir,
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @property
    def spark_config(self) -> dict:
        """Get Spark configuration as dictionary."""
        config = {
            "spark.app.name": self.spark_app_name,
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.advisoryPartitionSizeInBytes": "128MB",
            "spark.sql.execution.arrow.pyspark.enabled": "true",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        }

        if self.spark_master:
            config["spark.master"] = self.spark_master

        config.update(
            {
                "spark.executor.memory": self.spark_executor_memory,
                "spark.driver.memory": self.spark_driver_memory,
                "spark.executor.cores": str(self.spark_executor_cores),
            }
        )

        return config

    @property
    def pollutant_columns(self) -> List[str]:
        """Standard pollutant columns."""
        return ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

    @property
    def weather_columns(self) -> List[str]:
        """Weather-related columns."""
        return ["temperature", "humidity", "pressure", "wind_speed", "wind_direction"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.setup_directories()
    return settings
