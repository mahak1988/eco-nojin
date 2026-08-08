import * as React from "react"

export interface SwitchProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onChange"> {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}
export const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(({ className, checked, onCheckedChange, ...props }, ref) => {
  const [internalChecked, setInternalChecked] = React.useState(checked ?? false)
  const isChecked = checked ?? internalChecked
  const toggle = () => {
    const next = !isChecked
    setInternalChecked(next)
    onCheckedChange?.(next)
  }
  return React.createElement("button", {
    ref, type: "button", role: "switch", "aria-checked": isChecked, "data-state": isChecked ? "checked" : "unchecked",
    className: `peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50 ${isChecked ? "bg-primary" : "bg-input"} ${className ?? ""}`,
    onClick: toggle, ...props
  }, React.createElement("span", {
    "data-state": isChecked ? "checked" : "unchecked",
    className: `pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform ${isChecked ? "translate-x-4" : "translate-x-0"}`
  }))
})
Switch.displayName = "Switch"