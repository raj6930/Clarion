import { useAuth } from '@/stores/authContext';
import { useState } from 'react';

const mockAccounts = [
  { id: '0013t00002qwhPMAAY', name: 'Transgrid Ltd', type: 'Cloud Estate', country: 'United States', openCases: 12, predictions: true },
  { id: '0013Z00001bHm19QAC', name: 'Transgrid Ltd', type: 'O/O (Owner/Operator)', country: 'Australia', openCases: 5, predictions: false },
  { id: '0013t00002ukY8pAAE', name: 'Origin Energy', type: 'Cloud Estate', country: 'Australia', openCases: 8, predictions: true },
];

const mockCases = [
  { id: '1', number: '00803992', subject: 'Performance Issues with Application', owner: 'Tim Trulis', age: 12, priority: 'P2', status: 'Working', product: 'EcoSys' },
  { id: '2', number: '00689632', subject: 'Database performance degradation', owner: 'Wolf Gassmann', age: 45, priority: 'P2', status: 'Working', product: 'EcoSys' },
  { id: '3', number: '00810445', subject: 'Report export timeout', owner: 'Haresh J', age: 3, priority: 'P3', status: 'Owner Assigned', product: 'EcoSys' },
];

export default function AccountsPage() {
  const { isCSM } = useAuth();
  const [expandedAccount, setExpandedAccount] = useState<string | null>(null);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-[var(--clarion-text)]">Accounts</h1>
          <p className="text-sm text-[var(--clarion-text-muted)] mt-1">
            {isCSM ? 'Your monitored accounts' : 'Account-based case monitoring'}
          </p>
        </div>
        <button className="px-3 py-1.5 text-sm font-medium rounded-lg bg-[var(--clarion-accent)] text-white hover:opacity-90 transition-opacity">
          + Add Account
        </button>
      </div>

      {/* Account list with drill-down */}
      <div className="space-y-2">
        {mockAccounts.map(account => (
          <div key={account.id} className="bg-[var(--clarion-surface)] border border-[var(--clarion-border)] rounded-xl overflow-hidden">
            {/* Account row */}
            <button
              onClick={() => setExpandedAccount(expandedAccount === account.id ? null : account.id)}
              className="w-full flex items-center justify-between p-4 hover:bg-[var(--clarion-bg)] transition-colors text-left"
            >
              <div className="flex items-center gap-4">
                <div className="w-9 h-9 rounded-lg bg-[var(--clarion-accent)]/10 flex items-center justify-center text-[var(--clarion-accent)] font-semibold text-sm">
                  {account.name[0]}
                </div>
                <div>
                  <p className="text-sm font-medium text-[var(--clarion-text)]">{account.name}</p>
                  <p className="text-xs text-[var(--clarion-text-muted)]">{account.type} · {account.country}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-[var(--clarion-accent)]/10 text-[var(--clarion-accent)]">
                  {account.openCases} open
                </span>
                {account.predictions && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600">Predictions ON</span>
                )}
                <svg className={`w-4 h-4 text-[var(--clarion-text-muted)] transition-transform ${expandedAccount === account.id ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {/* Expanded: case list */}
            {expandedAccount === account.id && (
              <div className="border-t border-[var(--clarion-border)]">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-[var(--clarion-bg)]">
                        <th className="text-left px-4 py-2 text-xs font-medium text-[var(--clarion-text-muted)]">Case #</th>
                        <th className="text-left px-4 py-2 text-xs font-medium text-[var(--clarion-text-muted)]">Subject</th>
                        <th className="text-left px-4 py-2 text-xs font-medium text-[var(--clarion-text-muted)]">Owner</th>
                        <th className="text-left px-4 py-2 text-xs font-medium text-[var(--clarion-text-muted)]">Age</th>
                        <th className="text-left px-4 py-2 text-xs font-medium text-[var(--clarion-text-muted)]">Priority</th>
                        <th className="text-left px-4 py-2 text-xs font-medium text-[var(--clarion-text-muted)]">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockCases.map(c => (
                        <tr key={c.id} className="border-t border-[var(--clarion-border)] hover:bg-[var(--clarion-bg)] cursor-pointer transition-colors">
                          <td className="px-4 py-2.5 font-mono text-xs text-[var(--clarion-accent)]">{c.number}</td>
                          <td className="px-4 py-2.5 text-[var(--clarion-text)]">{c.subject}</td>
                          <td className="px-4 py-2.5 text-[var(--clarion-text-muted)]">{c.owner}</td>
                          <td className="px-4 py-2.5 text-[var(--clarion-text-muted)]">{c.age}d</td>
                          <td className="px-4 py-2.5">
                            <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${c.priority === 'P2' ? 'bg-amber-500/10 text-amber-600' : 'bg-blue-500/10 text-blue-600'}`}>
                              {c.priority}
                            </span>
                          </td>
                          <td className="px-4 py-2.5 text-[var(--clarion-text-muted)]">{c.status}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
