import * as React from "react"

const TabsContext = React.createContext<{ value: string; onValueChange: (v: string) => void } | null>(null)

export interface TabsProps extends React.HTMLAttributes<HTMLDivElement> { defaultValue?: string; value?: string; onValueChange?: (v: string) => void }
export const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(({ defaultValue, value, onValueChange, ...props }, ref) => {
  const [internalValue, setInternalValue] = React.useState(value ?? defaultValue ?? "")
  const currentValue = value ?? internalValue
  const handleChange = onValueChange ?? setInternalValue
  return React.createElement(TabsContext.Provider, { value: { value: currentValue, onValueChange: handleChange } },
    React.createElement("div", { ref, ...props })
  )
})
Tabs.displayName = "Tabs"

export interface TabsListProps extends React.HTMLAttributes<HTMLDivElement> {}
export const TabsList = React.forwardRef<HTMLDivElement, TabsListProps>(({ className, ...props }, ref) =>
  React.createElement("div", { ref, className: `inline-flex rounded-lg bg-muted p-1 ${className ?? ""}`, role: "tablist", ...props })
)
TabsList.displayName = "TabsList"

export interface TabsTriggerProps extends React.HTMLAttributes<HTMLButtonElement> { value: string }
export const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(({ className, value, ...props }, ref) => {
  const ctx = React.useContext(TabsContext)
  const active = ctx?.value === value
  return React.createElement("button", {
    ref, type: "button", role: "tab", "aria-selected": active, "data-state": active ? "active" : "inactive",
    className: `px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${active ? "bg-background text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"} ${className ?? ""}`,
    onClick: () => ctx?.onValueChange(value), ...props
  })
})
TabsTrigger.displayName = "TabsTrigger"

export interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> { value: string }
export const TabsContent = React.forwardRef<HTMLDivElement, TabsContentProps>(({ className, value, ...props }, ref) => {
  const ctx = React.useContext(TabsContext)
  if (ctx?.value !== value) return null
  return React.createElement("div", { ref, role: "tabpanel", className: `mt-2 ${className ?? ""}`, ...props })
})
TabsContent.displayName = "TabsContent"