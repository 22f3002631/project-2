import unittest
import json
import tempfile
import os
from io import BytesIO
from app import app
import logging

# Disable logging during tests
logging.disable(logging.CRITICAL)

class TestDataAnalystAgent(unittest.TestCase):
    """Test cases for the Data Analyst Agent API"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_missing_questions_file(self):
        """Test API with missing questions.txt file"""
        response = self.app.post('/api/')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_empty_request(self):
        """Test API with no files"""
        response = self.app.post('/api/', data={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_wikipedia_questions(self):
        """Test Wikipedia scraping questions"""
        questions_content = """
        Scrape the list of highest grossing films from Wikipedia. It is at the URL:
        https://en.wikipedia.org/wiki/List_of_highest-grossing_films
        
        Answer the following questions and respond with a JSON array of strings containing the answer.
        
        1. How many $2 bn movies were released before 2000?
        2. Which is the earliest film that grossed over $1.5 bn?
        3. What's the correlation between the Rank and Peak?
        4. Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.
        """
        
        data = {
            'questions.txt': (BytesIO(questions_content.encode()), 'questions.txt')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        
        # Check response types
        self.assertIsInstance(result[0], int)  # Count
        self.assertIsInstance(result[1], str)  # Movie title
        self.assertIsInstance(result[2], (int, float))  # Correlation
        self.assertIsInstance(result[3], str)  # Base64 image
        self.assertTrue(result[3].startswith('data:image/'))
    
    def test_database_questions(self):
        """Test database analysis questions"""
        questions_content = """
        The Indian high court judgement dataset contains judgements from the Indian High Courts.
        
        Answer the following questions and respond with a JSON object containing the answer.
        
        {
          "Which high court disposed the most cases from 2019 - 2022?": "...",
          "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": "...",
          "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters": "data:image/webp:base64,..."
        }
        """
        
        data = {
            'questions.txt': (BytesIO(questions_content.encode()), 'questions.txt')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertIsInstance(result, dict)
    
    def test_csv_file_analysis(self):
        """Test analysis with uploaded CSV file"""
        questions_content = "Analyze the uploaded CSV file and provide basic statistics."
        
        # Create a sample CSV
        csv_content = "Name,Age,Score\nAlice,25,85\nBob,30,92\nCharlie,35,78"
        
        data = {
            'questions.txt': (BytesIO(questions_content.encode()), 'questions.txt'),
            'data.csv': (BytesIO(csv_content.encode()), 'data.csv')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        # Should return some analysis result
        result = json.loads(response.data)
        self.assertIsNotNone(result)
    
    def test_large_file_rejection(self):
        """Test that large files are rejected"""
        questions_content = "Analyze the data."
        
        # Create a large file (simulate)
        large_content = "x" * (60 * 1024 * 1024)  # 60MB
        
        data = {
            'questions.txt': (BytesIO(questions_content.encode()), 'questions.txt'),
            'large_file.txt': (BytesIO(large_content.encode()), 'large_file.txt')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        # Should still process but skip the large file
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_utf8_questions(self):
        """Test handling of invalid UTF-8 in questions file"""
        invalid_content = b'\xff\xfe\x00\x00'  # Invalid UTF-8
        
        data = {
            'questions.txt': (BytesIO(invalid_content), 'questions.txt')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('UTF-8', result['error'])
    
    def test_empty_questions_file(self):
        """Test handling of empty questions file"""
        data = {
            'questions.txt': (BytesIO(b''), 'questions.txt')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('empty', result['error'])
    
    def test_json_serialization(self):
        """Test that responses are JSON serializable"""
        questions_content = "What is 2 + 2?"
        
        data = {
            'questions.txt': (BytesIO(questions_content.encode()), 'questions.txt')
        }
        
        response = self.app.post('/api/', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        # Should be able to parse as JSON
        result = json.loads(response.data)
        self.assertIsNotNone(result)
        
        # Should be able to serialize back to JSON
        json.dumps(result)


class TestDataModules(unittest.TestCase):
    """Test individual data processing modules"""
    
    def test_data_sourcing_import(self):
        """Test that data sourcing module can be imported"""
        from data_sourcing import DataSourcing
        ds = DataSourcing()
        self.assertIsNotNone(ds)
    
    def test_data_analysis_import(self):
        """Test that data analysis module can be imported"""
        from data_analysis import DataAnalysis
        da = DataAnalysis()
        self.assertIsNotNone(da)
    
    def test_data_visualization_import(self):
        """Test that data visualization module can be imported"""
        from data_visualization import DataVisualization
        dv = DataVisualization()
        self.assertIsNotNone(dv)
    
    def test_question_processor_import(self):
        """Test that question processor module can be imported"""
        from question_processor import QuestionProcessor
        qp = QuestionProcessor()
        self.assertIsNotNone(qp)
    
    def test_llm_integration_import(self):
        """Test that LLM integration module can be imported"""
        from llm_integration import LLMIntegration
        llm = LLMIntegration()
        self.assertIsNotNone(llm)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
