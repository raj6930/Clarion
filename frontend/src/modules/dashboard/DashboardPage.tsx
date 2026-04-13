/**
 * Dashboard Page
 * Reads the user's selected layout preset and renders the grid dynamically.
 * Widgets are resolved from the widget registry by type string.
 * Phase 0: Layout rendering with stub widgets.
 * Phase 7: Live data injection via dashboard API.
 */
import { Suspense, useMemo } from 'react';
import { layoutRegistry, type LayoutPreset } from '@/layouts';
import { widgetRegistry, type WidgetProps } from '@/components/widgets/registry';
import { useAuth } from '@/stores/authContext';

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
    display: 'grid',
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
            display: 'grid',
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
  // Phase 0: hardcoded to editorial. Phase 2: from user_preferences API.
  const layoutId = 'editorial';
  const preset = useMemo(() => layoutRegistry.get(layoutId), [layoutId]);

  return (
    <div>
      <div className="mb-4">
        <h1 className="text-base font-semibold text-[var(--clarion-text)] tracking-tight">
          {user?.team_name ?? 'Dashboard'}
        </h1>
        <p className="text-[11px] text-[var(--clarion-text-muted)] mt-0.5">
          {viewMode === 'team' ? '12 engineers' : 'Account overview'} · {preset.name} layout
        </p>
      </div>
      {preset.layout === 'split' ? (
        <SplitLayout preset={preset} />
      ) : (
        <GridLayout preset={preset} />
      )}
    </div>
  );
}
