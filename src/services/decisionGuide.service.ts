import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api';

export interface DecisionGuideAnalysis {
  id: string;
  criteriaScores: Array<{
    criterion: string;
    score: number;
    weight: number;
    explanation: string;
    reference_from_document?: string;
    specific_improvement?: string;
  }>;
  weightedScore: number;
  feasibilityLevel: 'low' | 'medium' | 'high';
  recommendations: string[];
  modelUsed: string;
  processingTime: number;
  misuse_detected?: boolean;
  misuse_message?: string;
}

export async function clearDecisionGuideCache(): Promise<void> {
  try {
    await axios.post(`${API_BASE_URL}/decision-guide/clear-cache`);
  } catch (error) {
    console.error('Failed to clear cache:', error);
    throw new Error('Failed to clear cache');
  }
}

export async function analyzeDecisionDraft(
  file: File | null,
  text: string
): Promise<DecisionGuideAnalysis> {
  const formData = new FormData();
  
  if (file) {
    formData.append('file', file);
  } else if (text) {
    formData.append('text', text);
  } else {
    throw new Error('Either file or text must be provided');
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/decision-guide/analyze`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds timeout for large documents
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data.error || 'Invalid request');
      }
      throw new Error(error.response?.data?.error || 'Analysis failed');
    }
    throw error;
  }
}