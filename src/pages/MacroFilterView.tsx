/**
 * Macro Filter View Page
 * Advanced statistics dashboard for Israeli government decisions
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from '../macro_filter_view/components/layout/DashboardLayout';
import DataOptimizer from '../macro_filter_view/components/optimized/DataOptimizer';
import GovernmentComparisonChart from '../macro_filter_view/components/charts/GovernmentComparisonChart';
import SmartAlerts from '../macro_filter_view/components/shared/SmartAlerts';
import ReportSharing from '../macro_filter_view/components/shared/ReportSharing';
import PersonalWorkspace from '../macro_filter_view/components/shared/PersonalWorkspace';
import { getDefaultFilters } from '../macro_filter_view/utils/dataTransformers';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { DashboardFilters, UserPreferences } from '../macro_filter_view/types/decision';

// Create a separate query client for the macro filter view
const macroQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: 1,
    },
  },
});

// Mock user preferences
const mockUserPreferences: UserPreferences = {
  theme: 'light',
  defaultView: 'cards',
  // favoriteCharts: ['timeline', 'policy', 'kpi'], // Commented out as not in UserPreferences type
  // savedFilters: [], // Commented out as not in UserPreferences type
  notifications: {
    newDecisions: true,
    weeklyReports: true,
    systemAlerts: true,
  },
  language: 'he',
  dateFormat: 'hebrew',
};

const MacroFilterView = () => {
  const [filters, setFilters] = useState<DashboardFilters>(getDefaultFilters());
  const [userPreferences, setUserPreferences] = useState<UserPreferences>(mockUserPreferences);

  const handleFiltersChange = (newFilters: DashboardFilters) => {
    setFilters(newFilters);
  };

  const handlePreferencesChange = (newPreferences: UserPreferences) => {
    setUserPreferences(newPreferences);
  };

  const handleDecisionSelect = (decision: any) => {
    console.log('[MacroFilterView] Decision selected:', decision);
  };

  const handleShareReport = (report: any) => {
    console.log('[MacroFilterView] Report shared:', report);
  };

  return (
    <QueryClientProvider client={macroQueryClient}>
      <div className="container mx-auto px-4 py-8" dir="rtl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                📊 לוח מחוונים מתקדם
              </h1>
              <p className="text-gray-600 mt-2">
                ניתוח סטטיסטי מעמיק של החלטות ממשלה עם כלי מיטוב ביצועים
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-blue-50 text-blue-700">
                Macro Filter View
              </Badge>
              <Badge variant="outline" className="bg-green-50 text-green-700">
                ביצועים מותאמים
              </Badge>
            </div>
          </div>
          
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">24K+</div>
                  <div className="text-sm text-gray-500">החלטות במערכת</div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">13</div>
                  <div className="text-sm text-gray-500">ממשלות (25-37)</div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">15</div>
                  <div className="text-sm text-gray-500">תחומי מדיניות</div>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">Real-time</div>
                  <div className="text-sm text-gray-500">עדכונים</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Dashboard */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">סקירה כללית</TabsTrigger>
            <TabsTrigger value="optimizer">מיטוב נתונים</TabsTrigger>
            <TabsTrigger value="comparison">השוואת ממשלות</TabsTrigger>
            <TabsTrigger value="alerts">התראות חכמות</TabsTrigger>
            <TabsTrigger value="sharing">שיתוף דוחות</TabsTrigger>
            <TabsTrigger value="workspace">סביבת עבודה</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>סקירה כללית של המערכת</CardTitle>
                <CardDescription>
                  לוח מחוונים אינטראקטיבי עם מסננים מתקדמים וויזואליזציות
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DashboardLayout
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  userPreferences={userPreferences}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="optimizer" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>מיטוב ביצועים לנפחי נתונים גדולים</CardTitle>
                <CardDescription>
                  רשימות וירטואליות, קאש חכם ועיבוד באצוות עבור מיליוני החלטות
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DataOptimizer
                  filters={filters}
                  onDecisionSelect={handleDecisionSelect}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="comparison" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>השוואת ממשלות</CardTitle>
                <CardDescription>
                  ניתוח השוואתי של פעילות ממשלות שונות לאורך זמן
                </CardDescription>
              </CardHeader>
              <CardContent>
                <GovernmentComparisonChart
                  selectedGovernments={[35, 36, 37]}
                  onGovernmentChange={(govs) => console.log('Governments changed:', govs)}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>התראות חכמות ותחזיות</CardTitle>
                <CardDescription>
                  זיהוי מגמות, חריגות ותחזיות על בסיס למידת מכונה
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SmartAlerts filters={filters} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sharing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>שיתוף וייצוא דוחות</CardTitle>
                <CardDescription>
                  יצירת דוחות מותאמים אישית בפורמטים שונים ושיתוף מאובטח
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex justify-center">
                  <ReportSharing
                    filters={filters}
                    onShare={handleShareReport}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="workspace" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>סביבת עבודה אישית</CardTitle>
                <CardDescription>
                  מסננים שמורים, החלטות מועדפות והגדרות אישיות
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PersonalWorkspace
                  userPreferences={userPreferences}
                  onPreferencesChange={handlePreferencesChange}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer Info */}
        <div className="mt-12 p-6 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">ביצועים</h4>
              <p className="text-sm text-gray-600">
                מטמון חכם, רשימות וירטואליות וטעינה עצלה
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">נגישות</h4>
              <p className="text-sm text-gray-600">
                תמיכה מלאה בעברית RTL ונגישות מתקדמת
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">אבטחה</h4>
              <p className="text-sm text-gray-600">
                שיתוף מאובטח עם הגדרות פרטיות מתקדמות
              </p>
            </div>
          </div>
        </div>
      </div>
    </QueryClientProvider>
  );
};

export default MacroFilterView;