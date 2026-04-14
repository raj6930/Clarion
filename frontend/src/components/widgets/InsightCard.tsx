import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

export default function InsightCard({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse" />;
  }

  const { metrics, sla } = data;

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-[var(--clarion-radius)] border border-blue-100 p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-lg bg-[var(--clarion-primary)] flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
          </svg>
        </div>
        <p className="text-[10px] font-semibold text-blue-600 uppercase tracking-[1px]">Weekly Insight</p>
      </div>
      <p className="text-[13px] font-medium text-[var(--clarion-text)] leading-relaxed mb-3">
        Your team resolved more cases than opened this week.
        SLA compliance is at {sla.overall_compliance}% with {sla.breached} breach{sla.breached !== 1 ? 'es' : ''}.
      </p>
      <div className="mt-auto flex gap-4 text-[11px]">
        <div>
          <span className="text-[var(--clarion-text-muted)]">Open</span>
          <span className="ml-1 font-bold text-[var(--clarion-text)]">{metrics.open_cases}</span>
        </div>
        <div>
          <span className="text-[var(--clarion-text-muted)]">CSAT</span>
          <span className="ml-1 font-bold text-[var(--clarion-text)]">{metrics.csat_score}/5</span>
        </div>
        <div>
          <span className="text-[var(--clarion-text-muted)]">Escalations</span>
          <span className="ml-1 font-bold text-[var(--clarion-text)]">{metrics.active_escalations}</span>
        </div>
      </div>
    </div>
  );
}
