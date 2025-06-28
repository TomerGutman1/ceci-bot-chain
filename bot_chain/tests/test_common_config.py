"""
Unit tests for common config module.
"""
import unittest
import os
from unittest.mock import patch, mock_open
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import (
    BotConfig, get_config, load_config_file,
    get_redis_config, get_supabase_config, get_openai_config,
    BOT_CONFIGS
)


class TestBotConfig(unittest.TestCase):
    """Test BotConfig dataclass."""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_SERVICE_KEY': 'test-service-key'
    })
    def test_bot_config_creation(self):
        """Test creating a BotConfig instance."""
        config = BotConfig(
            layer_name='test_bot',
            port=8000,
            model='gpt-4',
            temperature=0.5
        )
        
        self.assertEqual(config.layer_name, 'test_bot')
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.model, 'gpt-4')
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.metrics_port, 9000)  # port + 1000
    
    def test_bot_config_missing_api_key(self):
        """Test BotConfig validation with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as cm:
                BotConfig(layer_name='test', port=8000)
            self.assertIn('OPENAI_API_KEY', str(cm.exception))
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'SUPABASE_URL': '',
        'SUPABASE_SERVICE_KEY': 'test-service-key'
    })
    def test_bot_config_missing_supabase_url(self):
        """Test BotConfig validation with missing Supabase URL."""
        with self.assertRaises(ValueError) as cm:
            BotConfig(layer_name='test', port=8000)
        self.assertIn('SUPABASE_URL', str(cm.exception))


class TestGetConfig(unittest.TestCase):
    """Test get_config function."""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_SERVICE_KEY': 'test-service-key'
    })
    def test_get_config_known_layer(self):
        """Test getting config for a known bot layer."""
        config = get_config('0_MAIN_REWRITE_BOT')
        
        self.assertEqual(config.layer_name, '0_MAIN_REWRITE_BOT')
        self.assertEqual(config.port, 8010)
        self.assertEqual(config.model, 'gpt-3.5-turbo')
    
    def test_get_config_unknown_layer(self):
        """Test getting config for an unknown bot layer."""
        with self.assertRaises(ValueError) as cm:
            get_config('UNKNOWN_BOT')
        self.assertIn('Unknown bot layer', str(cm.exception))
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_SERVICE_KEY': 'test-service-key',
        '0_MAIN_REWRITE_BOT_PORT': '9999',
        '0_MAIN_REWRITE_BOT_MODEL': 'gpt-4',
        '0_MAIN_REWRITE_BOT_TEMPERATURE': '0.8'
    })
    def test_get_config_env_overrides(self):
        """Test environment variable overrides."""
        config = get_config('0_MAIN_REWRITE_BOT')
        
        self.assertEqual(config.port, 9999)
        self.assertEqual(config.model, 'gpt-4')
        self.assertEqual(config.temperature, 0.8)


class TestLoadConfigFile(unittest.TestCase):
    """Test load_config_file function."""
    
    def test_load_config_file_exists(self):
        """Test loading existing config file."""
        mock_config = {'key': 'value', 'number': 42}
        mock_json = str(mock_config).replace("'", '"')
        
        with patch('builtins.open', mock_open(read_data=mock_json)):
            with patch('os.path.exists', return_value=True):
                config = load_config_file('test.json')
                self.assertEqual(config, mock_config)
    
    def test_load_config_file_not_exists(self):
        """Test loading non-existent config file."""
        with patch('os.path.exists', return_value=False):
            config = load_config_file('test.json')
            self.assertEqual(config, {})


class TestRedisConfig(unittest.TestCase):
    """Test Redis configuration."""
    
    def test_get_redis_config_default(self):
        """Test default Redis configuration."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_redis_config()
            
            self.assertEqual(config['host'], 'localhost')
            self.assertEqual(config['port'], 6379)
            self.assertEqual(config['db'], 0)
            self.assertIsNone(config['password'])
    
    @patch.dict(os.environ, {
        'REDIS_URL': 'redis://myhost:7000',
        'REDIS_DB': '2',
        'REDIS_PASSWORD': 'secret'
    })
    def test_get_redis_config_env(self):
        """Test Redis configuration from environment."""
        config = get_redis_config()
        
        self.assertEqual(config['host'], 'myhost')
        self.assertEqual(config['port'], 7000)
        self.assertEqual(config['db'], 2)
        self.assertEqual(config['password'], 'secret')


class TestSupabaseConfig(unittest.TestCase):
    """Test Supabase configuration."""
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_SERVICE_KEY': 'test-key',
        'SUPABASE_JWT_SECRET': 'jwt-secret'
    })
    def test_get_supabase_config(self):
        """Test Supabase configuration."""
        config = get_supabase_config()
        
        self.assertEqual(config['url'], 'https://test.supabase.co')
        self.assertEqual(config['key'], 'test-key')
        self.assertEqual(config['jwt_secret'], 'jwt-secret')
        self.assertEqual(config['schema'], 'public')
        self.assertTrue(config['auto_refresh_token'])


class TestOpenAIConfig(unittest.TestCase):
    """Test OpenAI configuration."""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'sk-test',
        'OPENAI_ORG_ID': 'org-123',
        'OPENAI_MAX_RETRIES': '5',
        'OPENAI_TIMEOUT': '60'
    })
    def test_get_openai_config(self):
        """Test OpenAI configuration."""
        config = get_openai_config('gpt-4')
        
        self.assertEqual(config['api_key'], 'sk-test')
        self.assertEqual(config['organization'], 'org-123')
        self.assertEqual(config['default_model'], 'gpt-4')
        self.assertEqual(config['max_retries'], 5)
        self.assertEqual(config['timeout'], 60)
    
    def test_get_openai_config_defaults(self):
        """Test OpenAI configuration defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_openai_config()
            
            self.assertEqual(config['api_key'], '')
            self.assertIsNone(config['organization'])
            self.assertEqual(config['default_model'], 'gpt-3.5-turbo')
            self.assertEqual(config['max_retries'], 3)
            self.assertEqual(config['timeout'], 30)


class TestBotConfigsConstant(unittest.TestCase):
    """Test BOT_CONFIGS constant."""
    
    def test_all_bot_configs_present(self):
        """Test that all expected bot configs are present."""
        expected_bots = [
            "0_MAIN_REWRITE_BOT",
            "1_MAIN_INTENT_BOT",
            "2Q_QUERY_SQL_GEN_BOT",
            "2X_MAIN_CTX_ROUTER_BOT",
            "2E_EVAL_EVALUATOR_BOT",
            "2C_CLARIFY_CLARIFY_BOT",
            "3Q_QUERY_RANKER_BOT",
            "4_MAIN_FORMATTER"
        ]
        
        for bot_name in expected_bots:
            self.assertIn(bot_name, BOT_CONFIGS)
            self.assertIsInstance(BOT_CONFIGS[bot_name], BotConfig)
    
    def test_formatter_has_no_model(self):
        """Test that formatter has no GPT model."""
        formatter_config = BOT_CONFIGS["4_MAIN_FORMATTER"]
        self.assertEqual(formatter_config.model, "")
        self.assertEqual(formatter_config.max_tokens, 0)


if __name__ == '__main__':
    unittest.main()