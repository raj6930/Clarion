import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

const METRIC_CONFIG: Record<string, { label: string; field: string; max: number; unit: string; format: (v: number) => string; color: string }> = {
  open_cases:     { label: 'Open Cases', field: 'open_cases', max: 100, unit: '', format: v => v.toString(), color: 'var(--clarion-primary)' },
  sla_compliance: { label: 'SLA Compliance', field: 'sla_compliance_pct', max: 100, unit: '%', format: v => v.toFixed(0), color: '#16A34A' },
  csat_score:     { label: 'CSAT', field: 'csat_score', max: 5, unit: '/5', format: v => v.toFixed(1), color: '#8B5CF6' },
};

export default function RingGauge({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();
  const config = METRIC_CONFIG[metric] || { label: metric, field: metric, max: 100, unit: '', format: (v: number) => v.toString(), color: 'var(--clarion-primary)' };

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse" />;
  }

  const value = (data.metrics as Record<string, number>)[config.field] ?? 0;
  const pct = Math.min((value / config.max) * 100, 100);
  const r = 45;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col items-center justify-center">
      <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px] mb-3">{config.label}</p>
      <div className="relative w-28 h-28">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          <circle cx="50" cy="50" r={r} fill="none" stroke="var(--clarion-border)" strokeWidth="8" />
          <circle cx="50" cy="50" r={r} fill="none" stroke={config.color} strokeWidth="8" strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset} className="transition-all duration-700" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-[var(--clarion-text)]">{config.format(value)}</span>
          {config.unit && <span className="text-[10px] text-[var(--clarion-text-muted)]">{config.unit}</span>}
        </div>
      </div>
    </div>
  );
}
