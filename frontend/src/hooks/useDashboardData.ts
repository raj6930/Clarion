/**
 * Dashboard data fetching hook.
 * Fetches from /analytics/dashboard and provides typed data to all widgets.
 */
import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { api } from '@/services/api';

// ─── Types matching the API response ───
export interface DashboardMetrics {
  open_cases: number;
  open_cases_change: number;
  p1p2_active: number;
  p1p2_change: number;
  avg_resolution_days: number;
  resolution_change: number;
  sla_compliance_pct: number;
  sla_change: number;
  csat_score: number;
  csat_change: number;
  active_escalations: number;
}

export interface VolumeDataPoint {
  date: string;
  opened: number;
  resolved: number;
}

export interface PriorityDistribution {
  p1: number;
  p2: number;
  p3: number;
  p4: number;
}

export interface EngineerWorkload {
  engineer_name: string;
  engineer_initials: string;
  case_count: number;
  capacity_pct: number;
}

export interface AttentionCase {
  case_id: string;
  case_number: string;
  subject: string;
  owner: string;
  age_days: number;
  priority: string;
  sla_status: string;
  risk: string;
  sentiment: string | null;
}

export interface SLAMetrics {
  overall_compliance: number;
  within_sla: number;
  breached: number;
  at_risk: number;
  by_priority: Record<string, number>;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  volume: VolumeDataPoint[];
  priority: PriorityDistribution;
  engineers: EngineerWorkload[];
  attention_cases: AttentionCase[];
  sla: SLAMetrics;
}

interface DashboardState {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

// ─── Context ───
const DashboardContext = createContext<DashboardState>({
  data: null, loading: true, error: null, refresh: () => {},
});

export function useDashboardData(): DashboardState {
  return useContext(DashboardContext);
}

export { DashboardContext };

// ─── Hook for the provider ───
export function useDashboardFetch(): DashboardState {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api<DashboardData>('/analytics/dashboard');
      setData(response);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load dashboard';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, loading, error, refresh: fetchData };
}
