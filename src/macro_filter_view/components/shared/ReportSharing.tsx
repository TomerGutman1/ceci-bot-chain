/**
 * Advanced Report Sharing Component
 * Generate, share, and manage dashboard reports
 */

import React, { useState } from 'react';
import { 
  Share2, 
  Download, 
  Link, 
  Mail, 
  FileText, 
  Image, 
  Settings,
  Copy,
  Clock,
  Users,
  Lock,
  Globe,
  Calendar,
  QrCode,
  Check
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';
import { formatHebrewDate, countActiveFilters } from '../../utils/dataTransformers';
import { useExportDecisions } from '../../hooks/useDecisions';
import { generatePDFReport, exportChartsAsPNG } from '../../utils/pdfExport';
import type { DashboardFilters, ExportConfig, ShareableReport } from '../../types/decision';

interface ReportSharingProps {
  filters: DashboardFilters;
  onShare?: (report: ShareableReport) => void;
  className?: string;
}

export default function ReportSharing({ filters, onShare, className }: ReportSharingProps) {
  const [showDialog, setShowDialog] = useState(false);
  const [reportConfig, setReportConfig] = useState({
    title: '',
    description: '',
    includeCharts: true,
    includeFilters: true,
    isPublic: false,
    expiresIn: '7d',
    emailRecipients: '',
    selectedCharts: ['kpi', 'timeline', 'policy', 'committee'],
  });
  
  const [generatedReport, setGeneratedReport] = useState<ShareableReport | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  
  const exportMutation = useExportDecisions();

  const availableCharts = [
    { id: 'kpi', name: 'כרטיסי מדדים', description: 'סטטיסטיקות כלליות ומדדי ביצועים' },
    { id: 'timeline', name: 'ציר זמן', description: 'התפלגות החלטות לאורך זמן' },
    { id: 'policy', name: 'תחומי מדיניות', description: 'התפלגות לפי תחום מדיניות' },
    { id: 'committee', name: 'פעילות ועדות', description: 'פעילות ועדות וגופים' },
    { id: 'comparison', name: 'השוואת ממשלות', description: 'השוואה בין ממשלות שונות' },
  ];

  const generateReport = async () => {
    // Simulate report generation
    const reportId = `report_${Date.now()}`;
    const expirationDate = getExpirationDate(reportConfig.expiresIn);
    
    const report: ShareableReport = {
      id: reportId,
      title: reportConfig.title || 'דוח סטטיסטיקות החלטות ממשלה',
      description: reportConfig.description,
      filters,
      chartConfig: reportConfig.selectedCharts.reduce((acc, chartId) => {
        acc[chartId] = { visible: true, position: 0, size: 'medium' };
        return acc;
      }, {} as any),
      isPublic: reportConfig.isPublic,
      expiresAt: expirationDate,
      createdAt: new Date(),
    };
    
    setGeneratedReport(report);
    onShare?.(report);
    
    // Copy link to clipboard
    const reportUrl = `${window.location.origin}/reports/${reportId}`;
    await navigator.clipboard.writeText(reportUrl);
  };

  const getExpirationDate = (expiresIn: string): Date | null => {
    const now = new Date();
    switch (expiresIn) {
      case '1d': return new Date(now.getTime() + 24 * 60 * 60 * 1000);
      case '7d': return new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
      case '30d': return new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
      case 'never': return null;
      default: return new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    }
  };

  const handleExport = async (format: 'csv' | 'excel' | 'pdf' | 'png') => {
    if (format === 'csv' || format === 'excel') {
      exportMutation.mutate({ filters, format });
    } else if (format === 'pdf') {
      // Show loading state
      setIsGeneratingPDF(true);
      
      try {
        // Generate full report with charts
        await generatePDFReport({
          title: reportConfig.title || 'דוח סטטיסטיקות החלטות ממשלה',
          description: reportConfig.description || `נוצר בתאריך ${new Date().toLocaleDateString('he-IL')}`,
          filters: filters,
          selectedCharts: reportConfig.selectedCharts,
          includeFilters: reportConfig.includeFilters,
        });
        
        // Show success message
        alert('הדוח נוצר בהצלחה!');
      } catch (error) {
        console.error('Error generating PDF:', error);
        alert('שגיאה ביצירת הדוח. אנא נסה שנית.');
      } finally {
        setIsGeneratingPDF(false);
      }
    } else if (format === 'png') {
      // Export charts as images
      try {
        await exportChartsAsPNG(reportConfig.selectedCharts);
        alert('התרשימים יוצאו בהצלחה!');
      } catch (error) {
        console.error('Error exporting charts:', error);
        alert('שגיאה בייצוא התרשימים. אנא נסה שנית.');
      }
    }
  };

  const sendByEmail = async () => {
    const emails = reportConfig.emailRecipients.split(',').map(e => e.trim()).filter(Boolean);
    if (emails.length === 0) return;
    
    // Simulate email sending
    console.log('Sending report to:', emails);
    alert(`דוח נשלח ל-${emails.length} נמענים`);
  };

  const activeFiltersCount = countActiveFilters(filters);

  return (
    <Dialog open={showDialog} onOpenChange={setShowDialog}>
      <DialogTrigger asChild>
        <Button variant="outline" className={className}>
          <Download className="h-4 w-4 mr-2" />
          ייצוא דוח
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            שיתוף וייצוא דוח
          </DialogTitle>
          <DialogDescription>
            צור דוח בר שיתוף או ייצא את הנתונים בפורמטים שונים
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="share" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="share">שיתוף</TabsTrigger>
            <TabsTrigger value="export">ייצוא</TabsTrigger>
            <TabsTrigger value="schedule">תזמון</TabsTrigger>
          </TabsList>

          <TabsContent value="share" className="space-y-4">
            <div className="space-y-4">
              <div>
                <Label htmlFor="report-title">כותרת הדוח</Label>
                <Input
                  id="report-title"
                  placeholder="דוח סטטיסטיקות החלטות ממשלה..."
                  value={reportConfig.title}
                  onChange={(e) => setReportConfig(prev => ({ ...prev, title: e.target.value }))}
                  className="text-right"
                />
              </div>

              <div>
                <Label htmlFor="report-description">תיאור</Label>
                <Textarea
                  id="report-description"
                  placeholder="תיאור קצר של הדוח ומטרתו..."
                  value={reportConfig.description}
                  onChange={(e) => setReportConfig(prev => ({ ...prev, description: e.target.value }))}
                  className="text-right"
                  rows={3}
                />
              </div>

              {/* Filter Summary */}
              {activeFiltersCount > 0 && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">מסננים פעילים</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1 text-sm">
                      {filters.governments.length > 0 && (
                        <div>ממשלות: {filters.governments.join(', ')}</div>
                      )}
                      {filters.policyAreas.length > 0 && (
                        <div>תחומי מדיניות: {filters.policyAreas.length} נבחרו</div>
                      )}
                      {filters.committees.length > 0 && (
                        <div>ועדות: {filters.committees.length} נבחרו</div>
                      )}
                      {(filters.dateRange.start || filters.dateRange.end) && (
                        <div>טווח תאריכים: 
                          {filters.dateRange.start && ` מ-${formatHebrewDate(filters.dateRange.start)}`}
                          {filters.dateRange.end && ` עד ${formatHebrewDate(filters.dateRange.end)}`}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Chart Selection */}
              <div>
                <Label className="text-base font-medium">תרשימים לכלול</Label>
                <div className="mt-2 space-y-2">
                  {availableCharts.map((chart) => (
                    <div key={chart.id} className="flex items-center space-x-2 space-x-reverse">
                      <Checkbox
                        id={chart.id}
                        checked={reportConfig.selectedCharts.includes(chart.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setReportConfig(prev => ({
                              ...prev,
                              selectedCharts: [...prev.selectedCharts, chart.id]
                            }));
                          } else {
                            setReportConfig(prev => ({
                              ...prev,
                              selectedCharts: prev.selectedCharts.filter(id => id !== chart.id)
                            }));
                          }
                        }}
                      />
                      <div className="grid gap-1.5 leading-none">
                        <Label
                          htmlFor={chart.id}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        >
                          {chart.name}
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          {chart.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Privacy Settings */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base">דוח ציבורי</Label>
                    <p className="text-sm text-muted-foreground">
                      אפשר גישה לדוח ללא צורך באימות
                    </p>
                  </div>
                  <Switch
                    checked={reportConfig.isPublic}
                    onCheckedChange={(checked) => 
                      setReportConfig(prev => ({ ...prev, isPublic: checked }))
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="expires">תפוגה</Label>
                  <Select
                    value={reportConfig.expiresIn}
                    onValueChange={(value) => 
                      setReportConfig(prev => ({ ...prev, expiresIn: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1d">יום אחד</SelectItem>
                      <SelectItem value="7d">שבוע</SelectItem>
                      <SelectItem value="30d">חודש</SelectItem>
                      <SelectItem value="never">ללא תפוגה</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Email Sharing */}
              <div className="space-y-2">
                <Label htmlFor="email-recipients">שליחה במייל (אופציונלי)</Label>
                <Input
                  id="email-recipients"
                  placeholder="email1@example.com, email2@example.com"
                  value={reportConfig.emailRecipients}
                  onChange={(e) => setReportConfig(prev => ({ ...prev, emailRecipients: e.target.value }))}
                  className="text-left"
                />
                <p className="text-xs text-muted-foreground">
                  הפרד כתובות מייל בפסיקים
                </p>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="export" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                onClick={() => handleExport('pdf')}
                disabled={isGeneratingPDF}
                className="h-20 flex-col gap-2"
              >
                <FileText className="h-6 w-6" />
                <span>דוח מלא</span>
                <span className="text-xs text-muted-foreground">
                  {isGeneratingPDF ? 'מייצר...' : 'כולל תרשימים'}
                </span>
              </Button>

              <Button
                variant="outline"
                onClick={() => handleExport('excel')}
                disabled={exportMutation.isPending}
                className="h-20 flex-col gap-2"
              >
                <FileText className="h-6 w-6" />
                <span>Excel</span>
                <span className="text-xs text-muted-foreground">קובץ עבודה</span>
              </Button>

              <Button
                variant="outline"
                onClick={() => handleExport('csv')}
                disabled={exportMutation.isPending}
                className="h-20 flex-col gap-2"
              >
                <FileText className="h-6 w-6" />
                <span>CSV</span>
                <span className="text-xs text-muted-foreground">נתונים בלבד</span>
              </Button>

              <Button
                variant="outline"
                onClick={() => handleExport('png')}
                disabled={reportConfig.selectedCharts.length === 0}
                className="h-20 flex-col gap-2"
              >
                <Image className="h-6 w-6" />
                <span>תמונה</span>
                <span className="text-xs text-muted-foreground">
                  {reportConfig.selectedCharts.length === 0 ? 'בחר תרשימים' : 'תרשימים'}
                </span>
              </Button>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Settings className="h-4 w-4 text-blue-600" />
                <span className="font-medium text-blue-900">אפשרויות ייצוא</span>
              </div>
              <div className="space-y-2 text-sm text-blue-800">
                <div className="flex items-center justify-between">
                  <span>כלול מסננים</span>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <span>כלול תרשימים</span>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <span>רזולוציה גבוהה</span>
                  <Switch />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="schedule" className="space-y-4">
            <div className="text-center py-8 text-gray-500">
              <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <h3 className="font-medium mb-2">דוחות מתוזמנים</h3>
              <p className="text-sm">
                קבל דוחות אוטומטיים במועדים קבועים
              </p>
              <Button variant="outline" className="mt-4">
                הגדר דוח מתוזמן
              </Button>
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={() => setShowDialog(false)}>
            ביטול
          </Button>
          
          {reportConfig.emailRecipients && (
            <Button variant="outline" onClick={sendByEmail}>
              <Mail className="h-4 w-4 mr-2" />
              שלח במייל
            </Button>
          )}
          
          <Button onClick={generateReport}>
            <Link className="h-4 w-4 mr-2" />
            צור קישור שיתוף
          </Button>
        </DialogFooter>

        {/* Generated Report Success */}
        {generatedReport && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Check className="h-4 w-4 text-green-600" />
              <span className="font-medium text-green-900">הדוח נוצר בהצלחה!</span>
            </div>
            <p className="text-sm text-green-800 mb-2">
              הקישור הועתק ללוח העתקה
            </p>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">
                {generatedReport.isPublic ? <Globe className="h-3 w-3 mr-1" /> : <Lock className="h-3 w-3 mr-1" />}
                {generatedReport.isPublic ? 'ציבורי' : 'פרטי'}
              </Badge>
              {generatedReport.expiresAt && (
                <Badge variant="outline">
                  <Clock className="h-3 w-3 mr-1" />
                  פג ב-{formatHebrewDate(generatedReport.expiresAt)}
                </Badge>
              )}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}