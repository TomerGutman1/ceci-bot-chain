/**
 * Government Comparison Chart Component
 * Side-by-side comparison of different Israeli governments
 */

import React, { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { 
  Users, 
  TrendingUp, 
  Calendar, 
  Target,
  ArrowRight,
  ArrowLeft,
  BarChart3,
  PieChart as PieChartIcon
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
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { useGovernmentComparison } from '../../hooks/useDecisions';
import { formatHebrewNumber, formatHebrewDate } from '../../utils/dataTransformers';

interface GovernmentComparisonChartProps {
  selectedGovernments: number[];
  onGovernmentChange: (governments: number[]) => void;
  className?: string;
}

// Available governments for comparison
const AVAILABLE_GOVERNMENTS = [
  { number: 37, name: 'ממשלה 37', pm: 'בנימין נתניהו', period: '2022-2025', color: '#3b82f6' },
  { number: 36, name: 'ממשלה 36', pm: 'בנט/לפיד', period: '2021-2022', color: '#10b981' },
  { number: 35, name: 'ממשלה 35', pm: 'בנימין נתניהו', period: '2020-2021', color: '#f59e0b' },
  { number: 34, name: 'ממשלה 34', pm: 'בנימין נתניהו', period: '2015-2020', color: '#ef4444' },
  { number: 33, name: 'ממשלה 33', pm: 'בנימין נתניהו', period: '2013-2015', color: '#8b5cf6' },
  { number: 32, name: 'ממשלה 32', pm: 'בנימין נתניהו', period: '2009-2013', color: '#06b6d4' },
];

export default function GovernmentComparisonChart({
  selectedGovernments,
  onGovernmentChange,
  className,
}: GovernmentComparisonChartProps) {
  const [viewType, setViewType] = useState<'overview' | 'timeline' | 'breakdown'>('overview');
  
  const { data: comparisonData, isLoading, error } = useGovernmentComparison(selectedGovernments);

  // Get government info
  const getGovernmentInfo = (govNumber: number) => 
    AVAILABLE_GOVERNMENTS.find(g => g.number === govNumber);

  // Add government to comparison
  const addGovernment = (govNumber: number) => {
    if (!selectedGovernments.includes(govNumber) && selectedGovernments.length < 4) {
      onGovernmentChange([...selectedGovernments, govNumber]);
    }
  };

  // Remove government from comparison
  const removeGovernment = (govNumber: number) => {
    onGovernmentChange(selectedGovernments.filter(g => g !== govNumber));
  };

  // Prepare data for charts
  const chartData = useMemo(() => {
    if (!comparisonData) return [];
    
    return comparisonData.map((gov: any) => {
      const info = getGovernmentInfo(gov.governmentNumber);
      return {
        name: `ממשלה ${gov.governmentNumber}`,
        government: gov.governmentNumber,
        totalDecisions: gov.totalDecisions,
        operational: gov.operationalCount,
        declarative: gov.declarativeCount,
        operationalPercentage: (gov.operationalCount / Math.max(gov.totalDecisions, 1)) * 100,
        declarativePercentage: (gov.declarativeCount / Math.max(gov.totalDecisions, 1)) * 100,
        avgPerMonth: gov.avgDecisionsPerMonth || 0,
        duration: gov.durationMonths || 0,
        color: info?.color || '#6b7280',
        pm: info?.pm || 'לא ידוע',
        period: info?.period || '',
      };
    });
  }, [comparisonData]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900 mb-2 text-right">{data.name}</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-4">
              <span>ראש ממשלה:</span>
              <span className="font-medium">{data.pm}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span>תקופה:</span>
              <span className="font-medium">{data.period}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span>סה״כ החלטות:</span>
              <span className="font-medium">{formatHebrewNumber(data.totalDecisions)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span>ממוצע חודשי:</span>
              <span className="font-medium">{formatHebrewNumber(Math.round(data.avgPerMonth))}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  if (selectedGovernments.length === 0) {
    return (
      <Card id="chart-comparison" className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            השוואה בין ממשלות
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-8">
          <Users className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            בחר ממשלות להשוואה
          </h3>
          <p className="text-gray-500 mb-6">
            השווה בין עד 4 ממשלות שונות לפי מגוון פרמטרים
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-w-2xl mx-auto">
            {AVAILABLE_GOVERNMENTS.slice(0, 6).map((gov) => (
              <Button
                key={gov.number}
                variant="outline"
                onClick={() => addGovernment(gov.number)}
                className="p-4 h-auto flex-col gap-2"
              >
                <div className="font-medium">{gov.name}</div>
                <div className="text-xs text-gray-500">{gov.pm}</div>
                <div className="text-xs text-gray-400">{gov.period}</div>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card id="chart-comparison" className={className}>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-96 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card id="chart-comparison" className={className}>
        <CardContent className="p-6 text-center">
          <p className="text-sm text-red-600">שגיאה בטעינת נתוני השוואת הממשלות</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card id="chart-comparison" className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            השוואה בין ממשלות
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Select onValueChange={(value) => addGovernment(parseInt(value))}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="הוסף ממשלה..." />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_GOVERNMENTS
                  .filter(gov => !selectedGovernments.includes(gov.number))
                  .map((gov) => (
                    <SelectItem key={gov.number} value={gov.number.toString()}>
                      {gov.name}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {/* Selected governments */}
        <div className="flex flex-wrap gap-2">
          {selectedGovernments.map((govNumber) => {
            const info = getGovernmentInfo(govNumber);
            return (
              <Badge
                key={govNumber}
                variant="secondary"
                className="px-3 py-1"
                style={{ backgroundColor: `${info?.color}20`, borderColor: info?.color }}
              >
                <div
                  className="w-2 h-2 rounded-full mr-2"
                  style={{ backgroundColor: info?.color }}
                />
                ממשלה {govNumber}
                <button
                  onClick={() => removeGovernment(govNumber)}
                  className="mr-2 text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              </Badge>
            );
          })}
        </div>
      </CardHeader>
      
      <CardContent>
        <Tabs value={viewType} onValueChange={(value: any) => setViewType(value)}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">מבט כללי</TabsTrigger>
            <TabsTrigger value="timeline">ציר זמן</TabsTrigger>
            <TabsTrigger value="breakdown">פירוט לפי סוג</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {chartData.map((gov) => (
                <div
                  key={gov.government}
                  className="p-4 border rounded-lg"
                  style={{ borderColor: gov.color }}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: gov.color }}
                    />
                    <span className="font-medium">{gov.name}</span>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div>סה״כ: {formatHebrewNumber(gov.totalDecisions)}</div>
                    <div>ממוצע חודשי: {formatHebrewNumber(Math.round(gov.avgPerMonth))}</div>
                    <div>אופרטיביות: {gov.operationalPercentage.toFixed(0)}%</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Comparison Chart */}
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  
                  <Bar
                    dataKey="totalDecisions"
                    name="סה״כ החלטות"
                    radius={[4, 4, 0, 0]}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="timeline" className="space-y-6">
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  
                  <Line
                    type="monotone"
                    dataKey="avgPerMonth"
                    name="ממוצע החלטות לחודש"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </TabsContent>

          <TabsContent value="breakdown" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {chartData.map((gov) => (
                <div key={gov.government} className="space-y-3">
                  <h4 className="font-medium text-center">{gov.name}</h4>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'אופרטיביות', value: gov.operational, color: '#10b981' },
                            { name: 'דקלרטיביות', value: gov.declarative, color: '#3b82f6' },
                          ]}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          dataKey="value"
                          label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                        >
                          <Cell fill="#10b981" />
                          <Cell fill="#3b82f6" />
                        </Pie>
                        <Tooltip 
                          formatter={(value) => formatHebrewNumber(value as number)}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}