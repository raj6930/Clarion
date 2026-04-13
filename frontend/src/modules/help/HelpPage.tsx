export default function HelpPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[var(--clarion-text)]">Help</h1>
        <p className="text-sm text-[var(--clarion-text-muted)] mt-1">User guide, technical documentation, and troubleshooting.</p>
      </div>
      <div className="grid gap-4">
        <div className="bg-[var(--clarion-surface)] border border-[var(--clarion-border)] rounded-xl p-6">
          <p className="text-sm text-[var(--clarion-text-muted)]">Phase 11 implementation. UI shell ready.</p>
        </div>
      </div>
    </div>
  );
}
