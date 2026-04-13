/**
 * Clarion — Frontend Module Registry
 * 
 * Mirrors the backend module registry pattern. Each feature module
 * exports a manifest that declares its routes, navigation items,
 * dashboard widgets, and admin panels. The app shell dynamically
 * builds the UI from registered modules.
 * 
 * Usage in a module's index.ts:
 * 
 *   export const manifest: ModuleManifest = {
 *     id: 'cases',
 *     nav: { label: 'cases', icon: Briefcase, position: 1 },
 *     routes: [...],
 *     dashboardWidgets: [...],
 *   };
 */

import { ComponentType, LazyExoticComponent } from 'react';

// ─── Types ───

export interface ModuleRoute {
  path: string;
  component: () => Promise<{ default: ComponentType }>;
  requiredPermission?: string;
}

export interface ModuleNavItem {
  /** Key into terminology map (e.g., 'cases' → resolved to 'Tickets' if customised) */
  label: string;
  icon: ComponentType<{ size?: number }>;
  position: number;
  requiredPermission?: string;
}

export interface ModuleDashboardWidget {
  id: string;
  component: () => Promise<{ default: ComponentType }>;
  defaultWidth?: 1 | 2 | 3 | 4;
  defaultHeight?: 1 | 2;
}

export interface ModuleManifest {
  id: string;
  name: string;
  nav?: ModuleNavItem;
  routes: ModuleRoute[];
  dashboardWidgets?: ModuleDashboardWidget[];
  adminPanel?: () => Promise<{ default: ComponentType }>;
}

// ─── Registry ───

class FrontendModuleRegistry {
  private modules: Map<string, ModuleManifest> = new Map();
  private enabledModules: Set<string> = new Set();

  /**
   * Register a module manifest. Called at app startup.
   */
  register(manifest: ModuleManifest): void {
    this.modules.set(manifest.id, manifest);
    this.enabledModules.add(manifest.id); // Default enabled; feature flags applied later
  }

  /**
   * Apply feature flags from backend. Disables modules not in the enabled list.
   */
  applyFeatureFlags(flags: Record<string, boolean>): void {
    for (const [moduleId, enabled] of Object.entries(flags)) {
      if (enabled) {
        this.enabledModules.add(moduleId);
      } else {
        this.enabledModules.delete(moduleId);
      }
    }
  }

  /**
   * Get all enabled modules, sorted by nav position.
   */
  getEnabledModules(): ModuleManifest[] {
    return Array.from(this.modules.values())
      .filter(m => this.enabledModules.has(m.id))
      .sort((a, b) => (a.nav?.position ?? 999) - (b.nav?.position ?? 999));
  }

  /**
   * Get navigation items for the sidebar.
   * Filters by user permissions.
   */
  getNavItems(userPermissions: string[]): (ModuleNavItem & { moduleId: string })[] {
    return this.getEnabledModules()
      .filter(m => m.nav)
      .filter(m => {
        const perm = m.nav!.requiredPermission;
        return !perm || userPermissions.includes(perm);
      })
      .map(m => ({ ...m.nav!, moduleId: m.id }));
  }

  /**
   * Get all routes from enabled modules.
   */
  getRoutes(): (ModuleRoute & { moduleId: string })[] {
    return this.getEnabledModules().flatMap(m =>
      m.routes.map(r => ({ ...r, moduleId: m.id }))
    );
  }

  /**
   * Get dashboard widgets from enabled modules.
   */
  getDashboardWidgets(): (ModuleDashboardWidget & { moduleId: string })[] {
    return this.getEnabledModules().flatMap(m =>
      (m.dashboardWidgets ?? []).map(w => ({ ...w, moduleId: m.id }))
    );
  }

  /**
   * Check if a module is enabled.
   */
  isEnabled(moduleId: string): boolean {
    return this.enabledModules.has(moduleId);
  }
}

// Singleton
export const moduleRegistry = new FrontendModuleRegistry();

// ─── Module Registration ───
// Import and register all modules here. Lazy loading ensures
// disabled modules are never downloaded.

export function registerAllModules(): void {
  // Each module's index.ts is imported and its manifest registered.
  // This function is called once at app startup.

  // Core modules (always enabled)
  // import('./modules/admin').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/help').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/onboarding').then(m => moduleRegistry.register(m.manifest));

  // Feature modules (controlled by feature flags)
  // import('./modules/cases').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/analytics').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/reviews').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/predictions').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/notifications').then(m => moduleRegistry.register(m.manifest));
  // import('./modules/chatbot').then(m => moduleRegistry.register(m.manifest));

  // TODO: Uncomment as modules are built in later phases
}
