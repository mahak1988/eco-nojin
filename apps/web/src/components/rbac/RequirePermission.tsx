import { type ReactNode } from "react";
import { Link } from "react-router-dom";
import { ShieldOff } from "lucide-react";
import { can, readDemoRole, type Permission } from "../../lib/rbacStore";
import { useLang } from "../eco/i18n";

type Props = {
  perm: Permission;
  children: ReactNode;
  hide?: boolean;
};

export function RequirePermission({ perm, children, hide }: Props) {
  const role = readDemoRole();
  const { lang } = useLang();
  if (can(role, perm)) return <>{children}</>;
  if (hide) return null;

  const msg =
    lang === "fa"
      ? "شما به این بخش دسترسی ندارید. نقش فعلی خود را از صفحه کاربران یا سوئیچر نقش تغییر دهید."
      : lang === "ar"
        ? "ليس لديك صلاحية لهذا القسم. غيّر دورك الحالي من صفحة المستخدمين."
        : "You do not have access to this section. Change your demo role from Users page or the role switcher.";

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center gap-4 p-10 text-center">
      <div className="grid h-16 w-16 place-items-center rounded-2xl bg-rose-50 ring-1 ring-rose-200">
        <ShieldOff className="h-8 w-8 text-rose-600" />
      </div>
      <h2 className="font-display text-xl text-stone-800">
        {lang === "fa" ? "دسترسی محدود" : lang === "ar" ? "وصول محدود" : "Access restricted"}
      </h2>
      <p className="text-sm text-stone-600">{msg}</p>
      <p className="text-xs text-stone-400">
        {lang === "fa" ? `نقش فعلی: ${role}` : lang === "ar" ? `الدور الحالي: ${role}` : `Current role: ${role}`}
      </p>
      <div className="flex gap-2">
        <Link to="/users" className="rounded-xl bg-green-600 px-4 py-2 text-sm font-bold text-white">
          {lang === "fa" ? "صفحه کاربران" : "Users page"}
        </Link>
        <Link to="/" className="rounded-xl border border-stone-200 px-4 py-2 text-sm font-bold text-stone-700">
          {lang === "fa" ? "خانه" : "Home"}
        </Link>
      </div>
    </div>
  );
}
