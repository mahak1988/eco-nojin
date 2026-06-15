export default function VerificationPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold tracking-tight text-slate-50">
        Data Verification Monitor
      </h1>
      <p className="text-xs text-slate-400">
        This workspace will track data coverage, sensor vs model consistency and
        satellite vs field verification metrics across your pilots.
      </p>
      <div className="rounded-3xl border border-white/5 bg-slate-950/80 p-4 text-xs text-slate-400">
        QA/QC charts and tables will be wired to backend verification routines in the
        next iteration.
      </div>
    </div>
  );
}
