import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function AppLayout() {
  const [collapsed, setCollapsed] = useState(true); // Start collapsed per design

  return (
    <div className="min-h-screen bg-[var(--clarion-bg)]">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(p => !p)} />
      <Header sidebarCollapsed={collapsed} />
      <main className={`pt-[56px] transition-all duration-200 ${collapsed ? 'pl-[56px]' : 'pl-[228px]'}`}>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
