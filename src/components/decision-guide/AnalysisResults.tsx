import React from 'react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Card } from '@/components/ui/card';
import { CheckCircle2, AlertCircle, XCircle, Download, RotateCcw, ArrowRight } from 'lucide-react';
import { exportToPDF, exportToExcel } from '@/services/exportService';

interface AnalysisResultsProps {
  results: any;
  onReset: () => void;
  onBackToChat: () => void;
}

export function AnalysisResults({ results, onReset, onBackToChat }: AnalysisResultsProps) {
  const getFeasibilityColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getFeasibilityText = (level: string) => {
    switch (level) {
      case 'high':
        return 'ישימות גבוהה';
      case 'medium':
        return 'ישימות בינונית';
      case 'low':
        return 'ישימות נמוכה';
      default:
        return 'לא ידוע';
    }
  };

  const getScoreIcon = (score: number) => {
    if (score >= 8) return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    if (score >= 5) return <AlertCircle className="h-5 w-5 text-yellow-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'bg-green-100 text-green-800';
    if (score >= 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const handleExportPDF = async () => {
    await exportToPDF(results);
  };

  const handleExportExcel = async () => {
    await exportToExcel(results);
  };

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <Card className="p-6">
        <div className="text-center space-y-4">
          <h3 className="text-xl font-semibold">ציון ישימות משוקלל</h3>
          <div className="flex justify-center items-center gap-4">
            <div className="text-5xl font-bold">{results.weightedScore.toFixed(1)}</div>
            <div className="text-right">
              <p className={`text-lg font-medium ${getFeasibilityColor(results.feasibilityLevel)}`}>
                {getFeasibilityText(results.feasibilityLevel)}
              </p>
              <p className="text-sm text-gray-600">מתוך 10</p>
            </div>
          </div>
          <Progress value={results.weightedScore * 10} className="h-3" />
        </div>
      </Card>

      {/* Criteria Scores */}
      <div>
        <h3 className="text-lg font-semibold mb-4">ציונים לפי קריטריונים</h3>
        <Accordion type="single" collapsible className="space-y-2">
          {results.criteriaScores.map((criteria: any, index: number) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="hover:no-underline">
                <div className="flex items-center justify-between w-full pl-4">
                  <div className="flex items-center gap-3">
                    {getScoreIcon(criteria.score)}
                    <span className="font-medium">{criteria.criterion}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">משקל: {(criteria.weight * 100).toFixed(0)}%</span>
                    <span className={`px-2 py-1 rounded text-sm font-medium ${getScoreColor(criteria.score)}`}>
                      {criteria.score}/10
                    </span>
                  </div>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="pr-8 pt-2 pb-4 space-y-4">
                  <div>
                    <p className="font-medium text-gray-900 mb-1">הסבר:</p>
                    <p className="text-gray-700">{criteria.explanation}</p>
                  </div>
                  
                  {criteria.reference_from_document && (
                    <div>
                      <p className="font-medium text-gray-900 mb-1">ציטוט מהמסמך:</p>
                      <blockquote className="pr-4 border-r-2 border-gray-300 text-gray-600 italic" dir="rtl">
                        "{criteria.reference_from_document}"
                      </blockquote>
                    </div>
                  )}
                  
                  {criteria.specific_improvement && (
                    <div>
                      <p className="font-medium text-gray-900 mb-1">הצעה לשיפור:</p>
                      <p className="text-blue-700 bg-blue-50 p-3 rounded">
                        {criteria.specific_improvement}
                      </p>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      {/* Recommendations */}
      {results.recommendations && results.recommendations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">המלצות לשיפור</h3>
          <ul className="space-y-3">
            {results.recommendations.map((recommendation: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-primary mt-1">•</span>
                <span className="text-gray-700">{recommendation}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Model Info */}
      <div className="text-sm text-gray-600 text-center">
        <p>נותח באמצעות: {results.modelUsed}</p>
        <p>זמן עיבוד: {(results.processingTime / 1000).toFixed(1)} שניות</p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 justify-between">
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleExportPDF}>
            <Download className="ml-2 h-4 w-4" />
            ייצוא PDF
          </Button>
          <Button variant="outline" onClick={handleExportExcel}>
            <Download className="ml-2 h-4 w-4" />
            ייצוא Excel
          </Button>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={onReset}>
            <RotateCcw className="ml-2 h-4 w-4" />
            ניתוח חדש
          </Button>
          <Button onClick={onBackToChat}>
            <ArrowRight className="ml-2 h-4 w-4" />
            חזרה לצ'אט
          </Button>
        </div>
      </div>
    </div>
  );
}