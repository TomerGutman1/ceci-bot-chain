import axios from 'axios';

interface DecisionGuideRequest {
  id: string;
  text: string;
  documentInfo: {
    type: 'text' | 'file';
    originalName: string;
    size: number;
  };
  timestamp: Date;
}

interface CriteriaScore {
  criterion: string;
  score: number;
  weight: number;
  explanation: string;
  reference_from_document?: string;
  specific_improvement?: string;
}

interface DecisionGuideResponse {
  criteriaScores: CriteriaScore[];
  weightedScore: number;
  feasibilityLevel: 'low' | 'medium' | 'high';
  recommendations: string[];
  modelUsed: string;
  processingTime: number;
  misuse_detected?: boolean;
  misuse_message?: string;
}

// Criteria weights from the eval_prompt
const CRITERIA_WEIGHTS: Record<string, number> = {
  'לוח זמנים מחייב': 0.17,
  'צוות מתכלל': 0.07,
  'גורם מתכלל יחיד': 0.05,
  'מנגנון דיווח/בקרה': 0.09,
  'מנגנון מדידה והערכה': 0.06,
  'מנגנון ביקורת חיצונית': 0.04,
  'משאבים נדרשים': 0.19,
  'מעורבות של מספר דרגים בתהליך': 0.07,
  'מבנה סעיפים וחלוקת עבודה ברורה': 0.09,
  'מנגנון יישום בשטח': 0.09,
  'גורם מכריע': 0.03,
  'שותפות בין מגזרית': 0.03,
  'מדדי תוצאה ומרכיבי הצלחה': 0.02
};

export async function processDecisionGuideRequest(
  request: DecisionGuideRequest
): Promise<DecisionGuideResponse> {
  const startTime = Date.now();
  
  try {
    // Call the decision guide bot
    const botUrl = process.env.DECISION_GUIDE_BOT_URL || `http://decision-guide-bot:8018`;
    
    const response = await axios.post(`${botUrl}/analyze`, {
      text: request.text,
      documentInfo: request.documentInfo,
      requestId: request.id
    }, {
      timeout: 300000, // 300 second (5 minute) timeout for long documents
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const processingTime = Date.now() - startTime;
    
    // Process and validate the response
    const result = response.data;
    
    // Check for misuse detection
    if (result.misuse_detected) {
      return {
        criteriaScores: [],
        weightedScore: 0,
        feasibilityLevel: 'low',
        recommendations: [],
        modelUsed: result.model_used || 'gpt-4o',
        processingTime,
        misuse_detected: true,
        misuse_message: result.misuse_message
      };
    }
    
    // Calculate weighted score
    let weightedScore = 0;
    const criteriaScores: CriteriaScore[] = result.criteria_scores.map((score: any) => {
      const weight = CRITERIA_WEIGHTS[score.criterion] || 0;
      // Convert 0-5 scale to 1-10 scale
      const normalizedScore = Math.round((score.score * 2) + ((score.score > 0) ? 0 : 1));
      weightedScore += normalizedScore * weight;
      
      return {
        criterion: score.criterion,
        score: normalizedScore,
        weight: weight,
        explanation: score.explanation,
        reference_from_document: score.reference_from_document,
        specific_improvement: score.specific_improvement
      };
    });
    
    // Determine feasibility level
    let feasibilityLevel: 'low' | 'medium' | 'high';
    if (weightedScore < 5) {
      feasibilityLevel = 'low';
    } else if (weightedScore < 7.5) {
      feasibilityLevel = 'medium';
    } else {
      feasibilityLevel = 'high';
    }
    
    return {
      criteriaScores,
      weightedScore: Math.round(weightedScore * 10) / 10, // Round to 1 decimal
      feasibilityLevel,
      recommendations: result.recommendations || [],
      modelUsed: result.model_used || 'gpt-4o-turbo',
      processingTime
    };
    
  } catch (error) {
    console.error('[DecisionGuideService] Processing error:', error);
    
    // Always throw the error - no mock responses
    throw error;
  }
}