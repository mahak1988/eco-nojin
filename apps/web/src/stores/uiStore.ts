import { create } from "zustand";

interface UiStore {
  sidebarOpen: boolean;
  adminSidebarOpen: boolean;
  toggleSidebar: () => void;
  toggleAdminSidebar: () => void;
  setSidebarOpen: (v: boolean) => void;
}

export const useUiStore = create<UiStore>((set) => ({
  sidebarOpen: true,
  adminSidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleAdminSidebar: () => set((s) => ({ adminSidebarOpen: !s.adminSidebarOpen })),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
}));
