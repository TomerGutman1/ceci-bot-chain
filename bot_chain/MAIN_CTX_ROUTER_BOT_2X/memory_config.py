"""
Memory configuration for temporary conversation history.
Implements the specifications from TEMP_BANK_SPEC.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MemoryConfig:
    """Configuration for temporary conversation memory."""
    
    # Maximum number of conversation turns to keep (FIFO)
    max_turns: int = 20
    
    # TTL for conversation history in seconds (2 hours)
    ttl_seconds: int = 2 * 60 * 60
    
    # Redis key prefix for conversation history
    key_prefix: str = "chat"
    
    # Performance target for Redis operations (p95 in ms)
    performance_target_ms: int = 100
    
    # Whether to enable memory functionality
    enabled: bool = True
    
    # Redis connection settings
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Metrics configuration
    metrics_enabled: bool = True
    metrics_prefix: str = "memory"
    
    @classmethod
    def from_env(cls) -> 'MemoryConfig':
        """Create config from environment variables."""
        return cls(
            max_turns=int(os.getenv('MEMORY_MAX_TURNS', '20')),
            ttl_seconds=int(os.getenv('MEMORY_TTL_HOURS', '2')) * 60 * 60,
            key_prefix=os.getenv('MEMORY_KEY_PREFIX', 'chat'),
            performance_target_ms=int(os.getenv('MEMORY_PERF_TARGET_MS', '100')),
            enabled=os.getenv('MEMORY_ENABLED', 'true').lower() == 'true',
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            metrics_enabled=os.getenv('MEMORY_METRICS_ENABLED', 'true').lower() == 'true',
            metrics_prefix=os.getenv('MEMORY_METRICS_PREFIX', 'memory')
        )

# Global memory configuration instance
memory_config = MemoryConfig.from_env()