"""
Intelligent Orchestrator for Data Analyst Agent
Coordinates all components to provide comprehensive, flexible data analysis
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json
import pandas as pd
import numpy as np

from intelligent_question_processor import IntelligentQuestionProcessor
from flexible_data_loader import FlexibleDataLoader
from flexible_data_analyzer import FlexibleDataAnalyzer
from intelligent_visualizer import IntelligentVisualizer

logger = logging.getLogger(__name__)

class IntelligentOrchestrator:
    """Main orchestrator that coordinates intelligent data analysis"""
    
    def __init__(self):
        self.question_processor = IntelligentQuestionProcessor()
        self.data_loader = FlexibleDataLoader()
        self.data_analyzer = FlexibleDataAnalyzer()
        self.visualizer = IntelligentVisualizer()
    
    def process_analysis_request(self, questions_content: str, 
                               uploaded_files: Dict[str, str] = None) -> Union[Dict[str, Any], List[Any]]:
        """Main method to process any data analysis request intelligently"""
        
        try:
            logger.info("Starting intelligent analysis process")
            
            # Step 1: Analyze the question to understand requirements
            question_analysis = self.question_processor.analyze_question(
                questions_content, 
                list(uploaded_files.keys()) if uploaded_files else []
            )
            
            logger.info(f"Question analysis: {question_analysis}")
            
            # Step 2: Load appropriate data
            data_sources = question_analysis.get('data_sources', [])
            loaded_data = self.data_loader.load_data(data_sources, uploaded_files)
            
            if not loaded_data:
                return {"error": "No data could be loaded for analysis"}
            
            logger.info(f"Loaded {len(loaded_data)} datasets")
            
            # Step 3: Perform intelligent analysis on each dataset
            all_results = {}
            
            for data_name, data_df in loaded_data.items():
                logger.info(f"Analyzing dataset: {data_name}")
                
                # Enhance analysis spec with data-driven suggestions
                enhanced_analysis_spec = self._enhance_analysis_spec(
                    question_analysis, data_df
                )
                
                # Perform analysis
                analysis_results = self.data_analyzer.analyze_data(
                    data_df, enhanced_analysis_spec
                )
                
                # Generate insights
                insights = self.data_analyzer.generate_insights(
                    analysis_results, questions_content
                )
                
                # Generate visualizations
                visualizations = self.visualizer.generate_visualizations(
                    data_df, analysis_results, 
                    question_analysis.get('visualizations', [])
                )
                
                all_results[data_name] = {
                    'analysis': analysis_results,
                    'insights': insights,
                    'visualizations': visualizations
                }
            
            # Step 4: Format output according to detected requirements
            formatted_output = self._format_output(
                all_results, question_analysis, questions_content
            )
            
            logger.info("Analysis completed successfully")
            return formatted_output
            
        except Exception as e:
            logger.error(f"Error in analysis process: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _enhance_analysis_spec(self, question_analysis: Dict[str, Any], 
                             data_df: pd.DataFrame) -> Dict[str, Any]:
        """Enhance analysis specification with data-driven insights"""
        
        enhanced_spec = question_analysis.copy()
        
        # Add data-driven analysis suggestions
        suggested_analyses = self.data_loader.suggest_analysis_types(data_df)
        
        # Merge with question-derived analysis types
        existing_types = enhanced_spec.get('analysis_types', [])
        enhanced_spec['analysis_types'] = list(set(existing_types + suggested_analyses))
        
        # Add data characteristics
        enhanced_spec['data_characteristics'] = {
            'shape': data_df.shape,
            'numerical_columns': list(data_df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(data_df.select_dtypes(include=['object', 'category']).columns),
            'has_missing_values': data_df.isnull().any().any()
        }
        
        return enhanced_spec
    
    def _format_output(self, results: Dict[str, Any], 
                      question_analysis: Dict[str, Any],
                      original_content: str) -> Union[Dict[str, Any], List[Any]]:
        """Format output according to detected requirements and question structure"""
        
        try:
            output_format = question_analysis.get('output_format', 'json_object')
            
            # If multiple datasets, choose the most relevant one
            primary_dataset = self._select_primary_dataset(results, question_analysis)
            primary_results = results.get(primary_dataset, {})
            
            # Extract key information for response
            response_data = self._extract_response_data(
                primary_results, question_analysis, original_content
            )
            
            # Format according to detected output format
            if output_format == 'json_array':
                return self._format_as_array(response_data, original_content)
            elif output_format == 'json_object':
                return self._format_as_object(response_data, question_analysis)
            else:
                # Default to object format
                return self._format_as_object(response_data, question_analysis)
                
        except Exception as e:
            logger.error(f"Error formatting output: {str(e)}")
            return {"error": f"Output formatting failed: {str(e)}"}
    
    def _select_primary_dataset(self, results: Dict[str, Any], 
                              question_analysis: Dict[str, Any]) -> str:
        """Select the most relevant dataset for the response"""
        
        # If only one dataset, use it
        if len(results) == 1:
            return list(results.keys())[0]
        
        # Prioritize based on data sources mentioned in question
        data_sources = question_analysis.get('data_sources', [])
        for source in data_sources:
            source_name = source.get('name', '')
            if source_name in results:
                return source_name
        
        # Default to first dataset
        return list(results.keys())[0]
    
    def _extract_response_data(self, results: Dict[str, Any], 
                             question_analysis: Dict[str, Any],
                             original_content: str) -> Dict[str, Any]:
        """Extract key data for response"""
        
        response_data = {}
        
        # Get analysis results
        analysis_results = results.get('analysis', {}).get('analysis_results', {})
        insights = results.get('insights', {})
        visualizations = results.get('visualizations', {})
        
        # Extract direct answers if available
        direct_answers = insights.get('direct_answers', [])
        if direct_answers:
            response_data['direct_answers'] = direct_answers
        
        # Extract key metrics from different analysis types
        for analysis_type, analysis_data in analysis_results.items():
            if isinstance(analysis_data, dict):
                response_data.update(self._flatten_analysis_data(analysis_data, analysis_type))
        
        # Add visualizations (convert to base64 without data URI prefix)
        for viz_name, viz_data in visualizations.items():
            if viz_data and isinstance(viz_data, str):
                response_data[viz_name] = viz_data
        
        return response_data
    
    def _flatten_analysis_data(self, data: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested analysis data for easier access"""
        
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}_{key}" if prefix else key
            
            if isinstance(value, dict) and len(value) < 10:  # Avoid deeply nested structures
                flattened.update(self._flatten_analysis_data(value, new_key))
            elif isinstance(value, (int, float, str, bool)):
                flattened[new_key] = value
            elif isinstance(value, list) and len(value) < 20:  # Reasonable list size
                flattened[new_key] = value
        
        return flattened
    
    def _format_as_array(self, response_data: Dict[str, Any], 
                        original_content: str) -> List[Any]:
        """Format response as JSON array (for numbered questions)"""
        
        # Try to extract direct answers first
        if 'direct_answers' in response_data:
            return response_data['direct_answers']
        
        # Otherwise, create array from key values
        array_response = []
        
        # Look for numbered questions in original content
        import re
        questions = re.findall(r'\d+\.\s*(.+?)(?=\d+\.|$)', original_content, re.DOTALL)
        
        if questions:
            # Try to match answers to questions
            for i, question in enumerate(questions):
                answer = self._find_answer_for_question(question.strip(), response_data)
                array_response.append(answer)
        else:
            # Just return key values as array
            for key, value in response_data.items():
                if not key.endswith('_chart') and not key.endswith('_graph'):
                    array_response.append(value)
        
        return array_response
    
    def _format_as_object(self, response_data: Dict[str, Any], 
                         question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format response as JSON object"""
        
        # Return the response data as-is (it's already a dict)
        return response_data
    
    def _find_answer_for_question(self, question: str, 
                                response_data: Dict[str, Any]) -> Any:
        """Find the most appropriate answer for a specific question"""
        
        question_lower = question.lower()
        
        # Look for specific patterns and match to data
        if 'how many' in question_lower or 'count' in question_lower:
            for key, value in response_data.items():
                if 'count' in key.lower() or 'total' in key.lower():
                    return value
        
        elif 'correlation' in question_lower:
            for key, value in response_data.items():
                if 'correlation' in key.lower():
                    return value
        
        elif 'average' in question_lower or 'mean' in question_lower:
            for key, value in response_data.items():
                if 'average' in key.lower() or 'mean' in key.lower():
                    return value
        
        elif 'highest' in question_lower or 'maximum' in question_lower:
            for key, value in response_data.items():
                if 'highest' in key.lower() or 'max' in key.lower() or 'top' in key.lower():
                    return value
        
        elif 'visualization' in question_lower or 'plot' in question_lower or 'chart' in question_lower:
            for key, value in response_data.items():
                if any(viz_type in key.lower() for viz_type in ['chart', 'graph', 'plot', 'histogram']):
                    return value
        
        # Default: return first relevant value
        for key, value in response_data.items():
            if isinstance(value, (int, float, str)) and not key.endswith('_error'):
                return value
        
        return "Unable to determine from available data"
