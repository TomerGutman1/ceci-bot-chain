"""
Response Validator for CECI-AI PandasAI Service
Validates that PandasAI responses contain real data from the database
"""

import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class ResponseValidator:
    """Validates PandasAI responses to prevent hallucination"""
    
    def __init__(self, source_dataframe: pd.DataFrame):
        """
        Initialize validator with the source dataframe
        
        Args:
            source_dataframe: The original dataframe containing all valid decisions
        """
        self.source_df = source_dataframe
        self.valid_decision_numbers = set(source_dataframe['decision_number'].astype(str).tolist())
        logger.info(f"ResponseValidator initialized with {len(self.valid_decision_numbers)} valid decisions")
    
    def validate_response(self, response: Any, query: str) -> Dict[str, Any]:
        """
        Validate a PandasAI response
        
        Args:
            response: The response from PandasAI
            query: The original query
            
        Returns:
            Dict with validation results and cleaned response
        """
        validation_result = {
            "is_valid": True,
            "cleaned_response": response,
            "removed_items": [],
            "warnings": [],
            "error": None
        }
        
        try:
            if isinstance(response, pd.DataFrame):
                validation_result = self._validate_dataframe(response)
            elif isinstance(response, dict):
                validation_result = self._validate_dict(response)
            elif isinstance(response, str):
                validation_result = self._validate_string(response, query)
            else:
                # For other types (numbers, etc.), assume valid
                validation_result["cleaned_response"] = response
                
        except Exception as e:
            logger.error(f"Error validating response: {e}")
            validation_result["is_valid"] = False
            validation_result["error"] = str(e)
        
        return validation_result
    
    def _validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate a dataframe response"""
        result = {
            "is_valid": True,
            "cleaned_response": df,
            "removed_items": [],
            "warnings": []
        }
        
        if df.empty:
            return result
        
        # Check if dataframe has decision_number column
        if 'decision_number' not in df.columns:
            logger.warning("DataFrame response missing decision_number column")
            result["warnings"].append("Response missing decision_number column")
            return result
        
        # Validate each decision number
        df_copy = df.copy()
        invalid_mask = pd.Series([False] * len(df_copy))
        
        for idx, row in df_copy.iterrows():
            decision_num = str(row['decision_number'])
            if decision_num not in self.valid_decision_numbers:
                logger.warning(f"Invalid decision number found: {decision_num}")
                result["removed_items"].append({
                    "decision_number": decision_num,
                    "reason": "Decision not found in database"
                })
                invalid_mask.iloc[idx] = True
        
        # Remove invalid rows
        if invalid_mask.any():
            df_copy = df_copy[~invalid_mask]
            result["is_valid"] = False
            result["warnings"].append(f"Removed {invalid_mask.sum()} invalid decisions")
        
        # Additional validation: check for duplicate decision numbers
        if df_copy.duplicated(subset=['decision_number']).any():
            df_copy = df_copy.drop_duplicates(subset=['decision_number'])
            result["warnings"].append("Removed duplicate decisions")
        
        result["cleaned_response"] = df_copy
        
        # If all rows were invalid, return empty dataframe
        if df_copy.empty and not df.empty:
            result["is_valid"] = False
            result["warnings"].append("All returned decisions were invalid")
        
        return result
    
    def _validate_dict(self, response_dict: dict) -> Dict[str, Any]:
        """Validate a dictionary response"""
        result = {
            "is_valid": True,
            "cleaned_response": response_dict,
            "removed_items": [],
            "warnings": []
        }
        
        # Check if dict contains dataframe
        if 'value' in response_dict and isinstance(response_dict['value'], pd.DataFrame):
            df_validation = self._validate_dataframe(response_dict['value'])
            response_dict['value'] = df_validation['cleaned_response']
            result.update(df_validation)
            result["cleaned_response"] = response_dict
        
        # Check for decision numbers in dict values
        elif 'decision_number' in response_dict:
            decision_num = str(response_dict['decision_number'])
            if decision_num not in self.valid_decision_numbers:
                result["is_valid"] = False
                result["warnings"].append(f"Invalid decision number: {decision_num}")
        
        return result
    
    def _validate_string(self, response_str: str, query: str) -> Dict[str, Any]:
        """Validate a string response for hallucinated decision numbers"""
        import re
        
        result = {
            "is_valid": True,
            "cleaned_response": response_str,
            "removed_items": [],
            "warnings": []
        }
        
        # Look for decision numbers in the response
        decision_pattern = r'החלטה מס[\'"]?\s*(\d+)'
        matches = re.findall(decision_pattern, response_str)
        
        for decision_num in matches:
            if decision_num not in self.valid_decision_numbers:
                logger.warning(f"String response contains invalid decision number: {decision_num}")
                result["warnings"].append(f"Response mentions non-existent decision: {decision_num}")
                result["is_valid"] = False
        
        # Check for specific known problematic decision
        if '4272' in response_str and '4272' not in self.valid_decision_numbers:
            result["warnings"].append("Response contains known problematic decision 4272")
            result["is_valid"] = False
        
        return result
    
    def get_valid_decision(self, decision_number: str) -> Optional[pd.Series]:
        """Get a valid decision by number"""
        decision_number = str(decision_number)
        if decision_number in self.valid_decision_numbers:
            return self.source_df[self.source_df['decision_number'] == decision_number].iloc[0]
        return None
    
    def find_similar_decisions(self, invalid_decision_num: str, limit: int = 5) -> pd.DataFrame:
        """Find similar valid decision numbers (for typo correction)"""
        try:
            # Try to find decisions with similar numbers
            invalid_num = int(invalid_decision_num)
            
            # Look for decisions within range of +/- 10
            similar = self.source_df[
                (self.source_df['decision_number'].astype(int) >= invalid_num - 10) &
                (self.source_df['decision_number'].astype(int) <= invalid_num + 10)
            ]
            
            if not similar.empty:
                return similar.head(limit)
                
        except ValueError:
            pass
        
        return pd.DataFrame()
    
    def validate_decision_content(self, decision_number: str, content: str) -> bool:
        """Validate that content matches the decision number"""
        valid_decision = self.get_valid_decision(decision_number)
        if valid_decision is None:
            return False
        
        # Check if content is from the correct decision
        actual_content = valid_decision.get('decision_content', '')
        actual_summary = valid_decision.get('summary', '')
        
        # Basic check - content should be substring of actual content or summary
        if content and (content in str(actual_content) or content in str(actual_summary)):
            return True
        
        return False
