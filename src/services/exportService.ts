import { DecisionGuideAnalysis } from './decisionGuide.service';

export async function exportToPDF(results: DecisionGuideAnalysis): Promise<void> {
  // TODO: Implement PDF export
  console.log('PDF export not yet implemented', results);
  alert('ייצוא PDF יהיה זמין בקרוב');
}

export async function exportToExcel(results: DecisionGuideAnalysis): Promise<void> {
  // TODO: Implement Excel export
  console.log('Excel export not yet implemented', results);
  alert('ייצוא Excel יהיה זמין בקרוב');
}