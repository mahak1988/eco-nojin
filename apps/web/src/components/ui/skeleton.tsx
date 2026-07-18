/**
 * ============================================================================
 *  Skeleton — placeholder shimmer for loading states
 * ============================================================================
 *
 *  Use instead of a spinner when content has a known layout (tables, cards,
 *  text). The shimmer respects prefers-reduced-motion automatically.
 * ============================================================================
 */

import * as React from "react";

import { cn } from "@/lib/utils";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /** "rect" | "circle" | "text" — controls border-radius. */
  shape?: "rect" | "circle" | "text";
}

const SHAPE_CLASS = {
  rect: "rounded-md",
  circle: "rounded-full",
  text: "rounded",
} as const;

export function Skeleton({
  shape = "rect",
  className,
  ...props
}: SkeletonProps): JSX.Element {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn(
        "animate-pulse bg-gray-200 motion-reduce:animate-none",
        SHAPE_CLASS[shape],
        className,
      )}
      {...props}
    />
  );
}

// ---------------------------------------------------------------------------
// Pre-built skeleton rows / cards for tables and grids
// ---------------------------------------------------------------------------

export function SkeletonRow({ columns = 5 }: { columns?: number }): JSX.Element {
  return (
    <div className="grid gap-4 px-4 py-3" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton key={i} className="h-4" />
      ))}
    </div>
  );
}

export function SkeletonTable({ rows = 6, columns = 5 }: { rows?: number; columns?: number }): JSX.Element {
  return (
    <div className="divide-y divide-gray-100">
      {Array.from({ length: rows }).map((_, r) => (
        <SkeletonRow key={r} columns={columns} />
      ))}
    </div>
  );
}

export function SkeletonStatCard(): JSX.Element {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-8 w-28" />
        </div>
        <Skeleton shape="circle" className="h-11 w-11" />
      </div>
    </div>
  );
}

export default Skeleton;
