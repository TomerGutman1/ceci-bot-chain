/**
 * Committee Activity Bar Chart Component
 * Horizontal bar chart showing committee activity with sorting options
 */

import React, { useState, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Users, TrendingUp, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
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
import { useCommitteeStats } from '../../hooks/useDecisions';
import { formatHebrewNumber } from '../../utils/dataTransformers';
import type { DashboardFilters } from '../../types/decision';

interface CommitteeActivityChartProps {
  filters: DashboardFilters;
  className?: string;
}

type SortOption = 'count' | 'name' | 'recent';
type SortDirection = 'asc' | 'desc';

export default function CommitteeActivityChart({ filters, className }: CommitteeActivityChartProps) {
  const [sortBy, setSortBy] = useState<SortOption>('count');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [maxItems, setMaxItems] = useState(10);
  
  const { data: committeeStats, isLoading, error } = useCommitteeStats(filters);

  // Sort and limit data
  const sortedData = useMemo(() => {
    if (!committeeStats) return [];
    
    const sorted = [...committeeStats].sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'count':
          comparison = a.count - b.count;
          break;
        case 'name':
          comparison = a.committee.localeCompare(b.committee, 'he');
          break;
        case 'recent':
          comparison = a.recentActivity - b.recentActivity;
          break;
      }
      
      return sortDirection === 'asc' ? comparison : -comparison;
    });
    
    return sorted.slice(0, maxItems).map((stat, index) => ({
      ...stat,
      shortName: stat.committee.length > 25 
        ? stat.committee.substring(0, 25) + '...' 
        : stat.committee,
      rank: index + 1,
      color: getCommitteeColor(stat.committee, stat.recentActivity),
    }));
  }, [committeeStats, sortBy, sortDirection, maxItems]);

  function getCommitteeColor(committee: string, recentActivity: number): string {
    if (recentActivity > 5) return '#10b981'; // Green for high activity
    if (recentActivity > 2) return '#f59e0b'; // Orange for medium activity
    if (committee.includes('הממשלה')) return '#3b82f6'; // Blue for government
    return '#6b7280'; // Gray for others
  }

  const toggleSort = (option: SortOption) => {
    if (sortBy === option) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(option);
      setSortDirection('desc');
    }
  };

  const getSortIcon = (option: SortOption) => {
    if (sortBy !== option) return <ArrowUpDown className="h-3 w-3 opacity-50" />;
    return sortDirection === 'asc' 
      ? <ArrowUp className="h-3 w-3" />
      : <ArrowDown className="h-3 w-3" />;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg max-w-xs">
          <p className="font-medium text-gray-900 mb-2 text-right">{data.committee}</p>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between gap-4">
              <span>סה״כ החלטות:</span>
              <span className="font-medium">{formatHebrewNumber(data.count)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span>פעילות אחרונה:</span>
              <span className="font-medium">{formatHebrewNumber(data.recentActivity)}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span>אחוז מכלל:</span>
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
      <Card id="chart-committee" className={className}>
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
      <Card id="chart-committee" className={className}>
        <CardContent className="p-6 text-center">
          <p className="text-sm text-red-600">שגיאה בטעינת נתוני פעילות הועדות</p>
        </CardContent>
      </Card>
    );
  }

  if (!sortedData || sortedData.length === 0) {
    return (
      <Card id="chart-committee" className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            פעילות ועדות וגופים
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-8">
          <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-gray-500">אין נתוני ועדות להצגה</p>
        </CardContent>
      </Card>
    );
  }

  const totalDecisions = sortedData.reduce((sum, item) => sum + item.count, 0);

  return (
    <Card id="chart-committee" className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            פעילות ועדות וגופים
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-gray-100">
              {formatHebrewNumber(totalDecisions)} החלטות
            </Badge>
            
            <Select value={maxItems.toString()} onValueChange={(value) => setMaxItems(parseInt(value))}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="15">15</SelectItem>
                <SelectItem value="20">20</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant={sortBy === 'count' ? 'default' : 'outline'}
            size="sm"
            onClick={() => toggleSort('count')}
            className="h-8"
          >
            לפי כמות
            {getSortIcon('count')}
          </Button>
          <Button
            variant={sortBy === 'recent' ? 'default' : 'outline'}
            size="sm"
            onClick={() => toggleSort('recent')}
            className="h-8"
          >
            לפי פעילות אחרונה
            {getSortIcon('recent')}
          </Button>
          <Button
            variant={sortBy === 'name' ? 'default' : 'outline'}
            size="sm"
            onClick={() => toggleSort('name')}
            className="h-8"
          >
            לפי שם
            {getSortIcon('name')}
          </Button>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sortedData}
              layout="horizontal"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis 
                dataKey="shortName" 
                type="category" 
                width={120}
                tick={{ fontSize: 11, textAnchor: 'end' }}
                interval={0}
              />
              <Tooltip content={<CustomTooltip />} />
              
              <Bar
                dataKey="count"
                fill={(entry) => entry.color}
                radius={[0, 4, 4, 0]}
              >
                {sortedData.map((entry, index) => (
                  <Bar key={`bar-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Activity Legend */}
        <div className="mt-4 flex items-center justify-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded" />
            <span>פעילות גבוהה (5+ החלטות אחרונות)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded" />
            <span>פעילות בינונית (2-5 החלטות)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-500 rounded" />
            <span>פעילות נמוכה</span>
          </div>
        </div>

        {/* Top Performers Summary */}
        {sortedData.length > 0 && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="font-medium text-green-600">
                  {sortedData[0]?.committee}
                </div>
                <div className="text-xs text-gray-500">ועדה מובילה</div>
                <div className="text-xs text-gray-400">
                  {formatHebrewNumber(sortedData[0]?.count || 0)} החלטות
                </div>
              </div>
              
              <div className="text-center">
                <div className="font-medium text-orange-600">
                  {sortedData.filter(s => s.recentActivity > 0).length}
                </div>
                <div className="text-xs text-gray-500">ועדות פעילות</div>
                <div className="text-xs text-gray-400">בתקופה האחרונה</div>
              </div>
              
              <div className="text-center">
                <div className="font-medium text-blue-600">
                  {formatHebrewNumber(Math.round(totalDecisions / sortedData.length))}
                </div>
                <div className="text-xs text-gray-500">ממוצע החלטות</div>
                <div className="text-xs text-gray-400">לועדה</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}