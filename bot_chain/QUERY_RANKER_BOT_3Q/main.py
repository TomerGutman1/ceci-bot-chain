#!/usr/bin/env python3
"""
QUERY Ranker Bot 3Q - Rank and prioritize search results.

This bot takes search results and ranks them using a combination of:
- BM25 text relevance scoring
- GPT-4 semantic relevance analysis
- Entity matching scores
- Temporal relevance (newer decisions prioritized)
- Topic clustering and diversity
"""

import os
import asyncio
import openai
import math
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.logging import setup_logging
from common.config import get_config

# Initialize logging and config
logger = setup_logging('QUERY_RANKER_BOT_3Q')
config = get_config('QUERY_RANKER_BOT_3Q')

# Configure OpenAI
openai.api_key = config.openai_api_key

app = FastAPI(
    title="QUERY_RANKER_BOT_3Q",
    description="Result Ranking and Prioritization Service",
    version="1.0.0"
)

class RankingStrategy(str, Enum):
    RELEVANCE = "relevance"  # Pure relevance scoring
    TEMPORAL = "temporal"    # Newer decisions first
    HYBRID = "hybrid"       # Combination of relevance + temporal
    DIVERSITY = "diversity"  # Maximize topic diversity

@dataclass
class RankingScore:
    total_score: float
    bm25_score: float
    semantic_score: float
    entity_score: float
    temporal_score: float
    popularity_score: float
    explanation: str

class RankingRequest(BaseModel):
    conv_id: str
    original_query: str
    intent: str
    entities: Dict[str, Any]
    results: List[Dict[str, Any]]
    strategy: Optional[str] = "hybrid"
    max_results: Optional[int] = 10
    context_history: Optional[List[str]] = []

class RankingResponse(BaseModel):
    success: bool
    conv_id: str
    ranked_results: List[Dict[str, Any]]
    ranking_explanation: str
    total_results: int
    strategy_used: str
    confidence: float

# BM25 parameters
BM25_K1 = 1.2
BM25_B = 0.75

# Ranking weights for hybrid strategy
RANKING_WEIGHTS = {
    "bm25": 0.30,
    "semantic": 0.25,
    "entity": 0.20,
    "temporal": 0.15,
    "popularity": 0.10
}

# Hebrew stop words
HEBREW_STOP_WORDS = {
    "של", "את", "על", "אל", "מן", "עם", "לפי", "בין", "אצל", "נגד",
    "זה", "זו", "זאת", "הם", "הן", "הוא", "היא", "אני", "אתה", "את",
    "כל", "כמה", "מה", "איך", "למה", "מתי", "איפה", "מי", "באיזה",
    "ו", "ה", "ב", "ל", "מ", "ש", "כ", "א", "ע", "ר", "ת", "ן", "ם"
}

def tokenize_hebrew_text(text: str) -> List[str]:
    """Tokenize Hebrew text for BM25 scoring."""
    if not text:
        return []
    
    # Remove punctuation and normalize
    text = re.sub(r'[^\u0590-\u05FF\s]', ' ', text.lower())
    
    # Split into tokens
    tokens = text.split()
    
    # Remove stop words and short tokens
    tokens = [token for token in tokens 
              if len(token) > 1 and token not in HEBREW_STOP_WORDS]
    
    return tokens

def calculate_bm25_score(query_tokens: List[str], doc_tokens: List[str], 
                        corpus_stats: Dict[str, float]) -> float:
    """Calculate BM25 relevance score."""
    if not query_tokens or not doc_tokens:
        return 0.0
    
    score = 0.0
    doc_length = len(doc_tokens)
    avg_doc_length = corpus_stats.get("avg_doc_length", doc_length)
    
    # Count term frequencies in document
    doc_term_freq = Counter(doc_tokens)
    
    for query_term in query_tokens:
        if query_term in doc_term_freq:
            tf = doc_term_freq[query_term]
            
            # IDF approximation (simplified for efficiency)
            idf = corpus_stats.get(f"idf_{query_term}", 1.0)
            
            # BM25 formula
            numerator = tf * (BM25_K1 + 1)
            denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * (doc_length / avg_doc_length))
            
            score += idf * (numerator / denominator)
    
    return score

