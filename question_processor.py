import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class QuestionProcessor:
    """Processes and parses natural language questions to determine analysis requirements"""
    
    def __init__(self):
        self.wikipedia_patterns = [
            r'scrape.*wikipedia',
            r'wikipedia.*url',
            r'list.*highest.*grossing.*films'
        ]
        
        self.database_patterns = [
            r'duckdb',
            r'indian.*high.*court',
            r'judgments?.*dataset',
            r'parquet.*files?'
        ]

        self.network_patterns = [
            r'network',
            r'edges\.csv',
            r'undirected.*network',
            r'degree',
            r'shortest.*path',
            r'network.*density',
            r'network.*graph'
        ]
        
        self.analysis_patterns = {
            'count': [r'how many', r'count', r'number of'],
            'correlation': [r'correlation', r'relationship between'],
            'regression': [r'regression', r'slope', r'trend'],
            'earliest': [r'earliest', r'first', r'oldest'],
            'latest': [r'latest', r'most recent', r'newest'],
            'plot': [r'plot', r'chart', r'graph', r'scatterplot', r'visualization']
        }
    
    def parse_questions(self, questions_content: str) -> List[Dict[str, Any]]:
        """Parse questions content and return structured question data"""
        try:
            # Clean the content
            content = questions_content.strip()
            
            # Check if it's the Wikipedia example
            if self._is_wikipedia_question(content):
                return self._parse_wikipedia_questions(content)

            # Check if it's the database example
            elif self._is_database_question(content):
                return self._parse_database_questions(content)

            # Check if it's a network analysis question
            elif self._is_network_question(content):
                return self._parse_network_questions(content)

            # Generic question parsing
            else:
                return self._parse_generic_questions(content)
                
        except Exception as e:
            logger.error(f"Error parsing questions: {str(e)}")
            return [{'type': 'generic', 'text': questions_content}]
    
    def _is_wikipedia_question(self, content: str) -> bool:
        """Check if this is a Wikipedia scraping question"""
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in self.wikipedia_patterns)
    
    def _is_database_question(self, content: str) -> bool:
        """Check if this is a database analysis question"""
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in self.database_patterns)
    
    def _parse_wikipedia_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse Wikipedia scraping questions"""
        try:
            # Extract URL
            url_match = re.search(r'https?://[^\s]+', content)
            url = url_match.group(0) if url_match else 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films'
            
            # Extract numbered questions
            questions = re.findall(r'\d+\.\s*([^?\n]+\??)', content)
            
            return [{
                'type': 'wikipedia_scraping',
                'url': url,
                'sub_questions': questions,
                'text': content
            }]
            
        except Exception as e:
            logger.error(f"Error parsing Wikipedia questions: {str(e)}")
            return [{'type': 'wikipedia_scraping', 'url': 'https://en.wikipedia.org/wiki/List_of_highest-grossing_films', 'text': content}]
    
    def _parse_database_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse database analysis questions"""
        try:
            # Look for JSON structure in the content
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            
            questions_dict = {}
            if json_match:
                try:
                    questions_dict = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            return [{
                'type': 'database_analysis',
                'questions': questions_dict,
                'text': content
            }]
            
        except Exception as e:
            logger.error(f"Error parsing database questions: {str(e)}")
            return [{'type': 'database_analysis', 'text': content}]
    
    def _parse_generic_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse generic questions"""
        try:
            # Split by question marks or numbered items
            questions = re.split(r'[?\n]\s*(?=\d+\.|\w)', content)
            questions = [q.strip() for q in questions if q.strip()]
            
            parsed_questions = []
            for question in questions:
                question_type = self._classify_question(question)
                parsed_questions.append({
                    'type': question_type,
                    'text': question,
                    'analysis_type': self._get_analysis_type(question)
                })
            
            return parsed_questions if parsed_questions else [{'type': 'generic', 'text': content}]
            
        except Exception as e:
            logger.error(f"Error parsing generic questions: {str(e)}")
            return [{'type': 'generic', 'text': content}]
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of question"""
        question_lower = question.lower()
        
        if any(re.search(pattern, question_lower) for pattern in self.wikipedia_patterns):
            return 'wikipedia_scraping'
        elif any(re.search(pattern, question_lower) for pattern in self.database_patterns):
            return 'database_analysis'
        elif 'csv' in question_lower or 'data' in question_lower:
            return 'file_analysis'
        else:
            return 'generic'
    
    def _get_analysis_type(self, question: str) -> List[str]:
        """Determine what type of analysis is needed"""
        question_lower = question.lower()
        analysis_types = []
        
        for analysis_type, patterns in self.analysis_patterns.items():
            if any(re.search(pattern, question_lower) for pattern in patterns):
                analysis_types.append(analysis_type)
        
        return analysis_types if analysis_types else ['general']
    
    def extract_parameters(self, question: str) -> Dict[str, Any]:
        """Extract specific parameters from questions"""
        params = {}
        
        # Extract years
        years = re.findall(r'\b(19|20)\d{2}\b', question)
        if years:
            params['years'] = [int(year) for year in years]
        
        # Extract monetary amounts
        money_patterns = [
            r'\$(\d+(?:\.\d+)?)\s*bn',
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'(\d+(?:\.\d+)?)\s*billion'
        ]
        
        for pattern in money_patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                params['amounts'] = [float(match) for match in matches]
                break
        
        # Extract column names (common patterns)
        column_patterns = [
            r'between\s+(\w+)\s+and\s+(\w+)',
            r'correlation.*?(\w+).*?(\w+)',
            r'plot.*?(\w+).*?(\w+)'
        ]
        
        for pattern in column_patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                params['columns'] = list(match.groups())
                break
        
        return params
    
    def is_visualization_required(self, question: str) -> bool:
        """Check if the question requires visualization"""
        question_lower = question.lower()
        viz_keywords = ['plot', 'chart', 'graph', 'scatterplot', 'visualization', 'draw']
        return any(keyword in question_lower for keyword in viz_keywords)
    
    def get_expected_response_format(self, questions: List[Dict[str, Any]]) -> str:
        """Determine expected response format based on questions"""
        
        # Check if it's the Wikipedia example (expects array)
        if any(q.get('type') == 'wikipedia_scraping' for q in questions):
            return 'array'
        
        # Check if it's the database example (expects object)
        if any(q.get('type') == 'database_analysis' for q in questions):
            return 'object'
        
        # Default to array for multiple questions, single value for one question
        return 'array' if len(questions) > 1 else 'single'

    def _is_network_question(self, content: str) -> bool:
        """Check if the content contains network analysis questions"""
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in self.network_patterns)

    def _parse_network_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse network analysis questions"""
        questions = []

        # This is a network analysis question
        questions.append({
            'type': 'network_analysis',
            'content': content,
            'data_source': 'edges.csv',
            'analysis_type': 'network_metrics',
            'visualization_required': True,
            'expected_format': 'object'
        })

        return questions
