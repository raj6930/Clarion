import { type WidgetProps } from './registry';
import { useDashboardData } from '@/hooks/useDashboardData';

const METRIC_CONFIG: Record<string, { label: string; field: string; changeField: string; unit: string; format: (v: number) => string }> = {
  resolution_time: { label: 'Avg Resolution', field: 'avg_resolution_days', changeField: 'resolution_change', unit: 'days', format: (v) => v.toFixed(1) },
  sla_compliance:  { label: 'SLA Compliance', field: 'sla_compliance_pct', changeField: 'sla_change', unit: '%', format: (v) => v.toFixed(0) },
  csat_score:      { label: 'CSAT Score', field: 'csat_score', changeField: 'csat_change', unit: '/5', format: (v) => v.toFixed(1) },
  open_cases:      { label: 'Open Cases', field: 'open_cases', changeField: 'open_cases_change', unit: '', format: (v) => v.toString() },
  p1p2_active:     { label: 'P1/P2 Active', field: 'p1p2_active', changeField: 'p1p2_change', unit: '', format: (v) => v.toString() },
  active_escalations: { label: 'Escalations', field: 'active_escalations', changeField: '', unit: '', format: (v) => v.toString() },
};

export default function StatCard({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();
  const config = METRIC_CONFIG[metric] || { label: metric.replace(/_/g, ' '), field: metric, changeField: '', unit: '', format: (v: number) => v.toString() };

  if (loading || !data) {
    return (
      <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-[var(--clarion-card-padding)] h-full animate-pulse">
        <div className="h-3 bg-[var(--clarion-border)] rounded w-20 mb-3" />
        <div className="h-6 bg-[var(--clarion-border)] rounded w-16" />
      </div>
    );
  }

  const metrics = data.metrics as Record<string, number>;
  const value = metrics[config.field] ?? 0;
  const change = config.changeField ? metrics[config.changeField] ?? 0 : 0;
  const isPositive = metric === 'resolution_time' ? change < 0 : change > 0;
  const isNeutral = change === 0;

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-[var(--clarion-card-padding)] h-full flex flex-col justify-between">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px]">
        {config.label}
      </p>
      <div className="mt-2">
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-bold text-[var(--clarion-text)] tracking-tight">{config.format(value)}</span>
          {config.unit && <span className="text-xs text-[var(--clarion-text-muted)]">{config.unit}</span>}
        </div>
        {config.changeField && (
          <div className={`flex items-center gap-1 mt-1.5 text-[11px] font-medium ${isNeutral ? 'text-[var(--clarion-text-muted)]' : isPositive ? 'text-emerald-600' : 'text-red-500'}`}>
            {!isNeutral && (
              <svg className={`w-3 h-3 ${isPositive ? '' : 'rotate-180'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
              </svg>
            )}
            <span>{change > 0 ? '+' : ''}{typeof change === 'number' && change % 1 !== 0 ? change.toFixed(1) : change}</span>
            <span className="text-[var(--clarion-text-muted)] font-normal">vs last week</span>
          </div>
        )}
      </div>
    </div>
  );
}
