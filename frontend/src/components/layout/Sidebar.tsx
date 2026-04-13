import { NavLink } from 'react-router-dom';
import { useAuth } from '@/stores/authContext';
import { useTheme } from '@/theme/ThemeProvider';
import { useState } from 'react';

const navSections = [
  { label: 'Overview', items: [
    { path: '/dashboard', label: 'Dashboard', icon: 'M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z', roles: ['admin','manager','csm'] },
    { path: '/cases', label: 'Cases', icon: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z', roles: ['admin','manager'], badge: '47', badgeType: 'info' },
    { path: '/accounts', label: 'Accounts', icon: 'M2.25 21h19.5M3.75 3v18m4.5-18v18m4.5-18v18m4.5-18v18m4.5-18v18', roles: ['admin','manager','csm'] },
    { path: '/reviews', label: 'Reviews', icon: 'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V19.5a2.25 2.25 0 002.25 2.25h.75', roles: ['admin','manager'], badge: '3', badgeType: 'danger' },
  ]},
  { label: 'Intelligence', items: [
    { path: '/analytics', label: 'Analytics', icon: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z', roles: ['admin','manager','csm'] },
    { path: '/predictions', label: 'Predictions', icon: 'M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941', roles: ['admin','manager','csm'] },
    { path: '/notifications', label: 'Alerts', icon: 'M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0', roles: ['admin','manager'] },
  ]},
  { label: 'System', items: [
    { path: '/admin', label: 'Settings', icon: 'M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z M15 12a3 3 0 11-6 0 3 3 0 016 0z', roles: ['admin'] },
    { path: '/help', label: 'Help', icon: 'M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z', roles: ['admin','manager','csm'] },
  ]},
];

function Icon({ d }: { d: string }) {
  return (
    <svg className="w-[18px] h-[18px] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  );
}

export function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { user } = useAuth();
  const { tokens } = useTheme();
  const role = user?.role || 'manager';

  return (
    <aside className={`fixed left-0 top-0 h-screen bg-[var(--clarion-surface)] border-r border-[var(--clarion-border)] z-30 flex flex-col transition-all duration-200 ${collapsed ? 'w-[56px]' : 'w-[228px]'}`}>
      {/* Logo */}
      <div className={`flex items-center gap-[10px] border-b border-[var(--clarion-border)] ${collapsed ? 'p-[14px] justify-center' : 'p-[18px]'}`}>
        <svg width="28" height="28" viewBox="0 0 30 30" fill="none" className="flex-shrink-0">
          <rect width="30" height="30" rx="8" fill="var(--clarion-primary)" />
          <path d="M8 20L12 12L16 16L22 8" stroke="#93C5FD" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="22" cy="8" r="2.5" fill="white" /><circle cx="16" cy="16" r="2" fill="white" opacity=".7" />
          <circle cx="12" cy="12" r="2" fill="white" opacity=".7" /><circle cx="8" cy="20" r="2" fill="white" opacity=".5" />
        </svg>
        {!collapsed && <span className="text-[15px] font-semibold text-[var(--clarion-text)] tracking-tight">{tokens.companyName}</span>}
      </div>

      {/* Arrow toggle */}
      <button
        onClick={onToggle}
        className="absolute top-1/2 -right-[13px] -translate-y-1/2 w-[26px] h-[26px] rounded-full bg-[var(--clarion-surface)] border border-[var(--clarion-border)] flex items-center justify-center z-10 hover:border-[var(--clarion-accent)] hover:bg-blue-50 transition-all"
      >
        <svg className={`w-[14px] h-[14px] text-[var(--clarion-text-muted)] transition-transform ${collapsed ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
      </button>

      {/* Navigation */}
      <nav className={`flex-1 overflow-y-auto ${collapsed ? 'p-[8px_6px]' : 'p-[12px_10px]'}`}>
        {navSections.map(section => (
          <div key={section.label}>
            {!collapsed && (
              <p className="text-[9px] font-bold text-[var(--clarion-text-muted)] uppercase tracking-[1.2px] px-[10px] pt-[12px] pb-[6px]">
                {section.label}
              </p>
            )}
            {section.items.filter(i => i.roles.includes(role)).map(item => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] py-[9px] rounded-[10px] transition-all overflow-hidden whitespace-nowrap ${collapsed ? 'justify-center px-[9px]' : 'px-[11px]'} ${
                    isActive
                      ? 'bg-blue-50 text-[var(--clarion-primary)] font-medium'
                      : 'text-[var(--clarion-text-muted)] hover:bg-blue-50/50 hover:text-[var(--clarion-accent)]'
                  }`
                }
              >
                <Icon d={item.icon} />
                {!collapsed && <span className="text-[13px]">{item.label}</span>}
                {!collapsed && item.badge && (
                  <span className={`ml-auto text-[10px] font-semibold px-[7px] py-[2px] rounded-[6px] ${
                    item.badgeType === 'danger' ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-[var(--clarion-primary)]'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className={`border-t border-[var(--clarion-border)] flex items-center gap-[10px] ${collapsed ? 'justify-center p-[10px]' : 'p-[14px_16px]'}`}>
        <div className="w-[34px] h-[34px] rounded-[10px] bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
          {user?.displayName?.split(' ').map(n => n[0]).join('') || '?'}
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <p className="text-xs font-medium text-[var(--clarion-text)] truncate">{user?.displayName}</p>
            <p className="text-[10px] text-[var(--clarion-text-muted)]">{user?.teamName}</p>
          </div>
        )}
      </div>
    </aside>
  );
}
