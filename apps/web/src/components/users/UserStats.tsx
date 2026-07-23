// apps/web/src/components/users/UserStats.tsx
import { Users, UserCheck, Shield, UserX } from "lucide-react";
import { SectionReveal } from "../eco/SectionReveal";
import { AnimatedCounter } from "../eco/AnimatedCounter";
import type { AppUser } from "./usersData";
import { countByRole, countByStatus } from "./usersData";
import type { UsersStrings } from "./usersI18n";

interface Props { users: AppUser[]; strings: UsersStrings; }

export function UserStats({ users, strings: s }: Props) {
  const cards = [
    { icon: Users, label: s.statTotal, value: users.length, color: "text-stone-700", bg: "bg-stone-100" },
    { icon: UserCheck, label: s.statActive, value: countByStatus(users, "active"), color: "text-green-700", bg: "bg-green-50" },
    { icon: Shield, label: s.statAdmins, value: countByRole(users, "admin"), color: "text-amber-700", bg: "bg-amber-50" },
    { icon: UserX, label: s.statInactive, value: countByStatus(users, "inactive"), color: "text-blue-700", bg: "bg-blue-50" },
  ];
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {cards.map((c, i) => (
        <SectionReveal key={c.label} delay={i * 70}>
          <div className={`flex items-center gap-3 rounded-2xl border border-stone-200/80 p-4 shadow-sm ${c.bg}`}>
            <c.icon className={`h-5 w-5 shrink-0 ${c.color}`} />
            <div className="min-w-0">
              <p className={`font-display text-2xl font-black tabular-nums leading-none ${c.color}`}><AnimatedCounter end={c.value} /></p>
              <p className="mt-1 truncate text-xs font-medium text-stone-600">{c.label}</p>
            </div>
          </div>
        </SectionReveal>
      ))}
    </div>
  );
}