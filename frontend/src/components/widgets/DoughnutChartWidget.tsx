import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

export default function DoughnutChartWidget({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse" />;
  }

  const { sla } = data;
  const total = sla.within_sla + sla.breached + sla.at_risk;
  const segments = [
    { label: 'Within SLA', value: sla.within_sla, color: '#16A34A' },
    { label: 'At Risk', value: sla.at_risk, color: '#F59E0B' },
    { label: 'Breached', value: sla.breached, color: '#DC2626' },
  ];

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col items-center">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px] mb-3">SLA Breakdown</p>
      <div className="flex gap-3 text-[10px]">
        {segments.map(s => (
          <span key={s.label} className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
            {s.label}: {s.value}
          </span>
        ))}
      </div>
    </div>
  );
}
