import { Link, Outlet, useLocation } from "react-router-dom";
import { useUiStore } from "../../stores/uiStore";

const LINKS = [
  { to: "/admin", label: "Overview" },
  { to: "/admin/users", label: "Users" },
  { to: "/admin/modules", label: "Modules" },
  { to: "/admin/health", label: "Health" },
  { to: "/admin/settings", label: "Settings" },
];

export function AdminShell() {
  const { pathname } = useLocation();
  const { adminSidebarOpen, toggleAdminSidebar } = useUiStore();

  return (
    <div className="flex min-h-screen bg-stone-50">
      <aside
        className={`${adminSidebarOpen ? "w-56" : "w-14"} border-r border-stone-200 bg-white transition-all`}
      >
        <div className="flex items-center justify-between p-3">
          <span className="text-sm font-bold text-stone-800">{adminSidebarOpen ? "Admin" : "A"}</span>
          <button type="button" onClick={toggleAdminSidebar} className="text-xs text-stone-500">
            {adminSidebarOpen ? "«" : "»"}
          </button>
        </div>
        <nav className="space-y-1 px-2 pb-4">
          {LINKS.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`block rounded-lg px-3 py-2 text-sm ${
                pathname === l.to ? "bg-emerald-50 font-semibold text-emerald-800" : "text-stone-600 hover:bg-stone-50"
              }`}
            >
              {adminSidebarOpen ? l.label : l.label[0]}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}
