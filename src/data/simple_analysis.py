"""Simple analysis methods using pandas (no Spark required)."""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

from ..core.config import get_settings
from ..core.logging import get_logger


class SimpleAnalyzer:
    """Simple analysis methods for time patterns and correlations using pandas."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
    
    def daily_patterns(self, df: pd.DataFrame, pollutant: str) -> Dict[str, Any]:
        """Analyze daily patterns for a pollutant."""
        try:
            if pollutant not in df.columns:
                raise ValueError(f"Pollutant {pollutant} not found in data")
            
            # Ensure datetime column
            if 'datetime' not in df.columns:
                raise ValueError("datetime column not found")
            
            df = df.copy()
            df['hour'] = pd.to_datetime(df['datetime']).dt.hour
            
            # Calculate hourly statistics
            hourly_stats = df.groupby('hour')[pollutant].agg([
                ('mean', 'mean'),
                ('std', 'std'),
                ('min', 'min'),
                ('max', 'max'),
                ('count', 'count')
            ]).reset_index()
            
            result = {
                "hourly_stats": hourly_stats.to_dict('records'),
                "peak_hour": int(hourly_stats.loc[hourly_stats['mean'].idxmax(), 'hour']),
                "lowest_hour": int(hourly_stats.loc[hourly_stats['mean'].idxmin(), 'hour']),
                "overall_mean": float(df[pollutant].mean()),
                "overall_std": float(df[pollutant].std())
            }
            
            self.logger.info("Daily pattern analysis completed", pollutant=pollutant)
            return result
            
        except Exception as e:
            self.logger.error("Daily pattern analysis failed", error=str(e))
            raise
    
    def weekly_patterns(self, df: pd.DataFrame, pollutant: str) -> Dict[str, Any]:
        """Analyze weekly patterns for a pollutant."""
        try:
            if pollutant not in df.columns:
                raise ValueError(f"Pollutant {pollutant} not found in data")
            
            df = df.copy()
            df['day_of_week'] = pd.to_datetime(df['datetime']).dt.dayofweek
            df['day_name'] = pd.to_datetime(df['datetime']).dt.day_name()
            
            # Calculate daily statistics
            daily_stats = df.groupby(['day_of_week', 'day_name'])[pollutant].agg([
                ('mean', 'mean'),
                ('std', 'std'),
                ('min', 'min'),
                ('max', 'max'),
                ('count', 'count')
            ]).reset_index()
            
            result = {
                "daily_stats": daily_stats.to_dict('records'),
                "peak_day": daily_stats.loc[daily_stats['mean'].idxmax(), 'day_name'],
                "lowest_day": daily_stats.loc[daily_stats['mean'].idxmin(), 'day_name']
            }
            
            self.logger.info("Weekly pattern analysis completed", pollutant=pollutant)
            return result
            
        except Exception as e:
            self.logger.error("Weekly pattern analysis failed", error=str(e))
            raise
    
    def monthly_patterns(self, df: pd.DataFrame, pollutant: str) -> Dict[str, Any]:
        """Analyze monthly patterns for a pollutant."""
        try:
            if pollutant not in df.columns:
                raise ValueError(f"Pollutant {pollutant} not found in data")
            
            df = df.copy()
            df['month'] = pd.to_datetime(df['datetime']).dt.month
            df['month_name'] = pd.to_datetime(df['datetime']).dt.month_name()
            
            # Calculate monthly statistics
            monthly_stats = df.groupby(['month', 'month_name'])[pollutant].agg([
                ('mean', 'mean'),
                ('std', 'std'),
                ('min', 'min'),
                ('max', 'max'),
                ('count', 'count')
            ]).reset_index()
            
            result = {
                "monthly_stats": monthly_stats.to_dict('records'),
                "peak_month": monthly_stats.loc[monthly_stats['mean'].idxmax(), 'month_name'],
                "lowest_month": monthly_stats.loc[monthly_stats['mean'].idxmin(), 'month_name']
            }
            
            self.logger.info("Monthly pattern analysis completed", pollutant=pollutant)
            return result
            
        except Exception as e:
            self.logger.error("Monthly pattern analysis failed", error=str(e))
            raise
    
    def yearly_trends(self, df: pd.DataFrame, pollutant: str) -> Dict[str, Any]:
        """Analyze yearly trends for a pollutant."""
        try:
            if pollutant not in df.columns:
                raise ValueError(f"Pollutant {pollutant} not found in data")
            
            df = df.copy()
            df['year'] = pd.to_datetime(df['datetime']).dt.year
            
            # Calculate yearly statistics
            yearly_stats = df.groupby('year')[pollutant].agg([
                ('mean', 'mean'),
                ('std', 'std'),
                ('min', 'min'),
                ('max', 'max'),
                ('count', 'count')
            ]).reset_index()
            
            result = {
                "yearly_stats": yearly_stats.to_dict('records'),
                "trend": "increasing" if yearly_stats['mean'].is_monotonic_increasing else 
                        "decreasing" if yearly_stats['mean'].is_monotonic_decreasing else "variable"
            }
            
            self.logger.info("Yearly trend analysis completed", pollutant=pollutant)
            return result
            
        except Exception as e:
            self.logger.error("Yearly trend analysis failed", error=str(e))
            raise
    
    def comprehensive_time_analysis(self, df: pd.DataFrame, pollutants: List[str]) -> Dict[str, Any]:
        """Perform comprehensive time-based analysis for multiple pollutants."""
        try:
            results = {}
            
            for pollutant in pollutants:
                if pollutant in df.columns:
                    results[pollutant] = {
                        "daily": self.daily_patterns(df, pollutant),
                        "weekly": self.weekly_patterns(df, pollutant),
                        "monthly": self.monthly_patterns(df, pollutant),
                        "yearly": self.yearly_trends(df, pollutant)
                    }
            
            return {
                "individual_analyses": results,
                "pollutants_analyzed": list(results.keys()),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error("Comprehensive time analysis failed", error=str(e))
            raise
    
    def pollutant_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlations between pollutants."""
        try:
            # Get pollutant columns
            pollutant_cols = [col for col in self.settings.pollutant_columns if col in df.columns]
            
            if len(pollutant_cols) < 2:
                raise ValueError("Need at least 2 pollutants for correlation analysis")
            
            # Calculate correlation matrix
            corr_matrix = df[pollutant_cols].corr()
            
            # Find strong correlations (|r| > 0.7)
            strong_correlations = []
            for i in range(len(pollutant_cols)):
                for j in range(i + 1, len(pollutant_cols)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            "pollutant1": pollutant_cols[i],
                            "pollutant2": pollutant_cols[j],
                            "correlation": float(corr_value),
                            "strength": "strong" if abs(corr_value) > 0.8 else "moderate",
                            "direction": "positive" if corr_value > 0 else "negative"
                        })
            
            result = {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_correlations,
                "pollutants_analyzed": pollutant_cols
            }
            
            self.logger.info("Pollutant correlation analysis completed")
            return result
            
        except Exception as e:
            self.logger.error("Pollutant correlation analysis failed", error=str(e))
            raise
    
    def weather_pollutant_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlations between weather and pollutants."""
        try:
            # Get weather and pollutant columns
            weather_cols = [col for col in ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM'] if col in df.columns]
            pollutant_cols = [col for col in self.settings.pollutant_columns if col in df.columns]
            
            if not weather_cols or not pollutant_cols:
                raise ValueError("Need both weather and pollutant data for correlation analysis")
            
            # Calculate correlations
            correlations = []
            for weather in weather_cols:
                for pollutant in pollutant_cols:
                    corr_value = df[[weather, pollutant]].corr().iloc[0, 1]
                    if not np.isnan(corr_value):
                        correlations.append({
                            "weather_variable": weather,
                            "pollutant": pollutant,
                            "correlation": float(corr_value),
                            "strength": "strong" if abs(corr_value) > 0.7 else 
                                       "moderate" if abs(corr_value) > 0.4 else "weak",
                            "direction": "positive" if corr_value > 0 else "negative"
                        })
            
            result = {
                "correlations": correlations,
                "weather_variables": weather_cols,
                "pollutants": pollutant_cols
            }
            
            self.logger.info("Weather-pollutant correlation analysis completed")
            return result
            
        except Exception as e:
            self.logger.error("Weather-pollutant correlation analysis failed", error=str(e))
            raise
    
    def comprehensive_correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive correlation analysis."""
        try:
            result = {
                "pollutant_correlations": self.pollutant_correlations(df),
                "weather_pollutant_correlations": self.weather_pollutant_correlations(df),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("Comprehensive correlation analysis completed")
            return result
            
        except Exception as e:
            self.logger.error("Comprehensive correlation analysis failed", error=str(e))
            raise
