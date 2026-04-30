"""Model evaluation utilities for AirSense.

Provides comprehensive model evaluation, comparison, and performance tracking
for time series forecasting models.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    mean_absolute_percentage_error
)

from ..core.config import get_settings
from ..core.logging import get_logger
from ..core.exceptions import ModelError


class ModelEvaluator:
    """Comprehensive model evaluation and comparison."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        self.evaluation_history = []
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_name: str,
        pollutant: str,
        additional_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Evaluate model predictions with comprehensive metrics.
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            model_name: Name of the model
            pollutant: Target pollutant
            additional_metrics: Optional additional metrics to include
            
        Returns:
            Dictionary containing all evaluation metrics
        """
        try:
            # Ensure arrays are 1D
            y_true = np.asarray(y_true).flatten()
            y_pred = np.asarray(y_pred).flatten()
            
            # Check for valid data
            if len(y_true) != len(y_pred):
                raise ModelError(f"Length mismatch: y_true={len(y_true)}, y_pred={len(y_pred)}")
            
            if len(y_true) == 0:
                raise ModelError("Empty arrays provided for evaluation")
            
            # Calculate core metrics
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            
            # MAPE (handle division by zero)
            mask = y_true != 0
            if mask.sum() > 0:
                mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            else:
                mape = np.inf
            
            # Additional metrics
            max_error = np.max(np.abs(y_true - y_pred))
            median_ae = np.median(np.abs(y_true - y_pred))
            
            # Directional accuracy (for time series)
            if len(y_true) > 1:
                true_direction = np.sign(np.diff(y_true))
                pred_direction = np.sign(np.diff(y_pred))
                directional_accuracy = np.mean(true_direction == pred_direction) * 100
            else:
                directional_accuracy = None
            
            # Normalized metrics
            y_range = np.max(y_true) - np.min(y_true)
            if y_range > 0:
                normalized_rmse = rmse / y_range
                normalized_mae = mae / y_range
            else:
                normalized_rmse = None
                normalized_mae = None
            
            # Compile results
            results = {
                "model_name": model_name,
                "pollutant": pollutant,
                "timestamp": datetime.now().isoformat(),
                "n_samples": len(y_true),
                "metrics": {
                    "mae": float(mae),
                    "mse": float(mse),
                    "rmse": float(rmse),
                    "r2": float(r2),
                    "mape": float(mape) if not np.isinf(mape) else None,
                    "max_error": float(max_error),
                    "median_absolute_error": float(median_ae),
                    "directional_accuracy": float(directional_accuracy) if directional_accuracy is not None else None,
                    "normalized_rmse": float(normalized_rmse) if normalized_rmse is not None else None,
                    "normalized_mae": float(normalized_mae) if normalized_mae is not None else None
                },
                "statistics": {
                    "y_true_mean": float(np.mean(y_true)),
                    "y_true_std": float(np.std(y_true)),
                    "y_pred_mean": float(np.mean(y_pred)),
                    "y_pred_std": float(np.std(y_pred)),
                    "residual_mean": float(np.mean(y_true - y_pred)),
                    "residual_std": float(np.std(y_true - y_pred))
                }
            }
            
            # Add additional metrics if provided
            if additional_metrics:
                results["additional_metrics"] = additional_metrics
            
            # Store in history
            self.evaluation_history.append(results)
            
            self.logger.info(
                "Model evaluation completed",
                model=model_name,
                pollutant=pollutant,
                mae=mae,
                rmse=rmse,
                r2=r2
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Model evaluation failed: {e}")
            raise ModelError(f"Model evaluation failed: {e}")
    
    def compare_models(
        self,
        evaluations: List[Dict[str, Any]],
        metric: str = "rmse"
    ) -> pd.DataFrame:
        """Compare multiple model evaluations.
        
        Args:
            evaluations: List of evaluation results
            metric: Primary metric for ranking (default: rmse)
            
        Returns:
            DataFrame with model comparison
        """
        try:
            if not evaluations:
                raise ModelError("No evaluations provided for comparison")
            
            # Extract comparison data
            comparison_data = []
            for eval_result in evaluations:
                row = {
                    "model_name": eval_result["model_name"],
                    "pollutant": eval_result["pollutant"],
                    "n_samples": eval_result["n_samples"],
                    **eval_result["metrics"]
                }
                comparison_data.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(comparison_data)
            
            # Sort by primary metric (lower is better for most metrics)
            if metric in df.columns:
                ascending = metric != "r2"  # R2 is better when higher
                df = df.sort_values(by=metric, ascending=ascending)
            
            self.logger.info(
                "Model comparison completed",
                n_models=len(evaluations),
                metric=metric
            )
            
            return df
            
        except Exception as e:
            self.logger.error(f"Model comparison failed: {e}")
            raise ModelError(f"Model comparison failed: {e}")
    
    def cross_validate(
        self,
        model,
        data: pd.Series,
        n_splits: int = 5,
        test_size: int = 24
    ) -> Dict[str, Any]:
        """Perform time series cross-validation.
        
        Args:
            model: Model instance with train() and forecast() methods
            data: Time series data
            n_splits: Number of CV splits
            test_size: Size of test set for each split
            
        Returns:
            Cross-validation results
        """
        try:
            self.logger.info(
                "Starting cross-validation",
                n_splits=n_splits,
                test_size=test_size
            )
            
            cv_results = {
                "mae": [],
                "rmse": [],
                "r2": [],
                "mape": []
            }
            
            # Calculate split points
            total_size = len(data)
            min_train_size = total_size - (n_splits * test_size)
            
            if min_train_size < 100:
                raise ModelError(f"Insufficient data for {n_splits} splits with test_size={test_size}")
            
            # Perform time series CV
            for i in range(n_splits):
                # Split data
                train_end = total_size - ((n_splits - i) * test_size)
                test_end = train_end + test_size
                
                train_data = data[:train_end]
                test_data = data[train_end:test_end]
                
                # Train model
                model.train(train_data)
                
                # Generate forecasts
                forecasts = model.forecast(len(test_data))
                
                # Evaluate
                mae = mean_absolute_error(test_data, forecasts)
                rmse = np.sqrt(mean_squared_error(test_data, forecasts))
                r2 = r2_score(test_data, forecasts)
                
                # MAPE
                mask = test_data != 0
                if mask.sum() > 0:
                    mape = np.mean(np.abs((test_data[mask] - forecasts[mask]) / test_data[mask])) * 100
                else:
                    mape = np.inf
                
                cv_results["mae"].append(mae)
                cv_results["rmse"].append(rmse)
                cv_results["r2"].append(r2)
                cv_results["mape"].append(mape if not np.isinf(mape) else None)
            
            # Calculate summary statistics
            summary = {
                "n_splits": n_splits,
                "test_size": test_size,
                "mae_mean": float(np.mean(cv_results["mae"])),
                "mae_std": float(np.std(cv_results["mae"])),
                "rmse_mean": float(np.mean(cv_results["rmse"])),
                "rmse_std": float(np.std(cv_results["rmse"])),
                "r2_mean": float(np.mean(cv_results["r2"])),
                "r2_std": float(np.std(cv_results["r2"])),
                "mape_mean": float(np.nanmean([m for m in cv_results["mape"] if m is not None])),
                "mape_std": float(np.nanstd([m for m in cv_results["mape"] if m is not None])),
                "cv_results": cv_results
            }
            
            self.logger.info(
                "Cross-validation completed",
                mae_mean=summary["mae_mean"],
                rmse_mean=summary["rmse_mean"],
                r2_mean=summary["r2_mean"]
            )
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Cross-validation failed: {e}")
            raise ModelError(f"Cross-validation failed: {e}")
    
    def residual_analysis(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze prediction residuals.
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            Residual analysis results
        """
        try:
            residuals = y_true - y_pred
            
            # Basic statistics
            analysis = {
                "mean": float(np.mean(residuals)),
                "std": float(np.std(residuals)),
                "min": float(np.min(residuals)),
                "max": float(np.max(residuals)),
                "median": float(np.median(residuals)),
                "q25": float(np.percentile(residuals, 25)),
                "q75": float(np.percentile(residuals, 75)),
                "skewness": float(pd.Series(residuals).skew()),
                "kurtosis": float(pd.Series(residuals).kurtosis())
            }
            
            # Check for patterns
            analysis["is_centered"] = abs(analysis["mean"]) < 0.1 * analysis["std"]
            analysis["is_symmetric"] = abs(analysis["skewness"]) < 0.5
            
            # Autocorrelation of residuals (lag 1)
            if len(residuals) > 1:
                autocorr = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
                analysis["autocorrelation_lag1"] = float(autocorr)
                analysis["has_autocorrelation"] = abs(autocorr) > 0.3
            
            self.logger.info("Residual analysis completed")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Residual analysis failed: {e}")
            raise ModelError(f"Residual analysis failed: {e}")
    
    def save_evaluation_history(self, path: str) -> None:
        """Save evaluation history to file.
        
        Args:
            path: Path to save the history
        """
        try:
            output_path = Path(path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(self.evaluation_history, f, indent=2)
            
            self.logger.info(
                "Evaluation history saved",
                path=str(output_path),
                n_evaluations=len(self.evaluation_history)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to save evaluation history: {e}")
            raise ModelError(f"Failed to save evaluation history: {e}")
    
    def load_evaluation_history(self, path: str) -> None:
        """Load evaluation history from file.
        
        Args:
            path: Path to load the history from
        """
        try:
            with open(path, 'r') as f:
                self.evaluation_history = json.load(f)
            
            self.logger.info(
                "Evaluation history loaded",
                path=path,
                n_evaluations=len(self.evaluation_history)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load evaluation history: {e}")
            raise ModelError(f"Failed to load evaluation history: {e}")
    
    def get_best_model(
        self,
        pollutant: Optional[str] = None,
        metric: str = "rmse"
    ) -> Optional[Dict[str, Any]]:
        """Get the best performing model from evaluation history.
        
        Args:
            pollutant: Filter by pollutant (optional)
            metric: Metric to use for ranking
            
        Returns:
            Best model evaluation result or None
        """
        try:
            if not self.evaluation_history:
                return None
            
            # Filter by pollutant if specified
            evaluations = self.evaluation_history
            if pollutant:
                evaluations = [e for e in evaluations if e["pollutant"] == pollutant]
            
            if not evaluations:
                return None
            
            # Sort by metric
            ascending = metric != "r2"  # R2 is better when higher
            sorted_evals = sorted(
                evaluations,
                key=lambda x: x["metrics"].get(metric, float('inf')),
                reverse=not ascending
            )
            
            return sorted_evals[0]
            
        except Exception as e:
            self.logger.error(f"Failed to get best model: {e}")
            return None
