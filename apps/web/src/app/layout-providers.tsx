// frontend/src/app/layout-providers.tsx
"use client"

import { AuthProvider } from "@/lib/auth/useAuth"
import { createElement } from "react"

export default function Providers({ children }: { children: React.ReactNode }) {
  return createElement(AuthProvider as unknown as React.ComponentType<{ children: React.ReactNode }>, null, children)
}
