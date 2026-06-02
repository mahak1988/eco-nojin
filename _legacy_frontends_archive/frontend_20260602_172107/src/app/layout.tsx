import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import Providers from "./layout-providers";

export const metadata: Metadata = {
  title: "Economugin",
  description: "Dryland restoration platform",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
