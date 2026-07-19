/**
 * ============================================================================
 *  AgriSidebar — Collapsible sidebar for agriculture routes
 *  Inspired by agri-moon navigation patterns
 * ============================================================================
 */

import { useState } from "react";
import { NavLink } from "react-router-dom";
import { ChevronDown, ChevronRight, BarChart3, MapPin, Calendar, ShoppingBag, Droplets, ScanEye, Users, Leaf } from "lucide-react";

import { cn } from "@/lib/utils";

interface NavGroup {
  title: string;
  items: Array<{
    to: string;
    label: string;
    icon: React.ReactNode;
  }>;
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: "Agriculture",
    items: [
      { to: "/land-registry", label: "Land Registry", icon: <MapPin className="h-4 w-4" /> },
      { to: "/planting-seasons", label: "Planting Seasons", icon: <Calendar className="h-4 w-4" /> },
      { to: "/harvest-monitoring", label: "Harvest Monitoring", icon: <Leaf className="h-4 w-4" /> },
    ],
  },
  {
    title: "Resources",
    items: [
      { to: "/fertilizer", label: "Fertilizer", icon: <ShoppingBag className="h-4 w-4" /> },
      { to: "/water-irrigation", label: "Water & Irrigation", icon: <Droplets className="h-4 w-4" /> },
    ],
  },
  {
    title: "Analytics",
    items: [
      { to: "/production-analytics", label: "Production Analytics", icon: <BarChart3 className="h-4 w-4" /> },
      { to: "/gis-explorer", label: "GIS Explorer", icon: <ScanEye className="h-4 w-4" /> },
    ],
  },
  {
    title: "Community",
    items: [
      { to: "/reports", label: "Reports", icon: <BarChart3 className="h-4 w-4" /> },
      { to: "/administration", label: "Administration", icon: <Users className="h-4 w-4" /> },
    ],
  },
];

interface AgriSidebarProps {
  className?: string;
}

export function AgriSidebar({ className }: AgriSidebarProps): JSX.Element {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

  const toggleGroup = (title: string) => {
    setExpandedGroups((prev) => ({ ...prev, [title]: !prev[title] }));
  };

  return (
    <aside className={cn("flex h-full w-64 flex-col overflow-y-auto border-r border-gray-100 bg-white dark:border-gray-800 dark:bg-gray-950", className)}>
      <nav className="flex-1 space-y-1 p-4">
        {NAV_GROUPS.map((group) => (
          <div key={group.title}>
            <button
              type="button"
              onClick={() => toggleGroup(group.title)}
              className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
            >
              <span>{group.title}</span>
              {expandedGroups[group.title] ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
            {expandedGroups[group.title] && (
              <div className="mt-1 space-y-1 pl-4">
                {group.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition",
                        isActive
                          ? "bg-emerald-100/80 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200"
                      )
                    }
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </aside>
  );
}