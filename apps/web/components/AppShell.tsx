import type { ReactNode } from 'react';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';

export default function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      <Navigation />
      <div className="pt-20">
        {children}
      </div>
      <Footer />
    </>
  );
}
