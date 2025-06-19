import axios from 'axios';
import { getDataProviderService } from './dataProviderService';

// Types for PandasAI service
export interface PandasAIQuery {
  query: string;
  intent_type?: 'specific' | 'topic' | 'date' | 'government' | 'stats' | 'combined';
  parameters?: Record<string, any>;
  session_id?: string;  // Add session support
}

export interface PandasAIResponse {
  success: boolean;
  answer: any;
  query_type: string;
  metadata?: Record<string, any>;
  error?: string;
  session_id?: string;  // Session ID from response
  query_id?: string;    // Query ID for reference
}

export interface DecisionDetails {
  number: string;
  title: string;
  date: string;
  content: string;
  summary: string;
  government: number;
  prime_minister: string;
  committee: string;
  tags: {
    policy_area: string;
    government_body: string;
    location: string;
  };
  url: string;
}

export interface Statistics {
  total_decisions: number;
  governments: Record<string, number>;
  years: Record<string, number>;
  latest_decision: any;
  current_government: number;
  policy_areas: Record<string, number>;
}

export class PandasAIService {
  private baseUrl: string;
  private dataProvider = getDataProviderService();
  private dataUploaded = false;
  private isHealthy: boolean = false;

  constructor(baseUrl: string = process.env.PANDASAI_SERVICE_URL || 'http://localhost:8001') {
    this.baseUrl = baseUrl;
    this.checkHealth();
  }

  /**
   * Check if PandasAI service is healthy
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseUrl}/`);
      this.isHealthy = response.data.status === 'healthy';
      console.log('[PandasAIService] Health check:', response.data);
      
      // Upload data if not already uploaded and service is healthy
      if (this.isHealthy && !this.dataUploaded) {
        await this.uploadDataToPandasAI();
      }
      
      return this.isHealthy;
    } catch (error) {
      console.error('[PandasAIService] Health check failed:', error);
      this.isHealthy = false;
      return false;
    }
  }

  /**
   * Upload data from DataProvider to PandasAI
   */
  private async uploadDataToPandasAI(): Promise<void> {
    try {
      console.log('[PandasAI] Uploading data from DataProvider...');
      
      // Get all decisions from DataProvider
      const decisions = await this.dataProvider.getAllDecisions();
      
      if (decisions.length === 0) {
        console.warn('[PandasAI] No data to upload');
        return;
      }
      
      // Upload to PandasAI
      const response = await axios.post(`${this.baseUrl}/upload-data`, {
        data: decisions,
        source: 'DataProvider/Supabase'
      }, {
        timeout: 30000 // 30 seconds for large data
      });
      
      if (response.data.success) {
        this.dataUploaded = true;
        console.log(`[PandasAI] Successfully uploaded ${response.data.records_loaded} decisions`);
      } else {
        console.error('[PandasAI] Failed to upload data:', response.data);
      }
      
    } catch (error) {
      console.error('[PandasAI] Error uploading data:', error instanceof Error ? error.message : 'Unknown error');
      // Don't throw - PandasAI can still work with its own data loading
    }
  }

  /**
   * Process a query using PandasAI
   */
  async query(query: string, intentType?: string, parameters?: Record<string, any>, sessionId?: string): Promise<PandasAIResponse> {
    if (!this.isHealthy) {
      await this.checkHealth();
      if (!this.isHealthy) {
        throw new Error('PandasAI service is not available');
      }
    }

    try {
      const response = await axios.post<PandasAIResponse>(`${this.baseUrl}/query`, {
        query,
        intent_type: intentType,
        parameters,
        session_id: sessionId
      });

      return response.data;
    } catch (error) {
      console.error('[PandasAIService] Query error:', error);
      throw error;
    }
  }

  /**
   * Get a specific decision by number
   */
  async getDecisionByNumber(decisionNumber: string): Promise<DecisionDetails | null> {
    const response = await this.query(
      `החלטה ${decisionNumber}`,
      'specific',
      { decision_number: decisionNumber }
    );

    if (response.success && response.answer.found) {
      return response.answer.decision;
    }

    return null;
  }

  /**
   * Search decisions by topic
   */
  async searchByTopic(topic: string, limit: number = 10): Promise<any[]> {
    const response = await this.query(
      `הצג ${limit} החלטות בנושא ${topic} עם הפרטים: מספר החלטה, כותרת, תאריך, תקציר`,
      'topic',
      { topic, limit }
    );

    if (response.success && Array.isArray(response.answer)) {
      return response.answer;
    }

    return [];
  }

