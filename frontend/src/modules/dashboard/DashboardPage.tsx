/**
 * Dashboard Page
 * Fetches data from /analytics/dashboard and provides it to all widgets
 * via DashboardContext. Layout-driven rendering from preset configs.
 */
import { Suspense, useMemo } from 'react';
import { layoutRegistry, type LayoutPreset } from '@/layouts';
import { widgetRegistry, type WidgetProps } from '@/components/widgets/registry';
import { useAuth } from '@/stores/authContext';
import { useDashboardFetch, DashboardContext } from '@/hooks/useDashboardData';

function WidgetSlot({ type, metric, size }: { type: string; metric: string; size?: string }) {
  const Widget = widgetRegistry.get(type);
  if (!Widget) {
    return (
      <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-4 flex items-center justify-center">
        <p className="text-xs text-[var(--clarion-text-muted)]">Unknown widget: {type}</p>
      </div>
    );
  }
  return (
    <Suspense fallback={<div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-4 animate-pulse h-full" />}>
      <Widget metric={metric} size={(size as WidgetProps['size']) ?? 'md'} />
    </Suspense>
  );
}

function GridLayout({ preset }: { preset: LayoutPreset }) {
  if (!preset.grid || !preset.widgets) return null;
  const { grid, widgets } = preset;
  const style = {
    display: 'grid' as const,
    gridTemplateAreas: grid.areas.map(row => `"${row}"`).join(' '),
    gridTemplateColumns: grid.columns,
    gridTemplateRows: grid.rows,
    gap: grid.gap,
  };

  return (
    <div style={style}>
      {Object.entries(widgets).map(([area, widget]) => (
        <div key={area} style={{ gridArea: area }}>
          <WidgetSlot type={widget.type} metric={widget.metric} size={widget.size} />
        </div>
      ))}
    </div>
  );
}

function SplitLayout({ preset }: { preset: LayoutPreset }) {
  if (!preset.split) return null;
  const { left, right } = preset.split;

  return (
    <div className="flex gap-[var(--clarion-gap)] h-full">
      <div style={{ width: left.width, flexShrink: 0 }}>
        <WidgetSlot type={left.widget.type} metric={left.widget.metric} />
      </div>
      <div className="flex-1">
        {right.grid && right.widgets && (
          <div style={{
            display: 'grid' as const,
            gridTemplateAreas: right.grid.areas.map(r => `"${r}"`).join(' '),
            gridTemplateColumns: right.grid.columns,
            gridTemplateRows: right.grid.rows,
            gap: right.grid.gap,
          }}>
            {Object.entries(right.widgets).map(([area, widget]) => (
              <div key={area} style={{ gridArea: area }}>
                <WidgetSlot type={widget.type} metric={widget.metric} size={widget.size} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user, viewMode } = useAuth();
  const dashboardState = useDashboardFetch();
  const layoutId = 'editorial';
  const preset = useMemo(() => layoutRegistry.get(layoutId), [layoutId]);

  return (
    <DashboardContext.Provider value={dashboardState}>
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-base font-semibold text-[var(--clarion-text)] tracking-tight">
              {user?.team_name ?? 'Dashboard'}
            </h1>
            <p className="text-[11px] text-[var(--clarion-text-muted)] mt-0.5">
              {viewMode === 'team' ? '6 engineers' : 'Account overview'} · {preset.name} layout
            </p>
          </div>
          {dashboardState.error && (
            <button onClick={dashboardState.refresh} className="text-[11px] text-red-500 hover:text-red-700 flex items-center gap-1">
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
              </svg>
              Retry
            </button>
          )}
        </div>
        {preset.layout === 'split' ? (
          <SplitLayout preset={preset} />
        ) : (
          <GridLayout preset={preset} />
        )}
      </div>
    </DashboardContext.Provider>
  );
}
