import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

const PRIORITY_COLORS: Record<string, string> = {
  p1: '#DC2626', p2: '#F59E0B', p3: '#3B82F6', p4: '#94A3B8',
};
const PRIORITY_LABELS: Record<string, string> = {
  p1: 'P1 Critical', p2: 'P2 High', p3: 'P3 Medium', p4: 'P4 Low',
};

export default function PriorityBars({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse" />;
  }

  const pri = data.priority;
  const total = pri.p1 + pri.p2 + pri.p3 + pri.p4;
  const items = [
    { key: 'p1', count: pri.p1 },
    { key: 'p2', count: pri.p2 },
    { key: 'p3', count: pri.p3 },
    { key: 'p4', count: pri.p4 },
  ];

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px] mb-4">Priority Distribution</p>
      <div className="flex-1 flex flex-col gap-3 justify-center">
        {items.map(({ key, count }) => (
          <div key={key}>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-[var(--clarion-text-muted)]">{PRIORITY_LABELS[key]}</span>
              <span className="font-semibold text-[var(--clarion-text)]">{count}</span>
            </div>
            <div className="h-[6px] rounded-full bg-[var(--clarion-border)] overflow-hidden">
              <div className="h-full rounded-full transition-all duration-500" style={{ width: `${total > 0 ? (count / total) * 100 : 0}%`, backgroundColor: PRIORITY_COLORS[key] }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
