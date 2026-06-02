// frontend/src/lib/auth/useAuth.ts
import { useState, useEffect, createContext, useContext } from "react"
import { API_BASE } from "@/lib/api"

interface AuthContextType {
  token: string | null
  farmerId: string | null
  login: (fid: string, phone: string) => Promise<void>
  logout: () => void
  getHeaders: () => HeadersInit
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [farmerId, setFarmerId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    // Load from localStorage on mount
    const saved = localStorage.getItem("economugin_auth")
    if (saved) {
      try {
        const { token, farmerId } = JSON.parse(saved)
        setToken(token)
        setFarmerId(farmerId)
      } catch (e) {
        localStorage.removeItem("economugin_auth")
      }
    }
    setIsLoading(false)
  }, [])
  
  const login = async (fid: string, phone: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fid, phone })
    })
    if (!res.ok) throw new Error("Login failed")
    const data = await res.json()
    setToken(data.access_token)
    setFarmerId(data.farmer_id)
    localStorage.setItem("economugin_auth", JSON.stringify({ token: data.access_token, farmerId: data.farmer_id }))
  }
  
  const logout = () => {
    setToken(null)
    setFarmerId(null)
    localStorage.removeItem("economugin_auth")
  }
  
  const getHeaders = (): HeadersInit => ({
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {})
  })
  
  return (
    <AuthContext.Provider value={{ token, farmerId, login, logout, getHeaders, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
