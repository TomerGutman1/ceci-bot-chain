/**
 * KPI Dashboard Cards Component
 * Displays key performance indicators and statistics
 */

import React from 'react';
import { TrendingUp, TrendingDown, Users, Calendar, Target, Activity } from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { formatHebrewNumber } from '../../utils/dataTransformers';
import { useOverviewStats } from '../../hooks/useDecisions';
import type { DashboardFilters } from '../../types/decision';

interface KPICardsProps {
  filters: DashboardFilters;
  className?: string;
}

interface KPICardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    isPositive: boolean;
    period: string;
  };
  icon: React.ReactNode;
  color: string;
  description?: string;
  loading?: boolean;
}

function KPICard({ 
  title, 
  value, 
  change, 
  icon, 
  color, 
  description,
  loading = false 
}: KPICardProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-3 w-20" />
            </div>
            <Skeleton className="h-8 w-8 rounded" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="transition-all hover:shadow-md">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold text-gray-900">
                {typeof value === 'number' ? formatHebrewNumber(value) : value}
              </h3>
              {change && (
                <Badge
                  variant="secondary"
                  className={cn(
                    'text-xs',
                    change.isPositive 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  )}
                >
                  <span className="flex items-center gap-1">
                    {change.isPositive ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    {Math.abs(change.value)}%
                  </span>
                </Badge>
              )}
            </div>
            {description && (
              <p className="text-xs text-gray-500">{description}</p>
            )}
            {change && (
              <p className="text-xs text-gray-400">
                {change.period}
              </p>
            )}
          </div>
          
          <div className={cn(
            'p-3 rounded-lg',
            color
          )}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function KPICards({ filters, className }: KPICardsProps) {
  const { data: stats, isLoading, error } = useOverviewStats(filters);

  if (error) {
    return (
      <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4', className)}>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-sm text-red-600">שגיאה בטעינת הנתונים</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const kpiData = [
    {
      title: 'סה״כ החלטות',
      value: stats?.total || 0,
      change: stats?.periodComparison ? {
        value: stats.periodComparison.changePercent,
        isPositive: stats.periodComparison.changePercent > 0,
        period: 'לעומת התקופה הקודמת'
      } : undefined,
      icon: <Activity className="h-6 w-6 text-white" />,
      color: 'bg-blue-500',
      description: 'מספר ההחלטות הכולל בטווח הנבחר',
    },
    {
      title: 'החלטות אופרטיביות',
      value: stats?.operational || 0,
      change: undefined,
      icon: <Target className="h-6 w-6 text-white" />,
      color: 'bg-green-500',
      description: stats ? `${Math.round((stats.operational / Math.max(stats.total, 1)) * 100)}% מכלל ההחלטות` : '',
    },
    {
      title: 'החלטות דקלרטיביות',
      value: stats?.declarative || 0,
      change: undefined,
      icon: <Users className="h-6 w-6 text-white" />,
      color: 'bg-purple-500',
      description: stats ? `${Math.round((stats.declarative / Math.max(stats.total, 1)) * 100)}% מכלל ההחלטות` : '',
    },
    {
      title: 'ממוצע חודשי',
      value: stats ? Math.round(stats.avgPerMonth) : 0,
      change: undefined,
      icon: <Calendar className="h-6 w-6 text-white" />,
      color: 'bg-orange-500',
      description: 'מספר החלטות ממוצע לחודש',
    },
    {
      title: 'ועדה מובילה',
      value: stats?.mostActiveCommittee || '-',
      change: undefined,
      icon: <TrendingUp className="h-6 w-6 text-white" />,
      color: 'bg-indigo-500',
      description: 'הועדה עם המספר הגבוה ביותר של החלטות',
    },
  ];

  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4', className)}>
      {kpiData.map((kpi, index) => (
        <KPICard
          key={index}
          title={kpi.title}
          value={kpi.value}
          change={kpi.change}
          icon={kpi.icon}
          color={kpi.color}
          description={kpi.description}
          loading={isLoading}
        />
      ))}
    </div>
  );
}