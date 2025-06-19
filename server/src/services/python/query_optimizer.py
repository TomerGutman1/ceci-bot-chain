"""
Query Optimizer for PandasAI
Optimizes queries to reduce token usage and prevent context length errors
"""

import re
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """Optimizes queries for PandasAI to prevent context length issues"""
    
    def __init__(self):
        # Patterns that require full dataset
        self.full_dataset_patterns = [
            r'כל ההחלטות',
            r'כמה החלטות',
            r'סטטיסטיק',
            r'התפלגות',
            r'מגמ[הת]',
            r'ממוצע',
            r'סה"כ',
            r'סכום',
            r'count\(',
            r'groupby',
            r'aggregate'
        ]
        
        # Patterns that can work with filtered data
        self.filter_patterns = [
            (r'בנושא\s+([\u0590-\u05FF\s]+?)(?=\s+מ\d{4}|\s+משנת|\s+של|\s+ב|\s+ל|$)', 'topic'),
            (r'משנת\s+(\d{4})', 'year'),
            (r'מ-?(\d{4})', 'year'),
            (r'בשנת\s+(\d{4})', 'year'),
            (r'ממשלה\s+(\d+)', 'government'),
            (r'החלטה\s+מספר\s+(\d+)', 'decision_number'),
            (r'(\d+)\s+החלטות', 'limit')
        ]
    
    def needs_full_dataset(self, query: str) -> bool:
        """Check if query requires the full dataset"""
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.full_dataset_patterns)
    
    def extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from the query to reduce dataset size"""
        filters = {}
        
        for pattern, filter_type in self.filter_patterns:
            match = re.search(pattern, query)
            if match:
                if filter_type == 'topic':
                    filters['topic'] = match.group(1).strip()
                elif filter_type == 'year':
                    filters['year'] = int(match.group(1))
                elif filter_type == 'government':
                    filters['government'] = int(match.group(1))
                elif filter_type == 'decision_number':
                    filters['decision_number'] = match.group(1)
                elif filter_type == 'limit':
                    filters['limit'] = int(match.group(1))
        
        return filters
    
    def optimize_dataframe(self, df: pd.DataFrame, query: str) -> Tuple[pd.DataFrame, str]:
        """
        Optimize the dataframe based on the query to reduce size
        Returns: (optimized_df, modified_query)
        """
        # If query needs full dataset for statistics, keep columns but sample rows
        if self.needs_full_dataset(query):
            logger.info("Query needs full dataset for statistics")
            # For statistical queries, we can work with a sample
            # REDUCED FROM 5000 TO 1000 TO PREVENT CONTEXT LENGTH ERRORS
            if len(df) > 1000:
                sample_size = min(1000, len(df))
                optimized_df = df.sample(n=sample_size, random_state=42)
                modified_query = f"{query} (נתונים מבוססים על מדגם של {sample_size} החלטות מתוך {len(df)})"
                logger.info(f"Sampled {sample_size} rows for statistical analysis")
            else:
                optimized_df = df
                modified_query = query
        else:
            # Extract filters and apply them
            filters = self.extract_filters(query)
            optimized_df = df.copy()
            
            if filters:
                logger.info(f"Applying filters: {filters}")
                
                # Apply filters
                if 'topic' in filters:
                    optimized_df = optimized_df[
                        optimized_df['tags_policy_area'].str.contains(filters['topic'], na=False)
                    ]
                
                if 'year' in filters:
                    optimized_df = optimized_df[optimized_df['year'] == filters['year']]
                
                if 'government' in filters:
                    optimized_df = optimized_df[optimized_df['government_number'] == filters['government']]
                
                if 'decision_number' in filters:
                    optimized_df = optimized_df[
                        optimized_df['decision_number'] == filters['decision_number']
                    ]
                
                # If still too large, limit rows
                # REDUCED FROM 1000 TO 100 TO PREVENT CONTEXT LENGTH ERRORS
                if len(optimized_df) > 100 and 'limit' not in filters:
                    optimized_df = optimized_df.head(100)
                    modified_query = f"{query} (מוגבל ל-100 תוצאות ראשונות)"
                else:
                    modified_query = query
                
                logger.info(f"Filtered dataset from {len(df)} to {len(optimized_df)} rows")
            else:
                # No specific filters, limit to recent decisions
                # REDUCED FROM 500 TO 50 TO PREVENT CONTEXT LENGTH ERRORS
                optimized_df = df.nlargest(50, 'decision_date')
                modified_query = f"{query} (מתוך 50 ההחלטות האחרונות)"
                logger.info("No filters found, using 50 most recent decisions")
        
        # Always limit columns to essential ones for most queries
        essential_columns = [
            'decision_number', 'decision_title', 'decision_date', 'year', 'month',
            'government_number', 'prime_minister', 'tags_policy_area', 
            'tags_government_body', 'summary', 'decision_url', 'operativity'
        ]
        
        # AGGRESSIVE OPTIMIZATION: Remove summary for large datasets to save tokens
        if len(optimized_df) > 50:
            essential_columns = [
                'decision_number', 'decision_title', 'decision_date', 'year', 'month',
                'government_number', 'prime_minister', 'tags_policy_area'
            ]
            logger.info("Removed summary column for large dataset to save tokens")
        
        # Keep only columns that exist
        columns_to_keep = [col for col in essential_columns if col in optimized_df.columns]
        
        # For content queries, add decision_content ONLY for small datasets
        if any(word in query for word in ['תוכן', 'מלא', 'פרטים', 'טקסט']):
            if 'decision_content' in optimized_df.columns and len(optimized_df) <= 5:
                columns_to_keep.append('decision_content')
                logger.info("Added decision_content column for content query")
            elif len(optimized_df) > 5:
                logger.warning("Skipping decision_content due to dataset size")
        
        optimized_df = optimized_df[columns_to_keep]
        
        return optimized_df, modified_query
    
    def create_lightweight_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create a lightweight summary of the dataframe for context"""
        summary_data = {
            'שדה': [],
            'מידע': []
        }
        
        summary_data['שדה'].extend([
            'מספר החלטות',
            'תאריך ראשון',
            'תאריך אחרון',
            'ממשלות',
            'תחומים עיקריים'
        ])
        
        summary_data['מידע'].extend([
            f"{len(df):,}",
            str(df['decision_date'].min().date()) if not df.empty else 'N/A',
            str(df['decision_date'].max().date()) if not df.empty else 'N/A',
            f"{df['government_number'].min()}-{df['government_number'].max()}" if not df.empty else 'N/A',
            ', '.join(df['tags_policy_area'].value_counts().head(5).index.tolist()) if not df.empty else 'N/A'
        ])
        
        return pd.DataFrame(summary_data)
