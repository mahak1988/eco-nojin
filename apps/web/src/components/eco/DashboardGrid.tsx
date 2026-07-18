/**
 * ═════════════════════════
 *  DashboardGrid ℓ برًی ریٌسلان دانظود
 * ═════════════════════════
 */

import { cn } from "@/lib/utils";

export interface DashboardGridProps {
  children: React.ReactNode;
  cols?: 2 | 3 | 4 | "auto";
  className?: string;
}

export function DashboardGrid({
  children,
  cols = 3,
  className,
}: DashboardGridProps) {
  const gridCols = {
    2: "grid-cols-1 sm:grid-cols-2",
    3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
    auto: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
  };

  return (
    <div className={cn("grid gap-4 md:gap-6", gridCols[cols], className)}>
      {children}
    </div>
  );
}