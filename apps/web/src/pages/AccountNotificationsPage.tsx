import { useEffect, useState } from "react";
import { Bell } from "lucide-react";

export default function AccountNotificationsPage() {
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);

  useEffect(() => {
    fetch("/api/v1/notifications", { credentials: "include" })
      .then((r) => r.json())
      .then((j) => setItems(j.data || []))
      .catch(() => undefined);
  }, []);

  return (
    <div className="mx-auto max-w-lg space-y-4 p-8">
      <h1 className="flex items-center gap-2 font-display text-2xl">
        <Bell className="h-6 w-6" /> Notifications
      </h1>
      <ul className="space-y-2">
        {items.map((n) => (
          <li key={String(n.id)} className="rounded-xl border bg-white p-3 text-sm">
            <p className="font-bold">{String(n.title)}</p>
            <p className="text-stone-500">{String(n.body)}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
