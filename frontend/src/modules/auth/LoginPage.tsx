/**
 * Login Page
 * Clean, branded login form matching the Clarion design language.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/stores/authContext';
import { useTheme } from '@/theme/ThemeProvider';

export default function LoginPage() {
  const [email, setEmail] = useState('demo@hexagon.com');
  const [password, setPassword] = useState('Clarion2026!');
  const [submitting, setSubmitting] = useState(false);
  const { login, error } = useAuth();
  const { tokens } = useTheme();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch {}
    setSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-[var(--clarion-bg)] flex items-center justify-center p-4">
      <div className="w-full max-w-[380px]">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-8 justify-center">
          <svg width="36" height="36" viewBox="0 0 30 30" fill="none">
            <rect width="30" height="30" rx="8" fill="var(--clarion-primary)" />
            <path d="M8 20L12 12L16 16L22 8" stroke="#93C5FD" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="22" cy="8" r="2.5" fill="white" /><circle cx="16" cy="16" r="2" fill="white" opacity=".7" />
            <circle cx="12" cy="12" r="2" fill="white" opacity=".7" /><circle cx="8" cy="20" r="2" fill="white" opacity=".5" />
          </svg>
          <span className="text-xl font-semibold text-[var(--clarion-text)] tracking-tight">{tokens.companyName}</span>
        </div>

        {/* Form card */}
        <div className="bg-[var(--clarion-surface)] rounded-[var(--clarion-radius)] border border-[var(--clarion-border)] p-7">
          <h1 className="text-base font-semibold text-[var(--clarion-text)] mb-1">Sign in</h1>
          <p className="text-[12px] text-[var(--clarion-text-muted)] mb-6">Enter your credentials to access the dashboard</p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-[12px] px-3 py-2 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-medium text-[var(--clarion-text-muted)] mb-1.5">Email</label>
              <input
                type="email" value={email} onChange={e => setEmail(e.target.value)}
                className="w-full px-3 py-2.5 text-[13px] rounded-lg border border-[var(--clarion-border)] bg-[var(--clarion-bg)] text-[var(--clarion-text)] focus:outline-none focus:border-[var(--clarion-accent)] focus:ring-1 focus:ring-[var(--clarion-accent)] transition-all"
                required
              />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-[var(--clarion-text-muted)] mb-1.5">Password</label>
              <input
                type="password" value={password} onChange={e => setPassword(e.target.value)}
                className="w-full px-3 py-2.5 text-[13px] rounded-lg border border-[var(--clarion-border)] bg-[var(--clarion-bg)] text-[var(--clarion-text)] focus:outline-none focus:border-[var(--clarion-accent)] focus:ring-1 focus:ring-[var(--clarion-accent)] transition-all"
                required
              />
            </div>
            <button
              type="submit" disabled={submitting}
              className="w-full py-2.5 text-[13px] font-medium rounded-lg bg-[var(--clarion-primary)] text-white hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {submitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="text-center text-[11px] text-[var(--clarion-text-muted)] mt-5">
            Demo: demo@hexagon.com / Clarion2026!
          </p>
        </div>
      </div>
    </div>
  );
}
