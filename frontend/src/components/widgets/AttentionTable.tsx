import { useDashboardData } from '@/hooks/useDashboardData';
import { type WidgetProps } from './registry';

const PRIORITY_BADGE: Record<string, string> = {
  P1: 'bg-red-100 text-red-700', P2: 'bg-amber-100 text-amber-700', P3: 'bg-blue-100 text-blue-600', P4: 'bg-slate-100 text-slate-600',
};
const RISK_BADGE: Record<string, string> = {
  high: 'bg-red-50 text-red-600', medium: 'bg-amber-50 text-amber-600', low: 'bg-green-50 text-green-600',
};
const SENTIMENT_ICON: Record<string, string> = {
  frustrated: '😤', negative: '😟', neutral: '😐', positive: '🙂',
};

export default function AttentionTable({ metric }: WidgetProps) {
  const { data, loading } = useDashboardData();

  if (loading || !data) {
    return <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full animate-pulse"><div className="h-full bg-[var(--clarion-border)] rounded" /></div>;
  }

  const cases = data.attention_cases;

  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-5 h-full flex flex-col">
      <div className="flex justify-between items-center mb-3">
        <p className="text-[10px] font-semibold text-[var(--clarion-text-muted)] uppercase tracking-[1px]">Attention Queue</p>
        <span className="text-[10px] font-medium text-[var(--clarion-primary)]">{cases.length} cases</span>
      </div>
      <div className="flex-1 overflow-auto">
        <table className="w-full text-[12px]">
          <thead>
            <tr className="border-b border-[var(--clarion-border)]">
              <th className="text-left font-medium text-[var(--clarion-text-muted)] pb-2 pr-3">Case</th>
              <th className="text-left font-medium text-[var(--clarion-text-muted)] pb-2 pr-3">Owner</th>
              <th className="text-center font-medium text-[var(--clarion-text-muted)] pb-2 pr-3">Age</th>
              <th className="text-center font-medium text-[var(--clarion-text-muted)] pb-2 pr-3">Pri</th>
              <th className="text-center font-medium text-[var(--clarion-text-muted)] pb-2 pr-3">SLA</th>
              <th className="text-center font-medium text-[var(--clarion-text-muted)] pb-2 pr-3">Risk</th>
              <th className="text-center font-medium text-[var(--clarion-text-muted)] pb-2"></th>
            </tr>
          </thead>
          <tbody>
            {cases.map(c => (
              <tr key={c.case_id} className="border-b border-[var(--clarion-border)] last:border-0 hover:bg-blue-50/30 cursor-pointer transition-colors">
                <td className="py-2.5 pr-3">
                  <p className="font-medium text-[var(--clarion-text)] truncate max-w-[200px]">{c.subject}</p>
                  <p className="text-[10px] text-[var(--clarion-text-muted)]">{c.case_number}</p>
                </td>
                <td className="py-2.5 pr-3 text-[var(--clarion-text-muted)] whitespace-nowrap">{c.owner}</td>
                <td className="py-2.5 pr-3 text-center font-medium text-[var(--clarion-text)]">{c.age_days}d</td>
                <td className="py-2.5 pr-3 text-center"><span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${PRIORITY_BADGE[c.priority] || ''}`}>{c.priority}</span></td>
                <td className="py-2.5 pr-3 text-center"><span className={`text-[10px] font-medium ${c.sla_status === 'breached' ? 'text-red-600' : 'text-[var(--clarion-text-muted)]'}`}>{c.sla_status === 'breached' ? '⚠ Breached' : '✓ OK'}</span></td>
                <td className="py-2.5 pr-3 text-center"><span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${RISK_BADGE[c.risk] || ''}`}>{c.risk}</span></td>
                <td className="py-2.5 text-center text-sm">{c.sentiment ? SENTIMENT_ICON[c.sentiment] || '' : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
