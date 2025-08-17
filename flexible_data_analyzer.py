"""
Flexible Data Analyzer for Data Analyst Agent
Handles diverse data analysis scenarios with intelligent adaptation
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import networkx as nx
import logging
from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class FlexibleDataAnalyzer:
    """Intelligent data analyzer that adapts to different data types and analysis needs"""
    
    def __init__(self):
        self.label_encoders = {}
    
    def analyze_data(self, data: Union[pd.DataFrame, Dict, List], 
                    analysis_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis method that routes to appropriate analysis based on data and requirements"""
        
        try:
            # Convert data to DataFrame if needed
            df = self._ensure_dataframe(data)
            
            # Analyze data structure
            data_profile = self._profile_data(df)
            
            # Determine analysis approach based on spec and data
            analysis_types = analysis_spec.get('analysis_types', [])
            
            results = {
                'data_profile': data_profile,
                'analysis_results': {}
            }
            
            # Perform requested analyses
            for analysis_type in analysis_types:
                if analysis_type == 'statistical':
                    results['analysis_results']['statistical'] = self._statistical_analysis(df)
                elif analysis_type == 'aggregation':
                    results['analysis_results']['aggregation'] = self._aggregation_analysis(df, analysis_spec)
                elif analysis_type == 'time_series':
                    results['analysis_results']['time_series'] = self._time_series_analysis(df)
                elif analysis_type == 'network':
                    results['analysis_results']['network'] = self._network_analysis(df)
                elif analysis_type == 'comparison':
                    results['analysis_results']['comparison'] = self._comparison_analysis(df, analysis_spec)
            
            # If no specific analysis types, perform intelligent auto-analysis
            if not analysis_types:
                results['analysis_results']['auto'] = self._auto_analysis(df, analysis_spec)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in data analysis: {str(e)}")
            return {'error': f"Analysis failed: {str(e)}"}
    
    def _ensure_dataframe(self, data: Union[pd.DataFrame, Dict, List]) -> pd.DataFrame:
        """Convert various data formats to DataFrame"""
        
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                return pd.DataFrame(data)
            else:
                return pd.DataFrame({'values': data})
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _profile_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze the structure and characteristics of the data"""
        
        profile = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'column_types': {}
        }
        
        # Classify column types
        for col in df.columns:
            col_type = self._classify_column_type(df[col])
            profile['column_types'][col] = col_type
        
        return profile
    
    def _classify_column_type(self, series: pd.Series) -> str:
        """Classify the type of a column"""
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            return 'numerical'
        
        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'temporal'
        
        # Try to parse as datetime
        try:
            pd.to_datetime(series.dropna().head(10))
            return 'temporal'
        except:
            pass
        
        # Check if categorical (low cardinality)
        unique_ratio = series.nunique() / len(series)
        if unique_ratio < 0.5 and series.nunique() < 20:
            return 'categorical'
        
        return 'textual'
    
    def _statistical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        
        results = {}
        
        # Analyze numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numerical_cols:
            col_stats = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'quartiles': df[col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
            results[f'{col}_statistics'] = col_stats
        
        # Correlation analysis
        if len(numerical_cols) > 1:
            correlation_matrix = df[numerical_cols].corr()
            results['correlations'] = correlation_matrix.to_dict()
        
        return results
    
    def _aggregation_analysis(self, df: pd.DataFrame, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform aggregation analysis based on requirements"""
        
        results = {}
        
        # Find numerical and categorical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Basic aggregations
        for col in numerical_cols:
            results[f'total_{col}'] = float(df[col].sum())
            results[f'average_{col}'] = float(df[col].mean())
            results[f'max_{col}'] = float(df[col].max())
            results[f'min_{col}'] = float(df[col].min())
        
        # Group by categorical columns
        for cat_col in categorical_cols:
            for num_col in numerical_cols:
                try:
                    grouped = df.groupby(cat_col)[num_col].agg(['sum', 'mean', 'count'])
                    results[f'{num_col}_by_{cat_col}'] = grouped.to_dict()
                    
                    # Find top category
                    top_category = grouped['sum'].idxmax()
                    results[f'top_{cat_col}_by_{num_col}'] = top_category
                except:
                    continue
        
        return results
    
    def _time_series_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform time series analysis"""
        
        results = {}
        
        # Find date columns
        date_cols = []
        for col in df.columns:
            if self._classify_column_type(df[col]) == 'temporal':
                date_cols.append(col)
        
        if not date_cols:
            return {'error': 'No temporal columns found'}
        
        # Use first date column
        date_col = date_cols[0]
        
        try:
            # Convert to datetime
            df[date_col] = pd.to_datetime(df[date_col])
            df_sorted = df.sort_values(date_col)
            
            # Find numerical columns for time series analysis
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            
            for num_col in numerical_cols:
                # Calculate trends
                x = np.arange(len(df_sorted))
                y = df_sorted[num_col].values
                
                # Linear regression for trend
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                results[f'{num_col}_trend'] = {
                    'slope': float(slope),
                    'r_squared': float(r_value**2),
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing'
                }
                
                # Cumulative values
                results[f'{num_col}_cumulative'] = df_sorted[num_col].cumsum().tolist()
        
        except Exception as e:
            results['error'] = f"Time series analysis failed: {str(e)}"
        
        return results
    
    def _network_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform network analysis if data represents a network"""
        
        try:
            # Assume first two columns are source and target
            if df.shape[1] < 2:
                return {'error': 'Network analysis requires at least 2 columns'}
            
            source_col = df.columns[0]
            target_col = df.columns[1]
            
            # Create networkx graph
            G = nx.from_pandas_edgelist(df, source=source_col, target=target_col)
            
            # Calculate network metrics
            results = {
                'node_count': G.number_of_nodes(),
                'edge_count': G.number_of_edges(),
                'density': nx.density(G),
                'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes()
            }
            
            # Degree analysis
            degrees = dict(G.degree())
            results['highest_degree_node'] = max(degrees, key=degrees.get)
            results['degree_distribution'] = degrees
            
            # Centrality measures
            try:
                betweenness = nx.betweenness_centrality(G)
                results['most_central_node'] = max(betweenness, key=betweenness.get)
            except:
                pass
            
            # Shortest paths (sample)
            nodes = list(G.nodes())
            if len(nodes) >= 2:
                try:
                    sample_path_length = nx.shortest_path_length(G, nodes[0], nodes[1])
                    results['sample_shortest_path'] = sample_path_length
                except:
                    pass
            
            return results
            
        except Exception as e:
            return {'error': f"Network analysis failed: {str(e)}"}
    
    def _comparison_analysis(self, df: pd.DataFrame, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comparison analysis"""
        
        results = {}
        
        # Find columns to compare
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Compare numerical columns
        for i, col1 in enumerate(numerical_cols):
            for col2 in numerical_cols[i+1:]:
                correlation = df[col1].corr(df[col2])
                results[f'{col1}_vs_{col2}_correlation'] = float(correlation)
        
        # Compare categories
        for cat_col in categorical_cols:
            for num_col in numerical_cols:
                try:
                    grouped = df.groupby(cat_col)[num_col].mean()
                    results[f'{num_col}_by_{cat_col}_comparison'] = grouped.to_dict()
                except:
                    continue
        
        return results

    def generate_insights(self, analysis_results: Dict[str, Any],
                         question_content: str) -> Dict[str, Any]:
        """Generate intelligent insights based on analysis results and question"""

        insights = {}

        # Extract key findings
        if 'statistical' in analysis_results.get('analysis_results', {}):
            stats = analysis_results['analysis_results']['statistical']
            insights['key_statistics'] = self._extract_key_statistics(stats)

        if 'aggregation' in analysis_results.get('analysis_results', {}):
            agg = analysis_results['analysis_results']['aggregation']
            insights['key_aggregations'] = self._extract_key_aggregations(agg)

        # Answer specific questions from content
        insights['direct_answers'] = self._answer_direct_questions(
            question_content, analysis_results
        )

        return insights

    def _extract_key_statistics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most important statistical findings"""
        key_stats = {}

        for key, value in stats.items():
            if isinstance(value, dict) and 'mean' in value:
                key_stats[f'{key}_summary'] = {
                    'average': value['mean'],
                    'range': value['max'] - value['min'],
                    'variability': value['std']
                }

        return key_stats

    def _extract_key_aggregations(self, agg: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most important aggregation findings"""
        key_agg = {}

        for key, value in agg.items():
            if 'total_' in key:
                key_agg[key] = value
            elif 'top_' in key:
                key_agg[key] = value

        return key_agg

    def _answer_direct_questions(self, content: str, results: Dict[str, Any]) -> List[Any]:
        """Try to answer direct questions from the content"""
        answers = []

        # Look for numbered questions
        questions = re.findall(r'\d+\.\s*(.+?)(?=\d+\.|$)', content, re.DOTALL)

        for question in questions:
            answer = self._answer_single_question(question.strip(), results)
            answers.append(answer)

        return answers

    def _answer_single_question(self, question: str, results: Dict[str, Any]) -> Any:
        """Answer a single question based on analysis results"""

        question_lower = question.lower()

        # Try to find relevant data in results
        all_results = results.get('analysis_results', {})

        # Look for specific patterns and match to results
        if 'how many' in question_lower or 'count' in question_lower:
            # Look for count-related results
            for key, value in all_results.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if 'count' in subkey or 'total' in subkey:
                            return subvalue

        elif 'correlation' in question_lower:
            # Look for correlation results
            for key, value in all_results.items():
                if isinstance(value, dict) and 'correlations' in value:
                    return value['correlations']

        elif 'average' in question_lower or 'mean' in question_lower:
            # Look for average results
            for key, value in all_results.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if 'average' in subkey or 'mean' in subkey:
                            return subvalue

        # Default: return first relevant numeric result
        for key, value in all_results.items():
            if isinstance(value, (int, float)):
                return value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (int, float)):
                        return subvalue

        return "Unable to determine from available data"
    
    def _auto_analysis(self, df: pd.DataFrame, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Perform intelligent auto-analysis based on data characteristics"""
        
        results = {}
        
        # Basic statistics for all numerical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) > 0:
            results.update(self._statistical_analysis(df))
        
        # Aggregations if categorical columns exist
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0 and len(numerical_cols) > 0:
            results.update(self._aggregation_analysis(df, spec))
        
        # Network analysis if data looks like edges
        if df.shape[1] >= 2 and df.shape[0] > 2:
            network_results = self._network_analysis(df)
            if 'error' not in network_results:
                results['network_analysis'] = network_results
        
        return results
