import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "./utils"

const toastVariants = cva(
  "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all",
  {
    variants: {
      variant: {
        default: "border bg-background",
        destructive:
          "destructive group border-destructive bg-destructive text-destructive-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

type ToasterToast = {
  id: string
  title?: string
  description?: string
  action?: React.ReactNode
  variant?: "default" | "destructive"
}

const ToastProvider = ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) =>
  React.createElement("div", { ...props, "data-toast-provider": "" }, children)
ToastProvider.displayName = "ToastProvider"

const ToastViewport = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) =>
  React.createElement("div", {
    ref,
    className: cn(
      "fixed top-0 right-0 z-[100] flex max-h-screen w-full flex-col-reverse gap-2 p-4 sm:top-auto sm:flex-col md:max-w-[420px]",
      className
    ),
    ...props,
  })
)
ToastViewport.displayName = "ToastViewport"

const ToastAction = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) =>
  React.createElement("button", {
    ref,
    className: cn(
      "inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium transition-colors hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 group-[.destructive]:hover:bg-destructive group-[.destructive]:hover:text-destructive-foreground group-[.destructive]:focus:ring-destructive",
      className
    ),
    ...props,
  })
)
ToastAction.displayName = "ToastAction"

const ToastClose = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) =>
  React.createElement("button", {
    ref,
    className: cn(
      "absolute right-2 top-2 rounded-md p-1 text-foreground/50 opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100 group-[.destructive]:text-red-300 group-[.destructive]:hover:text-red-50 group-[.destructive]:focus:ring-red-400 group-[.destructive]:focus:ring-offset-red-600",
      className
    ),
    ...props,
  },
    React.createElement("svg", { className: "h-4 w-4", xmlns: "http://www.w3.org/2000/svg", fill: "none", viewBox: "0 0 24 24", stroke: "currentColor" },
      React.createElement("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M6 18L18 6M6 6l12 12" })
    )
  )
)
ToastClose.displayName = "ToastClose"

const ToastTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) =>
  React.createElement("div", {
    ref,
    className: cn("text-sm font-semibold", className),
    ...props,
  })
)
ToastTitle.displayName = "ToastTitle"

const ToastDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) =>
  React.createElement("div", {
    ref,
    className: cn("text-sm opacity-90", className),
    ...props,
  })
)
ToastDescription.displayName = "ToastDescription"

const ToastComponent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof toastVariants>
>(({ className, variant, ...props }, ref) =>
  React.createElement("div", {
    ref,
    className: cn(toastVariants({ variant }), className),
    ...props,
  })
)
ToastComponent.displayName = "Toast"

export {
  ToastProvider,
  ToastViewport,
  ToastComponent as Toast,
  ToastTitle,
  ToastDescription,
  ToastClose,
  ToastAction,
  type ToasterToast,
}

type ToastOptions = Omit<ToasterToast, "id">

const TOAST_LIMIT = 1
let toastCount = 0

function genId(): string {
  toastCount = (toastCount + 1) % Number.MAX_SAFE_INTEGER
  return `toast-${Date.now()}-${toastCount}`
}

type Action =
  | { type: "ADD_TOAST"; toast: ToasterToast }
  | { type: "UPDATE_TOAST"; toast: ToasterToast }
  | { type: "DISMISS_TOAST"; toastId?: string }
  | { type: "REMOVE_TOAST"; toastId?: string }

interface State {
  toasts: ToasterToast[]
}

export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case "ADD_TOAST":
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      }
    case "UPDATE_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      }
    case "DISMISS_TOAST": {
      const toastId = action.toastId
      if (toastId) {
        return {
          ...state,
          toasts: state.toasts.map((t) =>
            t.id === toastId ? { ...t } : t
          ),
        }
      }
      return {
        ...state,
        toasts: state.toasts.map((t) => ({ ...t })),
      }
    }
    case "REMOVE_TOAST":
      if (action.toastId === undefined) {
        return { ...state, toasts: [] }
      }
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      }
  }
}

export type ToastAction = Action

export const useToast = () => {
  const [state, dispatch] = React.useReducer(reducer, { toasts: [] })

  return {
    toasts: state.toasts,
    toast: (options: ToastOptions) => {
      const id = genId()
      dispatch({ type: "ADD_TOAST", toast: { id, ...options } })
      setTimeout(() => {
        dispatch({ type: "DISMISS_TOAST", toastId: id })
      }, 5000)
      return { id }
    },
    dismiss: (toastId: string) => dispatch({ type: "DISMISS_TOAST", toastId }),
  }
}
