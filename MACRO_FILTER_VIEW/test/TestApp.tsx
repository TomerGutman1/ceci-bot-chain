/**
 * Test Application for Macro Filter View Dashboard
 * Standalone testing environment before integration
 */

import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from '../components/layout/DashboardLayout';
import DataOptimizer from '../components/optimized/DataOptimizer';
import GovernmentComparisonChart from '../components/charts/GovernmentComparisonChart';
import SmartAlerts from '../components/shared/SmartAlerts';
import ReportSharing from '../components/shared/ReportSharing';
import PersonalWorkspace from '../components/shared/PersonalWorkspace';
import { getDefaultFilters } from '../utils/dataTransformers';
import type { DashboardFilters, UserPreferences } from '../types/decision';

// Create a query client for React Query
const queryClient = new QueryClient({
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
  favoriteCharts: ['timeline', 'policy', 'kpi'],
  savedFilters: [],
  notifications: {
    newDecisions: true,
    weeklyReports: true,
    systemAlerts: true,
  },
  language: 'he',
  dateFormat: 'hebrew',
};

export default function TestApp() {
  const [filters, setFilters] = useState<DashboardFilters>(getDefaultFilters());
  const [userPreferences, setUserPreferences] = useState<UserPreferences>(mockUserPreferences);
  const [activeTab, setActiveTab] = useState<string>('overview');

  const handleFiltersChange = (newFilters: DashboardFilters) => {
    setFilters(newFilters);
    console.log('[TestApp] Filters changed:', newFilters);
  };

  const handlePreferencesChange = (newPreferences: UserPreferences) => {
    setUserPreferences(newPreferences);
    console.log('[TestApp] Preferences changed:', newPreferences);
  };

  const handleDecisionSelect = (decision: any) => {
    console.log('[TestApp] Decision selected:', decision);
  };

  const handleShareReport = (report: any) => {
    console.log('[TestApp] Report shared:', report);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50" dir="rtl">
        {/* Test Header */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  📊 בדיקת לוח המחוונים - Macro Filter View
                </h1>
                <p className="text-sm text-gray-500">
                  סביבת בדיקה עצמאית לפני אינטגרציה
                </p>
              </div>
              
              <div className="flex items-center gap-2">
                <div className="text-sm text-gray-500">
                  Active Filters: {Object.values(filters).flat().length}
                </div>
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" title="Test Environment"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Test Navigation */}
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav className="flex space-x-reverse space-x-8">
              {[
                { id: 'overview', label: 'סקירה כללית' },
                { id: 'optimizer', label: 'מיטוב נתונים' },
                { id: 'comparison', label: 'השוואת ממשלות' },
                { id: 'alerts', label: 'התראות חכמות' },
                { id: 'sharing', label: 'שיתוף דוחות' },
                { id: 'workspace', label: 'סביבת עבודה' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Test Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-8">
            {/* Active Tab Content */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h2 className="font-medium text-blue-900 mb-2">🔍 סקירה כללית - בדיקות</h2>
                  <p className="text-sm text-blue-800">
                    הלוח מכיל {Object.keys(filters).length} סוגי מסננים ותומך בחיפוש בעברית.
                    כל הרכיבים פועלים במצב בדיקה עם נתונים מדומים.
                  </p>
                </div>

                <DashboardLayout
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  userPreferences={userPreferences}
                  className="border rounded-lg bg-white shadow-sm"
                />
              </div>
            )}

            {activeTab === 'optimizer' && (
              <div className="space-y-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h2 className="font-medium text-yellow-900 mb-2">⚡ בדיקת מיטוב ביצועים</h2>
                  <p className="text-sm text-yellow-800">
                    רכיב זה מדמה טיפול בנפחי נתונים גדולים עם רשימות וירטואליות וקאש חכם.
                  </p>
                </div>

                <DataOptimizer
                  filters={filters}
                  onDecisionSelect={handleDecisionSelect}
                  className="border rounded-lg bg-white shadow-sm"
                />
              </div>
            )}

            {activeTab === 'comparison' && (
              <div className="space-y-6">
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h2 className="font-medium text-purple-900 mb-2">📊 השוואת ממשלות</h2>
                  <p className="text-sm text-purple-800">
                    תרשים השוואה מתקדם עם תצוגות מרובות ואפשרויות ניתוח.
                  </p>
                </div>

                <GovernmentComparisonChart
                  selectedGovernments={[35, 36, 37]}
                  onGovernmentChange={(govs) => console.log('Governments changed:', govs)}
                  className="border rounded-lg bg-white shadow-sm"
                />
              </div>
            )}

            {activeTab === 'alerts' && (
              <div className="space-y-6">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h2 className="font-medium text-red-900 mb-2">🚨 התראות חכמות</h2>
                  <p className="text-sm text-red-800">
                    מערכת התראות מתקדמת עם זיהוי מגמות ותחזיות.
                  </p>
                </div>

                <SmartAlerts
                  filters={filters}
                  className="border rounded-lg bg-white shadow-sm"
                />
              </div>
            )}

            {activeTab === 'sharing' && (
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h2 className="font-medium text-green-900 mb-2">📤 שיתוף דוחות</h2>
                  <p className="text-sm text-green-800">
                    יצירת דוחות בפורמטים שונים ושיתוף מאובטח.
                  </p>
                </div>

                <div className="border rounded-lg bg-white shadow-sm p-6">
                  <ReportSharing
                    filters={filters}
                    onShare={handleShareReport}
                  />
                </div>
              </div>
            )}

            {activeTab === 'workspace' && (
              <div className="space-y-6">
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <h2 className="font-medium text-indigo-900 mb-2">👤 סביבת עבודה אישית</h2>
                  <p className="text-sm text-indigo-800">
                    ניהול מסננים שמורים, החלטות מועדפות והגדרות אישיות.
                  </p>
                </div>

                <PersonalWorkspace
                  userPreferences={userPreferences}
                  onPreferencesChange={handlePreferencesChange}
                  className="border rounded-lg bg-white shadow-sm"
                />
              </div>
            )}
          </div>
        </div>

        {/* Test Footer */}
        <div className="bg-gray-100 border-t mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div>
                🧪 מצב בדיקה | React {React.version} | TypeScript
              </div>
              <div>
                נוצר ע״י Claude Code | {new Date().toLocaleDateString('he-IL')}
              </div>
            </div>
          </div>
        </div>
      </div>
    </QueryClientProvider>
  );
}