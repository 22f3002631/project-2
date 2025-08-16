import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import logging
from typing import Any, Optional, Tuple, List
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class DataAnalysis:
    """Handles statistical analysis and data processing"""
    
    def __init__(self):
        pass
    
    def count_movies_before_year(self, df: pd.DataFrame, year: int, gross_threshold: float) -> int:
        """Count movies that grossed over threshold before a given year"""
        try:
            if df.empty:
                return 0
            
            # Filter by year and gross
            filtered = df[
                (df['Year'] < year) & 
                (df['Worldwide gross'] >= gross_threshold)
            ]
            
            count = len(filtered)
            logger.info(f"Found {count} movies grossing over ${gross_threshold}bn before {year}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting movies: {str(e)}")
            return 0
    
    def find_earliest_movie_over_amount(self, df: pd.DataFrame, gross_threshold: float) -> str:
        """Find the earliest movie that grossed over the threshold"""
        try:
            if df.empty:
                return "No data available"
            
            # Filter movies over threshold
            filtered = df[df['Worldwide gross'] >= gross_threshold]
            
            if filtered.empty:
                return "No movies found over threshold"
            
            # Find earliest by year
            earliest = filtered.loc[filtered['Year'].idxmin()]
            title = earliest.get('Title', 'Unknown')
            
            logger.info(f"Earliest movie over ${gross_threshold}bn: {title}")
            return title
            
        except Exception as e:
            logger.error(f"Error finding earliest movie: {str(e)}")
            return "Error processing data"
    
    def calculate_correlation(self, df: pd.DataFrame, col1: str, col2: str) -> float:
        """Calculate correlation between two columns"""
        try:
            if df.empty or col1 not in df.columns or col2 not in df.columns:
                return 0.0
            
            # Remove non-numeric values
            clean_df = df[[col1, col2]].dropna()
            clean_df = clean_df[
                pd.to_numeric(clean_df[col1], errors='coerce').notna() &
                pd.to_numeric(clean_df[col2], errors='coerce').notna()
            ]
            
            if len(clean_df) < 2:
                return 0.0
            
            correlation = clean_df[col1].astype(float).corr(clean_df[col2].astype(float))
            
            if pd.isna(correlation):
                return 0.0
            
            logger.info(f"Correlation between {col1} and {col2}: {correlation:.6f}")
            return round(correlation, 6)
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {str(e)}")
            return 0.0
    
    def calculate_regression_slope(self, df: pd.DataFrame, x_col: str, y_col: str) -> float:
        """Calculate regression slope between two variables"""
        try:
            if df.empty or x_col not in df.columns or y_col not in df.columns:
                return 0.0
            
            # Clean data
            clean_df = df[[x_col, y_col]].dropna()
            clean_df[x_col] = pd.to_numeric(clean_df[x_col], errors='coerce')
            clean_df[y_col] = pd.to_numeric(clean_df[y_col], errors='coerce')
            clean_df = clean_df.dropna()
            
            if len(clean_df) < 2:
                return 0.0
            
            X = clean_df[x_col].values.reshape(-1, 1)
            y = clean_df[y_col].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            logger.info(f"Regression slope for {x_col} vs {y_col}: {slope}")
            return slope
            
        except Exception as e:
            logger.error(f"Error calculating regression slope: {str(e)}")
            return 0.0
    
    def calculate_date_difference_days(self, df: pd.DataFrame, date_col1: str, date_col2: str) -> pd.Series:
        """Calculate difference in days between two date columns"""
        try:
            if df.empty or date_col1 not in df.columns or date_col2 not in df.columns:
                return pd.Series()
            
            # Convert to datetime
            date1 = pd.to_datetime(df[date_col1], errors='coerce')
            date2 = pd.to_datetime(df[date_col2], errors='coerce')
            
            # Calculate difference in days
            diff_days = (date2 - date1).dt.days
            
            return diff_days
            
        except Exception as e:
            logger.error(f"Error calculating date difference: {str(e)}")
            return pd.Series()
    
    def group_and_count(self, df: pd.DataFrame, group_col: str, filter_conditions: Optional[dict] = None) -> pd.DataFrame:
        """Group data and count occurrences"""
        try:
            if df.empty or group_col not in df.columns:
                return pd.DataFrame()
            
            # Apply filters if provided
            filtered_df = df.copy()
            if filter_conditions:
                for col, condition in filter_conditions.items():
                    if col in filtered_df.columns:
                        if isinstance(condition, dict):
                            if 'min' in condition:
                                filtered_df = filtered_df[filtered_df[col] >= condition['min']]
                            if 'max' in condition:
                                filtered_df = filtered_df[filtered_df[col] <= condition['max']]
                        else:
                            filtered_df = filtered_df[filtered_df[col] == condition]
            
            # Group and count
            result = filtered_df.groupby(group_col).size().reset_index(name='count')
            result = result.sort_values('count', ascending=False)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in group and count: {str(e)}")
            return pd.DataFrame()
    
    def analyze_dataframe(self, df: pd.DataFrame, question: str) -> Any:
        """Analyze dataframe based on natural language question"""
        try:
            question_lower = question.lower()
            
            # Simple keyword-based analysis
            if 'correlation' in question_lower:
                # Find numeric columns for correlation
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) >= 2:
                    return self.calculate_correlation(df, numeric_cols[0], numeric_cols[1])
            
            elif 'count' in question_lower or 'how many' in question_lower:
                return len(df)
            
            elif 'mean' in question_lower or 'average' in question_lower:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    return df[numeric_cols[0]].mean()
            
            elif 'max' in question_lower or 'maximum' in question_lower:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    return df[numeric_cols[0]].max()
            
            elif 'min' in question_lower or 'minimum' in question_lower:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    return df[numeric_cols[0]].min()
            
            # Default: return basic statistics
            return {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing dataframe: {str(e)}")
            return None
    
    def get_basic_statistics(self, df: pd.DataFrame) -> dict:
        """Get basic statistics for a dataframe"""
        try:
            if df.empty:
                return {}
            
            stats = {
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'numeric_summary': {}
            }
            
            # Add numeric column statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                stats['numeric_summary'][col] = {
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max()
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting basic statistics: {str(e)}")
            return {}
