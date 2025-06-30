"""
Logging configuration for BOT CHAIN components.
"""
import logging
import logging.config
import os
import sys
from typing import Dict, Any
import json
from datetime import datetime


def get_logger_config(layer_name: str) -> Dict[str, Any]:
    """Get logging configuration for a specific bot layer."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_format = os.getenv('LOG_FORMAT', 'json')
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'format': '%(message)s'  # Use simple format for now
            },
            'standard': {
                'format': f'%(asctime)s - {layer_name} - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': log_format,
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        },
        'loggers': {
            'bot_chain': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            }
        }
    }
    
    return config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, layer: str = 'unknown'):
        super().__init__()
        self.layer = layer
        self.hostname = os.getenv('HOSTNAME', 'localhost')
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'layer': self.layer,
            'hostname': self.hostname,
            'logger': record.name,
            'message': record.getMessage(),
            'pathname': record.pathname,
            'line': record.lineno,
            'function': record.funcName
        }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'pathname', 'process', 
                          'processName', 'relativeCreated', 'thread', 
                          'threadName', 'getMessage']:
                log_obj[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(layer_name: str) -> logging.Logger:
    """Setup logging for a bot layer."""
    config = get_logger_config(layer_name)
    logging.config.dictConfig(config)
    logger = logging.getLogger(f'bot_chain.{layer_name}')
    
    # Log startup info
    logger.info(f"Logging initialized for {layer_name}", extra={
        'event': 'logging_initialized',
        'python_version': sys.version,
        'log_level': config['root']['level']
    })
    
    return logger


def log_api_call(logger: logging.Logger, method: str, url: str, 
                 status_code: int = None, duration_ms: float = None,
                 error: str = None) -> None:
    """Log API call details."""
    extra = {
        'event': 'api_call',
        'method': method,
        'url': url
    }
    
    if status_code is not None:
        extra['status_code'] = status_code
    if duration_ms is not None:
        extra['duration_ms'] = duration_ms
    if error:
        extra['error'] = error
        logger.error(f"API call failed: {method} {url}", extra=extra)
    else:
        logger.info(f"API call: {method} {url}", extra=extra)


def log_gpt_usage(logger: logging.Logger, model: str, 
                  prompt_tokens: int, completion_tokens: int,
                  total_tokens: int) -> None:
    """Log GPT token usage."""
    logger.info("GPT usage", extra={
        'event': 'gpt_usage',
        'model': model,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens
    })