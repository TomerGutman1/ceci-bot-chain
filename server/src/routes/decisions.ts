import { Router } from 'express';
import { supabase } from '../dal/supabaseClient';
import logger from '../utils/logger';

const router = Router();

// Get specific decision by government and decision number
router.get('/decision/:governmentNumber/:decisionNumber', async (req: any, res: any) => {
  try {
    const { governmentNumber, decisionNumber } = req.params;
    
    logger.info('Fetching specific decision', { governmentNumber, decisionNumber });
    
    const { data, error } = await supabase
      .from('israeli_government_decisions')
      .select('id, government_number, decision_number, decision_title, decision_date, summary, decision_content, tags_policy_area, tags_government_body, operativity, decision_url')
      .eq('government_number', governmentNumber)
      .eq('decision_number', decisionNumber)
      .single();
    
    if (error) {
      if (error.code === 'PGRST116') {
        // No rows found
        return res.status(404).json({ 
          error: 'Decision not found',
          governmentNumber,
          decisionNumber 
        });
      }
      throw error;
    }
    
    // Map to expected format
    // Use decision_content if available, otherwise fall back to summary
    const fullContent = data.decision_content || data.summary || data.decision_title || '';
    const mappedDecision = {
      id: data.id,
      government_number: data.government_number,
      decision_number: data.decision_number,
      decision_title: data.decision_title,
      decision_content: fullContent,  // Use decision_content or fallback to summary
      content: fullContent,  // Use decision_content or fallback to summary
      summary: data.summary,
      decision_date: data.decision_date,
      operativity: data.operativity || 'אופרטיבית',
      topics: data.tags_policy_area || [],
      ministries: data.tags_government_body || [],
      decision_url: data.decision_url
    };
    
    logger.info('Mapped decision data', { 
      hasFullContent: !!data.decision_content,
      contentLength: fullContent.length,
      decisionNumber: data.decision_number 
    });
    
    res.json(mappedDecision);
    
  } catch (error) {
    logger.error('Error fetching decision', { error });
    res.status(500).json({ error: 'Failed to fetch decision' });
  }
});

export default router;