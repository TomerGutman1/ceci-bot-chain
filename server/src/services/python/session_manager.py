"""
Session Manager for CECI-AI PandasAI Service
Manages conversation sessions and query context for reference resolution
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import deque
import uuid
import pandas as pd
import json
import logging
from enum import Enum
import os

# Import Redis session store if available
try:
    from redis_session_store import get_redis_store
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis session store not available, using in-memory storage only")

logger = logging.getLogger(__name__)

class SessionState(Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    CLOSED = "closed"

@dataclass
class QueryContext:
    """Stores context for a single query within a session"""
    query_id: str
    session_id: str
    timestamp: datetime
    original_query: str
    resolved_query: str  # Query after reference resolution
    results: Optional[pd.DataFrame] = None
    results_metadata: Dict[str, Any] = field(default_factory=dict)
    response_type: str = "text"  # text, dataframe, number
    formatted_response: str = ""
    references: List[str] = field(default_factory=list)  # IDs of referenced queries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "query_id": self.query_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "original_query": self.original_query,
            "resolved_query": self.resolved_query,
            "results_count": len(self.results) if self.results is not None else 0,
            "results_metadata": self.results_metadata,
            "response_type": self.response_type,
            "formatted_response": self.formatted_response,
            "references": self.references
        }

@dataclass
class Session:
    """Represents a conversation session"""
    id: str
    created_at: datetime
    last_activity: datetime
    state: SessionState = SessionState.ACTIVE
    query_chain: List[QueryContext] = field(default_factory=list)
    context_window: deque = field(default_factory=lambda: deque(maxlen=10))
    named_results: Dict[str, pd.DataFrame] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_query(self, query_context: QueryContext):
        """Add a query to the session"""
        self.query_chain.append(query_context)
        self.context_window.append(query_context)
        self.last_activity = datetime.now()
        
    def get_recent_queries(self, n: int = 5) -> List[QueryContext]:
        """Get n most recent queries"""
        return list(self.query_chain[-n:])
    
    def get_query_by_id(self, query_id: str) -> Optional[QueryContext]:
        """Find a specific query by ID"""
        for query in self.query_chain:
            if query.query_id == query_id:
                return query
        return None
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired"""
        if self.state == SessionState.EXPIRED:
            return True
        
        time_since_activity = datetime.now() - self.last_activity
        if time_since_activity > timedelta(minutes=timeout_minutes):
            self.state = SessionState.EXPIRED
            return True
            
        return False

