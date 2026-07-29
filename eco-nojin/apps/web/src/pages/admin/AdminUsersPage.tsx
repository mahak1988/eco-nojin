export default function AdminUsersPage() {
  return (
    <div className="space-y-4">
      <h1 className="font-display text-3xl text-stone-800">Users</h1>
      <p className="text-stone-600">
        Manage platform users. Wire to <code className="text-sm">GET /api/v1/users</code> with superuser token.
      </p>
      <div className="rounded-2xl border border-dashed border-stone-300 bg-white p-8 text-center text-sm text-stone-500">
        User table connected via admin API in next iteration. Use main Users page for current UI.
      </div>
    </div>
  );
}
