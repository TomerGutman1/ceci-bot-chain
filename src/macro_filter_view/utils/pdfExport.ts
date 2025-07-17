/**
 * PDF Export Utilities
 * Functions for generating PDF reports with charts and data
 */

import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import html2canvas from 'html2canvas';
import { formatHebrewDate } from './dataTransformers';
import { hebrewToEnglish, formatDateForPDF } from './hebrewPdfHelper';
import type { DashboardFilters } from '../types/decision';

// Configure jsPDF for better text handling
const configurePDF = (doc: jsPDF) => {
  // Set default font and size
  doc.setFont('helvetica');
  doc.setFontSize(12);
};

/**
 * Capture a chart element as an image
 */
export async function captureChartAsImage(
  elementId: string,
  options: { scale?: number; backgroundColor?: string } = {}
): Promise<string | null> {
  try {
    const element = document.getElementById(elementId);
    if (!element) {
      console.error(`Element with id ${elementId} not found`);
      return null;
    }

    const canvas = await html2canvas(element, {
      scale: options.scale || 2,
      backgroundColor: options.backgroundColor || '#ffffff',
      logging: false,
      useCORS: true,
    });

    return canvas.toDataURL('image/png');
  } catch (error) {
    console.error('Error capturing chart:', error);
    return null;
  }
}

/**
 * Generate a comprehensive PDF report
 */
export async function generatePDFReport(config: {
  title: string;
  description?: string;
  filters: DashboardFilters;
  selectedCharts: string[];
  includeFilters: boolean;
  decisions?: any[];
}) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  configurePDF(doc);

  let currentY = 20;

  // Title Page
  doc.setFontSize(24);
  doc.text(hebrewToEnglish(config.title || 'דוח סטטיסטיקות החלטות ממשלה'), 105, currentY, { align: 'center' });
  currentY += 15;

  if (config.description) {
    doc.setFontSize(12);
    const lines = doc.splitTextToSize(config.description, 170);
    doc.text(lines, 105, currentY, { align: 'center' });
    currentY += lines.length * 7;
  }

  // Date
  doc.setFontSize(10);
  doc.text(`Created on: ${formatDateForPDF(new Date())}`, 105, currentY + 10, { align: 'center' });
  currentY += 25;

  // Filters Summary
  if (config.includeFilters && hasActiveFilters(config.filters)) {
    doc.setFontSize(16);
    doc.text(hebrewToEnglish('מסננים פעילים'), 105, currentY, { align: 'center' });
    currentY += 10;

    doc.setFontSize(10);
    const filterLines = getFilterSummaryLines(config.filters);
    filterLines.forEach(line => {
      doc.text(line, 20, currentY);
      currentY += 7;
    });
    currentY += 10;
  }

  // Add new page for charts
  if (config.selectedCharts.length > 0) {
    doc.addPage();
    currentY = 20;

    // Capture and add charts
    for (const chartId of config.selectedCharts) {
      const chartName = getChartName(chartId);
      
      // Add chart title
      doc.setFontSize(14);
      doc.text(hebrewToEnglish(chartName), 105, currentY, { align: 'center' });
      currentY += 10;

      // Capture chart
      const chartImage = await captureChartAsImage(`chart-${chartId}`);
      if (chartImage) {
        // Calculate dimensions to fit the page
        const imgWidth = 170;
        const imgHeight = 100; // Adjust based on actual chart aspect ratio
        
        // Check if we need a new page
        if (currentY + imgHeight > 270) {
          doc.addPage();
          currentY = 20;
        }

        doc.addImage(chartImage, 'PNG', 20, currentY, imgWidth, imgHeight);
        currentY += imgHeight + 15;
      }
    }
  }

  // Add data table if decisions are provided
  if (config.decisions && config.decisions.length > 0) {
    doc.addPage();
    doc.setFontSize(16);
    doc.text(hebrewToEnglish('רשימת החלטות'), 105, 20, { align: 'center' });

    // Create table
    autoTable(doc, {
      startY: 30,
      head: [[hebrewToEnglish('מספר'), hebrewToEnglish('תאריך'), hebrewToEnglish('כותרת'), hebrewToEnglish('ממשלה'), hebrewToEnglish('תחום')]],
      body: config.decisions.slice(0, 50).map(decision => [
        decision.decision_number,
        formatDateForPDF(new Date(decision.decision_date)),
        decision.decision_title.substring(0, 40) + '...',
        decision.government_number,
        decision.tags_policy_area || '-'
      ]),
      styles: {
        font: 'helvetica',
        fontSize: 9,
        cellPadding: 2,
      },
      headStyles: {
        fillColor: [44, 62, 80],
        halign: 'center',
      },
      columnStyles: {
        0: { halign: 'center', cellWidth: 20 },
        1: { halign: 'center', cellWidth: 25 },
        2: { halign: 'right', cellWidth: 70 },
        3: { halign: 'center', cellWidth: 20 },
        4: { halign: 'right', cellWidth: 35 },
      },
    });
  }

  // Save the PDF
  doc.save(`government-decisions-report-${Date.now()}.pdf`);
}

