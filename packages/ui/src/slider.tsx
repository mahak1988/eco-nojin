import * as React from "react"

export interface SliderProps extends Omit<React.HTMLAttributes<HTMLDivElement>, "defaultValue" | "onChange"> {
  defaultValue?: number[]
  value?: number[]
  min?: number
  max?: number
  step?: number
  onValueChange?: (value: number[]) => void
}
export const Slider = React.forwardRef<HTMLDivElement, SliderProps>(({ className, defaultValue, value, min = 0, max = 100, step = 1, onValueChange, ...props }, ref) => {
  const currentValue = value?.[0] ?? defaultValue?.[0] ?? 50
  const pct = ((currentValue - min) / (max - min)) * 100
  return React.createElement("div", {
    ref, className: `relative flex w-full touch-none select-none items-center ${className ?? ""}`, ...props
  },
    React.createElement("div", { className: "relative h-2 w-full grow overflow-hidden rounded-full bg-secondary" },
      React.createElement("div", { className: "absolute h-full bg-primary rounded-full", style: { width: `${pct}%` } })
    ),
    React.createElement("span", { className: "absolute block h-4 w-4 rounded-full border-2 border-primary bg-background ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", style: { left: `calc(${pct}% - 0.5rem)` }, role: "slider", "aria-valuenow": currentValue, "aria-valuemin": min, "aria-valuemax": max, tabIndex: 0 })
  )
})
Slider.displayName = "Slider"