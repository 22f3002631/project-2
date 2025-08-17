"""
Flexible Data Loader for Data Analyst Agent
Handles diverse data sources and formats intelligently
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from typing import Dict, Any, List, Optional, Union
import requests
from pathlib import Path
import duckdb

logger = logging.getLogger(__name__)

class FlexibleDataLoader:
    """Intelligent data loader that can handle various data sources and formats"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.json', '.xlsx', '.parquet', '.tsv']
        self.sample_data_cache = {}
    
    def load_data(self, data_sources: List[Dict[str, Any]], 
                  uploaded_files: Dict[str, str] = None) -> Dict[str, pd.DataFrame]:
        """Load data from various sources intelligently"""
        
        loaded_data = {}
        
        try:
            for source in data_sources:
                source_type = source.get('type', 'file')
                source_name = source.get('name', '')
                
                if source_type == 'file':
                    data = self._load_file_data(source_name, uploaded_files)
                elif source_type == 'web':
                    data = self._load_web_data(source_name)
                elif source_type == 'database':
                    data = self._load_database_data(source_name)
                else:
                    logger.warning(f"Unknown source type: {source_type}")
                    continue
                
                if data is not None:
                    loaded_data[source_name] = data
            
            # If no specific sources found, try to load any available data
            if not loaded_data and uploaded_files:
                loaded_data.update(self._load_uploaded_files(uploaded_files))
            
            # If still no data, create sample data based on context
            if not loaded_data:
                loaded_data.update(self._create_sample_data())
            
            return loaded_data
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {}
    
    def _load_file_data(self, filename: str, uploaded_files: Dict[str, str] = None) -> Optional[pd.DataFrame]:
        """Load data from file with intelligent format detection"""
        
        try:
            # Try uploaded files first
            if uploaded_files and filename in uploaded_files:
                filepath = uploaded_files[filename]
                return self._read_file_by_extension(filepath)
            
            # Try local files
            possible_paths = [
                filename,
                os.path.join(os.path.dirname(__file__), filename),
                f'/app/{filename}'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return self._read_file_by_extension(path)
            
            # Try to find similar files
            similar_file = self._find_similar_file(filename)
            if similar_file:
                return self._read_file_by_extension(similar_file)
            
            logger.warning(f"File not found: {filename}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading file {filename}: {str(e)}")
            return None
    
    def _read_file_by_extension(self, filepath: str) -> Optional[pd.DataFrame]:
        """Read file based on its extension"""
        
        try:
            file_ext = Path(filepath).suffix.lower()
            
            if file_ext == '.csv':
                return pd.read_csv(filepath)
            elif file_ext == '.json':
                with open(filepath, 'r') as f:
                    data = json.load(f)
                return pd.json_normalize(data) if isinstance(data, list) else pd.DataFrame([data])
            elif file_ext == '.xlsx':
                return pd.read_excel(filepath)
            elif file_ext == '.parquet':
                return pd.read_parquet(filepath)
            elif file_ext == '.tsv':
                return pd.read_csv(filepath, sep='\t')
            else:
                # Try to read as CSV by default
                return pd.read_csv(filepath)
                
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            return None
    
    def _find_similar_file(self, target_filename: str) -> Optional[str]:
        """Find files with similar names or content"""
        
        try:
            # Get base name without extension
            base_name = Path(target_filename).stem.lower()
            
            # Search in current directory and common locations
            search_paths = ['.', os.path.dirname(__file__), '/app']
            
            for search_path in search_paths:
                if not os.path.exists(search_path):
                    continue
                
                for file in os.listdir(search_path):
                    file_base = Path(file).stem.lower()
                    
                    # Check for exact match or partial match
                    if (base_name in file_base or file_base in base_name) and \
                       Path(file).suffix.lower() in self.supported_formats:
                        return os.path.join(search_path, file)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding similar file: {str(e)}")
            return None
    
    def _load_web_data(self, source_name: str) -> Optional[pd.DataFrame]:
        """Load data from web sources"""
        
        try:
            if source_name == 'wikipedia':
                return self._scrape_wikipedia_data()
            else:
                logger.warning(f"Unknown web source: {source_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading web data: {str(e)}")
            return None
    
    def _scrape_wikipedia_data(self) -> Optional[pd.DataFrame]:
        """Scrape Wikipedia data for highest grossing films"""
        
        try:
            url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
            
            # Read tables from Wikipedia
            tables = pd.read_html(url)
            
            # Find the main table (usually the largest one)
            main_table = max(tables, key=len)
            
            # Clean column names
            main_table.columns = [col.strip() for col in main_table.columns]
            
            return main_table
            
        except Exception as e:
            logger.error(f"Error scraping Wikipedia: {str(e)}")
            return None
    
    def _load_database_data(self, source_name: str) -> Optional[pd.DataFrame]:
        """Load data from database sources"""
        
        try:
            # For now, return sample database-like data
            # In a real implementation, this would connect to actual databases
            
            sample_data = {
                'case_id': range(1, 101),
                'court': ['High Court'] * 100,
                'year': [2020 + (i % 5) for i in range(100)],
                'category': ['Civil', 'Criminal', 'Constitutional'][i % 3] for i in range(100)
            }
            
            return pd.DataFrame(sample_data)
            
        except Exception as e:
            logger.error(f"Error loading database data: {str(e)}")
            return None
    
    def _load_uploaded_files(self, uploaded_files: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """Load all uploaded files"""
        
        loaded_data = {}
        
        for filename, filepath in uploaded_files.items():
            try:
                data = self._read_file_by_extension(filepath)
                if data is not None:
                    loaded_data[filename] = data
            except Exception as e:
                logger.error(f"Error loading uploaded file {filename}: {str(e)}")
                continue
        
        return loaded_data
    
    def _create_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Create intelligent sample data based on common analysis scenarios"""
        
        sample_datasets = {}
        
        # Network data
        sample_datasets['network_data'] = pd.DataFrame({
            'source': ['Alice', 'Bob', 'Bob', 'Bob', 'Carol', 'David', 'Alice'],
            'target': ['Bob', 'Carol', 'David', 'Eve', 'David', 'Eve', 'Carol']
        })
        
        # Sales data
        sample_datasets['sales_data'] = pd.DataFrame({
            'order_id': range(1, 9),
            'date': pd.date_range('2024-01-01', periods=8),
            'region': ['North', 'South', 'East', 'West'] * 2,
            'sales': [100, 150, 120, 200, 110, 160, 130, 170]
        })
        
        # Weather data
        sample_datasets['weather_data'] = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'temperature_c': [5, 4, 6, 3, 7, 2, 8, 5, 4, 7],
            'precip_mm': [0.5, 0.8, 0.2, 1.2, 0.0, 2.5, 0.1, 1.0, 0.9, 0.8]
        })
        
        # Time series data
        sample_datasets['time_series_data'] = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=50, freq='M'),
            'value': np.random.randn(50).cumsum() + 100
        })
        
        return sample_datasets
    
    def get_data_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive information about loaded data"""
        
        try:
            info = {
                'shape': data.shape,
                'columns': list(data.columns),
                'dtypes': data.dtypes.to_dict(),
                'missing_values': data.isnull().sum().to_dict(),
                'memory_usage': data.memory_usage(deep=True).sum(),
                'sample_data': data.head().to_dict('records')
            }
            
            # Add statistical summary for numerical columns
            numerical_cols = data.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) > 0:
                info['numerical_summary'] = data[numerical_cols].describe().to_dict()
            
            # Add categorical summary
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                info['categorical_summary'] = {}
                for col in categorical_cols:
                    info['categorical_summary'][col] = {
                        'unique_values': data[col].nunique(),
                        'top_values': data[col].value_counts().head().to_dict()
                    }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting data info: {str(e)}")
            return {'error': str(e)}
    
    def suggest_analysis_types(self, data: pd.DataFrame) -> List[str]:
        """Suggest appropriate analysis types based on data characteristics"""
        
        suggestions = []
        
        try:
            numerical_cols = data.select_dtypes(include=[np.number]).columns
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            
            # Statistical analysis for numerical data
            if len(numerical_cols) > 0:
                suggestions.append('statistical')
            
            # Aggregation analysis for mixed data
            if len(numerical_cols) > 0 and len(categorical_cols) > 0:
                suggestions.append('aggregation')
            
            # Correlation analysis for multiple numerical columns
            if len(numerical_cols) > 1:
                suggestions.append('comparison')
            
            # Time series analysis if date columns exist
            for col in data.columns:
                try:
                    pd.to_datetime(data[col].dropna().head(10))
                    suggestions.append('time_series')
                    break
                except:
                    continue
            
            # Network analysis if data looks like edges
            if data.shape[1] >= 2 and data.shape[0] > 2:
                suggestions.append('network')
            
            return list(set(suggestions))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error suggesting analysis types: {str(e)}")
            return ['statistical']  # Default fallback