class ReferenceResolver:
    """Resolves references to previous queries and results"""
    
    # Patterns for different types of references
    DIRECT_REFERENCES = [
        (r'ההחלטה (הראשונה|השנייה|השלישית|הרביעית|החמישית)', 'ordinal'),
        (r'החלטה מספר (\d+) (מהרשימה|מהתוצאות)', 'list_index'),
        (r'ההחלטה (האחרונה|הקודמת)', 'relative'),
    ]
    
    CONTENT_REFERENCES = [
        (r'התוכן המלא של', 'full_content'),
        (r'תוכן ההחלטה', 'full_content'),
        (r'את תוכן ההחלטה', 'full_content'),
        (r'פרטים נוספים על', 'more_details'),
        (r'הטקסט המלא', 'full_text'),
    ]
    
    RELATIVE_REFERENCES = [
        (r'עוד (כמו זה|כאלה|דומות)', 'more_like_this'),
        (r'אותו דבר (אבל|רק)', 'same_but'),
        (r'עכשיו|כעת', 'now_with'),
    ]
    
    def __init__(self):
        self.ordinal_map = {
            'הראשונה': 0, 'השנייה': 1, 'השלישית': 2, 
            'הרביעית': 3, 'החמישית': 4, 'האחרונה': -1
        }
    
    def resolve_references(self, query: str, session: Session) -> Tuple[str, List[str]]:
        """
        Resolve references in a query to previous results
        Returns: (resolved_query, list_of_referenced_query_ids)
        """
        if not session.query_chain:
            logger.info("No previous queries in session")
            return query, []
        
        logger.info(f"Resolving references for query: {query}")
        logger.info(f"Session has {len(session.query_chain)} previous queries")
        
        # Debug: log the patterns we're checking
        logger.debug(f"Checking content patterns: {[p[0] for p in self.CONTENT_REFERENCES]}")
        logger.debug(f"Query text: '{query}'")
        
        # Simple check for common content request patterns
        if 'תוכן' in query and 'החלטה' in query:
            logger.info("Detected content request pattern (simple check)")
            # Get the last query with results
            last_context = self._get_last_with_results(session)
            if last_context:
                logger.info(f"Found last context with query: {last_context.original_query}")
                resolved_query, refs = self._build_content_query(query, last_context, 'full_content'), [last_context.query_id]
                logger.info(f"Resolved to: {resolved_query}")
                return resolved_query, refs
        
        resolved_query = query
        referenced_ids = []
        
        # Check for direct references
        for pattern, ref_type in self.DIRECT_REFERENCES:
            import re
            match = re.search(pattern, query)
            if match:
                if ref_type == 'ordinal':
                    ordinal = match.group(1)
                    index = self.ordinal_map.get(ordinal, -1)
                    context = self._get_result_by_index(session, index)
                    if context:
                        referenced_ids.append(context.query_id)
                        resolved_query = self._build_resolved_query(query, context, ref_type)
                
                elif ref_type == 'list_index':
                    index = int(match.group(1)) - 1  # Convert to 0-based
                    context = self._get_result_by_index(session, index)
                    if context:
                        referenced_ids.append(context.query_id)
                        resolved_query = self._build_resolved_query(query, context, ref_type)
        
        # Check for content references
        for pattern, ref_type in self.CONTENT_REFERENCES:
            if re.search(pattern, query):
                logger.info(f"Found content reference pattern: {pattern}")
                # Get the last query with results
                last_context = self._get_last_with_results(session)
                if last_context:
                    logger.info(f"Found last context with query: {last_context.original_query}")
                    referenced_ids.append(last_context.query_id)
                    resolved_query = self._build_content_query(query, last_context, ref_type)
                else:
                    logger.warning("No previous context with results found")
        
        # Check for relative references
        for pattern, ref_type in self.RELATIVE_REFERENCES:
            if re.search(pattern, query):
                last_context = session.query_chain[-1] if session.query_chain else None
                if last_context:
                    referenced_ids.append(last_context.query_id)
                    resolved_query = self._build_relative_query(query, last_context, ref_type)
        
        return resolved_query, referenced_ids
    
    def _get_result_by_index(self, session: Session, index: int) -> Optional[QueryContext]:
        """Get a result from the last query that returned multiple results"""
        for context in reversed(session.query_chain):
            if context.results is not None and len(context.results) > 0:
                if context.response_type == 'dataframe' and len(context.results) > abs(index):
                    return context
        return None
    
    def _get_last_with_results(self, session: Session) -> Optional[QueryContext]:
        """Get the last query that had results"""
        for context in reversed(session.query_chain):
            if context.results is not None:
                return context
        return None
    
    def _build_resolved_query(self, original: str, context: QueryContext, ref_type: str) -> str:
        """Build a resolved query for direct references"""
        if context.results is not None and len(context.results) > 0:
            # Extract the specific decision being referenced
            if ref_type == 'ordinal':
                # Find which index was requested
                import re
                match = re.search(r'ההחלטה (הראשונה|השנייה|השלישית|הרביעית|החמישית)', original)
                if match:
                    ordinal = match.group(1)
                    idx = self.ordinal_map.get(ordinal, 0)
                    if 0 <= idx < len(context.results):
                        decision_num = context.results.iloc[idx].get('decision_number', '')
                        return f"{original} - מתכוון להחלטה מספר {decision_num}"
        
        return original
    
    def _build_content_query(self, original: str, context: QueryContext, ref_type: str) -> str:
        """Build a query for content references"""
        logger.info(f"Building content query for: {original}")
        
        # First, try to extract decision number from the formatted response
        import re
        decision_match = re.search(r'מספר החלטה: (\d+)', context.formatted_response)
        if not decision_match:
            # Try alternative patterns
            decision_match = re.search(r'החלטת ממשלה מס[\'"]? (\d+)', context.formatted_response)
        
        if decision_match:
            decision_num = decision_match.group(1)
            logger.info(f"Found decision number in formatted response: {decision_num}")
            # Be MORE explicit about getting ONLY this specific decision
            return f"""הבא לי את התוכן המלא של החלטה מספר {decision_num} בלבד. 
השתמש בקוד הבא:
filtered_df = df[df['decision_number'] == '{decision_num}']
if len(filtered_df) == 0:
    result = {{'type': 'string', 'value': 'לא נמצאה החלטה מספר {decision_num} במסד הנתונים'}}
else:
    content = filtered_df.iloc[0]['decision_content']
    if pd.isna(content) or content is None or content == '':
        content = filtered_df.iloc[0].get('summary', 'אין תוכן זמין')
    result = {{'type': 'string', 'value': content}}"""
        
        # Fallback: if we have results, use the first one
        if context.results is not None and len(context.results) > 0:
            decision_num = context.results.iloc[0].get('decision_number', '')
            if decision_num:
                logger.info(f"Using decision number from results: {decision_num}")
                # Be MORE explicit about getting ONLY this specific decision
                return f"""הבא לי את התוכן המלא של החלטה מספר {decision_num} בלבד. 
השתמש בקוד הבא:
filtered_df = df[df['decision_number'] == '{decision_num}']
if len(filtered_df) == 0:
    result = {{'type': 'string', 'value': 'לא נמצאה החלטה מספר {decision_num} במסד הנתונים'}}
else:
    content = filtered_df.iloc[0]['decision_content']
    if pd.isna(content) or content is None or content == '':
        content = filtered_df.iloc[0].get('summary', 'אין תוכן זמין')
    result = {{'type': 'string', 'value': content}}"""
        
        logger.warning("Could not find decision number for content reference")
        return original
    
    def _build_relative_query(self, original: str, context: QueryContext, ref_type: str) -> str:
        """Build a query for relative references"""
        # Add context from previous query
        if ref_type == 'now_with' and 'משנת' in original:
            # Extract the year and apply to previous context
            import re
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', original)
            if year_match and context.resolved_query:
                year = year_match.group(1)
                # Modify the previous query with the new year
                base_query = context.resolved_query.split(' - ')[0]  # Remove previous instructions
                return f"{base_query} משנת {year}"
        
        elif ref_type == 'more_like_this':
            # Request more results similar to the last query
            return f"{context.resolved_query} - הבא עוד תוצאות דומות"
        
        return original

