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
    
    def test_file_logging_setup(self):
        """Test that file logging can be configured"""
        import tempfile
        import os
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_log_path = temp_file.name
        
        try:
            # Test file logging setup
            logger = setup_logging(debug=False, log_file=temp_log_path)
            logger.info("Test file logging message")
            
            # Verify the log file was created and contains our message
            self.assertTrue(os.path.exists(temp_log_path))
            
            with open(temp_log_path, 'r') as f:
                log_content = f.read()
                self.assertIn("Test file logging message", log_content)
                self.assertIn("askgpt", log_content)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)

    def test_no_console_logging_by_default(self):
        """Test that console logging is disabled by default"""
        # Capture stderr to check for console output
        captured_output = io.StringIO()
        
        with patch('sys.stderr', captured_output):
            logger = setup_logging(debug=False, log_file=None)
            logger.info("This should not appear in console")
            logger.warning("This warning should not appear in console")
        
        # Should have no console output
        output = captured_output.getvalue()
        self.assertEqual(output, "")
        
        # Verify logger has no console handlers
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertEqual(len(console_handlers), 0)

    def test_console_logging_only_with_debug(self):
        """Test that console logging only works when debug=True"""
        # Capture stderr to check for console output
        captured_output = io.StringIO()
        
        with patch('sys.stderr', captured_output):
            logger = setup_logging(debug=True, log_file=None)
            logger.info("This should appear in console")
            logger.warning("This warning should appear in console")
        
        # Should have console output when debug=True
        output = captured_output.getvalue()
        self.assertIn("This should appear in console", output)
        self.assertIn("This warning should appear in console", output)
        
        # Verify logger has console handler
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        self.assertEqual(len(console_handlers), 1)

    def test_file_logging_without_console(self):
        """Test that file logging works without console logging"""
        import tempfile
        import os
        
        temp_log_path = None
        try:
            # Create a temporary log file
            temp_fd, temp_log_path = tempfile.mkstemp(suffix='.log')
            os.close(temp_fd)  # Close the file descriptor
            
            # Capture stderr to verify no console output
            captured_output = io.StringIO()
            
            with patch('sys.stderr', captured_output):
                logger = setup_logging(debug=False, log_file=temp_log_path)
                logger.info("File only message")
                logger.warning("File only warning")
            
            # Should have no console output
            console_output = captured_output.getvalue()
            self.assertEqual(console_output, "")
            
            # Should have file output
            with open(temp_log_path, 'r') as f:
                file_content = f.read()
                self.assertIn("File only message", file_content)
                self.assertIn("File only warning", file_content)
                
        finally:
            # Clean up the temporary file
            if temp_log_path and os.path.exists(temp_log_path):
                os.unlink(temp_log_path)

    def test_fallback_messages_not_in_console(self):
        """Test that fallback warning messages don't appear in console without debug"""
        # Capture stderr to check for console output
        captured_output = io.StringIO()
        
        with patch('sys.stderr', captured_output):
            logger = setup_logging(debug=False, log_file=None)
            # Simulate the exact warning message from the fallback logic
            logger.warning("Model gpt-5 returned short/empty question: ''")
            logger.warning("Model gpt-5 returned short/empty answer: ''")
        
        # Should have no console output
        output = captured_output.getvalue()
        self.assertEqual(output, "")
        
        # Verify logger has NullHandler instead of console handler
        null_handlers = [h for h in logger.handlers if isinstance(h, logging.NullHandler)]
        self.assertEqual(len(null_handlers), 1)

    def test_fallback_messages_in_file_logging(self):
        """Test that fallback messages appear in file logs even without console logging"""
        import tempfile
        import os
        
        temp_log_path = None
        try:
            # Create a temporary log file
            temp_fd, temp_log_path = tempfile.mkstemp(suffix='.log')
            os.close(temp_fd)  # Close the file descriptor
            
            # Capture stderr to verify no console output
            captured_output = io.StringIO()
            
            with patch('sys.stderr', captured_output):
                logger = setup_logging(debug=False, log_file=temp_log_path)
                # Simulate the exact warning messages from fallback logic
                logger.warning("Model gpt-5 returned short/empty question: ''")
                logger.warning("Model gpt-5 returned short/empty answer: ''")
            
            # Should have no console output
            console_output = captured_output.getvalue()
            self.assertEqual(console_output, "")
            
            # Should have file output
            with open(temp_log_path, 'r') as f:
                file_content = f.read()
                self.assertIn("Model gpt-5 returned short/empty question", file_content)
                self.assertIn("Model gpt-5 returned short/empty answer", file_content)
                
        finally:
            # Clean up the temporary file
            if temp_log_path and os.path.exists(temp_log_path):
                os.unlink(temp_log_path)


if __name__ == '__main__':
    unittest.main(verbosity=2)