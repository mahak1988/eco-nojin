export default function AdminSettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="font-display text-3xl text-stone-800">Admin settings</h1>
      <ul className="list-disc space-y-2 pl-5 text-sm text-stone-600">
        <li>REQUIRE_AUTH_FOR_WRITES should be true outside local.</li>
        <li>SECRET_KEY must be rotated and stored only in environment secrets.</li>
        <li>Disable public /docs in production.</li>
        <li>Configure CORS to production web origin only.</li>
      </ul>
    </div>
  );
}
