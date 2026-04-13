/**
 * AttentionTable Widget
 * Cases requiring attention with priority, SLA, risk columns.
 * Phase 0: Stub with placeholder. Phase 7: Live data rendering.
 */
import { type WidgetProps } from './registry';

export default function AttentionTable({ metric, size = 'md' }: WidgetProps) {
  return (
    <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-[var(--clarion-card-padding)] h-full">
      <p className="text-[10px] font-medium text-[var(--clarion-text-muted)] uppercase tracking-wide mb-1">
        {metric.replace(/_/g, ' ')}
      </p>
      <p className="text-xs text-[var(--clarion-text-muted)]">AttentionTable — {size}</p>
    </div>
  );
}
