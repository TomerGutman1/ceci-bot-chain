"""
Configuration management for BOT CHAIN components.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class BotConfig:
    """Configuration for a bot layer."""
    layer_name: str
    port: int
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.3
    max_tokens: int = 1000
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # API Keys and URLs
    openai_api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    supabase_url: str = field(default_factory=lambda: os.getenv('SUPABASE_URL', ''))
    supabase_key: str = field(default_factory=lambda: os.getenv('SUPABASE_SERVICE_KEY', ''))
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379'))
    
    # Health check
    health_check_interval: int = 30
    
    # Metrics
    metrics_enabled: bool = True
    metrics_port: Optional[int] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.supabase_key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable is required")
        
        # Set metrics port if not specified
        if self.metrics_port is None:
            self.metrics_port = self.port + 1000


# Bot layer configurations
BOT_CONFIGS = {
    "UNIFIED_INTENT_BOT_1": BotConfig(
        layer_name="UNIFIED_INTENT_BOT_1",
        port=8011,
        model="gpt-4o",
        temperature=0.3,
        max_tokens=1000
    ),
    "QUERY_SQL_GEN_BOT_2Q": BotConfig(
        layer_name="QUERY_SQL_GEN_BOT_2Q",
        port=8012,
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=1000
    ),
    "MAIN_CTX_ROUTER_BOT_2X": BotConfig(
        layer_name="MAIN_CTX_ROUTER_BOT_2X",
        port=8013,
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=500
    ),
    "EVAL_EVALUATOR_BOT_2E": BotConfig(
        layer_name="EVAL_EVALUATOR_BOT_2E",
        port=8014,
        model="gpt-4-turbo",
        temperature=0.3,
        max_tokens=1000
    ),
    "CLARIFY_CLARIFY_BOT_2C": BotConfig(
        layer_name="CLARIFY_CLARIFY_BOT_2C",
        port=8015,
        model="gpt-3.5-turbo",
        temperature=0.5,
        max_tokens=200
    ),
    "QUERY_RANKER_BOT_3Q": BotConfig(
        layer_name="QUERY_RANKER_BOT_3Q",
        port=8016,
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=800
    ),
    "LLM_FORMATTER_BOT_4": BotConfig(
        layer_name="LLM_FORMATTER_BOT_4",
        port=8017,
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=1000
    )
}


def get_config(layer_name: str) -> BotConfig:
    """Get configuration for a specific bot layer."""
    if layer_name not in BOT_CONFIGS:
        raise ValueError(f"Unknown bot layer: {layer_name}")
    
    config = BOT_CONFIGS[layer_name]
    
    # Override with environment variables if present
    env_overrides = {
        'port': f'{layer_name}_PORT',
        'model': f'{layer_name}_MODEL',
        'temperature': f'{layer_name}_TEMPERATURE',
        'max_tokens': f'{layer_name}_MAX_TOKENS',
        'timeout': f'{layer_name}_TIMEOUT',
        'retry_count': f'{layer_name}_RETRY_COUNT',
        'retry_delay': f'{layer_name}_RETRY_DELAY'
    }
    
    for attr, env_var in env_overrides.items():
        env_value = os.getenv(env_var)
        if env_value:
            attr_type = type(getattr(config, attr))
            if attr_type == bool:
                setattr(config, attr, env_value.lower() in ['true', '1', 'yes'])
            else:
                setattr(config, attr, attr_type(env_value))
    
    return config


def load_config_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration."""
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Parse Redis URL
    if redis_url.startswith('redis://'):
        parts = redis_url.replace('redis://', '').split(':')
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 6379
    else:
        host = 'localhost'
        port = 6379
    
    return {
        'host': host,
        'port': port,
        'db': int(os.getenv('REDIS_DB', '0')),
        'password': os.getenv('REDIS_PASSWORD'),
        'decode_responses': True,
        'socket_timeout': 5,
        'socket_connect_timeout': 5,
        'retry_on_timeout': True
    }


def get_supabase_config() -> Dict[str, Any]:
    """Get Supabase configuration."""
    return {
        'url': os.getenv('SUPABASE_URL', ''),
        'key': os.getenv('SUPABASE_SERVICE_KEY', ''),
        'jwt_secret': os.getenv('SUPABASE_JWT_SECRET', ''),
        'schema': 'public',
        'auto_refresh_token': True,
        'persist_session': True,
        'local_storage': False
    }


def get_openai_config(model: str = None) -> Dict[str, Any]:
    """Get OpenAI configuration."""
    return {
        'api_key': os.getenv('OPENAI_API_KEY', ''),
        'organization': os.getenv('OPENAI_ORG_ID'),
        'default_model': model or 'gpt-3.5-turbo',
        'max_retries': int(os.getenv('OPENAI_MAX_RETRIES', '3')),
        'timeout': int(os.getenv('OPENAI_TIMEOUT', '30')),
        'base_url': os.getenv('OPENAI_BASE_URL')  # For Azure OpenAI or custom endpoints
    }