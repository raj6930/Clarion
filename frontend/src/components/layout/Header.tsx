import { useAuth } from '@/stores/authContext';
import { useTheme } from '@/theme/ThemeProvider';

function ViewToggle() {
  const { viewMode, setViewMode, isManager } = useAuth();
  if (!isManager) return null;

  return (
    <div className="flex gap-[6px]">
      {(['team', 'account'] as const).map(mode => {
        const active = viewMode === mode;
        return (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`px-[18px] py-[5px] text-[12px] font-medium rounded-lg border-[1.5px] transition-all ${
              active
                ? 'border-[var(--clarion-accent)] text-[var(--clarion-primary)] bg-blue-50/80'
                : 'border-[var(--clarion-border)] text-[#7BA4CC] hover:border-[#93C5FD] hover:text-[var(--clarion-accent)]'
            }`}
          >
            {mode === 'team' ? 'Team view' : 'Account view'}
          </button>
        );
      })}
    </div>
  );
}

export function Header({ sidebarCollapsed }: { sidebarCollapsed: boolean }) {
  const { user } = useAuth();
  const { toggleDarkMode } = useTheme();

  return (
    <header className={`fixed top-0 right-0 h-[56px] bg-[var(--clarion-surface)] border-b border-[var(--clarion-border)] z-20 flex items-center justify-between px-6 transition-all duration-200 ${sidebarCollapsed ? 'left-[56px]' : 'left-[228px]'}`}>
      <div className="flex items-center gap-4">
        <div className="text-sm">
          <span className="font-semibold text-[var(--clarion-text)]">{user?.teamName}</span>
          <span className="text-[var(--clarion-text-muted)] ml-1">· 12 engineers</span>
        </div>
        <ViewToggle />
      </div>

      <div className="flex items-center gap-1">
        <div className="flex items-center gap-[5px] mr-2 text-[11px] text-[var(--clarion-text-muted)]">
          <span className="w-[6px] h-[6px] rounded-full bg-green-500 animate-pulse" />
          Live
        </div>
        <div className="w-px h-5 bg-[var(--clarion-border)] mx-1" />

        <button onClick={toggleDarkMode} className="w-[34px] h-[34px] rounded-[10px] flex items-center justify-center text-[var(--clarion-text-muted)] hover:bg-blue-50 hover:text-[var(--clarion-accent)] transition-all">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
          </svg>
        </button>

        <button className="w-[34px] h-[34px] rounded-[10px] flex items-center justify-center text-[var(--clarion-text-muted)] hover:bg-blue-50 hover:text-[var(--clarion-accent)] transition-all relative">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
          </svg>
          <span className="absolute top-[5px] right-[5px] w-[6px] h-[6px] rounded-full bg-red-500 border-[1.5px] border-[var(--clarion-surface)]" />
        </button>
      </div>
    </header>
  );
}
