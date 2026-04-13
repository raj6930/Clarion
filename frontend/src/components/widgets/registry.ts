/**
 * Widget Registry
 * Maps widget type strings (from layout presets) to React components.
 * Adding a new widget: create component, import here, add to registry map.
 */
import { lazy, ComponentType } from 'react';

// Lazy-load all widgets for code splitting
const StatCard = lazy(() => import('./StatCard'));
const SparklineCard = lazy(() => import('./SparklineCard'));
const RingGauge = lazy(() => import('./RingGauge'));
const BarChart = lazy(() => import('./BarChartWidget'));
const LineChart = lazy(() => import('./LineChartWidget'));
const DoughnutChart = lazy(() => import('./DoughnutChartWidget'));
const PriorityBars = lazy(() => import('./PriorityBars'));
const AttentionTable = lazy(() => import('./AttentionTable'));
const CaseCardQueue = lazy(() => import('./CaseCardQueue'));
const EngineerLoad = lazy(() => import('./EngineerLoad'));
const InsightCard = lazy(() => import('./InsightCard'));

export interface WidgetProps {
  metric: string;
  data?: any;
  size?: 'sm' | 'md' | 'lg';
}

const widgetMap: Record<string, ComponentType<WidgetProps>> = {
  StatCard,
  SparklineCard,
  RingGauge,
  BarChart,
  LineChart,
  DoughnutChart,
  PriorityBars,
  AttentionTable,
  CaseCardQueue,
  EngineerLoad,
  InsightCard,
};

export const widgetRegistry = {
  get: (type: string) => widgetMap[type],
  has: (type: string) => type in widgetMap,
  types: () => Object.keys(widgetMap),
};
