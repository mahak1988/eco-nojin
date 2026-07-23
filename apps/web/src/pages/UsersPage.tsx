// apps/web/src/pages/UsersPage.tsx
import { useEffect, useMemo, useState } from "react";
import { Users, Search, UserPlus, Download, Check } from "lucide-react";
import { useLang } from "../components/eco/i18n";
import { SectionReveal } from "../components/eco/SectionReveal";
import { UserStats } from "../components/users/UserStats";
import { UsersTable } from "../components/users/UsersTable";
import { AddUserModal, type NewUserData } from "../components/users/AddUserModal";
import { USR_STR, usrText, roleText, statusText, localeOf, type UsrLang } from "../components/users/usersI18n";
import {
  INITIAL_USERS, ROLES, STATUSES, ROLE_ORDER, PAGE_SIZE, downloadCSV,
  type AppUser, type Role, type UserStatus, type SortKey, type SortDir,
} from "../components/users/usersData";

export default function UsersPage() {
  const { lang } = useLang();
  const s = USR_STR[lang as UsrLang];
  const locale = localeOf(lang as UsrLang);

  const [users, setUsers] = useState<AppUser[]>(INITIAL_USERS);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<"all" | Role>("all");
  const [statusFilter, setStatusFilter] = useState<"all" | UserStatus>("all");
  const [sortKey, setSortKey] = useState<SortKey>("joined");
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const [page, setPage] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [exported, setExported] = useState(false);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = users.filter((u) =>
      (roleFilter === "all" || u.role === roleFilter) &&
      (statusFilter === "all" || u.status === statusFilter) &&
      (q === "" || u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
    );
    list.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "name") cmp = a.name.localeCompare(b.name);
      else if (sortKey === "email") cmp = a.email.localeCompare(b.email);
      else if (sortKey === "role") cmp = ROLE_ORDER[a.role] - ROLE_ORDER[b.role];
      else if (sortKey === "status") cmp = a.status.localeCompare(b.status);
      else cmp = +new Date(a.joined) - +new Date(b.joined);
      return sortDir === "asc" ? cmp : -cmp;
    });
    return list;
  }, [users, search, roleFilter, statusFilter, sortKey, sortDir]);

  // ریست صفحه هنگام تغییر فیلتر/جست‌وجو/sort
  useEffect(() => { setPage(1); }, [search, roleFilter, statusFilter, sortKey, sortDir]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageItems = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const onSort = (k: SortKey) => {
    if (k === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(k); setSortDir(k === "name" || k === "email" ? "asc" : "desc"); }
  };
  const changeRole = (id: string, r: Role) => setUsers((p) => p.map((u) => (u.id === id ? { ...u, role: r } : u)));
  const toggleStatus = (id: string) => setUsers((p) => p.map((u) => (u.id === id ? { ...u, status: u.status === "active" ? "inactive" : "active" } : u)));
  const deleteUser = (id: string) => setUsers((p) => p.filter((u) => u.id !== id));
  const createUser = (d: NewUserData) =>
    setUsers((p) => [{ id: `u${Date.now()}`, name: d.name, email: d.email, role: d.role, status: d.status, joined: new Date().toISOString() }, ...p]);

  const exportAll = () => {
    const header = s.csvHeaders.split(",");
    const rows = filtered.map((u) => [u.id, u.name, u.email, roleText(s, u.role), statusText(s, u.status), u.joined.slice(0, 10)]
      .map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
    downloadCSV("users.csv", [header.join(","), ...rows].join("\n"));
    setExported(true); setTimeout(() => setExported(false), 1800);
  };

  const selectCls = "rounded-xl border border-stone-200 bg-white px-3 py-2.5 text-sm font-bold text-stone-700 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500/15";

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-5 sm:p-8">
      <SectionReveal>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-xl bg-green-50 ring-1 ring-green-600/15"><Users className="h-5 w-5 text-green-700" /></div>
            <div>
              <h1 className="font-display text-3xl text-stone-800">{s.title}</h1>
              <p className="mt-0.5 text-stone-600">{s.subtitle}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={exportAll} disabled={filtered.length === 0}
              className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold shadow-sm transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 ${exported ? "bg-green-50 text-green-700" : "bg-white text-stone-700 hover:bg-stone-50 border border-stone-200"}`}>
              {exported ? <Check className="h-4 w-4" /> : <Download className="h-4 w-4" />}{s.exportAll}
            </button>
            <button onClick={() => setModalOpen(true)} className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <UserPlus className="h-4 w-4" />{s.addUser}
            </button>
          </div>
        </div>
      </SectionReveal>

      <UserStats users={users} strings={s} />

      <SectionReveal delay={100}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-[220px] flex-1">
            <Search className="pointer-events-none absolute top-1/2 start-3 h-4 w-4 -translate-y-1/2 text-stone-400" />
            <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={s.searchPlaceholder}
              className="w-full rounded-xl border border-stone-200 bg-white py-2.5 ps-9 pe-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-green-500 focus:ring-2 focus:ring-green-500/15" />
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {(["all", ...ROLES] as ("all" | Role)[]).map((f) => (
              <button key={f} onClick={() => setRoleFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${roleFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {f === "all" ? s.filterAllRoles : roleText(s, f)}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-1 rounded-full border border-stone-200 bg-white p-1">
            {(["all", ...STATUSES] as ("all" | UserStatus)[]).map((f) => (
              <button key={f} onClick={() => setStatusFilter(f)}
                className={`rounded-full px-3 py-1.5 text-xs font-bold transition-colors ${statusFilter === f ? "bg-green-600 text-white shadow-sm" : "text-stone-600 hover:bg-stone-100"}`}>
                {f === "all" ? s.filterAllStatus : statusText(s, f)}
              </button>
            ))}
          </div>
        </div>
      </SectionReveal>

      <SectionReveal delay={120}>
        <UsersTable users={pageItems} strings={s} lang={lang as UsrLang}
          sortKey={sortKey} sortDir={sortDir} page={page} pageCount={pageCount}
          onSort={onSort} onPage={setPage} onChangeRole={changeRole} onToggleStatus={toggleStatus} onDelete={deleteUser} />
      </SectionReveal>

      <AddUserModal open={modalOpen} strings={s} lang={lang as UsrLang}
        existingEmails={users.map((u) => u.email)} onClose={() => setModalOpen(false)} onCreate={createUser} />
    </div>
  );
}