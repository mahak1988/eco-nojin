/**
 * HydrologyFrontendCard component | کامپوننت کارت HydrologyFrontend
 *
 * Auto-scaffolded by phase1_complete_apps.py
 */

import React from "react";

import type { HydrologyFrontend } from "../types";

interface HydrologyFrontendCardProps {
  item: HydrologyFrontend;
  onClick?: (item: HydrologyFrontend) => void;
}

export function HydrologyFrontendCard({ item, onClick }: HydrologyFrontendCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick?.(item)}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
        <span
          className={`
            px-2 py-1 text-xs rounded-full
            ${item.is_active
              ? "bg-green-100 text-green-800"
              : "bg-gray-100 text-gray-600"}
          `}
        >
          {item.is_active ? "Active" : "Inactive"}
        </span>
      </div>
      {item.description && (
        <p className="text-sm text-gray-600">{item.description}</p>
      )}
      <div className="mt-2 text-xs text-gray-400">
        ID: #{item.id} • Updated: {new Date(item.updated_at).toLocaleDateString()}
      </div>
    </div>
  );
}

export default HydrologyFrontendCard;
