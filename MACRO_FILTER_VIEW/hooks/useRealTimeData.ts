/**
 * Real-time Data Loading Hooks
 * WebSocket connections and live data updates for dashboard
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from './useDecisions';
import type { DashboardFilters, DashboardStats } from '../types/decision';

// WebSocket connection state
type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error';

interface UseRealTimeDataOptions {
  enabled?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface RealTimeUpdate {
  type: 'stats_update' | 'new_decision' | 'decision_update' | 'system_alert';
  data: any;
  timestamp: string;
}

export function useRealTimeData(
  filters: DashboardFilters,
  options: UseRealTimeDataOptions = {}
) {
  const {
    enabled = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
  } = options;

  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [updateCount, setUpdateCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();

  // Get WebSocket URL (would be configured based on environment)
  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    return `${protocol}//${host}/api/ws/dashboard`;
  }, []);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const update: RealTimeUpdate = JSON.parse(event.data);
      
      console.log('[RealTime] Received update:', update.type);
      
      setLastUpdate(new Date());
      setUpdateCount(prev => prev + 1);

      // Handle different types of updates
      switch (update.type) {
        case 'stats_update':
          // Invalidate statistics queries to trigger refetch
          queryClient.invalidateQueries({ queryKey: ['statistics'] });
          queryClient.invalidateQueries({ queryKey: ['overview'] });
          break;

        case 'new_decision':
          // Invalidate decisions and statistics
          queryClient.invalidateQueries({ queryKey: ['decisions'] });
          queryClient.invalidateQueries({ queryKey: ['statistics'] });
          
          // Show notification for new decisions
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('החלטה חדשה התקבלה', {
              body: update.data.title || 'החלטה חדשה נוספה למערכת',
              icon: '/favicon.ico',
            });
          }
          break;

        case 'decision_update':
          // Invalidate specific decision queries
          queryClient.invalidateQueries({ 
            queryKey: ['decisions'],
            exact: false 
          });
          break;

        case 'system_alert':
          // Handle system-wide alerts
          console.log('[RealTime] System alert:', update.data);
          break;

        default:
          console.warn('[RealTime] Unknown update type:', update.type);
      }
    } catch (error) {
      console.error('[RealTime] Error parsing message:', error);
    }
  }, [queryClient]);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      setConnectionState('connecting');
      setError(null);

      const ws = new WebSocket(getWebSocketUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[RealTime] Connected to WebSocket');
        setConnectionState('connected');
        reconnectAttemptRef.current = 0;

        // Send subscription message with current filters
        ws.send(JSON.stringify({
          type: 'subscribe',
          filters: filters,
        }));

        // Request notification permission
        if ('Notification' in window && Notification.permission === 'default') {
          Notification.requestPermission();
        }
      };

      ws.onmessage = handleMessage;

      ws.onclose = (event) => {
        console.log('[RealTime] WebSocket closed:', event.code, event.reason);
        setConnectionState('disconnected');
        wsRef.current = null;

        // Auto-reconnect if not intentionally closed
        if (enabled && event.code !== 1000 && reconnectAttemptRef.current < maxReconnectAttempts) {
          reconnectAttemptRef.current++;
          console.log(`[RealTime] Reconnecting... (attempt ${reconnectAttemptRef.current})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval * reconnectAttemptRef.current);
        }
      };

      ws.onerror = (error) => {
        console.error('[RealTime] WebSocket error:', error);
        setConnectionState('error');
        setError('שגיאה בחיבור לשרת');
      };

    } catch (error) {
      console.error('[RealTime] Failed to create WebSocket:', error);
      setConnectionState('error');
      setError('לא ניתן להתחבר לשרת');
    }
  }, [enabled, filters, getWebSocketUrl, handleMessage, maxReconnectAttempts, reconnectInterval]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setConnectionState('disconnected');
  }, []);

  // Manually trigger reconnection
  const reconnect = useCallback(() => {
    disconnect();
    reconnectAttemptRef.current = 0;
    setTimeout(connect, 1000);
  }, [connect, disconnect]);

  // Update subscription when filters change
  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'update_subscription',
        filters: filters,
      }));
    }
  }, [filters]);

  // Connect/disconnect based on enabled state
  useEffect(() => {
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    connectionState,
    isConnected: connectionState === 'connected',
    lastUpdate,
    updateCount,
    error,
    reconnect,
    disconnect,
  };
}

/**
 * Hook for real-time statistics updates
 */
export function useRealTimeStats(filters: DashboardFilters) {
  const [liveStats, setLiveStats] = useState<DashboardStats | null>(null);
  const [isLive, setIsLive] = useState(false);

  const { isConnected, updateCount } = useRealTimeData(filters);

  // Simulate live stats updates (in real implementation, this would come from WebSocket)
  useEffect(() => {
    if (!isConnected) {
      setIsLive(false);
      return;
    }

    setIsLive(true);

    // Simulate periodic updates
    const interval = setInterval(() => {
      // Mock live stats update
      const mockStats: DashboardStats = {
        total: Math.floor(Math.random() * 1000) + 500,
        operational: Math.floor(Math.random() * 300) + 200,
        declarative: Math.floor(Math.random() * 700) + 300,
        avgPerMonth: Math.floor(Math.random() * 50) + 25,
        mostActiveCommittee: 'הממשלה',
        policyCoverageScore: Math.floor(Math.random() * 100),
        periodComparison: {
          current: Math.floor(Math.random() * 100),
          previous: Math.floor(Math.random() * 100),
          changePercent: Math.floor(Math.random() * 40) - 20,
        },
      };

      setLiveStats(mockStats);
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [isConnected]);

  return {
    liveStats,
    isLive,
    updateCount,
  };
}

/**
 * Hook for live activity feed
 */
export function useActivityFeed(limit: number = 10) {
  const [activities, setActivities] = useState<Array<{
    id: string;
    type: 'new_decision' | 'decision_update' | 'user_action';
    message: string;
    timestamp: Date;
    metadata?: any;
  }>>([]);

  const { isConnected, updateCount } = useRealTimeData({} as DashboardFilters);

  // Simulate activity updates
  useEffect(() => {
    if (!isConnected) return;

    const mockActivities = [
      'החלטה חדשה התקבלה בנושא חינוך',
      'עדכון בהחלטה 2989 של ממשלה 37',
      'משתמש חדש הצטרף למערכת',
      'דוח חודשי נוצר אוטומטית',
      'התראה: פעילות חריגה בועדת השרים',
    ];

    // Add new activity every time there's an update
    if (updateCount > 0) {
      const newActivity = {
        id: Date.now().toString(),
        type: 'new_decision' as const,
        message: mockActivities[Math.floor(Math.random() * mockActivities.length)],
        timestamp: new Date(),
      };

      setActivities(prev => [newActivity, ...prev.slice(0, limit - 1)]);
    }
  }, [updateCount, isConnected, limit]);

  return {
    activities,
    isLive: isConnected,
  };
}

/**
 * Hook for connection status monitoring
 */
export function useConnectionStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionQuality, setConnectionQuality] = useState<'good' | 'fair' | 'poor'>('good');

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Monitor connection quality (simplified)
    const startTime = Date.now();
    fetch('/api/health', { method: 'HEAD' })
      .then(() => {
        const responseTime = Date.now() - startTime;
        if (responseTime < 200) setConnectionQuality('good');
        else if (responseTime < 1000) setConnectionQuality('fair');
        else setConnectionQuality('poor');
      })
      .catch(() => setConnectionQuality('poor'));

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return {
    isOnline,
    connectionQuality,
  };
}