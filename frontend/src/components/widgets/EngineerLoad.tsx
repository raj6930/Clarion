import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

export default function EngineerLoad({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse" />;
  }

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px] mb-3">Engineer Workload</p>
      <div className="flex-1 flex flex-col gap-2.5 justify-center">
        {data.engineers.map(e => (
          <div key={e.engineer_initials} className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center text-white text-[9px] font-bold flex-shrink-0">
              {e.engineer_initials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between text-[11px] mb-0.5">
                <span className="text-[var(--clarion-text)] truncate">{e.engineer_name}</span>
                <span className="font-semibold text-[var(--clarion-text)] ml-2">{e.case_count}</span>
              </div>
              <div className="h-[4px] rounded-full bg-[var(--clarion-border)] overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${e.capacity_pct > 80 ? 'bg-red-500' : e.capacity_pct > 60 ? 'bg-amber-400' : 'bg-emerald-400'}`}
                  style={{ width: `${Math.min(e.capacity_pct, 100)}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
