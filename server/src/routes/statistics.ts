import { Router } from 'express';
import { getStatisticsService } from '../services/statisticsService';

const router = Router();
const statisticsService = getStatisticsService();

// Debug route
router.get('/test', (_req, res) => {
  res.json({ message: 'Statistics router is working' });
});

/**
 * GET /api/statistics/overview
 * Get overview statistics (KPI cards)
 */
router.get('/overview', async (req, res) => {
  try {
    const filters = {
      startDate: req.query.startDate as string,
      endDate: req.query.endDate as string,
      government: req.query.government as string,
      policyArea: req.query.policyArea as string,
      operativity: req.query.operativity as string,
      committee: req.query.committee as string,
      primeMinister: req.query.primeMinister as string,
    };

    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined || filters[key as keyof typeof filters] === '') {
        delete filters[key as keyof typeof filters];
      }
    });

    const overview = await statisticsService.getOverview(filters);
    res.json(overview);
  } catch (error) {
    console.error('Error getting overview statistics:', error);
    res.status(500).json({ 
      error: 'Failed to get overview statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/statistics/decisions
 * Get filtered decisions list
 */
router.get('/decisions', async (req, res) => {
  try {
    const filters = {
      startDate: req.query.startDate as string,
      endDate: req.query.endDate as string,
      government: req.query.government as string,
      policyArea: req.query.policyArea as string,
      operativity: req.query.operativity as string,
      committee: req.query.committee as string,
      primeMinister: req.query.primeMinister as string,
    };

    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined || filters[key as keyof typeof filters] === '') {
        delete filters[key as keyof typeof filters];
      }
    });

    const decisions = await statisticsService.getFilteredDecisions(filters);
    
    // Add pagination
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 20;
    const offset = (page - 1) * limit;
    
    const paginatedDecisions = decisions.slice(offset, offset + limit);
    
    res.json({
      decisions: paginatedDecisions,
      pagination: {
        page,
        limit,
        total: decisions.length,
        totalPages: Math.ceil(decisions.length / limit)
      }
    });
  } catch (error) {
    console.error('Error getting filtered decisions:', error);
    res.status(500).json({ 
      error: 'Failed to get filtered decisions',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/statistics/timeline
 * Get timeline data for charts
 */
router.get('/timeline', async (req, res) => {
  try {
    const filters = {
      startDate: req.query.startDate as string,
      endDate: req.query.endDate as string,
      government: req.query.government as string,
      policyArea: req.query.policyArea as string,
      operativity: req.query.operativity as string,
      committee: req.query.committee as string,
      primeMinister: req.query.primeMinister as string,
    };

    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined || filters[key as keyof typeof filters] === '') {
        delete filters[key as keyof typeof filters];
      }
    });

    const timeline = await statisticsService.getTimeline(filters);
    res.json(timeline);
  } catch (error) {
    console.error('Error getting timeline data:', error);
    res.status(500).json({ 
      error: 'Failed to get timeline data',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/statistics/policy-areas
 * Get policy area distribution
 */
router.get('/policy-areas', async (req, res) => {
  try {
    const filters = {
      startDate: req.query.startDate as string,
      endDate: req.query.endDate as string,
      government: req.query.government as string,
      policyArea: req.query.policyArea as string,
      operativity: req.query.operativity as string,
      committee: req.query.committee as string,
      primeMinister: req.query.primeMinister as string,
    };

    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined || filters[key as keyof typeof filters] === '') {
        delete filters[key as keyof typeof filters];
      }
    });

    const policyAreas = await statisticsService.getPolicyAreaStats(filters);
    res.json(policyAreas);
  } catch (error) {
    console.error('Error getting policy area statistics:', error);
    res.status(500).json({ 
      error: 'Failed to get policy area statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/statistics/committees
 * Get committee activity stats
 */
router.get('/committees', async (req, res) => {
  try {
    const filters = {
      startDate: req.query.startDate as string,
      endDate: req.query.endDate as string,
      government: req.query.government as string,
      policyArea: req.query.policyArea as string,
      operativity: req.query.operativity as string,
      committee: req.query.committee as string,
      primeMinister: req.query.primeMinister as string,
    };

    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined || filters[key as keyof typeof filters] === '') {
        delete filters[key as keyof typeof filters];
      }
    });

    const committees = await statisticsService.getCommitteeStats(filters);
    res.json(committees);
  } catch (error) {
    console.error('Error getting committee statistics:', error);
    res.status(500).json({ 
      error: 'Failed to get committee statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/statistics/governments
 * Get government comparison stats
 */
router.get('/governments', async (req, res) => {
  try {
    const filters = {
      startDate: req.query.startDate as string,
      endDate: req.query.endDate as string,
      government: req.query.government as string,
      policyArea: req.query.policyArea as string,
      operativity: req.query.operativity as string,
      committee: req.query.committee as string,
      primeMinister: req.query.primeMinister as string,
    };

    // Remove undefined values
    Object.keys(filters).forEach(key => {
      if (filters[key as keyof typeof filters] === undefined || filters[key as keyof typeof filters] === '') {
        delete filters[key as keyof typeof filters];
      }
    });

    const governments = await statisticsService.getGovernmentStats(filters);
    res.json(governments);
  } catch (error) {
    console.error('Error getting government statistics:', error);
    res.status(500).json({ 
      error: 'Failed to get government statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/statistics/filter-options
 * Get available filter options for dropdowns
 */
router.get('/filter-options', async (_req, res) => {
  try {
    const options = await statisticsService.getFilterOptions();
    res.json(options);
  } catch (error) {
    console.error('Error getting filter options:', error);
    res.status(500).json({ 
      error: 'Failed to get filter options',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/statistics/export
 * Export filtered data (CSV/JSON)
 */
router.post('/export', async (req, res) => {
  try {
    const { format = 'csv', filters = {} } = req.body;
    
    const decisions = await statisticsService.getFilteredDecisions(filters);
    
    if (format === 'csv') {
      // Generate CSV
      const headers = [
        'מספר החלטה',
        'תאריך',
        'ממשלה',
        'ראש ממשלה',
        'כותרת',
        'ועדה',
        'אופרטיביות',
        'תחום מדיניות',
        'גוף ממשלתי',
        'תגיות'
      ];
      
      const csvData = decisions.map(decision => [
        decision.decision_number,
        decision.decision_date,
        decision.government_number,
        decision.prime_minister,
        decision.decision_title,
        decision.committee || '',
        decision.operativity,
        decision.tags_policy_area,
        decision.tags_government_body,
        decision.all_tags
      ]);
      
      const csvContent = [headers, ...csvData]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');
      
      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.setHeader('Content-Disposition', 'attachment; filename="government-decisions.csv"');
      res.send('\uFEFF' + csvContent); // Add BOM for Hebrew support
    } else if (format === 'excel') {
      // Excel export - same as CSV but with correct extension
      const headers = [
        'מספר החלטה',
        'תאריך',
        'ממשלה',
        'ראש ממשלה',
        'כותרת',
        'ועדה',
        'אופרטיביות',
        'תחום מדיניות',
        'גוף ממשלתי',
        'תגיות'
      ];
      
      const csvData = decisions.map(decision => [
        decision.decision_number,
        decision.decision_date,
        decision.government_number,
        decision.prime_minister,
        decision.decision_title,
        decision.committee || '',
        decision.operativity,
        decision.tags_policy_area,
        decision.tags_government_body,
        decision.all_tags
      ]);
      
      const csvContent = [headers, ...csvData]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');
      
      res.setHeader('Content-Type', 'application/vnd.ms-excel; charset=utf-8');
      res.setHeader('Content-Disposition', 'attachment; filename="government-decisions.xlsx"');
      res.send('\uFEFF' + csvContent); // Add BOM for Hebrew support
    } else {
      // JSON export
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Content-Disposition', 'attachment; filename="government-decisions.json"');
      res.json(decisions);
    }
  } catch (error) {
    console.error('Error exporting data:', error);
    res.status(500).json({ 
      error: 'Failed to export data',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Paginated decisions endpoint
router.post('/decisions/paginated', async (req, res) => {
  try {
    const { page = 1, limit = 50, filters = {} } = req.body;
    
    const statsFilters = {
      startDate: filters.startDate,
      endDate: filters.endDate,
      government: filters.government,
      policyArea: filters.policyArea,
      operativity: filters.operativity,
      committee: filters.committee,
      primeMinister: filters.primeMinister,
    };

    // Remove undefined values
    Object.keys(statsFilters).forEach(key => {
      if (statsFilters[key as keyof typeof statsFilters] === undefined || statsFilters[key as keyof typeof statsFilters] === '') {
        delete statsFilters[key as keyof typeof statsFilters];
      }
    });

    const decisions = await statisticsService.getFilteredDecisions(statsFilters);
    
    // Paginate results
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedDecisions = decisions.slice(startIndex, endIndex);
    
    res.json({
      decisions: paginatedDecisions,
      pagination: {
        page,
        limit,
        total: decisions.length,
        totalPages: Math.ceil(decisions.length / limit)
      }
    });
  } catch (error) {
    console.error('Error getting paginated decisions:', error);
    res.status(500).json({ 
      error: 'Failed to get paginated decisions',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Optimized statistics endpoint
router.post('/optimized', async (req, res) => {
  try {
    const { filters = {} } = req.body;
    
    const statsFilters = {
      startDate: filters.startDate,
      endDate: filters.endDate,
      government: filters.government,
      policyArea: filters.policyArea,
      operativity: filters.operativity,
      committee: filters.committee,
      primeMinister: filters.primeMinister,
    };

    // Remove undefined values
    Object.keys(statsFilters).forEach(key => {
      if (statsFilters[key as keyof typeof statsFilters] === undefined || statsFilters[key as keyof typeof statsFilters] === '') {
        delete statsFilters[key as keyof typeof statsFilters];
      }
    });

    // Get all statistics in parallel for optimized performance
    const [overview, timeline, policyAreas, committees] = await Promise.all([
      statisticsService.getOverview(statsFilters),
      statisticsService.getTimeline(statsFilters),
      statisticsService.getPolicyAreaStats(statsFilters),
      statisticsService.getCommitteeStats(statsFilters)
    ]);
    
    res.json({
      overview,
      timeline,
      policyAreas,
      committees
    });
  } catch (error) {
    console.error('Error getting optimized statistics:', error);
    res.status(500).json({ 
      error: 'Failed to get optimized statistics',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;