def calculate_entity_match_score(query_entities: Dict[str, Any], 
                               result: Dict[str, Any]) -> float:
    """Calculate entity matching score."""
    if not query_entities:
        return 1.0  # No entities to match
    
    matches = 0
    total_entities = len(query_entities)
    
    for entity_key, entity_value in query_entities.items():
        if entity_key == "government_number":
            if result.get("government_number") == entity_value:
                matches += 1
        elif entity_key == "decision_number":
            if result.get("decision_number") == entity_value:
                matches += 1
        elif entity_key == "topic":
            result_topics = result.get("topics", [])
            if isinstance(result_topics, list) and entity_value in result_topics:
                matches += 1
        elif entity_key == "ministries":
            result_ministries = result.get("ministries", [])
            if isinstance(result_ministries, list):
                if isinstance(entity_value, list):
                    if any(ministry in result_ministries for ministry in entity_value):
                        matches += 1
                elif entity_value in result_ministries:
                    matches += 1
        elif entity_key == "year":
            decision_date = result.get("decision_date", "")
            if str(entity_value) in decision_date:
                matches += 1
    
    return matches / total_entities if total_entities > 0 else 1.0

def calculate_temporal_score(result: Dict[str, Any], decay_months: int = 24) -> float:
    """Calculate temporal relevance score (newer = higher)."""
    decision_date_str = result.get("decision_date", "")
    if not decision_date_str:
        return 0.5  # Neutral score for missing dates
    
    try:
        # Parse date (assuming YYYY-MM-DD format)
        decision_date = datetime.strptime(decision_date_str[:10], "%Y-%m-%d")
        now = datetime.now()
        
        # Calculate months difference
        months_diff = (now.year - decision_date.year) * 12 + (now.month - decision_date.month)
        
        # Exponential decay: newer decisions get higher scores
        if months_diff <= 0:
            return 1.0  # Very recent or future
        elif months_diff >= decay_months:
            return 0.1  # Very old
        else:
            # Exponential decay over decay_months period
            return math.exp(-months_diff / (decay_months / 3))
            
    except (ValueError, TypeError):
        return 0.5  # Invalid date format

def calculate_popularity_score(result: Dict[str, Any]) -> float:
    """Calculate popularity score based on decision characteristics."""
    score = 0.5  # Base score
    
    # Boost for decisions with more content
    content_length = len(result.get("content", ""))
    if content_length > 500:
        score += 0.2
    elif content_length > 200:
        score += 0.1
    
    # Boost for decisions with multiple topics
    topics_count = len(result.get("topics", []))
    if topics_count >= 3:
        score += 0.2
    elif topics_count >= 2:
        score += 0.1
    
    # Boost for decisions involving multiple ministries
    ministries_count = len(result.get("ministries", []))
    if ministries_count >= 2:
        score += 0.1
    
    # Boost for decisions with specific numbers (often important)
    title = result.get("title", "")
    if re.search(r'\d+', title):
        score += 0.1
    
    return min(1.0, score)

async def calculate_semantic_score_with_gpt(
    query: str, 
    result: Dict[str, Any],
    intent: str
) -> Tuple[float, str]:
    """Calculate semantic relevance using GPT-4."""
    
    try:
        result_text = f"{result.get('title', '')} {result.get('content', '')}"[:500]
        
        system_prompt = f"""אתה מומחה בניתוח רלוונטיות של החלטות ממשלה לשאילתות משתמשים.

חזר מספר בין 0.0 ל-1.0 שמייצג עד כמה התוצאה רלוונטית לשאילתא.
כלל גם הסבר קצר בעברית.

כוונת השאילתא: {intent}

הערכה:
- 0.0-0.3: לא רלוונטי או רלוונטי מעט
- 0.4-0.6: רלוונטי באופן חלקי
- 0.7-0.8: רלוונטי מאוד
- 0.9-1.0: רלוונטי לחלוטין

החזר בפורמט JSON:
{{"score": 0.x, "explanation": "הסבר בעברית"}}"""

        user_prompt = f"""שאילתא: "{query}"

תוצאה להערכה:
{result_text}

עד כמה התוצאה רלוונטית לשאילתא?"""

        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.1  # Low temperature for consistent scoring
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            import json
            result_data = json.loads(content)
            score = float(result_data.get("score", 0.5))
            explanation = result_data.get("explanation", "ניתוח סמנטי")
            return max(0.0, min(1.0, score)), explanation
        except (json.JSONDecodeError, ValueError):
            # Fallback: try to extract score from text
            score_match = re.search(r'0\.\d+|1\.0', content)
            if score_match:
                score = float(score_match.group())
                return max(0.0, min(1.0, score)), "ניתוח GPT"
            else:
                return 0.5, "ניתוח בסיסי"
                
    except Exception as e:
        logger.error(f"GPT semantic scoring failed: {e}")
        return 0.5, "ניתוח fallback"

