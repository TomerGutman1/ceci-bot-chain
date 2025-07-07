/**
 * Main Dashboard Layout Component
 * Responsive layout with filter panel and chart grid
 */

import React, { useState } from 'react';
import { Filter, LayoutGrid, Table, List, Settings, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';

import FilterPanel from '../filters/FilterPanel';
import KPICards from '../charts/KPICards';
import TimelineChart from '../charts/TimelineChart';
import PolicyDistributionChart from '../charts/PolicyDistributionChart';
import CommitteeActivityChart from '../charts/CommitteeActivityChart';

import { getDefaultFilters, countActiveFilters } from '../../utils/dataTransformers';
import { useExportDecisions } from '../../hooks/useDecisions';
import type { DashboardFilters } from '../../types/decision';

interface DashboardLayoutProps {
  className?: string;
}

export default function DashboardLayout({ className }: DashboardLayoutProps) {
  const [filters, setFilters] = useState<DashboardFilters>(getDefaultFilters());
  const [filterCollapsed, setFilterCollapsed] = useState(false);
  const [currentView, setCurrentView] = useState<'overview' | 'detailed'>('overview');
  
  const exportMutation = useExportDecisions();
  
  const activeFilterCount = countActiveFilters(filters);

  const handleExport = (format: 'csv' | 'excel') => {
    exportMutation.mutate({ filters, format });
  };

  return (
    <div className={cn('min-h-screen bg-gray-50', className)}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              סטטיסטיקות החלטות ממשלה
            </h1>
            <p className="text-gray-600 mt-1">
              מערכת ניתוח ותצוגת נתונים על החלטות ממשלת ישראל
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {activeFilterCount > 0 && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                {activeFilterCount} מסננים פעילים
              </Badge>
            )}
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport('csv')}
              disabled={exportMutation.isPending}
            >
              <Download className="h-4 w-4 mr-2" />
              ייצוא CSV
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFilterCollapsed(!filterCollapsed)}
            >
              <Filter className="h-4 w-4 mr-2" />
              {filterCollapsed ? 'הצג מסננים' : 'הסתר מסננים'}
            </Button>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row">
        {/* Filter Sidebar */}
        <div className={cn(
          'lg:w-80 flex-shrink-0 p-6',
          filterCollapsed && 'lg:w-16'
        )}>
          <FilterPanel
            filters={filters}
            onChange={setFilters}
            collapsed={filterCollapsed}
            onCollapsedChange={setFilterCollapsed}
          />
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          <Tabs value={currentView} onValueChange={(value: any) => setCurrentView(value)}>
            <TabsList className="grid grid-cols-2 w-fit mb-6">
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <LayoutGrid className="h-4 w-4" />
                מבט-על
              </TabsTrigger>
              <TabsTrigger value="detailed" className="flex items-center gap-2">
                <Table className="h-4 w-4" />
                פירוט נתונים
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              {/* KPI Cards */}
              <KPICards filters={filters} />

              {/* Charts Grid */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <TimelineChart filters={filters} />
                <PolicyDistributionChart filters={filters} />
              </div>
              
              <div className="grid grid-cols-1 gap-6">
                <CommitteeActivityChart filters={filters} />
              </div>
            </TabsContent>

            <TabsContent value="detailed" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <List className="h-5 w-5" />
                    רשימת החלטות מפורטת
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    <Table className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>תצוגת רשימה מפורטת תמומש בשלב הבא</p>
                    <p className="text-sm mt-2">
                      כולל טבלה עם מיון, סינון וייצוא נתונים
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 px-6 py-4 mt-8">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div>
            © 2025 מערכת ניתוח החלטות ממשלה • פותח עם Claude Code
          </div>
          <div className="flex items-center gap-4">
            <span>עדכון אחרון: {new Date().toLocaleDateString('he-IL')}</span>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}