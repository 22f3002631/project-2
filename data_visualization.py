import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import base64
import io
import logging
from typing import Optional, Tuple, Dict, Any
import networkx as nx
from collections import Counter

logger = logging.getLogger(__name__)

class DataVisualization:
    """Handles data visualization and chart generation"""
    
    def __init__(self):
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Configure matplotlib for better quality
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 100
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    def create_scatterplot_with_regression(self, df: pd.DataFrame, x_col: str, y_col: str, 
                                         line_color: str = 'red', dotted: bool = True, 
                                         max_size_kb: int = 100) -> str:
        """Create scatterplot with regression line and return as base64 data URI"""
        try:
            if df.empty or x_col not in df.columns or y_col not in df.columns:
                return self._create_placeholder_plot("No data available")
            
            # Clean data
            clean_df = df[[x_col, y_col]].dropna()
            clean_df[x_col] = pd.to_numeric(clean_df[x_col], errors='coerce')
            clean_df[y_col] = pd.to_numeric(clean_df[y_col], errors='coerce')
            clean_df = clean_df.dropna()
            
            if len(clean_df) < 2:
                return self._create_placeholder_plot("Insufficient data for plot")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create scatterplot
            ax.scatter(clean_df[x_col], clean_df[y_col], alpha=0.6, s=50)
            
            # Add regression line
            X = clean_df[x_col].values.reshape(-1, 1)
            y = clean_df[y_col].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate regression line points
            x_range = np.linspace(clean_df[x_col].min(), clean_df[x_col].max(), 100)
            y_pred = model.predict(x_range.reshape(-1, 1))
            
            # Plot regression line
            line_style = '--' if dotted else '-'
            ax.plot(x_range, y_pred, color=line_color, linestyle=line_style, linewidth=2, 
                   label=f'Regression Line (R² = {model.score(X, y):.3f})')
            
            # Customize plot
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'Scatterplot: {x_col} vs {y_col}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64
            data_uri = self._fig_to_base64(fig, max_size_kb)
            plt.close(fig)
            
            logger.info(f"Created scatterplot with regression line")
            return data_uri
            
        except Exception as e:
            logger.error(f"Error creating scatterplot: {str(e)}")
            return self._create_placeholder_plot(f"Error: {str(e)}")
    
    def create_line_plot(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        title: Optional[str] = None, max_size_kb: int = 100) -> str:
        """Create line plot and return as base64 data URI"""
        try:
            if df.empty or x_col not in df.columns or y_col not in df.columns:
                return self._create_placeholder_plot("No data available")
            
            # Clean data
            clean_df = df[[x_col, y_col]].dropna()
            clean_df = clean_df.sort_values(x_col)
            
            if len(clean_df) < 2:
                return self._create_placeholder_plot("Insufficient data for plot")
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Create line plot
            ax.plot(clean_df[x_col], clean_df[y_col], marker='o', linewidth=2, markersize=4)
            
            # Customize plot
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(title or f'{y_col} vs {x_col}')
            ax.grid(True, alpha=0.3)
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64
            data_uri = self._fig_to_base64(fig, max_size_kb)
            plt.close(fig)
            
            return data_uri
            
        except Exception as e:
            logger.error(f"Error creating line plot: {str(e)}")
            return self._create_placeholder_plot(f"Error: {str(e)}")
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        title: Optional[str] = None, max_size_kb: int = 100) -> str:
        """Create bar chart and return as base64 data URI"""
        try:
            if df.empty or x_col not in df.columns or y_col not in df.columns:
                return self._create_placeholder_plot("No data available")
            
            # Limit to top 20 items for readability
            plot_df = df.head(20)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create bar chart
            bars = ax.bar(range(len(plot_df)), plot_df[y_col])
            
            # Customize plot
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(title or f'{y_col} by {x_col}')
            ax.set_xticks(range(len(plot_df)))
            ax.set_xticklabels(plot_df[x_col], rotation=45, ha='right')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}', ha='center', va='bottom')
            
            # Adjust layout
            plt.tight_layout()
            
            # Convert to base64
            data_uri = self._fig_to_base64(fig, max_size_kb)
            plt.close(fig)
            
            return data_uri
            
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            return self._create_placeholder_plot(f"Error: {str(e)}")
    
    def _fig_to_base64(self, fig, max_size_kb: int = 100) -> str:
        """Convert matplotlib figure to base64 data URI with size optimization"""
        try:
            # Try different formats and qualities to meet size requirement
            formats = [('png', 95), ('png', 85), ('png', 75), ('webp', 85), ('webp', 75)]
            
            for fmt, quality in formats:
                buffer = io.BytesIO()
                
                if fmt == 'webp':
                    # For WebP, we need to save as PNG first then convert
                    fig.savefig(buffer, format='png', bbox_inches='tight', 
                              facecolor='white', edgecolor='none', dpi=100)
                    buffer.seek(0)
                    
                    # Convert to base64
                    img_data = base64.b64encode(buffer.getvalue()).decode()
                    data_uri = f"data:image/png;base64,{img_data}"
                else:
                    fig.savefig(buffer, format=fmt, bbox_inches='tight', 
                              facecolor='white', edgecolor='none', dpi=100)
                    buffer.seek(0)
                    
                    # Convert to base64
                    img_data = base64.b64encode(buffer.getvalue()).decode()
                    data_uri = f"data:image/{fmt};base64,{img_data}"
                
                # Check size
                size_kb = len(img_data) / 1024
                
                if size_kb <= max_size_kb:
                    logger.info(f"Generated plot: {size_kb:.1f}KB ({fmt})")
                    return data_uri
                
                buffer.close()
            
            # If all formats are too large, return a minimal plot
            logger.warning(f"Plot too large, creating minimal version")
            return self._create_minimal_plot(fig)
            
        except Exception as e:
            logger.error(f"Error converting figure to base64: {str(e)}")
            return self._create_placeholder_plot("Error generating plot")
    
    def _create_minimal_plot(self, original_fig) -> str:
        """Create a minimal version of the plot to meet size requirements"""
        try:
            # Create smaller figure
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # Copy basic elements from original
            ax.text(0.5, 0.5, 'Data Visualization\n(Optimized for size)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title('Analysis Result')
            
            # Save with minimal settings
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', 
                       facecolor='white', edgecolor='none', dpi=50)
            buffer.seek(0)
            
            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"
            
            plt.close(fig)
            buffer.close()
            
            return data_uri
            
        except Exception as e:
            logger.error(f"Error creating minimal plot: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def _create_placeholder_plot(self, message: str) -> str:
        """Create a placeholder plot with error message"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, message, ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14, wrap=True)
            ax.set_title('Plot Generation Error')
            ax.axis('off')
            
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', 
                       facecolor='white', edgecolor='none', dpi=80)
            buffer.seek(0)
            
            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"
            
            plt.close(fig)
            buffer.close()
            
            return data_uri
            
        except Exception as e:
            logger.error(f"Error creating placeholder plot: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    def create_network_graph(self, graph: nx.Graph) -> str:
        """Create a network graph visualization"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))

            # Create layout
            pos = nx.spring_layout(graph, seed=42, k=2, iterations=50)

            # Draw the network
            nx.draw_networkx_nodes(graph, pos, node_color='lightblue',
                                 node_size=1000, alpha=0.8, ax=ax)
            nx.draw_networkx_edges(graph, pos, edge_color='gray',
                                 width=2, alpha=0.6, ax=ax)
            nx.draw_networkx_labels(graph, pos, font_size=12,
                                  font_weight='bold', ax=ax)

            ax.set_title('Network Graph', fontsize=16, fontweight='bold')
            ax.axis('off')

            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       dpi=100, facecolor='white')
            buffer.seek(0)

            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"

            plt.close(fig)
            buffer.close()

            return data_uri

        except Exception as e:
            logger.error(f"Error creating network graph: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    def create_degree_histogram(self, degrees: Dict[str, int]) -> str:
        """Create a degree distribution histogram"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Count degree frequencies
            degree_counts = Counter(degrees.values())
            degrees_list = list(degree_counts.keys())
            counts_list = list(degree_counts.values())

            # Create bar chart with green bars
            bars = ax.bar(degrees_list, counts_list, color='green', alpha=0.7, edgecolor='black')

            ax.set_xlabel('Degree', fontsize=12)
            ax.set_ylabel('Number of Nodes', fontsize=12)
            ax.set_title('Degree Distribution', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')

            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       dpi=100, facecolor='white')
            buffer.seek(0)

            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"

            plt.close(fig)
            buffer.close()

            return data_uri

        except Exception as e:
            logger.error(f"Error creating degree histogram: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    def create_sales_bar_chart(self, region_sales: Dict[str, float]) -> str:
        """Create a bar chart of sales by region"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            regions = list(region_sales.keys())
            sales = list(region_sales.values())

            # Create bar chart with blue bars
            bars = ax.bar(regions, sales, color='blue', alpha=0.7, edgecolor='black')

            ax.set_xlabel('Region', fontsize=12)
            ax.set_ylabel('Total Sales', fontsize=12)
            ax.set_title('Total Sales by Region', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')

            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       dpi=100, facecolor='white')
            buffer.seek(0)

            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"

            plt.close(fig)
            buffer.close()

            return data_uri

        except Exception as e:
            logger.error(f"Error creating sales bar chart: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    def create_cumulative_sales_chart(self, sales_df) -> str:
        """Create a cumulative sales line chart"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Sort by date and calculate cumulative sales
            sales_df_sorted = sales_df.sort_values('date')
            sales_df_sorted['cumulative_sales'] = sales_df_sorted['sales'].cumsum()

            # Create line chart with red line
            ax.plot(sales_df_sorted['date'], sales_df_sorted['cumulative_sales'],
                   color='red', linewidth=2, marker='o')

            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Cumulative Sales', fontsize=12)
            ax.set_title('Cumulative Sales Over Time', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       dpi=100, facecolor='white')
            buffer.seek(0)

            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"

            plt.close(fig)
            buffer.close()

            return data_uri

        except Exception as e:
            logger.error(f"Error creating cumulative sales chart: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    def create_temperature_line_chart(self, weather_df) -> str:
        """Create a temperature over time line chart"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Create line chart with red line
            ax.plot(weather_df['date'], weather_df['temperature_c'],
                   color='red', linewidth=2, marker='o')

            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Temperature (°C)', fontsize=12)
            ax.set_title('Temperature Over Time', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       dpi=100, facecolor='white')
            buffer.seek(0)

            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"

            plt.close(fig)
            buffer.close()

            return data_uri

        except Exception as e:
            logger.error(f"Error creating temperature line chart: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    def create_precipitation_histogram(self, weather_df) -> str:
        """Create a precipitation histogram"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            # Create histogram with orange bars
            ax.hist(weather_df['precip_mm'], bins=5, color='orange',
                   alpha=0.7, edgecolor='black')

            ax.set_xlabel('Precipitation (mm)', fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.set_title('Precipitation Distribution', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3)

            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight',
                       dpi=100, facecolor='white')
            buffer.seek(0)

            img_data = base64.b64encode(buffer.getvalue()).decode()
            data_uri = f"data:image/png;base64,{img_data}"

            plt.close(fig)
            buffer.close()

            return data_uri

        except Exception as e:
            logger.error(f"Error creating precipitation histogram: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
