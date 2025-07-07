import { getDataProviderService } from './dataProviderService';

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

interface StatisticsFilters {
  startDate?: string;
  endDate?: string;
  government?: string;
  policyArea?: string;
  operativity?: string;
  committee?: string;
  primeMinister?: string;
}

interface OverviewStats {
  totalDecisions: number;
  operativeDecisions: number;
  nonOperativeDecisions: number;
  governmentCount: number;
  policyAreaCount: number;
  averageDecisionsPerMonth: number;
  recentDecisions: number;
}

interface TimelineEntry {
  month: string;
  year: number;
  count: number;
  operativeCount: number;
  nonOperativeCount: number;
}

interface PolicyAreaStats {
  name: string;
  count: number;
  operativeCount: number;
  percentage: number;
}

interface CommitteeStats {
  name: string;
  count: number;
  percentage: number;
}

interface GovernmentStats {
  number: string;
  primeMinister: string;
  count: number;
  operativeCount: number;
  startDate: string;
  endDate: string;
}

export class StatisticsService {
  private dataProvider = getDataProviderService();

  /**
   * Get filtered decisions based on criteria
   */
  async getFilteredDecisions(filters: StatisticsFilters = {}): Promise<Decision[]> {
    const decisions = await this.dataProvider.getAllDecisions();
    
    return decisions.filter(decision => {
      // Filter out decisions with invalid dates
      if (!decision.decision_date || decision.decision_date === null) return false;
      // Date filtering
      if (filters.startDate && decision.decision_date < filters.startDate) return false;
      if (filters.endDate && decision.decision_date > filters.endDate) return false;
      
      // Government filtering
      if (filters.government && decision.government_number !== filters.government) return false;
      
      // Policy area filtering - check each tag separately
      if (filters.policyArea) {
        if (!decision.tags_policy_area) return false;
        const areas = decision.tags_policy_area.split(/[,;]/).map(area => area.trim());
        if (!areas.some(area => area === filters.policyArea)) return false;
      }
      
      // Operativity filtering
      if (filters.operativity && decision.operativity !== filters.operativity) return false;
      
      // Committee filtering
      if (filters.committee && decision.committee !== filters.committee) return false;
      
      // Prime Minister filtering
      if (filters.primeMinister && decision.prime_minister !== filters.primeMinister) return false;
      
      return true;
    });
  }

  /**
   * Get overview statistics
   */
  async getOverview(filters: StatisticsFilters = {}): Promise<OverviewStats> {
    const decisions = await this.getFilteredDecisions(filters);
    
    const operativeDecisions = decisions.filter(d => d.operativity === 'אופרטיבית').length;
    const nonOperativeDecisions = decisions.filter(d => d.operativity === 'דקלרטיבית').length;
    
    const uniqueGovernments = new Set(decisions.map(d => d.government_number)).size;
    const uniquePolicyAreas = new Set(decisions.map(d => d.tags_policy_area)).size;
    
    // Calculate average decisions per month
    const dateSpan = this.getDateSpan(decisions);
    const averageDecisionsPerMonth = dateSpan.months > 0 ? Math.round(decisions.length / dateSpan.months) : 0;
    
    // Recent decisions (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentDecisions = decisions.filter(d => new Date(d.decision_date) >= thirtyDaysAgo).length;
    
    return {
      totalDecisions: decisions.length,
      operativeDecisions,
      nonOperativeDecisions,
      governmentCount: uniqueGovernments,
      policyAreaCount: uniquePolicyAreas,
      averageDecisionsPerMonth,
      recentDecisions
    };
  }

