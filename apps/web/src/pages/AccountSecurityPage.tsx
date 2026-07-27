import { Link } from "react-router-dom";

export default function AccountSecurityPage() {
  return (
    <div className="mx-auto max-w-lg space-y-4 p-8">
      <h1 className="font-display text-2xl">Security</h1>
      <p className="text-sm text-stone-500">Password change and session management (Phase 1 stub).</p>
      <Link to="/account" className="text-sm font-bold text-emerald-700">
        ← Account
      </Link>
    </div>
  );
}
