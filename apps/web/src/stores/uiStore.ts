import { useSyncExternalStore } from "react";

type Listener = () => void;

interface UiState {
  sidebarOpen: boolean;
  adminSidebarOpen: boolean;
}

let state: UiState = { sidebarOpen: true, adminSidebarOpen: true };
const listeners = new Set<Listener>();

function emit() {
  listeners.forEach((l) => l());
}

export const uiStore = {
  getState: () => state,
  subscribe: (l: Listener) => {
    listeners.add(l);
    return () => listeners.delete(l);
  },
  toggleSidebar: () => {
    state = { ...state, sidebarOpen: !state.sidebarOpen };
    emit();
  },
  toggleAdminSidebar: () => {
    state = { ...state, adminSidebarOpen: !state.adminSidebarOpen };
    emit();
  },
  setSidebarOpen: (v: boolean) => {
    state = { ...state, sidebarOpen: v };
    emit();
  },
};

export function useUiStore() {
  const snap = useSyncExternalStore(uiStore.subscribe, uiStore.getState, uiStore.getState);
  return {
    ...snap,
    toggleSidebar: uiStore.toggleSidebar,
    toggleAdminSidebar: uiStore.toggleAdminSidebar,
    setSidebarOpen: uiStore.setSidebarOpen,
  };
}
