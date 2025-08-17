"""
Intelligent Visualization Generator for Data Analyst Agent
Creates appropriate visualizations based on data characteristics and analysis results
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx
import base64
import io
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class IntelligentVisualizer:
    """Smart visualization generator that adapts to data and analysis requirements"""
    
    def __init__(self):
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def generate_visualizations(self, data: pd.DataFrame, 
                              analysis_results: Dict[str, Any],
                              viz_requirements: List[Dict[str, str]]) -> Dict[str, str]:
        """Generate appropriate visualizations based on data and requirements"""
        
        visualizations = {}
        
        try:
            # If specific visualizations are requested
            for viz_req in viz_requirements:
                viz_type = viz_req.get('type', 'auto_detect')
                
                if viz_type == 'auto_detect':
                    # Intelligently choose visualization based on data
                    auto_viz = self._auto_generate_visualization(data, analysis_results)
                    visualizations.update(auto_viz)
                else:
                    # Generate specific visualization type
                    viz_result = self._generate_specific_visualization(
                        data, viz_type, analysis_results
                    )
                    if viz_result:
                        visualizations[viz_type] = viz_result
            
            # If no specific requirements, generate intelligent defaults
            if not viz_requirements:
                auto_viz = self._auto_generate_visualization(data, analysis_results)
                visualizations.update(auto_viz)
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            return {'error': f"Visualization generation failed: {str(e)}"}
    
    def _auto_generate_visualization(self, data: pd.DataFrame, 
                                   analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Automatically generate appropriate visualizations based on data characteristics"""
        
        visualizations = {}
        
        # Analyze data characteristics
        numerical_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        # Generate visualizations based on data structure
        
        # 1. If we have network data (detected from analysis)
        if 'network_analysis' in analysis_results.get('analysis_results', {}):
            network_viz = self._create_network_visualization(data, analysis_results)
            if network_viz:
                visualizations['network_graph'] = network_viz
            
            # Degree distribution
            degree_hist = self._create_degree_histogram(analysis_results)
            if degree_hist:
                visualizations['degree_histogram'] = degree_hist
        
        # 2. If we have categorical and numerical data
        elif len(categorical_cols) > 0 and len(numerical_cols) > 0:
            # Bar chart showing numerical values by category
            bar_chart = self._create_intelligent_bar_chart(data, categorical_cols[0], numerical_cols[0])
            if bar_chart:
                visualizations['bar_chart'] = bar_chart
        
        # 3. If we have multiple numerical columns
        elif len(numerical_cols) > 1:
            # Correlation heatmap
            correlation_viz = self._create_correlation_heatmap(data[numerical_cols])
            if correlation_viz:
                visualizations['correlation_heatmap'] = correlation_viz
            
            # Scatter plot of first two numerical columns
            scatter_viz = self._create_scatter_plot(data, numerical_cols[0], numerical_cols[1])
            if scatter_viz:
                visualizations['scatter_plot'] = scatter_viz
        
        # 4. If we have time series data
        elif self._has_time_series_data(data):
            time_series_viz = self._create_time_series_plot(data)
            if time_series_viz:
                visualizations['time_series'] = time_series_viz
        
        # 5. Single numerical column - histogram
        elif len(numerical_cols) == 1:
            hist_viz = self._create_histogram(data, numerical_cols[0])
            if hist_viz:
                visualizations['histogram'] = hist_viz
        
        return visualizations
    
    def _generate_specific_visualization(self, data: pd.DataFrame, 
                                       viz_type: str, 
                                       analysis_results: Dict[str, Any]) -> Optional[str]:
        """Generate a specific type of visualization"""
        
        try:
            if viz_type == 'bar_chart':
                return self._create_intelligent_bar_chart(data)
            elif viz_type == 'line_chart':
                return self._create_line_chart(data)
            elif viz_type == 'scatter_plot':
                return self._create_scatter_plot(data)
            elif viz_type == 'histogram':
                return self._create_histogram(data)
            elif viz_type == 'network_graph':
                return self._create_network_visualization(data, analysis_results)
            elif viz_type == 'heatmap':
                return self._create_correlation_heatmap(data)
            else:
                logger.warning(f"Unknown visualization type: {viz_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating {viz_type}: {str(e)}")
            return None
    
    def _create_network_visualization(self, data: pd.DataFrame, 
                                    analysis_results: Dict[str, Any]) -> Optional[str]:
        """Create network graph visualization"""
        
        try:
            # Create networkx graph from data
            if data.shape[1] < 2:
                return None
            
            source_col = data.columns[0]
            target_col = data.columns[1]
            
            G = nx.from_pandas_edgelist(data, source=source_col, target=target_col)
            
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Create layout
            pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
            
            # Draw network
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=1000, alpha=0.8, ax=ax)
            nx.draw_networkx_edges(G, pos, edge_color='gray', 
                                 width=2, alpha=0.6, ax=ax)
            nx.draw_networkx_labels(G, pos, font_size=10, 
                                  font_weight='bold', ax=ax)
            
            ax.set_title('Network Graph', fontsize=16, fontweight='bold')
            ax.axis('off')
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating network visualization: {str(e)}")
            return None
    
    def _create_degree_histogram(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Create degree distribution histogram"""
        
        try:
            network_data = analysis_results.get('analysis_results', {}).get('network_analysis', {})
            degrees = network_data.get('degree_distribution', {})
            
            if not degrees:
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Count degree frequencies
            degree_values = list(degrees.values())
            
            ax.hist(degree_values, bins=max(1, len(set(degree_values))), 
                   color='green', alpha=0.7, edgecolor='black')
            
            ax.set_xlabel('Degree', fontsize=12)
            ax.set_ylabel('Number of Nodes', fontsize=12)
            ax.set_title('Degree Distribution', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating degree histogram: {str(e)}")
            return None
    
    def _create_intelligent_bar_chart(self, data: pd.DataFrame, 
                                    cat_col: str = None, 
                                    num_col: str = None) -> Optional[str]:
        """Create intelligent bar chart based on data"""
        
        try:
            # Auto-detect columns if not provided
            if cat_col is None:
                categorical_cols = data.select_dtypes(include=['object', 'category']).columns
                cat_col = categorical_cols[0] if len(categorical_cols) > 0 else None
            
            if num_col is None:
                numerical_cols = data.select_dtypes(include=[np.number]).columns
                num_col = numerical_cols[0] if len(numerical_cols) > 0 else None
            
            if cat_col is None or num_col is None:
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Group by category and sum numerical values
            grouped = data.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
            
            bars = ax.bar(grouped.index, grouped.values, 
                         color='blue', alpha=0.7, edgecolor='black')
            
            ax.set_xlabel(cat_col.title(), fontsize=12)
            ax.set_ylabel(f'Total {num_col.title()}', fontsize=12)
            ax.set_title(f'{num_col.title()} by {cat_col.title()}', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            return None
    
    def _create_correlation_heatmap(self, data: pd.DataFrame) -> Optional[str]:
        """Create correlation heatmap for numerical data"""
        
        try:
            numerical_data = data.select_dtypes(include=[np.number])
            
            if numerical_data.shape[1] < 2:
                return None
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            correlation_matrix = numerical_data.corr()
            
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', 
                       center=0, square=True, ax=ax)
            
            ax.set_title('Correlation Heatmap', fontsize=16, fontweight='bold')
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating correlation heatmap: {str(e)}")
            return None
    
    def _create_scatter_plot(self, data: pd.DataFrame, 
                           x_col: str = None, y_col: str = None) -> Optional[str]:
        """Create scatter plot"""
        
        try:
            numerical_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numerical_cols) < 2:
                return None
            
            x_col = x_col or numerical_cols[0]
            y_col = y_col or numerical_cols[1]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.scatter(data[x_col], data[y_col], alpha=0.6)
            
            ax.set_xlabel(x_col.title(), fontsize=12)
            ax.set_ylabel(y_col.title(), fontsize=12)
            ax.set_title(f'{y_col.title()} vs {x_col.title()}', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating scatter plot: {str(e)}")
            return None
    
    def _create_histogram(self, data: pd.DataFrame, col: str = None) -> Optional[str]:
        """Create histogram"""
        
        try:
            numerical_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numerical_cols) == 0:
                return None
            
            col = col or numerical_cols[0]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.hist(data[col].dropna(), bins=20, color='orange', 
                   alpha=0.7, edgecolor='black')
            
            ax.set_xlabel(col.title(), fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.set_title(f'Distribution of {col.title()}', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating histogram: {str(e)}")
            return None
    
    def _has_time_series_data(self, data: pd.DataFrame) -> bool:
        """Check if data contains time series information"""
        
        for col in data.columns:
            try:
                pd.to_datetime(data[col].dropna().head(10))
                return True
            except:
                continue
        
        return False
    
    def _create_time_series_plot(self, data: pd.DataFrame) -> Optional[str]:
        """Create time series plot"""
        
        try:
            # Find date column
            date_col = None
            for col in data.columns:
                try:
                    pd.to_datetime(data[col].dropna().head(10))
                    date_col = col
                    break
                except:
                    continue
            
            if date_col is None:
                return None
            
            # Find numerical column
            numerical_cols = data.select_dtypes(include=[np.number]).columns
            if len(numerical_cols) == 0:
                return None
            
            num_col = numerical_cols[0]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Convert date column and sort
            data_copy = data.copy()
            data_copy[date_col] = pd.to_datetime(data_copy[date_col])
            data_copy = data_copy.sort_values(date_col)
            
            ax.plot(data_copy[date_col], data_copy[num_col], 
                   color='red', linewidth=2, marker='o')
            
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel(num_col.title(), fontsize=12)
            ax.set_title(f'{num_col.title()} Over Time', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            
            return self._save_plot_as_base64(fig)
            
        except Exception as e:
            logger.error(f"Error creating time series plot: {str(e)}")
            return None
    
    def _save_plot_as_base64(self, fig) -> str:
        """Save matplotlib figure as base64 string"""
        
        try:
            plt.tight_layout()
            
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', 
                       dpi=100, facecolor='white')
            buffer.seek(0)
            
            img_data = base64.b64encode(buffer.getvalue()).decode()
            
            plt.close(fig)
            buffer.close()
            
            return img_data
            
        except Exception as e:
            logger.error(f"Error saving plot as base64: {str(e)}")
            return ""
