import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

export default function LineChartWidget({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse" />;
  }

  const volume = data.volume.slice(-21);
  const resolved = volume.map(d => d.resolved);
  const max = Math.max(...resolved, 1);
  const h = 100; const w = 300;
  const points = resolved.map((v, i) => `${(i / (resolved.length - 1)) * w},${h - (v / max) * h}`).join(' ');

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px] mb-3">Resolution Trend</p>
      <div className="flex-1 flex items-center">
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full" preserveAspectRatio="none" style={{ maxHeight: '120px' }}>
          <defs>
            <linearGradient id="line-fill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#16A34A" stopOpacity="0.12" />
              <stop offset="100%" stopColor="#16A34A" stopOpacity="0" />
            </linearGradient>
          </defs>
          <polygon points={`0,${h} ${points} ${w},${h}`} fill="url(#line-fill)" />
          <polyline points={points} fill="none" stroke="#16A34A" strokeWidth="2" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  );
}
