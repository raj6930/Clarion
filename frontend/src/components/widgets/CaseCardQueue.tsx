import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

const PRIORITY_COLOR: Record<string, string> = { P1: '#DC2626', P2: '#F59E0B', P3: '#3B82F6', P4: '#94A3B8' };
const SENTIMENT_ICON: Record<string, string> = { frustrated: '😤', negative: '😟', neutral: '😐', positive: '🙂' };

export default function CaseCardQueue({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-3 h-full animate-pulse" />;
  }

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] h-full flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-[var(--clarion-border)]">
        <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px]">Case Queue</p>
      </div>
      <div className="flex-1 overflow-y-auto">
        {data.attention_cases.map(c => (
          <div key={c.case_id} className="px-4 py-3 border-b border-[var(--clarion-border)] last:border-0 hover:bg-blue-50/30 cursor-pointer transition-colors">
            <div className="flex items-start gap-2">
              <div className="w-1 h-10 rounded-full flex-shrink-0 mt-0.5" style={{ backgroundColor: PRIORITY_COLOR[c.priority] || '#94A3B8' }} />
              <div className="flex-1 min-w-0">
                <p className="text-[12px] font-medium text-[var(--clarion-text)] truncate">{c.subject}</p>
                <div className="flex items-center gap-2 mt-1 text-[10px] text-[var(--clarion-text-muted)]">
                  <span>{c.case_number}</span>
                  <span>·</span>
                  <span>{c.owner}</span>
                  <span>·</span>
                  <span>{c.age_days}d</span>
                </div>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${c.risk === 'high' ? 'bg-red-50 text-red-600' : c.risk === 'medium' ? 'bg-amber-50 text-amber-600' : 'bg-slate-50 text-slate-500'}`}>{c.risk} risk</span>
                  {c.sla_status === 'breached' && <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-red-50 text-red-600">SLA ⚠</span>}
                  {c.sentiment && <span className="text-sm">{SENTIMENT_ICON[c.sentiment]}</span>}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
