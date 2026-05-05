"""Tests for data processor module."""

import pytest

pytest.importorskip("pyspark")
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, Mock, patch

from src.core.config import get_settings

from src.data.processor import SparkDataProcessor
from src.core.exceptions import DataProcessingError, SparkError


class TestSparkDataProcessor:
    """Test cases for SparkDataProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create test processor instance."""
        with patch('src.data.spark_processor.SparkSession') as mock_spark:
            mock_session = Mock()
            mock_spark.builder.appName.return_value.config.return_value.getOrCreate.return_value = mock_session
            return SparkDataProcessor(mock_session)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='h')
        data = {
            'datetime': dates.strftime('%Y-%m-%d %H:%M:%S'),
            'PM2.5': np.random.uniform(10, 100, 100),
            'PM10': np.random.uniform(20, 150, 100),
            'NO2': np.random.uniform(5, 50, 100),
            'SO2': np.random.uniform(2, 30, 100),
            'CO': np.random.uniform(100, 1000, 100),
            'O3': np.random.uniform(10, 80, 100),
            'temperature': np.random.uniform(-10, 30, 100),
            'humidity': np.random.uniform(20, 80, 100),
            'pressure': np.random.uniform(980, 1020, 100),
            'wind_speed': np.random.uniform(0, 10, 100),
            'wind_direction': np.random.uniform(0, 360, 100)
        }
        return pd.DataFrame(data)
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor.settings is not None
        assert processor.logger is not None
        assert processor.spark is not None
    
    def test_schema_property(self, processor):
        """Test schema property."""
        schema = processor.schema
        assert schema is not None
        assert 'datetime' in [field.name for field in schema.fields]
        assert 'PM2.5' in [field.name for field in schema.fields]
    
    def test_load_data_success(self, processor, sample_data):
        """Test successful data loading."""
        mock_df = Mock()
        mock_df.count.return_value = len(sample_data)
        mock_df.columns = sample_data.columns.tolist()
        mock_df.toPandas.return_value = sample_data

        read_chain = Mock()
        processor.spark.read = read_chain
        read_chain.option.return_value = read_chain
        read_chain.schema.return_value = read_chain
        read_chain.csv.return_value = mock_df

        result = processor.load_data("test_file.csv")

        assert result is not None
        read_chain.csv.assert_called_once_with("test_file.csv")
    
    @patch("src.data.spark_processor.Window")
    @patch("src.data.spark_processor.lag")
    @patch("src.data.spark_processor._mean")
    @patch("src.data.spark_processor.when")
    @patch("src.data.spark_processor.to_timestamp")
    @patch("src.data.spark_processor.col")
    def test_clean_data(self, mock_col, mock_ts, mock_when, mock_mean, mock_lag, mock_win, processor):
        """Test data cleaning functionality (Spark columns mocked — no active JVM)."""
        stub = MagicMock()
        mock_col.return_value = stub
        mock_ts.return_value = stub
        mock_when.return_value = stub
        mock_mean.return_value = stub
        mock_lag.return_value = stub

        mock_df = Mock()
        mock_df.filter.return_value = mock_df
        mock_df.withColumn.return_value = mock_df
        mock_df.dropDuplicates.return_value = mock_df
        mock_df.count.return_value = 100
        # Skip IQR filter branch (would compare MagicMock columns to floats otherwise)
        mock_df.approxQuantile.return_value = []
        ps = get_settings().pollutant_columns
        mock_df.columns = ["datetime"] + ps + [
            "temperature", "humidity", "pressure", "wind_speed", "wind_direction"
        ]

        result = processor.clean_data(mock_df)
        
        assert result is not None
        # Verify cleaning operations were called
        mock_df.filter.assert_called()
        mock_df.withColumn.assert_called()
        mock_df.dropDuplicates.assert_called()
    
    @patch("src.data.spark_processor.Window")
    @patch("src.data.spark_processor.lag")
    @patch("src.data.spark_processor._mean")
    @patch("src.data.spark_processor.cos")
    @patch("src.data.spark_processor.sin")
    @patch("src.data.spark_processor.year")
    @patch("src.data.spark_processor.month")
    @patch("src.data.spark_processor.dayofweek")
    @patch("src.data.spark_processor.hour")
    @patch("src.data.spark_processor.col")
    def test_feature_engineering(
        self,
        mock_col,
        mock_hour,
        mock_dow,
        mock_month,
        mock_year,
        mock_sin,
        mock_cos,
        mock_mean,
        mock_lag,
        mock_win,
        processor,
    ):
        """Test feature engineering (Spark columns mocked)."""
        expr = MagicMock()
        mock_col.return_value = expr
        for m in (mock_hour, mock_dow, mock_month, mock_year, mock_sin, mock_cos, mock_mean, mock_lag):
            m.return_value = expr

        cols = [
            "datetime",
            *get_settings().pollutant_columns,
            "temperature", "humidity", "pressure", "wind_speed", "wind_direction",
        ]
        mock_df = Mock()
        mock_df.withColumn.return_value = mock_df
        mock_df.columns = cols

        result = processor.feature_engineering(mock_df)
        
        assert result is not None
        # Verify feature engineering operations
        assert mock_df.withColumn.call_count > 0
    
    def test_create_ml_pipeline(self, processor):
        """Test ML pipeline creation."""
        feature_columns = ['hour', 'dayofweek', 'temperature', 'humidity']

        with patch('src.data.spark_processor.Pipeline') as mock_pipeline, patch(
            'src.data.spark_processor.VectorAssembler'
        ), patch('src.data.spark_processor.StandardScaler'):
            pipeline = processor.create_ml_pipeline(feature_columns)

            assert pipeline is not None
            mock_pipeline.assert_called_once()
    
    @patch('src.data.spark_processor.Path')
    def test_process_pipeline_success(self, mock_path, processor, sample_data):
        """Test complete processing pipeline."""
        engineered_cols = [
            'datetime', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3', 'AQI',
            'hour', 'dayofweek', 'month', 'temperature', 'humidity',
            'pressure', 'wind_speed', 'wind_direction', 'PM_ratio', 'NO2_SO2_ratio',
            'temp_humidity_interaction', 'wind_temp_interaction',
            'hour_sin', 'hour_cos', 'dayofweek_sin', 'dayofweek_cos', 'scaled_features',
        ]
        final_df = Mock()
        final_df.count.return_value = 100
        final_df.write.mode.return_value.parquet.return_value = Mock()

        transformed = Mock()
        transformed.columns = engineered_cols
        transformed.select.return_value = final_df

        mock_ml_pipeline = Mock()
        mock_ml_pipeline.fit.return_value.transform.return_value = transformed

        processor.load_data = Mock(return_value=Mock())
        processor.clean_data = Mock(return_value=Mock())
        processor.feature_engineering = Mock(return_value=transformed)
        processor.create_ml_pipeline = Mock(return_value=mock_ml_pipeline)
        processor.generate_summary = Mock(return_value={"test": "summary"})

        result = processor.process_pipeline("input.csv", "output.parquet")
        
        assert result['status'] == 'success'
        assert 'output_path' in result
        assert 'record_count' in result
    
    def test_generate_summary(self, processor):
        """Test summary generation."""
        # Mock DataFrame
        mock_df = Mock()
        mock_df.toPandas.return_value = pd.DataFrame({
            'datetime': pd.date_range('2024-01-01', periods=100, freq='h'),
            'PM2.5': np.random.uniform(10, 100, 100),
            'PM10': np.random.uniform(20, 150, 100)
        })
        
        summary = processor.generate_summary(mock_df)
        
        assert 'basic_stats' in summary
        assert 'date_range' in summary
        assert 'pollutant_stats' in summary
    
    def test_spark_error_handling(self, processor):
        """Test error handling for Spark operations."""
        # Mock Spark session to raise exception
        processor.spark.read.csv.side_effect = Exception("Spark error")
        
        with pytest.raises(DataProcessingError):
            processor.load_data("test_file.csv")
    
    def test_stop(self, processor):
        """Test stopping Spark session."""
        processor.spark.stop = Mock()
        
        processor.stop()
        
        processor.spark.stop.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
