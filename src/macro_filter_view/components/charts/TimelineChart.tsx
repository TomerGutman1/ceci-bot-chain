/**
 * Timeline Chart Component
 * Interactive chart showing decision volume over time
 */

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from 'recharts';
import { CalendarDays, ZoomIn, ZoomOut } from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { useTimelineData } from '../../hooks/useDecisions';
import { formatHebrewDate, formatHebrewNumber } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface TimelineChartProps {
  filters: DashboardFilters;
  className?: string;
}

// Hebrew month names for formatting
const HEBREW_MONTHS = [
  'ינו׳', 'פבר׳', 'מרץ', 'אפר׳', 'מאי', 'יוני',
  'יולי', 'אוג׳', 'ספט׳', 'אוק׳', 'נוב׳', 'דצמ׳'
];

export default function TimelineChart({ filters, className }: TimelineChartProps) {
  const [granularity, setGranularity] = useState<'day' | 'month' | 'year'>('month');
  const [showBrush, setShowBrush] = useState(true);
  
  const { data: timelineData, isLoading, error } = useTimelineData(filters, granularity);

  // Format data for recharts
  const chartData = timelineData?.map(item => ({
    date: item.date,
    dateStr: formatChartDate(item.date, granularity),
    total: item.count,
    operational: item.operationalCount,
    declarative: item.declarativeCount,
  })) || [];

  function formatChartDate(date: Date, granularity: 'day' | 'month' | 'year'): string {
    switch (granularity) {
      case 'day':
        return `${date.getDate()}/${date.getMonth() + 1}`;
      case 'month':
        return `${HEBREW_MONTHS[date.getMonth()]} ${date.getFullYear()}`;
      case 'year':
        return date.getFullYear().toString();
      default:
        return date.toLocaleDateString('he-IL');
    }
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-900 mb-2 text-right">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-4 text-sm">
              <span className="text-right" style={{ color: entry.color }}>
                {entry.name === 'total' ? 'סה״כ' : 
                 entry.name === 'operational' ? 'אופרטיביות' : 'דקלרטיביות'}:
              </span>
              <span className="font-medium">
                {formatHebrewNumber(entry.value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-80 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="p-6 text-center">
          <p className="text-sm text-red-600">שגיאה בטעינת נתוני הציר הזמן</p>
        </CardContent>
      </Card>
    );
  }

  const maxValue = Math.max(...chartData.map(d => d.total));

  return (
    <Card className={className} id="chart-timeline">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <CalendarDays className="h-5 w-5" />
            התפלגות החלטות לאורך זמן
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Select value={granularity} onValueChange={(value: any) => setGranularity(value)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="day">יומי</SelectItem>
                <SelectItem value="month">חודשי</SelectItem>
                <SelectItem value="year">שנתי</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowBrush(!showBrush)}
              className="h-8"
            >
              {showBrush ? <ZoomOut className="h-4 w-4" /> : <ZoomIn className="h-4 w-4" />}
            </Button>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span>סה״כ החלטות</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span>אופרטיביות</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-500 rounded-full" />
            <span>דקלרטיביות</span>
          </div>
          <Badge variant="secondary" className="bg-gray-100">
            {formatHebrewNumber(chartData.length)} נקודות זמן
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis 
                dataKey="dateStr"
                tick={{ fontSize: 12 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                domain={[0, Math.ceil(maxValue * 1.1)]}
              />
              <Tooltip content={<CustomTooltip />} />
              
              <Line
                type="monotone"
                dataKey="total"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                name="total"
              />
              <Line
                type="monotone"
                dataKey="operational"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#10b981', strokeWidth: 2, r: 3 }}
                name="operational"
              />
              <Line
                type="monotone"
                dataKey="declarative"
                stroke="#8b5cf6"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 3 }}
                name="declarative"
              />
              
              {showBrush && chartData.length > 10 && (
                <Brush
                  dataKey="dateStr"
                  height={30}
                  stroke="#3b82f6"
                  fill="#f1f5f9"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {chartData.length === 0 && (
          <div className="text-center text-gray-500 py-8">
            <CalendarDays className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>אין נתונים להצגה בטווח הזמן הנבחר</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}