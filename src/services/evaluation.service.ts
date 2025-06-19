export interface EvaluationResult {
  id?: string;
  decisionNumber?: string;
  decisionDate?: string;
  governmentNumber?: number;
  parameters: EvaluationParameter[];
  totalScore: number;
  evaluationText: string;
  createdAt: Date;
  updatedAt?: Date;
}

export interface EvaluationParameter {
  name: string;
  hebrewName: string;
  score: number;
  weight: number;
  description: string;
}

export interface DecisionEvaluation {
  id: string;
  decision_num: string;
  decision_date: string;
  eval: string;
  created_at: string;
  updated_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5173/api';

export class EvaluationService {
  private static instance: EvaluationService;
  
  private constructor() {}
  
  static getInstance(): EvaluationService {
    if (!EvaluationService.instance) {
      EvaluationService.instance = new EvaluationService();
    }
    return EvaluationService.instance;
  }

  async evaluateDecision(params: {
    decisionText: string;
    decisionNumber?: string;
    governmentNumber?: number;
  }): Promise<EvaluationResult> {
    const response = await fetch(`${API_BASE_URL}/evaluations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        decision_text: params.decisionText,
        decision_number: params.decisionNumber,
        government_number: params.governmentNumber,
      }),
    });

    if (!response.ok) {
      throw new Error(`Evaluation API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getEvaluation(
    decisionNumber: string, 
    decisionDate: string
  ): Promise<DecisionEvaluation | null> {
    const response = await fetch(
      `${API_BASE_URL}/evaluations/${decisionNumber}?date=${decisionDate}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Evaluation API error: ${response.statusText}`);
    }

    return response.json();
  }

  async listEvaluations(params?: {
    limit?: number;
    offset?: number;
    governmentNumber?: number;
  }): Promise<{
    evaluations: DecisionEvaluation[];
    total: number;
  }> {
    const queryParams = new URLSearchParams();
    
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.governmentNumber) {
      queryParams.append('government_number', params.governmentNumber.toString());
    }

    const response = await fetch(
      `${API_BASE_URL}/evaluations?${queryParams.toString()}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Evaluation API error: ${response.statusText}`);
    }

    return response.json();
  }

  parseEvaluationScores(evaluationText: string): {
    parameters: Array<{
      name: string;
      score: number;
      weight: number;
    }>;
    totalScore: number;
  } {
    const parameters: Array<{ name: string; score: number; weight: number }> = [];
    let totalScore = 0;

    // Parse logic here based on EVALUATION_PROMPT format
    const lines = evaluationText.split('\n');
    for (const line of lines) {
      // Extract parameter scores and weights
      // Add to parameters array
    }

    return { parameters, totalScore };
  }
}

export default EvaluationService.getInstance();
