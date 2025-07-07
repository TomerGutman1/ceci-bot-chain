"""
Reference resolution configuration for Context Router Bot.
Implements patterns and settings for detecting and resolving user references.
"""

import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ReferenceConfig:
    """Configuration for reference resolution functionality."""
    
    # Enable/disable reference resolution
    enabled: bool = True
    
    # Number of conversation turns to search in history  
    history_turns: int = 20
    
    # TTL for conversation history in hours
    ttl_hours: int = 2
    
    # Fuzzy matching threshold (0.0 - 1.0)
    fuzzy_threshold: float = 0.6
    
    # Whether to generate clarification when resolution fails
    clarify_on_fail: bool = True
    
    # Hebrew regex patterns for entity extraction
    decision_patterns: List[str] = None
    government_patterns: List[str] = None  
    date_range_patterns: List[str] = None
    
    # Recency emphasis - prioritize last N turns
    recency_emphasis_turns: int = 3
    
    # Performance target in milliseconds
    performance_target_ms: int = 100
    
    def __post_init__(self):
        """Initialize default patterns if not provided."""
        if self.decision_patterns is None:
            self.decision_patterns = [
                r'(?:החלטה|החלטת)\s*(?:מספר\s*)?(\d+)',
                r'החלטה\s+(\d+)',
                # Remove generic patterns that conflict
            ]
        
        if self.government_patterns is None:
            self.government_patterns = [
                r'ממשלה\s*(?:מספר\s*)?(\d+)',
                r'של\s*ממשלה\s*(\d+)',
                r'ממשלת\s*(\d+)',
                r'(?:עבור|בממשלה)\s*(\d+)',
            ]
        
        if self.date_range_patterns is None:
            self.date_range_patterns = [
                r'בין\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s*[-–—]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'מ[־\-]?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s*עד\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
                r'(?:מתאריך|מיום)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s*(?:עד|ל)\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            ]
    
    def get_compiled_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Get compiled regex patterns for efficient matching."""
        return {
            'decision_number': [re.compile(pattern, re.IGNORECASE) for pattern in self.decision_patterns],
            'government_number': [re.compile(pattern, re.IGNORECASE) for pattern in self.government_patterns],
            'date_range': [re.compile(pattern, re.IGNORECASE) for pattern in self.date_range_patterns],
        }
    
    @classmethod
    def from_env(cls) -> 'ReferenceConfig':
        """Create config from environment variables."""
        return cls(
            enabled=os.getenv('REF_RESOLUTION_ENABLED', 'true').lower() == 'true',
            history_turns=int(os.getenv('REF_HISTORY_TURNS', '20')),
            ttl_hours=int(os.getenv('REF_TTL_HOURS', '2')),
            fuzzy_threshold=float(os.getenv('REF_FUZZY_THRESHOLD', '0.6')),
            clarify_on_fail=os.getenv('REF_CLARIFY_ON_FAIL', 'true').lower() == 'true',
            recency_emphasis_turns=int(os.getenv('REF_RECENCY_TURNS', '3')),
            performance_target_ms=int(os.getenv('REF_PERF_TARGET_MS', '100'))
        )


# Hebrew entity labels for clarification prompts
HEBREW_ENTITY_LABELS = {
    'decision_number': 'מספר החלטה',
    'government_number': 'מספר ממשלה', 
    'date_range': 'טווח תאריכים'
}

# Required slots for different intents
REQUIRED_SLOTS_BY_INTENT = {
    'search': [],  # Search queries don't require specific entities
    'count': ['government_number'],
    'specific_decision': ['decision_number'],
    'comparison': [],  # Comparison queries can work with partial info
    'QUERY': [],  # QUERY is for general searches, no specific requirement
    'ANALYSIS': ['decision_number'],  # ANALYSIS specifically needs a decision
    'EVAL': ['decision_number']  # EVAL also needs a specific decision
}

# Global reference configuration instance
reference_config = ReferenceConfig.from_env()