/** Route catalog — helps diagnose “page won’t open” / missing nav links. */
import { Link } from "react-router-dom";
import { HUB_ROUTES } from "./hub/hubRoutes";

const CORE: { path: string; label: string }[] = [
  { path: "/", label: "Home" },
  { path: "/dashboard", label: "Dashboard" },
  { path: "/science", label: "Science" },
  { path: "/science/e2e", label: "Science E2E MRV" },
  { path: "/free-stack", label: "Free stack status" },
  { path: "/economics", label: "Economics" },
  { path: "/farms", label: "Farms" },
  { path: "/simulators", label: "Simulators" },
  { path: "/simulators/aquacrop", label: "AquaCrop" },
  { path: "/simulators/rothc", label: "RothC" },
  { path: "/satellite", label: "Satellite" },
  { path: "/mrv", label: "MRV" },
  { path: "/ecocoin", label: "EcoCoin" },
  { path: "/monitoring", label: "Monitoring" },
  { path: "/education", label: "Education" },
  { path: "/settings", label: "Settings" },
  { path: "/login", label: "Login" },
];

export default function SiteMapPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-display text-3xl font-bold text-stone-900">Site map / نقشه مسیرها</h1>
        <p className="mt-2 text-stone-600">
          If a page fails to open, check this list and browser console. Hub routes are lightweight stubs for parity.
        </p>
      </header>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Core</h2>
        <ul className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
          {CORE.map((r) => (
            <li key={r.path}>
              <Link className="text-emerald-700 underline hover:text-emerald-900" to={r.path}>
                {r.label} <span className="text-stone-400">{r.path}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="mb-3 text-lg font-semibold">Hub catalog ({HUB_ROUTES.length})</h2>
        <ul className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
          {HUB_ROUTES.map((r) => (
            <li key={r.slug}>
              <Link className="text-emerald-700 underline" to={`/hub/${r.slug}`}>
                {r.title} <span className="text-stone-400">/hub/{r.slug}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
