// apps/web/src/components/users/AddUserModal.tsx
import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { ROLES, STATUSES, isValidEmail, type Role, type UserStatus } from "./usersData";
import { usrText, roleText, statusText, type UsersStrings, type UsrLang } from "./usersI18n";

export interface NewUserData { name: string; email: string; role: Role; status: UserStatus; }

interface Props {
  open: boolean;
  strings: UsersStrings;
  lang: UsrLang;
  existingEmails: string[];
  onClose: () => void;
  onCreate: (d: NewUserData) => void;
}

export function AddUserModal({ open, strings: s, existingEmails, onClose, onCreate }: Props) {
  const [show, setShow] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<Role>("user");
  const [status, setStatus] = useState<UserStatus>("active");
  const [errors, setErrors] = useState<{ name?: string; email?: string }>({});

  useEffect(() => {
    if (open) { const r = requestAnimationFrame(() => setShow(true)); return () => cancelAnimationFrame(r); }
    setShow(false);
  }, [open]);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const submit = () => {
    const next: typeof errors = {};
    if (!name.trim()) next.name = s.nameRequired;
    const em = email.trim().toLowerCase();
    if (!isValidEmail(em)) next.email = s.emailInvalid;
    else if (existingEmails.some((x) => x.toLowerCase() === em)) next.email = s.emailExists;
    setErrors(next);
    if (Object.keys(next).length > 0) return;
    onCreate({ name: name.trim(), email: em, role, status });
    setName(""); setEmail(""); setRole("user"); setStatus("active"); setErrors({});
    onClose();
  };

  const inputCls = (bad?: string) =>
    `w-full rounded-xl border px-3 py-2.5 text-sm text-stone-800 outline-none transition-colors focus:ring-2 ${
      bad ? "border-red-300 focus:border-red-500 focus:ring-red-500/15" : "border-stone-200 focus:border-green-500 focus:ring-green-500/15"
    }`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div onClick={onClose} className="absolute inset-0 bg-stone-900/40 backdrop-blur-sm transition-opacity duration-200" style={{ opacity: show ? 1 : 0 }} />
      <div role="dialog" aria-modal="true" aria-label={s.modalTitle}
        className="relative w-full max-w-md rounded-2xl border border-stone-200 bg-white p-6 shadow-xl transition-all duration-200"
        style={{ opacity: show ? 1 : 0, transform: show ? "translateY(0)" : "translateY(12px)" }}>
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-xl text-stone-800">{s.modalTitle}</h2>
          <button onClick={onClose} className="grid h-8 w-8 place-items-center rounded-lg text-stone-500 hover:bg-stone-100"><X className="h-4 w-4" /></button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.nameLabel}</label>
            <input autoFocus value={name} onChange={(e) => setName(e.target.value)} placeholder={s.namePlaceholder} className={inputCls(errors.name)} />
            {errors.name && <p className="mt-1 text-xs font-bold text-red-700">{errors.name}</p>}
          </div>
          <div>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{s.emailLabel}</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder={s.emailPlaceholder} className={inputCls(errors.email)} />
            {errors.email && <p className="mt-1 text-xs font-bold text-red-700">{errors.email}</p>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-semibold text-stone-700">{s.roleLabel}</label>
              <select value={role} onChange={(e) => setRole(e.target.value as Role)} className={inputCls()}>
                {ROLES.map((r) => <option key={r} value={r}>{roleText(s, r)}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-stone-700">{s.statusLabel}</label>
              <select value={status} onChange={(e) => setStatus(e.target.value as UserStatus)} className={inputCls()}>
                {STATUSES.map((st) => <option key={st} value={st}>{statusText(s, st)}</option>)}
              </select>
            </div>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-2">
          <button onClick={submit} className="flex-1 rounded-xl bg-green-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">{s.create}</button>
          <button onClick={onClose} className="rounded-xl border border-stone-200 px-4 py-2.5 text-sm font-bold text-stone-700 hover:bg-stone-50">{s.cancel}</button>
        </div>
      </div>
    </div>
  );
}