// apps/web/src/components/account/ProfileCard.tsx
import { useEffect, useState, type ChangeEvent } from "react";
import { User, Mail, Phone, MapPin, Edit2, Check, X, Camera } from "lucide-react";
import type { UserProfile } from "./accountData";
import { roleText, localeOf, type AccountStrings, type AccLang } from "./accountI18n";

interface Props {
  user: UserProfile;
  strings: AccountStrings;
  lang: AccLang;
  onSave: (u: UserProfile) => void;
}

export function ProfileCard({ user, strings: s, lang, onSave }: Props) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<UserProfile>(user);
  const [saved, setSaved] = useState(false);
  const locale = localeOf(lang);

  useEffect(() => { setForm(user); }, [user]);
  useEffect(() => {
    if (!saved) return;
    const id = setTimeout(() => setSaved(false), 2500);
    return () => clearTimeout(id);
  }, [saved]);

  const startEdit = () => { setForm(user); setEditing(true); };
  const save = () => { onSave(form); setEditing(false); setSaved(true); };
  const cancel = () => { setForm(user); setEditing(false); };
  const set = (k: keyof UserProfile) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value } as UserProfile);

  const initials = user.name.trim().split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
  const joined = new Date(user.joinDate).toLocaleDateString(locale, { year: "numeric", month: "long", day: "numeric" });

  const fields: { key: keyof UserProfile; label: string; icon: typeof User; type: string }[] = [
    { key: "name", label: s.fullName, icon: User, type: "text" },
    { key: "email", label: s.email, icon: Mail, type: "email" },
    { key: "phone", label: s.phone, icon: Phone, type: "tel" },
    { key: "location", label: s.location, icon: MapPin, type: "text" },
  ];

  return (
    <div className="rounded-2xl border border-stone-200/80 bg-white p-6 shadow-sm">
      {/* header */}
      <div className="mb-6 flex flex-wrap items-center gap-5">
        <div className="relative">
          <div className="grid h-24 w-24 place-items-center rounded-full bg-gradient-to-br from-green-600 to-blue-600 text-3xl font-black text-white shadow-md">
            {initials}
          </div>
          {editing && (
            <button
              type="button"
              title={s.changePhoto}
              className="absolute -bottom-1 -end-1 grid h-8 w-8 place-items-center rounded-full border-2 border-white bg-stone-800 text-white shadow transition-colors hover:bg-stone-700"
            >
              <Camera className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <h2 className="font-display text-2xl text-stone-800">{user.name}</h2>
          <p className="text-stone-600">{roleText(s, user.roleKey)}</p>
          <p className="mt-1 text-xs text-stone-500">{s.memberSince}: {joined}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {saved && (
            <span className="inline-flex items-center gap-1 rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">
              <Check className="h-3.5 w-3.5" />{s.saved}
            </span>
          )}
          {!editing ? (
            <button onClick={startEdit} className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:bg-green-700">
              <Edit2 className="h-4 w-4" />{s.editProfile}
            </button>
          ) : (
            <>
              <button onClick={save} className="inline-flex items-center gap-2 rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition-colors hover:bg-green-700">
                <Check className="h-4 w-4" />{s.saveChanges}
              </button>
              <button onClick={cancel} className="inline-flex items-center gap-2 rounded-xl border border-stone-200 px-4 py-2 text-sm font-bold text-stone-700 transition-colors hover:bg-stone-50">
                <X className="h-4 w-4" />{s.cancel}
              </button>
            </>
          )}
        </div>
      </div>

      {/* fields */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {fields.map((f) => (
          <div key={f.key as string}>
            <label className="mb-1 block text-sm font-semibold text-stone-700">{f.label}</label>
            {editing ? (
              <div className="flex items-center rounded-xl border border-stone-200 bg-stone-50 px-3 transition-colors focus-within:border-green-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-green-500/15">
                <f.icon className="me-2 h-4 w-4 shrink-0 text-stone-400" />
                <input
                  type={f.type}
                  value={form[f.key] as string}
                  onChange={set(f.key)}
                  className="w-full bg-transparent py-2.5 text-stone-800 outline-none placeholder:text-stone-400"
                />
              </div>
            ) : (
              <div className="flex items-center rounded-xl border border-stone-200 bg-stone-50/70 px-3 py-2.5">
                <f.icon className="me-2 h-4 w-4 shrink-0 text-stone-400" />
                <span className="truncate text-stone-800">{user[f.key] as string}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}