class SessionManager:
    """Manages all active sessions"""
    
    def __init__(self, timeout_minutes: int = 30):
        self.sessions: Dict[str, Session] = {}
        self.timeout_minutes = timeout_minutes
        self.reference_resolver = ReferenceResolver()
        
        # Initialize Redis store if available
        self.redis_store = None
        if REDIS_AVAILABLE and os.getenv("REDIS_URL"):
            try:
                self.redis_store = get_redis_store()
                if self.redis_store.is_connected():
                    logger.info("Redis session store initialized successfully")
                else:
                    self.redis_store = None
                    logger.warning("Redis configured but not connected, using in-memory storage")
            except Exception as e:
                logger.error(f"Failed to initialize Redis session store: {e}")
                self.redis_store = None
    
    def create_session(self, session_id: Optional[str] = None) -> Session:
        """Create a new session"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = Session(
            id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session
        
        # Save to Redis if available
        if self.redis_store:
            try:
                session_data = {
                    'id': session.id,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'state': session.state.value,
                    'query_chain': [],
                    'metadata': session.metadata
                }
                self.redis_store.save_session(session_id, session_data, self.timeout_minutes * 60)
            except Exception as e:
                logger.error(f"Failed to save session to Redis: {e}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an existing session"""
        # Try to get from memory first
        session = self.sessions.get(session_id)
        
        # If not in memory, try Redis
        if not session and self.redis_store:
            try:
                session_data = self.redis_store.get_session(session_id)
                if session_data:
                    # Reconstruct session from Redis data
                    session = Session(
                        id=session_data['id'],
                        created_at=datetime.fromisoformat(session_data['created_at']),
                        last_activity=datetime.fromisoformat(session_data['last_activity']),
                        state=SessionState(session_data['state']),
                        metadata=session_data.get('metadata', {})
                    )
                    # Add to memory cache
                    self.sessions[session_id] = session
            except Exception as e:
                logger.error(f"Failed to get session from Redis: {e}")
        
        if session and not session.is_expired(self.timeout_minutes):
            # Extend TTL in Redis
            if self.redis_store:
                self.redis_store.extend_session_ttl(session_id, self.timeout_minutes * 60)
            return session
        
        # Remove expired session
        if session:
            del self.sessions[session_id]
            if self.redis_store:
                self.redis_store.delete_session(session_id)
        
        return None
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get existing session or create new one"""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        return self.create_session(session_id)
    
    def add_query_to_session(
        self, 
        session_id: str, 
        query: str,
        results: Optional[pd.DataFrame] = None,
        response_type: str = "text",
        formatted_response: str = "",
        metadata: Dict[str, Any] = None
    ) -> QueryContext:
        """Add a query to a session with reference resolution"""
        session = self.get_or_create_session(session_id)
        
        # Resolve references in the query
        resolved_query, referenced_ids = self.reference_resolver.resolve_references(query, session)
        
        # Create query context
        query_context = QueryContext(
            query_id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(),
            original_query=query,
            resolved_query=resolved_query,
            results=results,
            results_metadata=metadata or {},
            response_type=response_type,
            formatted_response=formatted_response,
            references=referenced_ids
        )
        
        # Add to session
        session.add_query(query_context)
        
        # Update Redis if available
        if self.redis_store:
            try:
                session_data = {
                    'id': session.id,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'state': session.state.value,
                    'query_chain': [q.to_dict() for q in session.query_chain[-10:]],  # Keep last 10 queries
                    'metadata': session.metadata
                }
                self.redis_store.save_session(session_id, session_data, self.timeout_minutes * 60)
            except Exception as e:
                logger.error(f"Failed to update session in Redis: {e}")
        
        return query_context
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.timeout_minutes)
        ]
        
        for sid in expired_ids:
            del self.sessions[sid]
        
        return len(expired_ids)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active sessions"""
        active_sessions = [s for s in self.sessions.values() if s.state == SessionState.ACTIVE]
        
        stats = {
            "total_sessions": len(self.sessions),
            "active_sessions": len(active_sessions),
            "total_queries": sum(len(s.query_chain) for s in self.sessions.values()),
            "average_queries_per_session": sum(len(s.query_chain) for s in self.sessions.values()) / max(len(self.sessions), 1),
            "storage_backend": "redis" if self.redis_store and self.redis_store.is_connected() else "memory"
        }
        
        # Add Redis stats if available
        if self.redis_store:
            redis_stats = self.redis_store.get_session_stats()
            stats["redis_stats"] = redis_stats
        
        return stats

# Singleton instance
_session_manager: Optional[SessionManager] = None

def get_session_manager() -> SessionManager:
    """Get or create the singleton SessionManager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
