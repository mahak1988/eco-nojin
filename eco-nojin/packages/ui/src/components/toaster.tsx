"use client";

import { useAppStore } from "@/store/useAppStore";
import { X } from "lucide-react";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: "default" | "success" | "warning" | "danger";
}

export function Toaster() {
  // Placeholder - in real app, use sonner or react-hot-toast
  return null;
}