  /**
   * Search decisions by date range
   */
  async searchByDateRange(startDate: string, endDate?: string, limit: number = 10): Promise<any[]> {
    let query: string;
    
    if (endDate) {
      query = `הצג ${limit} החלטות בין ${startDate} ל-${endDate}`;
    } else {
      query = `הצג ${limit} החלטות מ-${startDate} ואילך`;
    }

    const response = await this.query(
      query,
      'date',
      { start_date: startDate, end_date: endDate, limit }
    );

    if (response.success && Array.isArray(response.answer)) {
      return response.answer;
    }

    return [];
  }

  /**
   * Search decisions by government
   */
  async searchByGovernment(governmentNumber: number | 'current', limit: number = 10): Promise<any[]> {
    const query = governmentNumber === 'current' 
      ? `הצג ${limit} החלטות של הממשלה הנוכחית`
      : `הצג ${limit} החלטות של ממשלה ${governmentNumber}`;

    const response = await this.query(
      query,
      'government',
      { government_number: governmentNumber, limit }
    );

    if (response.success && Array.isArray(response.answer)) {
      return response.answer;
    }

    return [];
  }

  /**
   * Get statistics
   */
  async getStatistics(): Promise<Statistics> {
    try {
      const response = await axios.get<Statistics>(`${this.baseUrl}/stats`);
      return response.data;
    } catch (error) {
      console.error('[PandasAIService] Stats error:', error);
      throw error;
    }
  }

  /**
   * Process natural language query with intent detection
   */
  async processNaturalQuery(userQuery: string, sessionId?: string): Promise<{
    type: 'decisions' | 'statistics' | 'specific' | 'error';
    data: any;
    formatted: string;
    session_id?: string;
    query_id?: string;
  }> {
    try {
      // Detect query intent
      const intent = this.detectQueryIntent(userQuery);
      
      // Process based on intent
      const response = await this.query(userQuery, intent.type, intent.parameters, sessionId);

      if (!response.success) {
        return {
          type: 'error',
          data: null,
          formatted: response.error || 'שגיאה בעיבוד השאילתה',
          session_id: response.session_id,
          query_id: response.query_id
        };
      }

      // Format response based on query type
      switch (response.query_type) {
        case 'specific_decision':
          if (response.answer.found) {
            const decision = response.answer.decision;
            return {
              type: 'specific',
              data: decision,
              formatted: this.formatDecision(decision),
              session_id: response.session_id,
              query_id: response.query_id
            };
          } else {
            return {
              type: 'error',
              data: null,
              formatted: response.answer.message,
              session_id: response.session_id,
              query_id: response.query_id
            };
          }

        case 'list':
          return {
            type: 'decisions',
            data: response.answer,
            formatted: this.formatDecisionsList(response.answer),
            session_id: response.session_id,
            query_id: response.query_id
          };

        case 'numeric':
          return {
            type: 'statistics',
            data: response.answer,
            formatted: this.formatStatistics(response.answer),
            session_id: response.session_id,
            query_id: response.query_id
          };

        default:
          return {
            type: 'decisions',
            data: response.answer,
            formatted: String(response.answer),
            session_id: response.session_id,
            query_id: response.query_id
          };
      }
    } catch (error) {
      console.error('[PandasAIService] Natural query error:', error);
      return {
        type: 'error',
        data: null,
        formatted: 'שגיאה בתקשורת עם שירות הניתוח'
      };
    }
  }

  /**
   * Detect query intent
   */
  private detectQueryIntent(query: string): { type: string; parameters: any } {
    // Specific decision pattern
    const specificMatch = query.match(/החלטה\s*(?:מספר\s*)?(\d+)/);
    if (specificMatch) {
      return {
        type: 'specific',
        parameters: { decision_number: specificMatch[1] }
      };
    }

    // Statistics patterns
    if (query.includes('כמה') || query.includes('סטטיסטיקה') || query.includes('התפלגות')) {
      return { type: 'stats', parameters: {} };
    }

    // Government patterns
    if (query.includes('ממשלה') || query.includes('הממשלה הנוכחית')) {
      return { 
        type: 'government', 
        parameters: { 
          current: query.includes('הנוכחית')
        } 
      };
    }

    // Date patterns
    if (query.match(/\d{4}/) || query.includes('השנה') || query.includes('החודש')) {
      return { type: 'date', parameters: {} };
    }

    // Default to topic search
    return { type: 'topic', parameters: {} };
  }

