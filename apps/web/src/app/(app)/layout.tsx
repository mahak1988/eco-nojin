import type { Metadata } from "next";
import React from "react";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "EcoNojin GeoAI–DSS Console",
  description:
    "Integrated dashboard for water, soil, climate, carbon and livelihoods in arid and semi-arid landscapes.",
};

type AppLayoutProps = {
  children: React.ReactNode;
};

export default function AppLayout({ children }: AppLayoutProps) {
  return <AppShell>{children}</AppShell>;
}
