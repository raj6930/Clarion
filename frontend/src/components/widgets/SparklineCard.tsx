import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

export default function SparklineCard({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return (
      <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-6 h-full animate-pulse">
        <div className="h-4 bg-[var(--clarion-border)] rounded w-32 mb-4" />
        <div className="h-12 bg-[var(--clarion-border)] rounded w-24 mb-4" />
        <div className="h-20 bg-[var(--clarion-border)] rounded" />
      </div>
    );
  }

  const { metrics, volume } = data;
  const value = metrics.open_cases;
  const change = metrics.open_cases_change;

  // Build sparkline from last 14 days of volume
  const sparkData = volume.slice(-14).map(d => d.opened);
  const max = Math.max(...sparkData, 1);
  const h = 60;
  const w = 280;
  const points = sparkData.map((v, i) => `${(i / (sparkData.length - 1)) * w},${h - (v / max) * h}`).join(' ');

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-6 h-full flex flex-col">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px] mb-1">
        Open Cases
      </p>

      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-[42px] font-bold text-[var(--clarion-text)] tracking-tight leading-none">{value}</span>
        <div className={`flex items-center gap-0.5 text-xs font-medium ${change > 0 ? 'text-red-500' : change < 0 ? 'text-emerald-600' : 'text-[var(--clarion-text-muted)]'}`}>
          {change !== 0 && (
            <svg className={`w-3 h-3 ${change < 0 ? '' : 'rotate-180'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
            </svg>
          )}
          <span>{change > 0 ? '+' : ''}{change} this week</span>
        </div>
      </div>

      <p className="text-[11px] text-[var(--clarion-text-muted)] mb-3">
        {metrics.p1p2_active} P1/P2 · {metrics.active_escalations} escalated
      </p>

      <div className="flex-1 flex items-end">
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ maxHeight: '70px' }}>
          <defs>
            <linearGradient id="spark-fill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="var(--clarion-primary)" stopOpacity="0.15" />
              <stop offset="100%" stopColor="var(--clarion-primary)" stopOpacity="0" />
            </linearGradient>
          </defs>
          <polygon points={`0,${h} ${points} ${w},${h}`} fill="url(#spark-fill)" />
          <polyline points={points} fill="none" stroke="var(--clarion-primary)" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        </svg>
      </div>
    </div>
  );
}
