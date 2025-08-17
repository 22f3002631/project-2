"""
Intelligent Question Processor for Data Analyst Agent
Handles diverse data analysis scenarios with flexible, generalizable approach
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import os

logger = logging.getLogger(__name__)

class IntelligentQuestionProcessor:
    """Advanced question processor that intelligently analyzes questions and data"""
    
    def __init__(self):
        # Comprehensive analysis type detection
        self.analysis_keywords = {
            'statistical': [
                r'mean', r'average', r'median', r'mode', r'std', r'variance',
                r'correlation', r'regression', r'distribution', r'percentile',
                r'quartile', r'outlier', r'summary.*statistics', r'describe'
            ],
            'aggregation': [
                r'sum', r'total', r'count', r'group.*by', r'aggregate',
                r'maximum', r'minimum', r'max', r'min', r'top.*\d+', r'bottom.*\d+',
                r'highest', r'lowest', r'most', r'least', r'largest', r'smallest'
            ],
            'time_series': [
                r'time.*series', r'trend', r'seasonal', r'over.*time',
                r'daily', r'monthly', r'yearly', r'temporal',
                r'cumulative', r'moving.*average', r'growth.*rate',
                r'before.*\d{4}', r'after.*\d{4}', r'between.*\d{4}.*and.*\d{4}'
            ],
            'network': [
                r'network', r'graph', r'node', r'edge', r'degree',
                r'centrality', r'shortest.*path', r'density',
                r'connected.*components', r'clustering', r'undirected'
            ],
            'visualization': [
                r'plot', r'chart', r'graph', r'histogram', r'scatter',
                r'bar.*chart', r'line.*chart', r'pie.*chart',
                r'heatmap', r'box.*plot', r'visualiz', r'draw', r'encode.*base64'
            ],
            'comparison': [
                r'compare', r'difference', r'vs', r'versus',
                r'between.*and', r'relative.*to', r'ratio', r'which.*better'
            ],
            'filtering': [
                r'where', r'filter', r'only', r'exclude', r'include',
                r'greater.*than', r'less.*than', r'equal.*to', r'contains'
            ]
        }
        
        # Data type detection patterns
        self.data_type_patterns = {
            'numerical': [r'price', r'sales', r'revenue', r'temperature', r'age', r'score', r'rating'],
            'categorical': [r'region', r'category', r'type', r'class', r'group', r'status'],
            'temporal': [r'date', r'time', r'year', r'month', r'day', r'timestamp'],
            'textual': [r'name', r'title', r'description', r'comment', r'text']
        }
        
        # Output format detection
        self.output_format_patterns = {
            'json_object': [r'json.*object', r'return.*object', r'keys?:', r'\{.*\}'],
            'json_array': [r'json.*array', r'return.*array', r'list.*of', r'\[.*\]'],
            'base64_image': [r'base64', r'png', r'encode.*image', r'visualization']
        }
    
    def analyze_question(self, content: str, available_files: List[str] = None) -> Dict[str, Any]:
        """Intelligently analyze a question to determine analysis requirements"""
        
        content_lower = content.lower()
        
        # Detect analysis types needed
        analysis_types = self._detect_analysis_types(content_lower)
        
        # Detect data sources
        data_sources = self._detect_data_sources(content, available_files or [])
        
        # Detect expected output format
        output_format = self._detect_output_format(content_lower)
        
        # Extract specific requirements
        requirements = self._extract_requirements(content_lower)
        
        # Determine visualization needs
        visualizations = self._detect_visualizations(content_lower)
        
        return {
            'content': content,
            'analysis_types': analysis_types,
            'data_sources': data_sources,
            'output_format': output_format,
            'requirements': requirements,
            'visualizations': visualizations,
            'complexity': self._assess_complexity(analysis_types, requirements)
        }
    
    def _detect_analysis_types(self, content: str) -> List[str]:
        """Detect what types of analysis are needed"""
        detected_types = []
        
        for analysis_type, patterns in self.analysis_keywords.items():
            if any(re.search(pattern, content) for pattern in patterns):
                detected_types.append(analysis_type)
        
        return detected_types
    
    def _detect_data_sources(self, content: str, available_files: List[str]) -> List[Dict[str, Any]]:
        """Detect and analyze data sources mentioned in the question"""
        sources = []
        
        # Look for file references in the question
        file_patterns = [r'(\w+\.csv)', r'(\w+\.json)', r'(\w+\.xlsx)', r'(\w+\.parquet)']
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                sources.append({
                    'type': 'file',
                    'name': match,
                    'format': match.split('.')[-1].lower(),
                    'available': match in available_files
                })
        
        # Look for web sources
        if re.search(r'wikipedia|web.*scraping|url', content, re.IGNORECASE):
            sources.append({
                'type': 'web',
                'name': 'wikipedia',
                'format': 'html',
                'available': True
            })
        
        # Look for database references
        if re.search(r'database|duckdb|sql|table', content, re.IGNORECASE):
            sources.append({
                'type': 'database',
                'name': 'database',
                'format': 'sql',
                'available': True
            })
        
        return sources
    
    def _detect_output_format(self, content: str) -> str:
        """Detect expected output format"""
        
        # Check for specific format requirements
        if re.search(r'json.*object|return.*object.*with.*keys', content):
            return 'json_object'
        elif re.search(r'json.*array|return.*array', content):
            return 'json_array'
        elif re.search(r'base64.*png|encode.*image', content):
            return 'base64_image'
        
        # Default based on question structure
        if re.search(r'^\d+\.', content, re.MULTILINE):  # Numbered questions
            return 'json_array'
        else:
            return 'json_object'
    
    def _extract_requirements(self, content: str) -> Dict[str, Any]:
        """Extract specific requirements from the question"""
        requirements = {
            'calculations': [],
            'filters': [],
            'groupings': [],
            'comparisons': [],
            'thresholds': []
        }
        
        # Extract numerical thresholds
        thresholds = re.findall(r'(\d+(?:\.\d+)?)', content)
        requirements['thresholds'] = [float(t) for t in thresholds]
        
        # Extract comparison operators
        if re.search(r'greater.*than|more.*than|above', content):
            requirements['comparisons'].append('greater_than')
        if re.search(r'less.*than|fewer.*than|below', content):
            requirements['comparisons'].append('less_than')
        
        # Extract grouping requirements
        group_matches = re.findall(r'group.*by.*(\w+)|by.*(\w+)', content)
        for match in group_matches:
            requirements['groupings'].extend([g for g in match if g])
        
        return requirements
    
    def _detect_visualizations(self, content: str) -> List[Dict[str, str]]:
        """Detect what visualizations are needed"""
        visualizations = []
        
        viz_types = {
            'bar_chart': [r'bar.*chart', r'bar.*graph'],
            'line_chart': [r'line.*chart', r'line.*graph', r'time.*series.*plot'],
            'scatter_plot': [r'scatter.*plot', r'scatter.*chart', r'correlation.*plot'],
            'histogram': [r'histogram', r'distribution.*plot'],
            'pie_chart': [r'pie.*chart'],
            'heatmap': [r'heatmap', r'heat.*map'],
            'network_graph': [r'network.*graph', r'graph.*visualization']
        }
        
        for viz_type, patterns in viz_types.items():
            if any(re.search(pattern, content) for pattern in patterns):
                visualizations.append({
                    'type': viz_type,
                    'format': 'base64_png'
                })
        
        # If visualization is mentioned but type not specific, infer from analysis
        if re.search(r'plot|chart|graph|visualiz', content) and not visualizations:
            visualizations.append({
                'type': 'auto_detect',
                'format': 'base64_png'
            })
        
        return visualizations
    
    def _assess_complexity(self, analysis_types: List[str], requirements: Dict[str, Any]) -> str:
        """Assess the complexity of the analysis"""
        
        complexity_score = 0
        complexity_score += len(analysis_types)
        complexity_score += len(requirements.get('calculations', []))
        complexity_score += len(requirements.get('groupings', []))
        
        if complexity_score <= 2:
            return 'simple'
        elif complexity_score <= 5:
            return 'moderate'
        else:
            return 'complex'
