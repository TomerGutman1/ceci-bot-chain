"""
Redis Session Store for CECI-AI
Manages session persistence in Redis for production environment
"""

import os
import json
import redis
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)

class RedisSessionStore:
    """Redis-backed session storage for production"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection"""
        # Get Redis URL from environment or use default
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        
        try:
            # Connect to Redis using URL
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=False,  # We'll handle encoding/decoding ourselves
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis at {self._safe_redis_url()}")
            self.connected = True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {self._safe_redis_url()}: {e}")
            logger.warning("Session management will fall back to in-memory storage")
            self.redis_client = None
            self.connected = False
    
    def _safe_redis_url(self) -> str:
        """Return Redis URL with password masked"""
        if '@' in self.redis_url:
            # Mask password in URL for logging
            parts = self.redis_url.split('@')
            prefix = parts[0].split('//')[0] + '//'
            if ':' in parts[0].split('//')[-1]:
                user_pass = parts[0].split('//')[-1]
                user = user_pass.split(':')[0]
                masked = f"{prefix}{user}:****@{parts[1]}"
                return masked
        return self.redis_url
    
    def is_connected(self) -> bool:
        """Check if Redis is connected and responsive"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except:
            self.connected = False
            return False
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for a session"""
        return f"ceci-ai:session:{session_id}"
    
    def _get_query_key(self, session_id: str, query_id: str) -> str:
        """Get Redis key for a query"""
        return f"ceci-ai:session:{session_id}:query:{query_id}"
    
    def save_session(self, session_id: str, session_data: Dict[str, Any], ttl_seconds: int = 1800) -> bool:
        """Save session to Redis with TTL"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_session_key(session_id)
            
            # Serialize session data
            # Remove non-serializable objects before saving
            clean_data = self._clean_session_data(session_data)
            serialized = pickle.dumps(clean_data)
            
            # Save with TTL
            self.redis_client.setex(key, ttl_seconds, serialized)
            
            # Update session index
            self._update_session_index(session_id)
            
            logger.debug(f"Saved session {session_id} to Redis with TTL {ttl_seconds}s")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session {session_id} to Redis: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session from Redis"""
        if not self.is_connected():
            return None
        
        try:
            key = self._get_session_key(session_id)
            data = self.redis_client.get(key)
            
            if data:
                # Deserialize
                session_data = pickle.loads(data)
                logger.debug(f"Retrieved session {session_id} from Redis")
                return session_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id} from Redis: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_session_key(session_id)
            
            # Delete session and all associated queries
            pattern = f"ceci-ai:session:{session_id}*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                
            # Remove from index
            self._remove_from_session_index(session_id)
            
            logger.debug(f"Deleted session {session_id} from Redis")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id} from Redis: {e}")
            return False
    
    def extend_session_ttl(self, session_id: str, ttl_seconds: int = 1800) -> bool:
        """Extend session TTL"""
        if not self.is_connected():
            return False
        
        try:
            key = self._get_session_key(session_id)
            result = self.redis_client.expire(key, ttl_seconds)
            
            if result:
                logger.debug(f"Extended TTL for session {session_id} to {ttl_seconds}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extend TTL for session {session_id}: {e}")
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        if not self.is_connected():
            return []
        
        try:
            # Get from session index
            sessions = self.redis_client.smembers("ceci-ai:sessions:active")
            
            # Decode and verify sessions still exist
            active_sessions = []
            for session_id in sessions:
                session_id = session_id.decode('utf-8') if isinstance(session_id, bytes) else session_id
                if self.redis_client.exists(self._get_session_key(session_id)):
                    active_sessions.append(session_id)
                else:
                    # Clean up stale index entry
                    self._remove_from_session_index(session_id)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about sessions"""
        if not self.is_connected():
            return {"error": "Redis not connected"}
        
        try:
            active_sessions = self.get_active_sessions()
            
            stats = {
                "total_active_sessions": len(active_sessions),
                "redis_connected": True,
                "redis_url": self._safe_redis_url()
            }
            
            # Get memory usage if available
            try:
                info = self.redis_client.info('memory')
                stats["redis_memory_used_mb"] = round(info.get('used_memory', 0) / 1024 / 1024, 2)
            except:
                pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {"error": str(e)}
    
    def _clean_session_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean session data for serialization"""
        # Remove pandas DataFrames and other non-serializable objects
        clean_data = {}
        
        for key, value in data.items():
            if key in ['query_chain', 'state', 'created_at', 'last_activity', 'id', 'metadata']:
                clean_data[key] = value
            # Skip DataFrames and other complex objects
            
        return clean_data
    
    def _update_session_index(self, session_id: str):
        """Add session to active sessions index"""
        try:
            self.redis_client.sadd("ceci-ai:sessions:active", session_id)
        except:
            pass
    
    def _remove_from_session_index(self, session_id: str):
        """Remove session from active sessions index"""
        try:
            self.redis_client.srem("ceci-ai:sessions:active", session_id)
        except:
            pass
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from index"""
        if not self.is_connected():
            return 0
        
        try:
            cleaned = 0
            active_sessions = self.redis_client.smembers("ceci-ai:sessions:active")
            
            for session_id in active_sessions:
                session_id = session_id.decode('utf-8') if isinstance(session_id, bytes) else session_id
                if not self.redis_client.exists(self._get_session_key(session_id)):
                    self._remove_from_session_index(session_id)
                    cleaned += 1
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired sessions from index")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

# Singleton instance
_redis_store: Optional[RedisSessionStore] = None

def get_redis_store() -> RedisSessionStore:
    """Get or create the singleton RedisSessionStore instance"""
    global _redis_store
    if _redis_store is None:
        _redis_store = RedisSessionStore()
    return _redis_store
