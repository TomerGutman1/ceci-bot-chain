/**
 * Smart Alerts and Predictions Component
 * Intelligent notifications about trends, anomalies, and insights
 */

import React, { useState, useMemo } from 'react';
import { 
  Bell, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Info, 
  Target,
  Calendar,
  Activity,
  X,
  Settings,
  Zap
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { formatHebrewNumber, formatRelativeTime } from '../../utils/dataTransformers';
import { useDashboardLoading } from '../../hooks/useDecisions';
import type { DashboardFilters } from '../../types/decision';

interface SmartAlertsProps {
  filters: DashboardFilters;
  className?: string;
}

interface AlertConfig {
  id: string;
  type: 'trend' | 'anomaly' | 'milestone' | 'prediction';
  enabled: boolean;
  threshold?: number;
}

interface SmartAlert {
  id: string;
  type: 'trend' | 'anomaly' | 'milestone' | 'prediction';
  severity: 'info' | 'warning' | 'success' | 'error';
  title: string;
  description: string;
  value?: number;
  change?: number;
  timestamp: Date;
  actionable: boolean;
  dismissible: boolean;
}

export default function SmartAlerts({ filters, className }: SmartAlertsProps) {
  const [alertConfigs, setAlertConfigs] = useState<AlertConfig[]>([
    { id: 'high-activity', type: 'trend', enabled: true, threshold: 20 },
    { id: 'low-activity', type: 'trend', enabled: true, threshold: -20 },
    { id: 'anomaly-detection', type: 'anomaly', enabled: true },
    { id: 'milestone-tracker', type: 'milestone', enabled: true },
    { id: 'trend-prediction', type: 'prediction', enabled: false },
  ]);
  
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());
  const [showSettings, setShowSettings] = useState(false);
  
  const { isLoading, hasError } = useDashboardLoading(filters);

  // Generate smart alerts based on current data and filters
  const smartAlerts = useMemo<SmartAlert[]>(() => {
    const alerts: SmartAlert[] = [];
    const now = new Date();
    
    // Mock data analysis - in real implementation, this would analyze actual data
    const mockAnalysis = {
      currentMonthDecisions: 45,
      lastMonthDecisions: 52,
      avgMonthlyDecisions: 38,
      unusualCommitteeActivity: true,
      newPolicyAreas: ['קיימות', 'בינה מלאכותית'],
      governmentEfficiency: 0.72,
      trendDirection: 'declining',
    };

    // High Activity Alert
    if (alertConfigs.find(c => c.id === 'high-activity')?.enabled) {
      const change = ((mockAnalysis.currentMonthDecisions - mockAnalysis.avgMonthlyDecisions) / mockAnalysis.avgMonthlyDecisions) * 100;
      if (change > 15) {
        alerts.push({
          id: 'high-activity-1',
          type: 'trend',
          severity: 'success',
          title: 'פעילות גבוהה זוהתה',
          description: `מספר ההחלטות החודש גבוה ב-${change.toFixed(0)}% מהממוצע (${formatHebrewNumber(mockAnalysis.currentMonthDecisions)} לעומת ${formatHebrewNumber(mockAnalysis.avgMonthlyDecisions)})`,
          value: mockAnalysis.currentMonthDecisions,
          change: change,
          timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000), // 2 hours ago
          actionable: true,
          dismissible: true,
        });
      }
    }

    // Anomaly Detection
    if (alertConfigs.find(c => c.id === 'anomaly-detection')?.enabled && mockAnalysis.unusualCommitteeActivity) {
      alerts.push({
        id: 'anomaly-1',
        type: 'anomaly',
        severity: 'warning',
        title: 'פעילות חריגה בועדת השרים',
        description: 'זוהתה פעילות חריגה בועדת השרים לענייני כלכלה - עלייה של 300% בהחלטות השבוע',
        timestamp: new Date(now.getTime() - 4 * 60 * 60 * 1000), // 4 hours ago
        actionable: true,
        dismissible: true,
      });
    }

    // New Policy Areas
    if (mockAnalysis.newPolicyAreas.length > 0) {
      alerts.push({
        id: 'new-policy-1',
        type: 'milestone',
        severity: 'info',
        title: 'תחומי מדיניות חדשים',
        description: `זוהו תחומי מדיניות חדשים: ${mockAnalysis.newPolicyAreas.join(', ')}`,
        timestamp: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
        actionable: false,
        dismissible: true,
      });
    }

    // Government Efficiency Insight
    if (mockAnalysis.governmentEfficiency < 0.7) {
      alerts.push({
        id: 'efficiency-1',
        type: 'trend',
        severity: 'warning',
        title: 'ירידה ביעילות הממשלה',
        description: `יעילות הממשלה ירדה ל-${(mockAnalysis.governmentEfficiency * 100).toFixed(0)}% לפי אינדקס ההחלטות האופרטיביות`,
        value: mockAnalysis.governmentEfficiency,
        timestamp: new Date(now.getTime() - 6 * 60 * 60 * 1000), // 6 hours ago
        actionable: true,
        dismissible: true,
      });
    }

    // Prediction Alert (if enabled)
    if (alertConfigs.find(c => c.id === 'trend-prediction')?.enabled) {
      alerts.push({
        id: 'prediction-1',
        type: 'prediction',
        severity: 'info',
        title: 'חיזוי מגמות',
        description: 'לפי הניתוח הסטטיסטי, צפויה עלייה של 15% בהחלטות בתחום הבריאות בחודש הבא',
        timestamp: new Date(now.getTime() - 30 * 60 * 1000), // 30 minutes ago
        actionable: false,
        dismissible: true,
      });
    }

    return alerts.filter(alert => !dismissedAlerts.has(alert.id));
  }, [alertConfigs, dismissedAlerts]);

  const getAlertIcon = (type: SmartAlert['type'], severity: SmartAlert['severity']) => {
    const iconClass = "h-4 w-4";
    
    switch (type) {
      case 'trend':
        return severity === 'success' || severity === 'info' 
          ? <TrendingUp className={iconClass} />
          : <TrendingDown className={iconClass} />;
      case 'anomaly':
        return <AlertTriangle className={iconClass} />;
      case 'milestone':
        return <Target className={iconClass} />;
      case 'prediction':
        return <Zap className={iconClass} />;
      default:
        return <Info className={iconClass} />;
    }
  };

  const getAlertColor = (severity: SmartAlert['severity']) => {
    switch (severity) {
      case 'success': return 'bg-green-50 border-green-200 text-green-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error': return 'bg-red-50 border-red-200 text-red-800';
      default: return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const dismissAlert = (alertId: string) => {
    setDismissedAlerts(prev => new Set([...prev, alertId]));
  };

  const toggleAlertConfig = (configId: string) => {
    setAlertConfigs(prev => 
      prev.map(config => 
        config.id === configId 
          ? { ...config, enabled: !config.enabled }
          : config
      )
    );
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="h-6 w-32 bg-gray-200 rounded animate-pulse" />
            <div className="h-8 w-8 bg-gray-200 rounded animate-pulse" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            התראות חכמות
            {smartAlerts.length > 0 && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {smartAlerts.length}
              </Badge>
            )}
          </CardTitle>
          
          <Dialog open={showSettings} onOpenChange={setShowSettings}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>הגדרות התראות</DialogTitle>
                <DialogDescription>
                  בחר אילו סוגי התראות תרצה לקבל
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                {alertConfigs.map((config) => (
                  <div key={config.id} className="flex items-center justify-between">
                    <Label htmlFor={config.id} className="text-right flex-1">
                      {config.id === 'high-activity' && 'פעילות גבוהה'}
                      {config.id === 'low-activity' && 'פעילות נמוכה'}
                      {config.id === 'anomaly-detection' && 'זיהוי חריגות'}
                      {config.id === 'milestone-tracker' && 'מעקב אבני דרך'}
                      {config.id === 'trend-prediction' && 'חיזוי מגמות'}
                    </Label>
                    <Switch
                      id={config.id}
                      checked={config.enabled}
                      onCheckedChange={() => toggleAlertConfig(config.id)}
                    />
                  </div>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      
      <CardContent>
        {smartAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Bell className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>אין התראות חדשות</p>
            <p className="text-sm mt-1">המערכת תודיע לך על מגמות וחריגות מעניינות</p>
          </div>
        ) : (
          <div className="space-y-3">
            {smartAlerts.map((alert) => (
              <Alert
                key={alert.id}
                className={cn(
                  'relative',
                  getAlertColor(alert.severity)
                )}
              >
                <div className="flex items-start gap-3">
                  {getAlertIcon(alert.type, alert.severity)}
                  
                  <div className="flex-1 min-w-0">
                    <AlertTitle className="text-right">
                      {alert.title}
                      {alert.change && (
                        <Badge 
                          variant="secondary" 
                          className="mr-2 text-xs"
                        >
                          {alert.change > 0 ? '+' : ''}{alert.change.toFixed(0)}%
                        </Badge>
                      )}
                    </AlertTitle>
                    <AlertDescription className="text-right">
                      {alert.description}
                    </AlertDescription>
                    
                    <div className="flex items-center justify-between mt-2">
                      <div className="text-xs opacity-75">
                        {formatRelativeTime(alert.timestamp)}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {alert.actionable && (
                          <Button variant="ghost" size="sm" className="h-6 text-xs">
                            פעולה
                          </Button>
                        )}
                        {alert.dismissible && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => dismissAlert(alert.id)}
                            className="h-6 w-6 p-0"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </Alert>
            ))}
          </div>
        )}
        
        {dismissedAlerts.size > 0 && (
          <div className="mt-4 pt-3 border-t">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setDismissedAlerts(new Set())}
              className="text-xs text-gray-500"
            >
              הצג התראות שנדחו ({dismissedAlerts.size})
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}