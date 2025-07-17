import { DecisionGuideAnalysis } from './decisionGuide.service';
import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';

export async function exportToPDF(results: DecisionGuideAnalysis): Promise<void> {
  try {
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    // Create a visual representation of the scores
    let yPosition = 20;
    
    // Title
    pdf.setFontSize(20);
    pdf.text('Government Decision Analysis Report', 105, yPosition, { align: 'center' });
    yPosition += 10;
    
    // Date
    pdf.setFontSize(10);
    pdf.text(new Date().toLocaleDateString('en-US'), 105, yPosition, { align: 'center' });
    yPosition += 20;
    
    // Overall Score Section
    pdf.setFontSize(16);
    pdf.text('Weighted Feasibility Score', 105, yPosition, { align: 'center' });
    yPosition += 15;
    
    // Draw score visualization
    const centerX = 105;
    const radius = 15;
    
    // Background circle
    pdf.setDrawColor(200, 200, 200);
    pdf.setLineWidth(2);
    pdf.circle(centerX, yPosition, radius);
    
    // Score text
    pdf.setFontSize(24);
    pdf.setTextColor(0, 0, 0);
    pdf.text(results.weightedScore.toFixed(1), centerX, yPosition + 2, { align: 'center' });
    
    // Feasibility level
    yPosition += 25;
    pdf.setFontSize(12);
    const feasibilityText = `Feasibility Level: ${results.feasibilityLevel.toUpperCase()}`;
    const color = results.weightedScore >= 7.5 ? [76, 175, 80] : 
                  results.weightedScore >= 5 ? [255, 193, 7] : [244, 67, 54];
    pdf.setTextColor(color[0], color[1], color[2]);
    pdf.text(feasibilityText, centerX, yPosition, { align: 'center' });
    
    // Criteria Scores
    yPosition += 20;
    pdf.setTextColor(0, 0, 0);
    pdf.setFontSize(14);
    pdf.text('Criteria Scores', 20, yPosition);
    yPosition += 10;
    
    // Create visual representation for each criterion
    results.criteriaScores.forEach((criteria, index) => {
      if (yPosition > 250) {
        pdf.addPage();
        yPosition = 20;
      }
      
      // Criterion number and score
      pdf.setFontSize(10);
      pdf.setTextColor(0, 0, 0);
      pdf.text(`${index + 1}. Criterion ${index + 1}: ${criteria.score}/10 (Weight: ${(criteria.weight * 100).toFixed(0)}%)`, 20, yPosition);
      
      // Score bar
      const barWidth = 100;
      const barHeight = 5;
      const barX = 20;
      
      // Background bar
      pdf.setFillColor(230, 230, 230);
      pdf.rect(barX, yPosition + 2, barWidth, barHeight, 'F');
      
      // Score bar
      const scoreColor = criteria.score >= 8 ? [76, 175, 80] : 
                        criteria.score >= 5 ? [255, 193, 7] : [244, 67, 54];
      pdf.setFillColor(scoreColor[0], scoreColor[1], scoreColor[2]);
      pdf.rect(barX, yPosition + 2, (criteria.score / 10) * barWidth, barHeight, 'F');
      
      yPosition += 12;
    });
    
    // Summary section
    if (yPosition > 230) {
      pdf.addPage();
      yPosition = 20;
    }
    
    yPosition += 10;
    pdf.setFontSize(12);
    pdf.text('Analysis Summary', 20, yPosition);
    yPosition += 8;
    
    pdf.setFontSize(10);
    pdf.text(`- Total Criteria Evaluated: ${results.criteriaScores.length}`, 25, yPosition);
    yPosition += 6;
    pdf.text(`- Weighted Score: ${results.weightedScore.toFixed(1)}/10`, 25, yPosition);
    yPosition += 6;
    pdf.text(`- Feasibility Level: ${results.feasibilityLevel}`, 25, yPosition);
    yPosition += 6;
    pdf.text(`- Model Used: ${results.modelUsed}`, 25, yPosition);
    yPosition += 6;
    pdf.text(`- Processing Time: ${(results.processingTime / 1000).toFixed(1)} seconds`, 25, yPosition);
    
    // Save the PDF
    pdf.save(`decision-analysis-${new Date().toISOString().split('T')[0]}.pdf`);
    
  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('Error exporting PDF. Please try again.');
  }
}

export async function exportToCSV(results: DecisionGuideAnalysis): Promise<void> {
  try {
    // Prepare data for CSV
    const csvData = results.criteriaScores.map(criteria => ({
      'קריטריון': criteria.criterion,
      'ציון (1-10)': criteria.score,
      'משקל (%)': (criteria.weight * 100).toFixed(0),
      'הסבר': criteria.explanation,
      'ציטוט מהמסמך': criteria.reference_from_document || '',
      'הצעה לשיפור': criteria.specific_improvement || ''
    }));
    
    // Add summary row
    csvData.push({
      'קריטריון': 'ציון משוקלל כולל',
      'ציון (1-10)': results.weightedScore.toFixed(1),
      'משקל (%)': '100',
      'הסבר': `רמת ישימות: ${results.feasibilityLevel === 'high' ? 'גבוהה' : 
                           results.feasibilityLevel === 'medium' ? 'בינונית' : 'נמוכה'}`,
      'ציטוט מהמסמך': '',
      'הצעה לשיפור': ''
    });
    
    // Create worksheet
    const ws = XLSX.utils.json_to_sheet(csvData);
    
    // Set column widths
    ws['!cols'] = [
      { wch: 30 }, // קריטריון
      { wch: 12 }, // ציון
      { wch: 10 }, // משקל
      { wch: 50 }, // הסבר
      { wch: 40 }, // ציטוט
      { wch: 40 }  // הצעה לשיפור
    ];
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'ניתוח החלטת ממשלה');
    
    // Add recommendations sheet if exists
    if (results.recommendations && results.recommendations.length > 0) {
      const recData = results.recommendations.map((rec, index) => ({
        'מספר': index + 1,
        'המלצה': rec
      }));
      
      const wsRec = XLSX.utils.json_to_sheet(recData);
      wsRec['!cols'] = [{ wch: 10 }, { wch: 80 }];
      XLSX.utils.book_append_sheet(wb, wsRec, 'המלצות');
    }
    
    // Save file
    XLSX.writeFile(wb, `decision-analysis-${new Date().toISOString().split('T')[0]}.xlsx`);
    
  } catch (error) {
    console.error('Error generating CSV:', error);
    alert('שגיאה בייצוא Excel. אנא נסה שוב.');
  }
}

// Keep old function name for backward compatibility
export async function exportToExcel(results: DecisionGuideAnalysis): Promise<void> {
  return exportToCSV(results);
}