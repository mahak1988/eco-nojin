import { ReactNode } from "react";

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="rounded-2xl border border-dashed border-stone-300 bg-white p-10 text-center">
      <h3 className="font-display text-xl text-stone-800">{title}</h3>
      {description && <p className="mt-2 text-sm text-stone-600">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
