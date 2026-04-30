"""Simple data processor without Spark - for systems without Java."""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

def process_data_simple():
    """Process data using pandas instead of Spark."""
    
    print("=" * 60)
    print("AirSense Simple Data Processor (No Spark Required)")
    print("=" * 60)
    print()
    
    # Input and output paths
    input_file = Path("data/raw/beijing_demo.csv")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"processed_{timestamp}.parquet"
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print()
    
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        return False
    
    try:
        # Read data
        print("Reading data...")
        df = pd.read_csv(input_file)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        print()
        
        # Show columns
        print("Columns:", list(df.columns))
        print()
        
        # Convert datetime
        print("Processing datetime...")
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        elif 'date' in df.columns:
            df['datetime'] = pd.to_datetime(df['date'])
        else:
            print("  WARNING: No datetime column found")
        print()
        
        # Handle missing values
        print("Handling missing values...")
        missing_before = df.isnull().sum().sum()
        df = df.fillna(method='ffill').fillna(method='bfill')
        missing_after = df.isnull().sum().sum()
        print(f"  Missing values: {missing_before} → {missing_after}")
        print()
        
        # Basic feature engineering
        print("Creating features...")
        if 'datetime' in df.columns:
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek
            df['month'] = df['datetime'].dt.month
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            print("  Added time-based features")
        
        # Create lag features for pollutants
        pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
        for pollutant in pollutants:
            if pollutant in df.columns:
                df[f'{pollutant}_lag1'] = df[pollutant].shift(1)
                df[f'{pollutant}_lag24'] = df[pollutant].shift(24)
        print("  Added lag features")
        print()
        
        # Remove rows with NaN from lag features
        df = df.dropna()
        
        # Save to parquet
        print("Saving processed data...")
        df.to_parquet(output_file, compression='snappy', index=False)
        print(f"  Saved {len(df)} rows to {output_file}")
        print()
        
        # Summary statistics
        print("Summary Statistics:")
        print("-" * 60)
        for col in pollutants:
            if col in df.columns:
                print(f"  {col:10s}: mean={df[col].mean():.2f}, "
                      f"min={df[col].min():.2f}, max={df[col].max():.2f}")
        print()
        
        print("=" * 60)
        print("✓ Data processing completed successfully!")
        print("=" * 60)
        print()
        print("You can now run:")
        print("  - API: .venv\\Scripts\\python.exe src\\main.py api")
        print("  - Dashboard: .venv\\Scripts\\python.exe src\\main.py dashboard")
        print()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Data processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = process_data_simple()
    sys.exit(0 if success else 1)
