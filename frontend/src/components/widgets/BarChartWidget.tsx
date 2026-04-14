import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

export default function BarChartWidget({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse"><div className="h-full bg-[var(--clarion-border)] rounded" /></div>;
  }

  const volume = data.volume.slice(-14); // Last 14 days
  const max = Math.max(...volume.map(d => Math.max(d.opened, d.resolved)), 1);

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px]">Case Volume (14 days)</p>
        <div className="flex gap-3 text-[10px]">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-[var(--clarion-primary)]" />Opened</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-emerald-400" />Resolved</span>
        </div>
      </div>
      <div className="flex-1 flex items-end gap-[3px]">
        {volume.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-[2px]" style={{ minWidth: 0 }}>
            <div className="w-full flex flex-col items-center gap-[1px]" style={{ height: '120px' }}>
              <div className="w-full flex gap-[1px] items-end h-full">
                <div className="flex-1 rounded-t-[2px] bg-[var(--clarion-primary)] transition-all" style={{ height: `${(d.opened / max) * 100}%`, minHeight: d.opened > 0 ? '2px' : 0 }} />
                <div className="flex-1 rounded-t-[2px] bg-emerald-400 transition-all" style={{ height: `${(d.resolved / max) * 100}%`, minHeight: d.resolved > 0 ? '2px' : 0 }} />
              </div>
            </div>
            {i % 2 === 0 && <span className="text-[8px] text-[var(--clarion-text-muted)]">{d.date.slice(5)}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
