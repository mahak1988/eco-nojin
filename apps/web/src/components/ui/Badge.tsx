import { ReactNode } from "react";

const colors = {
  green: "bg-green-50 text-green-700",
  red: "bg-red-50 text-red-700",
  amber: "bg-amber-50 text-amber-700",
  blue: "bg-blue-50 text-blue-700",
  stone: "bg-stone-100 text-stone-700",
} as const;

export function Badge({
  children,
  color = "stone",
}: {
  children: ReactNode;
  color?: keyof typeof colors;
}) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-[11px] font-bold ${colors[color]}`}>
      {children}
    </span>
  );
}
