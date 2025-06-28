"""
Unit tests for common logging module.
"""
import unittest
import json
import logging
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logging import (
    get_logger_config, JSONFormatter, setup_logging, 
    log_api_call, log_gpt_usage
)


class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration."""
    
    def test_get_logger_config_default(self):
        """Test default logger configuration."""
        config = get_logger_config('test_layer')
        
        self.assertEqual(config['version'], 1)
        self.assertFalse(config['disable_existing_loggers'])
        self.assertIn('json', config['formatters'])
        self.assertIn('standard', config['formatters'])
        self.assertIn('console', config['handlers'])
        self.assertEqual(config['root']['level'], 'INFO')
    
    @patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG', 'LOG_FORMAT': 'standard'})
    def test_get_logger_config_env_override(self):
        """Test logger configuration with environment overrides."""
        config = get_logger_config('test_layer')
        
        self.assertEqual(config['root']['level'], 'DEBUG')
        self.assertEqual(config['handlers']['console']['formatter'], 'standard')


class TestJSONFormatter(unittest.TestCase):
    """Test JSON formatter."""
    
    def setUp(self):
        """Set up test logger with JSON formatter."""
        self.formatter = JSONFormatter(layer='test_layer')
        self.logger = logging.getLogger('test')
        self.logger.setLevel(logging.INFO)
        
        # Create a log record
        self.record = self.logger.makeRecord(
            name='test',
            level=logging.INFO,
            fn='test_file.py',
            lno=42,
            msg='Test message',
            args=(),
            exc_info=None,
            func='test_func'
        )
    
    def test_format_basic(self):
        """Test basic JSON formatting."""
        output = self.formatter.format(self.record)
        data = json.loads(output)
        
        self.assertEqual(data['level'], 'INFO')
        self.assertEqual(data['layer'], 'test_layer')
        self.assertEqual(data['message'], 'Test message')
        self.assertEqual(data['line'], 42)
        self.assertEqual(data['function'], 'test_func')
        self.assertIn('timestamp', data)
        self.assertIn('hostname', data)
    
    def test_format_with_extra(self):
        """Test JSON formatting with extra fields."""
        self.record.user_id = '12345'
        self.record.request_id = 'abc-def'
        
        output = self.formatter.format(self.record)
        data = json.loads(output)
        
        self.assertEqual(data['user_id'], '12345')
        self.assertEqual(data['request_id'], 'abc-def')
    
    def test_format_with_exception(self):
        """Test JSON formatting with exception info."""
        try:
            raise ValueError("Test error")
        except ValueError:
            self.record.exc_info = sys.exc_info()
        
        output = self.formatter.format(self.record)
        data = json.loads(output)
        
        self.assertIn('exception', data)
        self.assertIn('ValueError: Test error', data['exception'])


class TestLoggingFunctions(unittest.TestCase):
    """Test logging utility functions."""
    
    def setUp(self):
        """Set up test logger."""
        self.logger = MagicMock()
    
    def test_log_api_call_success(self):
        """Test logging successful API call."""
        log_api_call(
            self.logger, 
            method='GET',
            url='https://api.example.com/test',
            status_code=200,
            duration_ms=150.5
        )
        
        self.logger.info.assert_called_once()
        call_args = self.logger.info.call_args
        self.assertIn('API call: GET https://api.example.com/test', call_args[0])
        
        extra = call_args[1]['extra']
        self.assertEqual(extra['event'], 'api_call')
        self.assertEqual(extra['method'], 'GET')
        self.assertEqual(extra['status_code'], 200)
        self.assertEqual(extra['duration_ms'], 150.5)
    
    def test_log_api_call_error(self):
        """Test logging failed API call."""
        log_api_call(
            self.logger,
            method='POST',
            url='https://api.example.com/test',
            error='Connection timeout'
        )
        
        self.logger.error.assert_called_once()
        call_args = self.logger.error.call_args
        self.assertIn('API call failed: POST https://api.example.com/test', call_args[0])
        
        extra = call_args[1]['extra']
        self.assertEqual(extra['error'], 'Connection timeout')
    
    def test_log_gpt_usage(self):
        """Test logging GPT token usage."""
        log_gpt_usage(
            self.logger,
            model='gpt-4-turbo',
            prompt_tokens=150,
            completion_tokens=80,
            total_tokens=230
        )
        
        self.logger.info.assert_called_once()
        call_args = self.logger.info.call_args
        self.assertEqual(call_args[0][0], 'GPT usage')
        
        extra = call_args[1]['extra']
        self.assertEqual(extra['event'], 'gpt_usage')
        self.assertEqual(extra['model'], 'gpt-4-turbo')
        self.assertEqual(extra['prompt_tokens'], 150)
        self.assertEqual(extra['completion_tokens'], 80)
        self.assertEqual(extra['total_tokens'], 230)


class TestSetupLogging(unittest.TestCase):
    """Test logging setup."""
    
    @patch('logging.config.dictConfig')
    def test_setup_logging(self, mock_dict_config):
        """Test setting up logging for a layer."""
        logger = setup_logging('test_layer')
        
        mock_dict_config.assert_called_once()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, 'bot_chain.test_layer')


if __name__ == '__main__':
    unittest.main()