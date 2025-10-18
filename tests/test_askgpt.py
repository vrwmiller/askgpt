#!/usr/bin/env python3
"""
Unit tests for askgpt - A command line interface to ChatGPT

To run the tests:
    python3 -m pytest test_askgpt.py -v
    python3 -m pytest test_askgpt.py --cov=askgpt --cov-report=html
"""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, '.')

# Import the functions we want to test
from askgpt import (
    uses_max_completion_tokens,
    supports_custom_temperature,
    create_chat_completion,
    generate_question,
    get_answer,
    fetch_available_models,
    get_openai_client,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    FALLBACK_MODELS
)


class TestModelCompatibility(unittest.TestCase):
    """Test model compatibility detection functions"""
    
    def test_uses_max_completion_tokens_newer_models(self):
        """Test that newer models are correctly identified as using max_completion_tokens"""
        newer_models = ["gpt-5", "gpt-4o", "o1-mini", "o3-mini", "gpt-4.1"]
        
        for model in newer_models:
            with self.subTest(model=model):
                self.assertTrue(uses_max_completion_tokens(model))
    
    def test_uses_max_completion_tokens_older_models(self):
        """Test that older models are correctly identified as using max_tokens"""
        older_models = ["gpt-3.5-turbo", "gpt-4", "davinci-002"]
        
        for model in older_models:
            with self.subTest(model=model):
                self.assertFalse(uses_max_completion_tokens(model))
    
    def test_supports_custom_temperature_restricted_models(self):
        """Test that restricted models correctly report no custom temperature support"""
        restricted_models = ["gpt-5", "o1-mini", "o3-mini"]
        
        for model in restricted_models:
            with self.subTest(model=model):
                self.assertFalse(supports_custom_temperature(model))
    
    def test_supports_custom_temperature_flexible_models(self):
        """Test that flexible models correctly report custom temperature support"""
        flexible_models = ["gpt-4o", "gpt-3.5-turbo", "gpt-4"]
        
        for model in flexible_models:
            with self.subTest(model=model):
                self.assertTrue(supports_custom_temperature(model))


class TestAPIIntegration(unittest.TestCase):
    """Test OpenAI API integration"""
    
    @patch('askgpt.OpenAI')
    def test_get_openai_client_success(self, mock_openai):
        """Test successful OpenAI client creation with valid API key"""
        test_key = 'test-api-key-12345'
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}):
            client = get_openai_client()
            mock_openai.assert_called_once_with(api_key=test_key)
    
    def test_get_openai_client_missing_key(self):
        """Test that missing API key raises SystemExit"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                get_openai_client()
            self.assertEqual(cm.exception.code, 1)
    
    @patch('askgpt.OpenAI')
    def test_fetch_available_models_success(self, mock_openai):
        """Test successful model fetching from API"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_models = [Mock(id="gpt-4o"), Mock(id="gpt-5")]
        mock_client.models.list.return_value = mock_models
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            models = fetch_available_models()
            expected_models = ["gpt-4o", "gpt-5"]
            self.assertEqual(models, expected_models)
    
    @patch('askgpt.OpenAI')
    def test_create_chat_completion_newer_model(self, mock_openai):
        """Test chat completion creation with newer model parameters"""
        mock_client = Mock()
        mock_response = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        messages = [{"role": "user", "content": "test"}]
        create_chat_completion(mock_client, "gpt-5", messages, 100, 0.8)
        
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args['model'], "gpt-5")
        self.assertEqual(call_args['max_completion_tokens'], 100)
        self.assertNotIn('temperature', call_args)  # gpt-5 doesn't support custom temperature


class TestQuestionGeneration(unittest.TestCase):
    """Test question generation functionality"""
    
    def _create_mock_response(self, content):
        """Helper method to create properly structured mock response"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = content
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response
    
    @patch('askgpt.create_chat_completion')
    def test_generate_random_question_success(self, mock_completion):
        """Test successful random question generation"""
        # Create proper mock response structure
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "What is the meaning of life?"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response
        
        mock_client = Mock()
        question, model = generate_question(mock_client, model="gpt-4o", max_tokens=100)
        
        self.assertEqual(question, "What is the meaning of life?")
        self.assertEqual(model, "gpt-4o")
    
    @patch('askgpt.create_chat_completion')
    def test_generate_topic_question_success(self, mock_completion):
        """Test successful topic-specific question generation"""
        # Create proper mock response structure
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "How does AI impact society?"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response
        
        mock_client = Mock()
        question, model = generate_question(
            mock_client, 
            topic="artificial intelligence", 
            model="gpt-4o"
        )
        
        self.assertEqual(question, "How does AI impact society?")
        self.assertEqual(model, "gpt-4o")
        
        # Verify the prompt includes the topic
        call_args = mock_completion.call_args
        prompt = call_args[1]['messages'][0]['content']
        self.assertIn("artificial intelligence", prompt)
    
    @patch('askgpt.create_chat_completion')
    def test_generate_question_with_fallback(self, mock_completion):
        """Test question generation with model fallback"""
        # First attempt fails, second succeeds
        mock_completion.side_effect = [
            Exception("Model not available"),
            self._create_mock_response("What are the implications of quantum computing?")
        ]
        
        mock_client = Mock()
        question, model = generate_question(mock_client, model="invalid-model")
        
        self.assertEqual(question, "What are the implications of quantum computing?")
        # Should fallback to gpt-5 (first in FALLBACK_MODELS list)
        self.assertEqual(model, "gpt-5")


class TestAnswerGeneration(unittest.TestCase):
    """Test answer generation functionality"""
    
    def _create_mock_response(self, content):
        """Helper method to create properly structured mock response"""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = content
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response
    
    @patch('askgpt.create_chat_completion')
    def test_get_answer_success(self, mock_completion):
        """Test successful answer generation"""
        # Create proper mock response structure
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "This is a comprehensive answer."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response
        
        mock_client = Mock()
        answer, model = get_answer(mock_client, "What is ML?", model="gpt-4o")
        
        self.assertEqual(answer, "This is a comprehensive answer.")
        self.assertEqual(model, "gpt-4o")
    
    @patch('askgpt.create_chat_completion')
    def test_get_answer_with_model_fallback(self, mock_completion):
        """Test answer generation with model fallback"""
        # First attempt fails, second succeeds
        mock_completion.side_effect = [
            Exception("Model not found"),
            self._create_mock_response("Fallback answer")
        ]
        
        mock_client = Mock()
        answer, model = get_answer(mock_client, "Test question", model="invalid-model")
        
        self.assertEqual(answer, "Fallback answer")
        # Should fallback to gpt-5 (first in FALLBACK_MODELS list)
        self.assertEqual(model, "gpt-5")


class TestConfiguration(unittest.TestCase):
    """Test configuration and constants"""
    
    def test_default_values(self):
        """Test that default configuration values are correct"""
        self.assertEqual(DEFAULT_MODEL, "gpt-5")
        self.assertEqual(DEFAULT_MAX_TOKENS, 512)
        self.assertIsInstance(FALLBACK_MODELS, list)
        self.assertIn("gpt-5", FALLBACK_MODELS)


if __name__ == '__main__':
    unittest.main(verbosity=2)