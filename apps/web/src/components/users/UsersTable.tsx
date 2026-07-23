// apps/web/src/components/users/UsersTable.tsx
// table دسکتاپ (a11y + sort + actions) + card موبایل + pagination.
import { useState } from "react";
import { ArrowUp, ArrowDown, ArrowUpDown, Trash2, Users } from "lucide-react";
import type { AppUser, Role, UserStatus, SortKey, SortDir } from "./usersData";
import { ROLES, ROLE_STYLE, STATUS_STYLE, ROLE_ORDER, initials, formatDate } from "./usersData";
import { usrText, roleText, statusText, pageOfText, localeOf, type UsersStrings, type UsrLang } from "./usersI18n";

interface Props {
  users: AppUser[];          // صفحهٔ جاری (slice شده)
  strings: UsersStrings;
  lang: UsrLang;
  sortKey: SortKey;
  sortDir: SortDir;
  page: number;
  pageCount: number;
  onSort: (k: SortKey) => void;
  onPage: (p: number) => void;
  onChangeRole: (id: string, r: Role) => void;
  onToggleStatus: (id: string) => void;
  onDelete: (id: string) => void;
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ArrowUpDown className="h-3.5 w-3.5 opacity-40" />;
  return dir === "asc" ? <ArrowUp className="h-3.5 w-3.5" /> : <ArrowDown className="h-3.5 w-3.5" />;
}

function Avatar({ name, role }: { name: string; role: Role }) {
  return (
    <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-full text-xs font-black ring-1 ${ROLE_STYLE[role].avatar}`}>
      {initials(name)}
    </span>
  );
}

function RowActions({ u, s, confirmId, setConfirmId, onChangeRole, onToggleStatus, onDelete }: {
  u: AppUser; s: UsersStrings; confirmId: string | null; setConfirmId: (id: string | null) => void;
  onChangeRole: (id: string, r: Role) => void; onToggleStatus: (id: string) => void; onDelete: (id: string) => void;
}) {
  const confirming = confirmId === u.id;
  return (
    <div className="flex items-center gap-1.5">
      <select value={u.role} onChange={(e) => onChangeRole(u.id, e.target.value as Role)} aria-label={s.colRole}
        className={`cursor-pointer rounded-lg px-2 py-1 text-[11px] font-bold ring-1 outline-none ${ROLE_STYLE[u.role].badge}`}>
        {ROLES.map((r) => <option key={r} value={r}>{roleText(s, r)}</option>)}
      </select>
      <button role="switch" aria-checked={u.status === "active"} aria-label={s.toggleStatus} onClick={() => onToggleStatus(u.id)}
        className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${u.status === "active" ? "bg-green-600" : "bg-stone-300"}`}>
        <span className="absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-all"
          style={{ insetInlineStart: u.status === "active" ? "calc(100% - 1.125rem)" : "0.125rem" }} />
      </button>
      {confirming ? (
        <button onClick={() => { onDelete(u.id); setConfirmId(null); }}
          className="rounded-lg bg-red-600 px-2 py-1 text-[11px] font-bold text-white">{s.deleteConfirm}</button>
      ) : (
        <button onClick={() => { setConfirmId(u.id); setTimeout(() => setConfirmId(null), 2500); }} aria-label={s.delete}
          className="grid h-7 w-7 place-items-center rounded-lg text-stone-400 transition-colors hover:bg-red-50 hover:text-red-700">
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}

export function UsersTable(props: Props) {
  const { users, strings: s, lang, sortKey, sortDir, page, pageCount, onSort, onPage, onChangeRole, onToggleStatus, onDelete } = props;
  const locale = localeOf(lang);
  const [confirmId, setConfirmId] = useState<string | null>(null);

  if (users.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-stone-300 bg-white py-16 text-center">
        <Users className="h-10 w-10 text-stone-300" />
        <p className="text-stone-500">{s.noUsers}</p>
      </div>
    );
  }

  const thBase = "p-4 text-start text-xs font-bold uppercase tracking-wide text-stone-500";
  const sortable: SortKey[] = ["name", "email", "role", "status", "joined"];

  return (
    <div className="overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-sm">
      {/* دسکتاپ */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full min-w-[760px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-stone-200 bg-stone-50">
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("name")} aria-sort={sortKey === "name" ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
                  className="inline-flex items-center gap-1 hover:text-stone-700">{s.colUser}<SortIcon active={sortKey === "name"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("email")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colEmail}<SortIcon active={sortKey === "email"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("role")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colRole}<SortIcon active={sortKey === "role"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("status")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colStatus}<SortIcon active={sortKey === "status"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={thBase}>
                <button onClick={() => onSort("joined")} className="inline-flex items-center gap-1 hover:text-stone-700">{s.colJoined}<SortIcon active={sortKey === "joined"} dir={sortDir} /></button>
              </th>
              <th scope="col" className={`${thBase} !text-end`}>{s.colActions}</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-stone-100 transition-colors last:border-0 hover:bg-stone-50">
                <td className="p-4">
                  <div className="flex items-center gap-2.5">
                    <Avatar name={u.name} role={u.role} />
                    <span className="font-semibold text-stone-800">{u.name}</span>
                  </div>
                </td>
                <td className="p-4 text-stone-600">{u.email}</td>
                <td className="p-4"><span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${ROLE_STYLE[u.role].badge}`}>{roleText(s, u.role)}</span></td>
                <td className="p-4"><span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${STATUS_STYLE[u.status]}`}>{statusText(s, u.status)}</span></td>
                <td className="p-4 text-stone-500">{formatDate(u.joined, locale)}</td>
                <td className="p-4"><div className="flex justify-end"><RowActions u={u} s={s} confirmId={confirmId} setConfirmId={setConfirmId} onChangeRole={onChangeRole} onToggleStatus={onToggleStatus} onDelete={onDelete} /></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* موبایل */}
      <div className="divide-y divide-stone-100 md:hidden">
        {users.map((u) => (
          <div key={u.id} className="p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2.5">
                <Avatar name={u.name} role={u.role} />
                <div>
                  <p className="font-semibold text-stone-800">{u.name}</p>
                  <p className="mt-0.5 text-xs text-stone-500">{u.email}</p>
                  <p className="mt-0.5 text-[11px] text-stone-400">{formatDate(u.joined, locale)}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${ROLE_STYLE[u.role].badge}`}>{roleText(s, u.role)}</span>
                <span className={`rounded-full px-2 py-0.5 text-[11px] font-bold ring-1 ${STATUS_STYLE[u.status]}`}>{statusText(s, u.status)}</span>
              </div>
            </div>
            <div className="mt-3 flex justify-end">
              <RowActions u={u} s={s} confirmId={confirmId} setConfirmId={setConfirmId} onChangeRole={onChangeRole} onToggleStatus={onToggleStatus} onDelete={onDelete} />
            </div>
          </div>
        ))}
      </div>

      {/* pagination */}
      {pageCount > 1 && (
        <div className="flex items-center justify-between border-t border-stone-100 p-3">
          <button onClick={() => onPage(page - 1)} disabled={page <= 1}
            className="rounded-lg border border-stone-200 px-3 py-1.5 text-xs font-bold text-stone-700 transition-colors hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40">{s.prev}</button>
          <span className="text-xs font-bold tabular-nums text-stone-500">{pageOfText(s, page, pageCount, locale)}</span>
          <button onClick={() => onPage(page + 1)} disabled={page >= pageCount}
            className="rounded-lg border border-stone-200 px-3 py-1.5 text-xs font-bold text-stone-700 transition-colors hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-40">{s.next}</button>
        </div>
      )}
    </div>
  );
}