  /**
   * Get timeline data for charts
   */
  async getTimeline(filters: StatisticsFilters = {}): Promise<TimelineEntry[]> {
    const decisions = await this.getFilteredDecisions(filters);
    
    const timeline: Map<string, TimelineEntry> = new Map();
    
    decisions.forEach(decision => {
      // Skip decisions with invalid dates
      if (!decision.decision_date || decision.decision_date === null) return;
      
      const date = new Date(decision.decision_date);
      // Skip invalid dates
      if (isNaN(date.getTime()) || date.getFullYear() < 1990) return;
      
      const month = date.toLocaleString('he-IL', { month: 'long' });
      const year = date.getFullYear();
      const key = `${year}-${month}`;
      
      if (!timeline.has(key)) {
        timeline.set(key, {
          month,
          year,
          count: 0,
          operativeCount: 0,
          nonOperativeCount: 0
        });
      }
      
      const entry = timeline.get(key)!;
      entry.count++;
      
      if (decision.operativity === 'אופרטיבית') {
        entry.operativeCount++;
      } else if (decision.operativity === 'דקלרטיבית') {
        entry.nonOperativeCount++;
      }
    });
    
    return Array.from(timeline.values()).sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year;
      return a.month.localeCompare(b.month, 'he-IL');
    });
  }

  /**
   * Get policy area statistics
   */
  async getPolicyAreaStats(filters: StatisticsFilters = {}): Promise<PolicyAreaStats[]> {
    const decisions = await this.getFilteredDecisions(filters);
    
    const policyAreas: Map<string, { total: number; operative: number }> = new Map();
    
    decisions.forEach(decision => {
      if (!decision.tags_policy_area) return;
      
      // Split by both comma and semicolon
      const areas = decision.tags_policy_area.split(/[,;]/).map(area => area.trim()).filter(area => area);
      
      areas.forEach(area => {
        if (!policyAreas.has(area)) {
          policyAreas.set(area, { total: 0, operative: 0 });
        }
        
        const stats = policyAreas.get(area)!;
        stats.total++;
        
        if (decision.operativity === 'אופרטיבית') {
          stats.operative++;
        }
      });
    });
    
    const total = decisions.length;
    
    return Array.from(policyAreas.entries())
      .map(([name, stats]) => ({
        name,
        count: stats.total,
        operativeCount: stats.operative,
        percentage: total > 0 ? Math.round((stats.total / total) * 100) : 0
      }))
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Get committee statistics
   */
  async getCommitteeStats(filters: StatisticsFilters = {}): Promise<CommitteeStats[]> {
    const decisions = await this.getFilteredDecisions(filters);
    
    const committees: Map<string, number> = new Map();
    
    decisions.forEach(decision => {
      const committee = decision.committee || 'לא מוגדר';
      committees.set(committee, (committees.get(committee) || 0) + 1);
    });
    
    const total = decisions.length;
    
    return Array.from(committees.entries())
      .map(([name, count]) => ({
        name,
        count,
        percentage: total > 0 ? Math.round((count / total) * 100) : 0
      }))
      .sort((a, b) => b.count - a.count);
  }

  /**
   * Get government statistics
   */
  async getGovernmentStats(filters: StatisticsFilters = {}): Promise<GovernmentStats[]> {
    const decisions = await this.getFilteredDecisions(filters);
    
    const governments: Map<string, { 
      primeMinister: string; 
      count: number; 
      operative: number; 
      dates: string[] 
    }> = new Map();
    
    decisions.forEach(decision => {
      const gov = decision.government_number;
      if (!gov || gov === null) return;
      
      if (!governments.has(gov)) {
        governments.set(gov, {
          primeMinister: decision.prime_minister,
          count: 0,
          operative: 0,
          dates: []
        });
      }
      
      const stats = governments.get(gov)!;
      stats.count++;
      stats.dates.push(decision.decision_date);
      
      if (decision.operativity === 'אופרטיבית') {
        stats.operative++;
      }
    });
    
    return Array.from(governments.entries())
      .map(([number, stats]) => {
        const validDates = stats.dates
          .filter(d => d && d !== null)
          .map(d => new Date(d))
          .filter(d => !isNaN(d.getTime()) && d.getFullYear() >= 1990);
        
        const minTime = validDates.length > 0 ? Math.min(...validDates.map(d => d.getTime())) : Date.now();
        const maxTime = validDates.length > 0 ? Math.max(...validDates.map(d => d.getTime())) : Date.now();
        
        return {
          number,
          primeMinister: stats.primeMinister,
          count: stats.count,
          operativeCount: stats.operative,
          startDate: new Date(minTime).toISOString().split('T')[0],
          endDate: new Date(maxTime).toISOString().split('T')[0]
        };
      })
      .sort((a, b) => parseInt(b.number) - parseInt(a.number));
  }

  /**
   * Get filter options for dropdowns
   */
  async getFilterOptions(): Promise<{
    governments: { value: string; label: string }[];
    policyAreas: { value: string; label: string }[];
    committees: { value: string; label: string }[];
    primeMinisters: { value: string; label: string }[];
  }> {
    const decisions = await this.dataProvider.getAllDecisions();
    
    const governments = Array.from(new Set(decisions.map(d => d.government_number)))
      .filter(gov => gov && gov !== null)
      .sort((a, b) => parseInt(b) - parseInt(a))
      .map(gov => ({
        value: gov,
        label: `ממשלה ${gov}`
      }));
    
    const policyAreasSet = new Set<string>();
    decisions.forEach(d => {
      if (d.tags_policy_area) {
        // Split by both comma and semicolon
        const areas = d.tags_policy_area.split(/[,;]/).map(area => area.trim()).filter(area => area);
        areas.forEach(area => {
          if (area) policyAreasSet.add(area);
        });
      }
    });
    
    const policyAreas = Array.from(policyAreasSet)
      .sort()
      .map(area => ({
        value: area,
        label: area
      }));
    
    const committees = Array.from(new Set(decisions.map(d => d.committee || 'לא מוגדר')))
      .sort()
      .map(committee => ({
        value: committee,
        label: committee
      }));
    
    const primeMinisters = Array.from(new Set(decisions.map(d => d.prime_minister)))
      .sort()
      .map(pm => ({
        value: pm,
        label: pm
      }));
    
    return {
      governments,
      policyAreas,
      committees,
      primeMinisters
    };
  }

  /**
   * Helper method to calculate date span
   */
  private getDateSpan(decisions: Decision[]): { months: number; years: number } {
    if (decisions.length === 0) return { months: 0, years: 0 };
    
    const validDates = decisions
      .filter(d => d.decision_date && d.decision_date !== null)
      .map(d => new Date(d.decision_date))
      .filter(d => !isNaN(d.getTime()) && d.getFullYear() >= 1990);
    
    if (validDates.length === 0) return { months: 0, years: 0 };
    
    const minDate = new Date(Math.min(...validDates.map(d => d.getTime())));
    const maxDate = new Date(Math.max(...validDates.map(d => d.getTime())));
    
    const months = (maxDate.getFullYear() - minDate.getFullYear()) * 12 + 
                  (maxDate.getMonth() - minDate.getMonth());
    
    return {
      months: Math.max(1, months),
      years: Math.round(months / 12)
    };
  }
}

// Singleton instance
let instance: StatisticsService | null = null;

export function getStatisticsService(): StatisticsService {
  if (!instance) {
    instance = new StatisticsService();
  }
  return instance;
}