/**
 * Generate a simple PNG export of charts
 */
export async function exportChartsAsPNG(chartIds: string[]) {
  for (const chartId of chartIds) {
    const chartImage = await captureChartAsImage(`chart-${chartId}`, { scale: 3 });
    if (chartImage) {
      // Download the image
      const link = document.createElement('a');
      link.download = `chart-${chartId}-${Date.now()}.png`;
      link.href = chartImage;
      link.click();
    }
  }
}

// Helper functions
function hasActiveFilters(filters: DashboardFilters): boolean {
  return !!(
    filters.governments.length > 0 ||
    filters.committees.length > 0 ||
    filters.policyAreas.length > 0 ||
    filters.primeMinister ||
    filters.dateRange.start ||
    filters.dateRange.end ||
    filters.decisionType !== 'all'
  );
}

function getFilterSummaryLines(filters: DashboardFilters): string[] {
  const lines: string[] = [];

  if (filters.governments.length > 0) {
    lines.push(`${hebrewToEnglish('ממשלות')}: ${filters.governments.join(', ')}`);
  }

  if (filters.policyAreas.length > 0) {
    lines.push(`${hebrewToEnglish('תחומי מדיניות')}: ${filters.policyAreas.join(', ')}`);
  }

  if (filters.committees.length > 0) {
    lines.push(`${hebrewToEnglish('ועדות')}: ${filters.committees.length} ${hebrewToEnglish('נבחרו')}`);
  }

  if (filters.dateRange.start || filters.dateRange.end) {
    let dateStr = `${hebrewToEnglish('טווח תאריכים')}: `;
    if (filters.dateRange.start) {
      dateStr += `${hebrewToEnglish('מ-')}${formatDateForPDF(filters.dateRange.start)}`;
    }
    if (filters.dateRange.end) {
      dateStr += ` ${hebrewToEnglish('עד')} ${formatDateForPDF(filters.dateRange.end)}`;
    }
    lines.push(dateStr);
  }

  if (filters.primeMinister) {
    lines.push(`${hebrewToEnglish('ראש ממשלה')}: ${filters.primeMinister}`);
  }

  if (filters.decisionType !== 'all') {
    lines.push(`${hebrewToEnglish('סוג החלטה')}: ${hebrewToEnglish(filters.decisionType === 'operative' ? 'operative' : 'declarative')}`);
  }

  return lines;
}

function getChartName(chartId: string): string {
  const chartNames: { [key: string]: string } = {
    kpi: 'כרטיסי מדדים',
    timeline: 'ציר זמן',
    policy: 'התפלגות תחומי מדיניות',
    committee: 'פעילות ועדות',
    comparison: 'השוואת ממשלות',
  };
  return chartNames[chartId] || chartId;
}