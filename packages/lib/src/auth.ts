// src/lib/auth.ts
export interface User {
  name: string;
  email: string;
  token: string;
}

export const login = (email: string, name: string) => {
  const user: User = { 
    email, 
    name, 
    token: (process.env.NEXT_PUBLIC_MOCK_JWT_PREFIX || "mock-jwt-token-") + Date.now() 
  };
  localStorage.setItem("econojin_user", JSON.stringify(user));
  window.dispatchEvent(new Event("storage")); // Trigger UI update across components
  return user;
};

export const register = (name: string, email: string, password: string) => {
  // In a real app, this would call an API
  return login(email, name);
};

export const logout = () => {
  localStorage.removeItem("econojin_user");
  window.dispatchEvent(new Event("storage"));
};

export const getUser = (): User | null => {
  if (typeof window !== "undefined") {
    const userStr = localStorage.getItem("econojin_user");
    return userStr ? JSON.parse(userStr) : null;
  }
  return null;
};
