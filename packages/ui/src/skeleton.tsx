import * as React from "react"

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}
export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(({ className, ...props }, ref) =>
  React.createElement("div", { ref, className: `animate-pulse rounded-md bg-muted ${className ?? ""}`, ...props })
)
Skeleton.displayName = "Skeleton"