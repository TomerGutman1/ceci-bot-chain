import { createClient } from '@supabase/supabase-js';

interface Decision {
  id: number;
  decision_date: string;
  decision_number: string;
  committee: string | null;
  decision_title: string;
  decision_content: string;
  decision_url: string;
  summary: string;
  operativity: string;
  tags_policy_area: string;
  tags_government_body: string;
  tags_location: string | null;
  all_tags: string;
  government_number: string;
  prime_minister: string;
  decision_key: string;
  created_at: string;
  updated_at: string;
}

export class DataProviderService {
  private decisions: Decision[] = [];
  private isLoaded: boolean = false;
  private loadingPromise: Promise<void> | null = null;
  private supabase: any;
  private readonly EDGE_FUNCTION_URL = 'https://hthrsrekzyobmlvtquub.supabase.co/functions/v1/get-all-decisions';
  private readonly SUPABASE_URL = process.env.SUPABASE_URL || 'https://hthrsrekzyobmlvtquub.supabase.co';
  private readonly SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh0aHJzcmVrenlvYm1sdnRxdXViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5Mzc5MzMsImV4cCI6MjA2MzUxMzkzM30.V4ZIY4I1R3tUIWkuEU7t0ExC8gbLJKYjIPvrERbdbIw';
  private readonly SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY || '';

  constructor() {
    // Use service key if available for better access, otherwise use anon key
    const key = this.SUPABASE_SERVICE_KEY || this.SUPABASE_ANON_KEY;
    this.supabase = createClient(this.SUPABASE_URL, key);
    console.log('[DataProviderService] Initialized with', this.SUPABASE_SERVICE_KEY ? 'service key' : 'anon key');
  }

  /**
   * Get all decisions - loads them if not already loaded
   */
  async getAllDecisions(): Promise<Decision[]> {
    if (!this.isLoaded && !this.loadingPromise) {
      this.loadingPromise = this.loadDecisions();
    }
    
    if (this.loadingPromise) {
      await this.loadingPromise;
    }
    
    return this.decisions;
  }

  /**
   * Force reload of decisions
   */
  async reloadDecisions(): Promise<void> {
    this.isLoaded = false;
    this.decisions = [];
    this.loadingPromise = this.loadDecisions();
    await this.loadingPromise;
  }

  private async loadDecisions(): Promise<void> {
    try {
      console.log('[DataProviderService] Loading decisions from Supabase REST API...');
      
      // Try direct Supabase REST API with pagination
      let allDecisions: Decision[] = [];
      let from = 0;
      const limit = 1000;
      let hasMore = true;

      while (hasMore) {
        const { data, error } = await this.supabase
          .from('israeli_government_decisions')
          .select('*')
          .order('decision_date', { ascending: false })
          .range(from, from + limit - 1);

        if (error) {
          console.error('[DataProviderService] Error loading from Supabase:', error);
          // Try Edge Function as fallback
          await this.loadFromEdgeFunction();
          return;
        }

        if (data && data.length > 0) {
          allDecisions = allDecisions.concat(data);
          console.log(`[DataProviderService] Loaded ${allDecisions.length} decisions so far...`);
          
          if (data.length < limit) {
            hasMore = false;
          } else {
            from += limit;
          }
        } else {
          hasMore = false;
        }
      }

      this.decisions = allDecisions;
      this.isLoaded = true;
      this.loadingPromise = null;
      console.log(`[DataProviderService] Successfully loaded ${this.decisions.length} decisions`);

    } catch (error) {
      console.error('[DataProviderService] Error loading decisions:', error);
      // Try Edge Function as fallback
      await this.loadFromEdgeFunction();
    }
  }

  private async loadFromEdgeFunction(): Promise<void> {
    try {
      console.log('[DataProviderService] Attempting to load from Edge Function...');
      
      const response = await fetch(this.EDGE_FUNCTION_URL, {
        headers: {
          'Authorization': `Bearer ${this.SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Edge Function returned ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        this.decisions = result.data;
        this.isLoaded = true;
        this.loadingPromise = null;
        console.log(`[DataProviderService] Successfully loaded ${this.decisions.length} decisions from Edge Function`);
      } else {
        throw new Error('Invalid response from Edge Function');
      }

    } catch (error) {
      console.error('[DataProviderService] Error loading from Edge Function:', error);
      this.decisions = [];
      this.isLoaded = false;
      this.loadingPromise = null;
    }
  }

  /**
   * Export decisions as CSV format for PandasAI
   */
  async getDecisionsAsCSV(): Promise<string> {
    const decisions = await this.getAllDecisions();
    
    if (decisions.length === 0) {
      throw new Error('No decisions available');
    }

    // Create CSV header
    const headers = Object.keys(decisions[0]).join(',');
    
    // Create CSV rows
    const rows = decisions.map(decision => {
      return Object.values(decision).map(value => {
        // Escape values that contain commas or quotes
        const strValue = String(value || '');
        if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
          return `"${strValue.replace(/"/g, '""')}"`;
        }
        return strValue;
      }).join(',');
    });

    return [headers, ...rows].join('\n');
  }

  /**
   * Get status information
   */
  getStatus() {
    return {
      isLoaded: this.isLoaded,
      isLoading: this.loadingPromise !== null,
      decisionCount: this.decisions.length,
      source: this.decisions.length > 0 ? 'Supabase/Edge Function' : 'Not loaded'
    };
  }
}

// Singleton instance
let instance: DataProviderService | null = null;

export function getDataProviderService(): DataProviderService {
  if (!instance) {
    instance = new DataProviderService();
  }
  return instance;
}
