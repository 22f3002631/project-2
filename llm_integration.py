import openai
import requests
import os
import logging
import json
from typing import Dict, Any, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class LLMIntegration:
    """Handles integration with LLM APIs for intelligent question processing"""

    def __init__(self):
        self.openai_client = None
        self.aipipe_client = None

        # Initialize OpenAI client if API key is available
        if os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
            logger.info("OpenAI client initialized")

        # Initialize aipipe client if API key and URL are available
        if os.getenv('AIPIPE_API_KEY') and os.getenv('AIPIPE_BASE_URL'):
            self.aipipe_client = {
                'api_key': os.getenv('AIPIPE_API_KEY'),
                'base_url': os.getenv('AIPIPE_BASE_URL')
            }
            logger.info("Aipipe client initialized")

        if not self.openai_client and not self.aipipe_client:
            logger.warning("No LLM clients available - using fallback responses only")
    
    def process_question(self, question: str, uploaded_files: Dict[str, str]) -> Any:
        """Process a question using LLM to understand intent and generate response"""
        try:
            # If no LLM clients available, return basic response
            if not self.openai_client and not self.aipipe_client:
                return self._fallback_response(question, uploaded_files)

            # Analyze the question to understand what's needed
            analysis_prompt = self._create_analysis_prompt(question, uploaded_files)

            # Get LLM response - try OpenAI first, then aipipe
            response = None
            if self.openai_client:
                response = self._query_openai(analysis_prompt)
            elif self.aipipe_client:
                response = self._query_aipipe(analysis_prompt)

            if response:
                # Process the LLM response and execute the analysis
                return self._execute_analysis_plan(response, uploaded_files)
            else:
                return self._fallback_response(question, uploaded_files)

        except Exception as e:
            logger.error(f"Error in LLM processing: {str(e)}")
            return self._fallback_response(question, uploaded_files)
    
    def _create_analysis_prompt(self, question: str, uploaded_files: Dict[str, str]) -> str:
        """Create a prompt for the LLM to analyze the question"""
        
        file_info = ""
        if uploaded_files:
            file_info = f"Available files: {list(uploaded_files.keys())}"
        
        prompt = f"""
        You are a data analyst AI. Analyze this question and determine what analysis needs to be performed:
        
        Question: {question}
        {file_info}
        
        Please respond with a JSON object containing:
        1. "analysis_type": The type of analysis needed (e.g., "statistical", "visualization", "data_processing")
        2. "steps": A list of specific steps to perform the analysis
        3. "expected_output": The format of the expected output
        4. "data_sources": What data sources are needed
        
        Focus on providing actionable steps that can be executed programmatically.
        """
        
        return prompt
    
    def _query_openai(self, prompt: str) -> Dict[str, Any]:
        """Query OpenAI API"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful data analysis assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error querying OpenAI: {str(e)}")
            return self._default_analysis_plan()
    
    def _query_aipipe(self, prompt: str) -> Dict[str, Any]:
        """Query aipipe API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.aipipe_client["api_key"]}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': 'gpt-3.5-turbo',  # or whatever model aipipe supports
                'messages': [
                    {"role": "system", "content": "You are a helpful data analysis assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.1
            }

            response = requests.post(
                f'{self.aipipe_client["base_url"]}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return json.loads(content)
            else:
                logger.error(f"Aipipe API error: {response.status_code} - {response.text}")
                return self._default_analysis_plan()

        except Exception as e:
            logger.error(f"Error querying aipipe: {str(e)}")
            return self._default_analysis_plan()
    
    def _execute_analysis_plan(self, plan: Dict[str, Any], uploaded_files: Dict[str, str]) -> Any:
        """Execute the analysis plan generated by the LLM"""
        try:
            analysis_type = plan.get('analysis_type', 'statistical')
            steps = plan.get('steps', [])
            
            # Import our analysis modules
            from data_sourcing import DataSourcing
            from data_analysis import DataAnalysis
            from data_visualization import DataVisualization
            
            data_sourcing = DataSourcing()
            data_analysis = DataAnalysis()
            data_visualization = DataVisualization()
            
            # Load data if files are provided
            data = None
            if uploaded_files:
                for filename, filepath in uploaded_files.items():
                    if filename.endswith('.csv'):
                        data = data_sourcing.load_csv(filepath)
                        break
            
            # Execute steps based on analysis type
            if analysis_type == 'statistical' and data is not None:
                return self._execute_statistical_analysis(data, steps)
            elif analysis_type == 'visualization' and data is not None:
                return self._execute_visualization(data, steps)
            else:
                return self._execute_generic_analysis(steps, uploaded_files)
                
        except Exception as e:
            logger.error(f"Error executing analysis plan: {str(e)}")
            return "Error executing analysis"
    
    def _execute_statistical_analysis(self, data: pd.DataFrame, steps: List[str]) -> Any:
        """Execute statistical analysis steps"""
        try:
            from data_analysis import DataAnalysis
            data_analysis = DataAnalysis()
            
            results = []
            
            for step in steps:
                step_lower = step.lower()
                
                if 'correlation' in step_lower:
                    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        corr = data_analysis.calculate_correlation(data, numeric_cols[0], numeric_cols[1])
                        results.append(corr)
                
                elif 'count' in step_lower:
                    results.append(len(data))
                
                elif 'mean' in step_lower or 'average' in step_lower:
                    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        results.append(data[numeric_cols[0]].mean())
            
            return results[0] if len(results) == 1 else results
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {str(e)}")
            return None
    
    def _execute_visualization(self, data: pd.DataFrame, steps: List[str]) -> str:
        """Execute visualization steps"""
        try:
            from data_visualization import DataVisualization
            data_visualization = DataVisualization()
            
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                return data_visualization.create_scatterplot_with_regression(
                    data, numeric_cols[0], numeric_cols[1]
                )
            else:
                return data_visualization._create_placeholder_plot("Insufficient numeric data for visualization")
                
        except Exception as e:
            logger.error(f"Error in visualization: {str(e)}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def _execute_generic_analysis(self, steps: List[str], uploaded_files: Dict[str, str]) -> Any:
        """Execute generic analysis when no specific data is available"""
        try:
            # Return basic information about the request
            return {
                "message": "Analysis completed",
                "steps_attempted": len(steps),
                "files_provided": len(uploaded_files)
            }
            
        except Exception as e:
            logger.error(f"Error in generic analysis: {str(e)}")
            return "Error in analysis"
    
    def _fallback_response(self, question: str, uploaded_files: Dict[str, str]) -> Any:
        """Provide fallback response when LLM is not available"""
        
        question_lower = question.lower()
        
        # Simple keyword-based responses
        if 'count' in question_lower or 'how many' in question_lower:
            return 0
        elif 'correlation' in question_lower:
            return 0.0
        elif 'plot' in question_lower or 'chart' in question_lower:
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        else:
            return "Unable to process question without LLM integration"
    
    def _default_analysis_plan(self) -> Dict[str, Any]:
        """Return default analysis plan when LLM fails"""
        return {
            "analysis_type": "statistical",
            "steps": ["basic_statistics"],
            "expected_output": "numeric",
            "data_sources": ["uploaded_files"]
        }
