"""
Reference Resolution Module for Context Router Bot.
Automatically detects and resolves user references to previous conversation turns.
"""

import json
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from difflib import SequenceMatcher

from reference_config import reference_config, HEBREW_ENTITY_LABELS, REQUIRED_SLOTS_BY_INTENT


class ReferenceResolver:
    """Manages reference resolution for conversation context."""
    
    def __init__(self, memory_service=None):
        """Initialize reference resolver with memory service."""
        self.config = reference_config
        self.memory_service = memory_service
        self.compiled_patterns = self.config.get_compiled_patterns()
        self.metrics = {
            'resolution_attempts': 0,
            'successful_resolutions': 0,
            'pattern_matches': 0,
            'fuzzy_matches': 0,
            'clarifications_generated': 0,
            'performance_violations': 0
        }
    
    def _fuzzy_similarity(self, text1: str, text2: str) -> float:
        """Calculate fuzzy similarity between two text strings."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _extract_patterns_from_text(self, text: str) -> Dict[str, Any]:
        """Extract entity patterns from user text using regex."""
        matches = {}
        
        # Extract decision numbers
        for pattern in self.compiled_patterns['decision_number']:
            match = pattern.search(text)
            if match:
                matches['decision_number'] = match.group(1)
                self.metrics['pattern_matches'] += 1
                break
        
        # Extract government numbers  
        for pattern in self.compiled_patterns['government_number']:
            match = pattern.search(text)
            if match:
                matches['government_number'] = match.group(1)
                self.metrics['pattern_matches'] += 1
                break
        
        # Extract date ranges
        for pattern in self.compiled_patterns['date_range']:
            match = pattern.search(text)
            if match:
                matches['date_range'] = [match.group(1), match.group(2)]
                self.metrics['pattern_matches'] += 1
                break
        
        return matches
    
    def _search_history_for_entities(
        self, 
        conv_history: List[Dict[str, Any]], 
        missing_slots: List[str]
    ) -> Dict[str, Any]:
        """Search conversation history for missing entities with recency emphasis."""
        resolved_entities = {}
        
        # Sort history by recency (most recent first)
        # Limit to configured history turns
        recent_history = conv_history[-self.config.history_turns:] if conv_history else []
        recent_history.reverse()  # Most recent first
        
        # Filter only user messages (ignore bot responses)
        user_turns = [turn for turn in recent_history if turn.get('speaker') == 'user']
        
        for slot in missing_slots:
            # Search through user turns in recency order
            for i, turn in enumerate(user_turns):
                turn_text = turn.get('clean_text', '')
                turn_matches = self._extract_patterns_from_text(turn_text)
                
                # Check if this turn has the missing entity
                if slot in turn_matches:
                    # Apply recency weighting - prefer recent turns
                    # Since we filtered only user turns, recency calculation is different
                    recency_weight = 1.0
                    if i >= self.config.recency_emphasis_turns:
                        recency_weight = 0.8  # Lower weight for older user turns
                    
                    # Check fuzzy matching threshold
                    if self._fuzzy_similarity(turn_text, turn_text) >= self.config.fuzzy_threshold * recency_weight:
                        resolved_entities[slot] = turn_matches[slot]
                        self.metrics['fuzzy_matches'] += 1
                        break
        
        return resolved_entities
    
    def _generate_clarification_prompt(
        self, 
        known_parts: Dict[str, Any], 
        missing_slots: List[str]
    ) -> str:
        """Generate Hebrew clarification prompt for missing entities."""
        # Build known parts summary
        known_labels = []
        for key, value in known_parts.items():
            if key in HEBREW_ENTITY_LABELS and value:
                if key == 'date_range' and isinstance(value, list):
                    known_labels.append(f"{HEBREW_ENTITY_LABELS[key]} {value[0]} עד {value[1]}")
                else:
                    known_labels.append(f"{HEBREW_ENTITY_LABELS[key]} {value}")
        
        # Build missing parts labels
        missing_labels = [HEBREW_ENTITY_LABELS.get(slot, slot) for slot in missing_slots]
        
        # Construct clarification prompt
        if known_labels:
            known_text = ", ".join(known_labels)
            missing_text = " או ".join(missing_labels)
            prompt = f"לא ברור לי אם התכוונת ל־{known_text} או ל־{missing_text}. תוכל בבקשה לציין למה אתה מתכוון ולהרחיב קצת?"
        else:
            missing_text = " ו".join(missing_labels)
            prompt = f"לא ברור לי מה {missing_text} שאתה מחפש. תוכל בבקשה לציין בבירור?"
        
        return prompt
    
    def _enrich_query_text(self, original_query: str, resolved_entities: Dict[str, Any]) -> str:
        """Enrich original query with resolved entities."""
        enriched = original_query
        
        # Add decision number if resolved
        if 'decision_number' in resolved_entities:
            decision_num = resolved_entities['decision_number']
            if 'החלטה' not in enriched:
                enriched = f"הבא לי את החלטה {decision_num}"
            
        # Add government number if resolved
        if 'government_number' in resolved_entities:
            gov_num = resolved_entities['government_number']
            if 'ממשלה' not in enriched:
                enriched += f" של ממשלה {gov_num}"
        
        # Add date range if resolved
        if 'date_range' in resolved_entities:
            date_range = resolved_entities['date_range']
            if isinstance(date_range, list) and len(date_range) == 2:
                enriched += f" בין {date_range[0]} ל־{date_range[1]}"
        
        return enriched.strip()
    
    def resolve_references(
        self, 
        conv_id: str,
        user_text: str, 
        current_entities: Dict[str, Any],
        intent: str = None
    ) -> Dict[str, Any]:
        """
        Main reference resolution method.
        
        Args:
            conv_id: Conversation ID for history lookup
            user_text: Current user query text
            current_entities: Already extracted entities from intent bot
            intent: Detected intent for determining required slots
            
        Returns:
            Dictionary with resolution results:
            {
                'enriched_query': str,
                'resolved_entities': dict,
                'needs_clarification': bool,
                'clarification_prompt': str | None,
                'route': str,  # 'enriched', 'clarify', 'passthrough'
                'reasoning': str
            }
        """
        start_time = time.time()
        self.metrics['resolution_attempts'] += 1
        
        if not self.config.enabled:
            return {
                'enriched_query': user_text,
                'resolved_entities': current_entities,
                'needs_clarification': False,
                'clarification_prompt': None,
                'route': 'passthrough',
                'reasoning': 'Reference resolution disabled'
            }
        
        try:
            # Extract patterns from current user text
            extracted_patterns = self._extract_patterns_from_text(user_text)
            
            # Merge with current entities (patterns override current)
            all_entities = {**current_entities, **extracted_patterns}
            
            # Determine required slots based on intent
            required_slots = REQUIRED_SLOTS_BY_INTENT.get(intent, [])
            
            # Find missing slots
            missing_slots = [
                slot for slot in required_slots 
                if slot not in all_entities or not all_entities[slot]
            ]
            
            # If no missing slots, return enriched query
            if not missing_slots:
                enriched_query = self._enrich_query_text(user_text, all_entities)
                self.metrics['successful_resolutions'] += 1
                
                return {
                    'enriched_query': enriched_query,
                    'resolved_entities': all_entities,
                    'needs_clarification': False,
                    'clarification_prompt': None,
                    'route': 'enriched',
                    'reasoning': f'All required slots filled: {required_slots}'
                }
            
            # Fetch conversation history for missing entity resolution
            conversation_history = []
            if self.memory_service:
                conversation_history = self.memory_service.fetch(conv_id)
            
            # Search history for missing entities
            resolved_from_history = self._search_history_for_entities(
                conversation_history, missing_slots
            )
            
            # Merge resolved entities
            final_entities = {**all_entities, **resolved_from_history}
            
            # Check if we still have missing required slots
            still_missing = [
                slot for slot in required_slots
                if slot not in final_entities or not final_entities[slot]
            ]
            
            # If all required slots are now filled, return enriched query
            if not still_missing:
                enriched_query = self._enrich_query_text(user_text, final_entities)
                self.metrics['successful_resolutions'] += 1
                
                return {
                    'enriched_query': enriched_query,
                    'resolved_entities': final_entities,
                    'needs_clarification': False,
                    'clarification_prompt': None,
                    'route': 'enriched',
                    'reasoning': f'Resolved from history: {list(resolved_from_history.keys())}'
                }
            
            # Generate clarification if enabled and still missing slots
            if self.config.clarify_on_fail and still_missing:
                clarification_prompt = self._generate_clarification_prompt(
                    final_entities, still_missing
                )
                self.metrics['clarifications_generated'] += 1
                
                return {
                    'enriched_query': user_text,
                    'resolved_entities': final_entities,
                    'needs_clarification': True,
                    'clarification_prompt': clarification_prompt,
                    'route': 'clarify',
                    'reasoning': f'Missing required slots after resolution: {still_missing}'
                }
            
            # Fallback: pass through with partial resolution
            enriched_query = self._enrich_query_text(user_text, final_entities)
            return {
                'enriched_query': enriched_query,
                'resolved_entities': final_entities,
                'needs_clarification': False,
                'clarification_prompt': None,
                'route': 'passthrough',
                'reasoning': f'Partial resolution, missing: {still_missing}'
            }
            
        except Exception as e:
            # Error fallback: pass through original
            return {
                'enriched_query': user_text,
                'resolved_entities': current_entities,
                'needs_clarification': False,
                'clarification_prompt': None,
                'route': 'error',
                'reasoning': f'Reference resolution error: {str(e)}'
            }
        
        finally:
            # Track performance
            duration_ms = (time.time() - start_time) * 1000
            if duration_ms > self.config.performance_target_ms:
                self.metrics['performance_violations'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get reference resolution metrics."""
        success_rate = 0.0
        if self.metrics['resolution_attempts'] > 0:
            success_rate = self.metrics['successful_resolutions'] / self.metrics['resolution_attempts']
        
        return {
            'reference_resolution_attempts_total': self.metrics['resolution_attempts'],
            'reference_resolved_total': self.metrics['successful_resolutions'],
            'reference_pattern_matches_total': self.metrics['pattern_matches'],
            'reference_fuzzy_matches_total': self.metrics['fuzzy_matches'],
            'reference_clarifications_total': self.metrics['clarifications_generated'],
            'reference_performance_violations_total': self.metrics['performance_violations'],
            'reference_success_rate': success_rate,
            'reference_resolution_enabled': self.config.enabled
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on reference resolver."""
        return {
            'status': 'ok' if self.config.enabled else 'disabled',
            'enabled': self.config.enabled,
            'memory_service_available': self.memory_service is not None,
            'compiled_patterns_count': sum(len(patterns) for patterns in self.compiled_patterns.values()),
            'fuzzy_threshold': self.config.fuzzy_threshold,
            'history_turns': self.config.history_turns,
            'metrics': self.get_metrics()
        }