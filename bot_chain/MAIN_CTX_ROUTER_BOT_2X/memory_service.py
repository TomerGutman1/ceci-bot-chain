"""
Temporary conversation memory service for CECI Bot Chain.
Implements Redis-based conversation history storage with TTL.
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from uuid import uuid4

import redis
from memory_config import memory_config


@dataclass
class ConversationTurn:
    """Single conversation turn data structure."""
    turn_id: str
    speaker: str  # "user" or "bot"
    clean_text: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create from dictionary."""
        return cls(**data)


class ConversationMemory:
    """Manages temporary conversation history in Redis."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize memory service with Redis client."""
        self.config = memory_config
        self.redis_client = redis_client
        self.metrics = {
            'reads_total': 0,
            'writes_total': 0,
            'cache_misses': 0,
            'errors': 0
        }
        
        if not self.redis_client:
            self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            if self.config.enabled:
                print(f"Warning: Redis connection failed: {e}")
            self.redis_client = None
    
    def _get_key(self, conv_id: str) -> str:
        """Generate Redis key for conversation."""
        return f"{self.config.key_prefix}:{conv_id}:history"
    
    def _safe_redis_operation(self, operation_name: str, func):
        """Execute Redis operation with error handling."""
        if not self.config.enabled or not self.redis_client:
            return None
        
        start_time = time.time()
        try:
            result = func()
            
            # Track performance
            duration_ms = (time.time() - start_time) * 1000
            if duration_ms > self.config.performance_target_ms:
                print(f"Warning: {operation_name} took {duration_ms:.1f}ms (target: {self.config.performance_target_ms}ms)")
            
            return result
        except Exception as e:
            self.metrics['errors'] += 1
            print(f"Redis operation {operation_name} failed: {e}")
            return None
    
    def append(self, conv_id: str, turn_data: Dict[str, Any]) -> bool:
        """
        Append a new turn to conversation history.
        
        Args:
            conv_id: Conversation ID
            turn_data: Dictionary with turn_id, speaker, clean_text, timestamp
            
        Returns:
            True if successful, False otherwise
        """
        if not self.config.enabled:
            return True  # No-op when disabled
        
        def _append_operation():
            key = self._get_key(conv_id)
            
            # Create turn object
            turn = ConversationTurn(
                turn_id=turn_data.get('turn_id', str(uuid4())),
                speaker=turn_data['speaker'],
                clean_text=turn_data['clean_text'],
                timestamp=turn_data.get('timestamp', datetime.utcnow().isoformat())
            )
            
            # Serialize turn
            turn_json = json.dumps(turn.to_dict())
            
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Add to list (RPUSH for FIFO)
            pipe.rpush(key, turn_json)
            
            # Trim to max_turns (keep last N elements)
            pipe.ltrim(key, -self.config.max_turns, -1)
            
            # Set TTL (refresh on each write)
            pipe.expire(key, self.config.ttl_seconds)
            
            # Execute pipeline
            pipe.execute()
            
            self.metrics['writes_total'] += 1
            return True
        
        result = self._safe_redis_operation("append", _append_operation)
        return result is not None
    
    def fetch(self, conv_id: str) -> List[Dict[str, Any]]:
        """
        Fetch conversation history for a conversation ID.
        
        Args:
            conv_id: Conversation ID
            
        Returns:
            List of conversation turns (last 20 turns)
        """
        if not self.config.enabled:
            return []
        
        def _fetch_operation():
            key = self._get_key(conv_id)
            
            # Get last 20 turns using LRANGE
            turn_data = self.redis_client.lrange(key, -self.config.max_turns, -1)
            
            if not turn_data:
                self.metrics['cache_misses'] += 1
                return []
            
            # Parse turns
            turns = []
            for turn_json in turn_data:
                try:
                    turn_dict = json.loads(turn_json)
                    turns.append(turn_dict)
                except json.JSONDecodeError:
                    continue
            
            # Refresh TTL on read
            self.redis_client.expire(key, self.config.ttl_seconds)
            
            self.metrics['reads_total'] += 1
            return turns
        
        result = self._safe_redis_operation("fetch", _fetch_operation)
        return result if result is not None else []
    
    def clear(self, conv_id: str) -> bool:
        """Clear conversation history for a conversation ID."""
        if not self.config.enabled:
            return True
        
        def _clear_operation():
            key = self._get_key(conv_id)
            return self.redis_client.delete(key) > 0
        
        result = self._safe_redis_operation("clear", _clear_operation)
        return result is not None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get memory service metrics."""
        return {
            f"{self.config.metrics_prefix}_reads_total": self.metrics['reads_total'],
            f"{self.config.metrics_prefix}_writes_total": self.metrics['writes_total'],
            f"{self.config.metrics_prefix}_cache_misses": self.metrics['cache_misses'],
            f"{self.config.metrics_prefix}_errors": self.metrics['errors'],
            "redis_connected": self.redis_client is not None,
            "memory_enabled": self.config.enabled
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on memory service."""
        if not self.config.enabled:
            return {"status": "disabled", "redis_connected": False}
        
        if not self.redis_client:
            return {"status": "error", "redis_connected": False, "error": "No Redis connection"}
        
        try:
            # Test Redis connection
            response = self.redis_client.ping()
            
            # Get Redis info
            info = self.redis_client.info()
            
            return {
                "status": "ok",
                "redis_connected": True,
                "redis_ping": response,
                "redis_memory_used": info.get("used_memory_human", "unknown"),
                "conversation_keys": len(self.redis_client.keys(f"{self.config.key_prefix}:*:history"))
            }
        except Exception as e:
            return {
                "status": "error",
                "redis_connected": False,
                "error": str(e)
            }


# Global memory service instance
memory_service = ConversationMemory()