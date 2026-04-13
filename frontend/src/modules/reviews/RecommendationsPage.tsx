export default function RecommendationsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-[var(--clarion-text)]">Recommendations</h1>
        <p className="text-sm text-[var(--clarion-text-muted)] mt-1">AI-flagged cases pending review.</p>
      </div>
      <div className="grid gap-4">
        <div className="bg-[var(--clarion-surface)] border border-[var(--clarion-border)] rounded-xl p-6">
          <p className="text-sm text-[var(--clarion-text-muted)]">Phase 6 implementation. UI shell ready.</p>
        </div>
      </div>
    </div>
  );
}
