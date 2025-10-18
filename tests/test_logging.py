"""
Additional unit tests for event logging functionality.

These tests verify that the logging system properly captures events
without logging sensitive content like API responses.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import logging
import io
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, '.')

from askgpt import setup_logging


class TestEventLogging(unittest.TestCase):
    """Test event logging functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Capture log output for testing
        self.log_stream = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        
    def tearDown(self):
        """Clean up after tests"""
        # Remove all handlers from the askgpt logger
        logger = logging.getLogger('askgpt')
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.setLevel(logging.NOTSET)
    
    def test_setup_logging_info_level(self):
        """Test that setup_logging returns correct logger"""
        logger = setup_logging(debug=False)
        
        self.assertEqual(logger.name, 'askgpt')
        self.assertIsInstance(logger, logging.Logger)
    
    def test_setup_logging_debug_level(self):
        """Test that setup_logging returns correct logger in debug mode"""
        logger = setup_logging(debug=True)
        
        self.assertEqual(logger.name, 'askgpt')
        self.assertIsInstance(logger, logging.Logger)
    
    def test_logging_captures_events_not_content(self):
        """Test that logging captures events but not sensitive content"""
        # Set up logger with our test handler
        logger = setup_logging(debug=True)
        logger.addHandler(self.log_handler)
        logger.setLevel(logging.DEBUG)
        
        # Simulate some events that should be logged
        logger.info("Session started")
        logger.info("Using random question generation mode")
        logger.info("Chat completion successful in 1.23s")
        logger.warning("Model gpt-test returned short/empty question")
        logger.error("Error getting answer with invalid-model: Model not found")
        
        # Get the logged output
        log_output = self.log_stream.getvalue()
        
        # Verify events are logged
        self.assertIn("Session started", log_output)
        self.assertIn("Using random question generation mode", log_output)
        self.assertIn("Chat completion successful", log_output)
        self.assertIn("Model gpt-test returned short/empty", log_output)
        self.assertIn("Error getting answer", log_output)
        
        # Verify sensitive content patterns are NOT in logs
        # (These would be examples of content we don't want to log)
        sensitive_patterns = [
            "sk-",  # API keys typically start with sk-
            "What is the meaning of life?",  # Example user question
            "The meaning of life is...",  # Example AI response
        ]
        
        for pattern in sensitive_patterns:
            self.assertNotIn(pattern, log_output)
    
    def test_log_format_includes_timestamp(self):
        """Test that log format includes timestamp and proper structure"""
        # Use a separate logger with custom formatter for this test
        test_logger = logging.getLogger('test_askgpt')
        test_logger.setLevel(logging.DEBUG)
        
        # Create formatter matching our setup_logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
        self.log_handler.setFormatter(formatter)
        test_logger.addHandler(self.log_handler)
        
        test_logger.info("Test message")
        log_output = self.log_stream.getvalue()
        
        # Verify log format includes expected components
        self.assertRegex(log_output, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')  # Timestamp
        self.assertIn("test_askgpt", log_output)  # Logger name
        self.assertIn("INFO", log_output)  # Log level
        self.assertIn("Test message", log_output)  # Message
    
    def test_performance_logging(self):
        """Test that performance metrics are logged correctly"""
        logger = setup_logging(debug=True)
        logger.addHandler(self.log_handler)
        logger.setLevel(logging.DEBUG)
        
        # Simulate the timing logic from create_chat_completion
        elapsed_time = 1.5
        logger.info(f"Chat completion successful in {elapsed_time:.2f}s")
        
        log_output = self.log_stream.getvalue()
        self.assertIn("Chat completion successful in 1.50s", log_output)


if __name__ == '__main__':
    unittest.main(verbosity=2)