  /**
   * Format a single decision
   */
  private formatDecision(decision: DecisionDetails): string {
    let formatted = `# 📋 החלטה ${decision.number}`;
    
    if (decision.title) {
      formatted += ` - ${decision.title}`;
    }
    
    formatted += `\n\n`;
    
    // Metadata
    formatted += `## 📊 פרטי ההחלטה\n\n`;
    if (decision.date) formatted += `📅 **תאריך:** ${new Date(decision.date).toLocaleDateString('he-IL')}\n`;
    if (decision.government) formatted += `🏛️ **ממשלה:** ${decision.government}\n`;
    if (decision.prime_minister) formatted += `👤 **ראש ממשלה:** ${decision.prime_minister}\n`;
    if (decision.committee) formatted += `🏢 **ועדה:** ${decision.committee}\n`;
    
    // Tags
    if (decision.tags.policy_area || decision.tags.government_body || decision.tags.location) {
      formatted += `\n## 🏷️ תגיות\n\n`;
      if (decision.tags.policy_area) formatted += `**תחום:** ${decision.tags.policy_area}\n`;
      if (decision.tags.government_body) formatted += `**גופים:** ${decision.tags.government_body}\n`;
      if (decision.tags.location) formatted += `**מיקום:** ${decision.tags.location}\n`;
    }
    
    // Summary
    if (decision.summary) {
      formatted += `\n## 📝 תקציר\n\n${decision.summary}\n`;
    }
    
    // Content
    if (decision.content) {
      formatted += `\n## 📄 תוכן מלא\n\n${decision.content}\n`;
    }
    
    // Link
    formatted += `\n## 🔗 קישור\n\n[לצפייה באתר הממשלה](${decision.url})\n`;
    
    return formatted;
  }

  /**
   * Format a list of decisions
   */
  private formatDecisionsList(decisions: any[]): string {
    if (!decisions || decisions.length === 0) {
      return 'לא נמצאו החלטות התואמות לחיפוש.';
    }

    return decisions.map((d, index) => {
      // Use the formatted fields from PandasAI
      const parts = [
        `**${index + 1}. החלטה ${d.decision_number}**`,
        d.decision_title ? `**${d.decision_title}**` : ''
      ];
      
      const metadata = [];
      if (d.decision_date) metadata.push(`📅 תאריך: ${d.decision_date}`);
      if (d.government_number) metadata.push(`🏛️ ממשלה: ${d.government_number}`);
      if (d.prime_minister) metadata.push(`👤 ראש ממשלה: ${d.prime_minister}`);
      if (d.government_bodies) metadata.push(`🏢 גופים: ${d.government_bodies}`);
      
      if (metadata.length > 0) {
        parts.push(metadata.join(' | '));
      }
      
      if (d.summary) {
        parts.push(`📝 תקציר: ${d.summary}`);
      }
      
      if (d.url) {
        parts.push(`🔗 [קרא עוד](${d.url})`);
      }
      
      return parts.join('\n');
    }).join('\n\n---\n\n');
  }

  /**
   * Format statistics
   */
  private formatStatistics(stats: any): string {
    if (stats.value !== undefined) {
      return `התוצאה: **${stats.formatted}**`;
    }
    
    // Format complex statistics
    let formatted = '## 📊 סטטיסטיקות\n\n';
    
    Object.entries(stats).forEach(([key, value]) => {
      formatted += `**${key}:** ${value}\n`;
    });
    
    return formatted;
  }

  /**
   * Reload data in PandasAI service
   */
  async reloadData(): Promise<boolean> {
    try {
      const response = await axios.post(`${this.baseUrl}/reload`);
      return response.data.success;
    } catch (error) {
      console.error('[PandasAIService] Reload error:', error);
      return false;
    }
  }

  /**
   * Get session information
   */
  async getSessionInfo(sessionId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.baseUrl}/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('[PandasAIService] Session info error:', error);
      throw error;
    }
  }

  /**
   * Get sessions statistics
   */
  async getSessionsStats(): Promise<any> {
    try {
      const response = await axios.get(`${this.baseUrl}/sessions/stats`);
      return response.data;
    } catch (error) {
      console.error('[PandasAIService] Sessions stats error:', error);
      throw error;
    }
  }

  /**
   * Cleanup expired sessions
   */
  async cleanupSessions(): Promise<any> {
    try {
      const response = await axios.post(`${this.baseUrl}/sessions/cleanup`);
      return response.data;
    } catch (error) {
      console.error('[PandasAIService] Sessions cleanup error:', error);
      throw error;
    }
  }
}

// Singleton instance
let instance: PandasAIService | null = null;

export function getPandasAIService(): PandasAIService {
  if (!instance) {
    instance = new PandasAIService();
  }
  return instance;
}
