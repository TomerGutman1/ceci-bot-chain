/**
 * Policy Distribution Chart Component
 * Pie chart showing distribution of decisions by policy areas
 */

import React, { useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import { PieChart as PieChartIcon, Tag, Eye, EyeOff } from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { usePolicyAreaStats } from '../../hooks/useDecisions';
import { formatHebrewNumber, getPolicyAreaColor } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface PolicyDistributionChartProps {
  filters: DashboardFilters;
  className?: string;
}

// Custom label component for Hebrew text
const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
  if (percent < 0.05) return null; // Don't show labels for slices < 5%
  
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text 
      x={x} 
      y={y} 
      fill="white" 
      textAnchor={x > cx ? 'start' : 'end'} 
      dominantBaseline="central"
      fontSize={12}
      fontWeight="bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default function PolicyDistributionChart({ filters, className }: PolicyDistributionChartProps) {
  const [hiddenAreas, setHiddenAreas] = useState<Set<string>>(new Set());
  const [showDetails, setShowDetails] = useState(true);
  
  const { data: policyStats, isLoading, error } = usePolicyAreaStats(filters);

  // Process data for chart
  const chartData = policyStats?.map(stat => ({
    name: stat.area,
    value: stat.count,
    percentage: stat.percentage,
    color: getPolicyAreaColor(stat.area),
  })).filter(item => !hiddenAreas.has(item.name)) || [];

  const totalDecisions = chartData.reduce((sum, item) => sum + item.value, 0);

  const toggleAreaVisibility = (area: string) => {
    const newHidden = new Set(hiddenAreas);
    if (newHidden.has(area)) {
      newHidden.delete(area);
    } else {
      newHidden.add(area);
    }
    setHiddenAreas(newHidden);
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: data.color }}
            />
            <span className="font-medium text-right">{data.name}</span>
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-4">
              <span>מספר החלטות:</span>
              <span className="font-medium">{formatHebrewNumber(data.value)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span>אחוז:</span>
              <span className="font-medium">{data.percentage.toFixed(1)}%</span>
            </div>
          </div>
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
          <p className="text-sm text-red-600">שגיאה בטעינת נתוני התפלגות המדיניות</p>
        </CardContent>
      </Card>
    );
  }

  if (!chartData || chartData.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChartIcon className="h-5 w-5" />
            התפלגות לפי תחום מדיניות
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-8">
          <Tag className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-gray-500">אין נתונים להצגה</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <PieChartIcon className="h-5 w-5" />
            התפלגות לפי תחום מדיניות
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-gray-100">
              {formatHebrewNumber(totalDecisions)} החלטות
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDetails(!showDetails)}
              className="h-8"
            >
              {showDetails ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart */}
          <div className="lg:col-span-2">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomLabel}
                    outerRadius={120}
                    innerRadius={40}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {chartData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.color}
                        stroke="#fff"
                        strokeWidth={2}
                      />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Legend/Details */}
          {showDetails && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700 mb-3">תחומי מדיניות</h4>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {policyStats?.slice(0, 10).map((stat) => {
                  const isHidden = hiddenAreas.has(stat.area);
                  const color = getPolicyAreaColor(stat.area);
                  
                  return (
                    <div
                      key={stat.area}
                      className={cn(
                        'flex items-center justify-between p-2 rounded-lg border transition-colors cursor-pointer',
                        isHidden 
                          ? 'bg-gray-50 border-gray-200 opacity-50' 
                          : 'bg-white border-gray-200 hover:bg-gray-50'
                      )}
                      onClick={() => toggleAreaVisibility(stat.area)}
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <div
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: color }}
                        />
                        <span className="text-sm truncate text-right">
                          {stat.area}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{formatHebrewNumber(stat.count)}</span>
                        <span>({stat.percentage.toFixed(1)}%)</span>
                        {isHidden ? (
                          <EyeOff className="h-3 w-3" />
                        ) : (
                          <Eye className="h-3 w-3" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {hiddenAreas.size > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setHiddenAreas(new Set())}
                  className="w-full text-xs"
                >
                  הצג את כל התחומים
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}