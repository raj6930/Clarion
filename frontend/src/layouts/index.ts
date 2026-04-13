/**
 * Layout Registry
 * Loads all preset configs and provides lookup by ID.
 * Adding a new layout: create a new JSON in presets/ and import here.
 */
import editorial from './presets/editorial.json';
import command from './presets/command.json';
import executive from './presets/executive.json';
import ops from './presets/ops.json';
import magazine from './presets/magazine.json';
import flow from './presets/flow.json';

export interface WidgetPlacement {
  type: string;
  metric: string;
  size?: 'sm' | 'md' | 'lg';
}

export interface GridConfig {
  areas: string[];
  columns: string;
  rows: string;
  gap: string;
}

export interface SplitConfig {
  left: { width: string; widget: WidgetPlacement };
  right: { grid: GridConfig; widgets: Record<string, WidgetPlacement> };
}

export interface LayoutPreset {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  layout?: 'grid' | 'split';
  grid?: GridConfig;
  widgets?: Record<string, WidgetPlacement>;
  split?: SplitConfig;
}

const presets: LayoutPreset[] = [
  editorial as LayoutPreset,
  command as LayoutPreset,
  executive as LayoutPreset,
  ops as LayoutPreset,
  magazine as LayoutPreset,
  flow as LayoutPreset,
];

export const layoutRegistry = {
  all: () => presets,
  get: (id: string) => presets.find(p => p.id === id) ?? presets[0],
  default: () => presets[0],
};
