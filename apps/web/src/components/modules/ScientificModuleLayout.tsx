'use client';

import React from 'react';

export interface ScientificModuleLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function ScientificModuleLayout({ title, description, children }: ScientificModuleLayoutProps) {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-2">{title}</h1>
      {description && <p className="text-gray-600 mb-6">{description}</p>}
      <div className="space-y-6">{children}</div>
    </div>
  );
}

export function ModuleStat({ label, value, unit }: { label: string; value: string | number; unit?: string }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold">
        {value}
        {unit && <span className="text-sm ml-1">{unit}</span>}
      </div>
    </div>
  );
}

export function InfoCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 className="font-semibold text-blue-900 mb-2">{title}</h3>
      <div className="text-blue-800 text-sm">{children}</div>
    </div>
  );
}

export default ScientificModuleLayout;