def prepare_corpus_statistics(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Prepare corpus statistics for BM25 calculation."""
    if not results:
        return {"avg_doc_length": 10.0}
    
    doc_lengths = []
    term_doc_freq = defaultdict(int)
    
    for result in results:
        # Combine title and content for analysis
        text = f"{result.get('title', '')} {result.get('content', '')}"
        tokens = tokenize_hebrew_text(text)
        doc_lengths.append(len(tokens))
        
        # Count terms for IDF calculation
        unique_terms = set(tokens)
        for term in unique_terms:
            term_doc_freq[term] += 1
    
    avg_doc_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 10.0
    total_docs = len(results)
    
    stats = {"avg_doc_length": avg_doc_length}
    
    # Calculate IDF for each term
    for term, doc_freq in term_doc_freq.items():
        idf = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5))
        stats[f"idf_{term}"] = max(0.1, idf)  # Minimum IDF
    
    return stats

async def rank_results_by_strategy(
    query: str,
    intent: str,
    entities: Dict[str, Any],
    results: List[Dict[str, Any]],
    strategy: RankingStrategy
) -> List[Tuple[Dict[str, Any], RankingScore]]:
    """Rank results according to the specified strategy."""
    
    if not results:
        return []
    
    # Prepare for scoring
    query_tokens = tokenize_hebrew_text(query)
    corpus_stats = prepare_corpus_statistics(results)
    
    ranked_results = []
    
    for result in results:
        # Calculate individual scores
        result_text = f"{result.get('title', '')} {result.get('content', '')}"
        result_tokens = tokenize_hebrew_text(result_text)
        
        bm25_score = calculate_bm25_score(query_tokens, result_tokens, corpus_stats)
        entity_score = calculate_entity_match_score(entities, result)
        temporal_score = calculate_temporal_score(result)
        popularity_score = calculate_popularity_score(result)
        
        # GPT semantic scoring (async)
        semantic_score, semantic_explanation = await calculate_semantic_score_with_gpt(
            query, result, intent
        )
        
        # Calculate total score based on strategy
        if strategy == RankingStrategy.RELEVANCE:
            total_score = (bm25_score * 0.6 + semantic_score * 0.4)
            explanation = f"רלוונטיות: BM25={bm25_score:.2f}, סמנטי={semantic_score:.2f}"
            
        elif strategy == RankingStrategy.TEMPORAL:
            total_score = (temporal_score * 0.7 + bm25_score * 0.3)
            explanation = f"זמן: {temporal_score:.2f}, רלוונטיות: {bm25_score:.2f}"
            
        elif strategy == RankingStrategy.DIVERSITY:
            # Balance relevance with topic diversity (implement simple version)
            diversity_bonus = 0.1 if len(result.get("topics", [])) >= 2 else 0.0
            total_score = (bm25_score * 0.4 + semantic_score * 0.3 + 
                          entity_score * 0.2 + diversity_bonus)
            explanation = f"גיוון נושאים: רלוונטיות + גיוון"
            
        else:  # HYBRID (default)
            total_score = (
                bm25_score * RANKING_WEIGHTS["bm25"] +
                semantic_score * RANKING_WEIGHTS["semantic"] +
                entity_score * RANKING_WEIGHTS["entity"] +
                temporal_score * RANKING_WEIGHTS["temporal"] +
                popularity_score * RANKING_WEIGHTS["popularity"]
            )
            explanation = f"היברידי: כל הגורמים משוקללים"
        
        ranking_score = RankingScore(
            total_score=total_score,
            bm25_score=bm25_score,
            semantic_score=semantic_score,
            entity_score=entity_score,
            temporal_score=temporal_score,
            popularity_score=popularity_score,
            explanation=explanation
        )
        
        ranked_results.append((result, ranking_score))
    
    # Sort by total score (descending)
    ranked_results.sort(key=lambda x: x[1].total_score, reverse=True)
    
    return ranked_results

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "QUERY_RANKER_BOT_3Q"}

@app.post("/rank", response_model=RankingResponse)
async def rank_results(request: RankingRequest):
    """Rank search results using the specified strategy."""
    
    try:
        logger.info(f"Processing ranking request: {request.conv_id}")
        
        # Validate strategy
        try:
            strategy = RankingStrategy(request.strategy or "hybrid")
        except ValueError:
            strategy = RankingStrategy.HYBRID
        
        # Rank results
        ranked_pairs = await rank_results_by_strategy(
            request.original_query,
            request.intent,
            request.entities,
            request.results,
            strategy
        )
        
        # Apply max_results limit
        max_results = min(request.max_results or 10, len(ranked_pairs))
        limited_pairs = ranked_pairs[:max_results]
        
        # Prepare ranked results with scoring information
        ranked_results = []
        for result, score in limited_pairs:
            enhanced_result = result.copy()
            enhanced_result["_ranking"] = {
                "total_score": round(score.total_score, 3),
                "bm25_score": round(score.bm25_score, 3),
                "semantic_score": round(score.semantic_score, 3),
                "entity_score": round(score.entity_score, 3),
                "temporal_score": round(score.temporal_score, 3),
                "popularity_score": round(score.popularity_score, 3),
                "explanation": score.explanation
            }
            ranked_results.append(enhanced_result)
        
        # Generate ranking explanation
        if ranked_pairs:
            top_score = ranked_pairs[0][1].total_score
            avg_score = sum(score.total_score for _, score in ranked_pairs) / len(ranked_pairs)
            explanation = f"דירוג לפי {strategy.value}: {len(ranked_results)} תוצאות. ציון מקסימלי: {top_score:.3f}, ממוצע: {avg_score:.3f}"
        else:
            explanation = "אין תוצאות לדירוג"
        
        # Calculate confidence based on score distribution
        if ranked_pairs:
            scores = [score.total_score for _, score in ranked_pairs]
            if len(scores) >= 2:
                score_spread = max(scores) - min(scores)
                confidence = min(0.95, 0.6 + score_spread * 0.35)  # Higher spread = more confidence
            else:
                confidence = 0.8
        else:
            confidence = 0.0
        
        response = RankingResponse(
            success=True,
            conv_id=request.conv_id,
            ranked_results=ranked_results,
            ranking_explanation=explanation,
            total_results=len(request.results),
            strategy_used=strategy.value,
            confidence=confidence
        )
        
        logger.info(f"Ranked {len(ranked_results)} results with strategy {strategy.value}")
        return response
        
    except Exception as e:
        logger.error(f"Error in rank_results: {e}")
        raise HTTPException(status_code=500, detail=f"Ranking failed: {str(e)}")

@app.get("/strategies")
async def get_ranking_strategies():
    """Get available ranking strategies and their descriptions."""
    
    strategies = {
        "relevance": {
            "name": "רלוונטיות",
            "description": "דירוג לפי רלוונטיות טקסטואלית וסמנטית",
            "weights": {"bm25": 0.6, "semantic": 0.4},
            "best_for": ["חיפוש כללי", "שאילתות מורכבות"]
        },
        "temporal": {
            "name": "זמני",
            "description": "דירוג לפי חדשות התוצאות (החלטות אחרונות קודם)",
            "weights": {"temporal": 0.7, "relevance": 0.3},
            "best_for": ["חיפוש החלטות אחרונות", "מעקב אחר התפתחויות"]
        },
        "hybrid": {
            "name": "היברידי",
            "description": "שילוב מאוזן של כל הגורמים",
            "weights": RANKING_WEIGHTS,
            "best_for": ["רוב השאילתות", "דירוג מאוזן"]
        },
        "diversity": {
            "name": "גיוון",
            "description": "מקסום גיוון נושאים בתוצאות",
            "weights": {"relevance": 0.7, "diversity": 0.3},
            "best_for": ["חקירה רחבה", "סקירת נושאים"]
        }
    }
    
    return {
        "available_strategies": strategies,
        "default_strategy": "hybrid",
        "ranking_factors": [
            "רלוונטיות טקסטואלית (BM25)",
            "רלוונטיות סמנטית (GPT)",
            "התאמת ישויות",
            "רלוונטיות זמנית",
            "פופולריות החלטה"
        ]
    }

@app.get("/stats")
async def get_ranking_stats():
    """Get ranking statistics and performance metrics."""
    
    return {
        "ranking_weights": RANKING_WEIGHTS,
        "bm25_parameters": {
            "k1": BM25_K1,
            "b": BM25_B
        },
        "temporal_decay_months": 24,
        "hebrew_stop_words_count": len(HEBREW_STOP_WORDS),
        "supported_languages": ["עברית", "English (partial)"],
        "max_results_limit": 50,
        "default_max_results": 10
    }

if __name__ == "__main__":
    import uvicorn
    
    port = config.port
    logger.info(f"Starting QUERY_RANKER_BOT_3Q on port {port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )