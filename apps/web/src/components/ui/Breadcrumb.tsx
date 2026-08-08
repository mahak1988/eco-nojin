import { Link, useLocation } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";

interface BreadcrumbSegment {
  label: string;
  path: string;
}

// Map of route paths to human-readable labels (English fallback)
const ROUTE_LABELS: Record<string, string> = {
  "": "Home",
  dashboard: "Dashboard",
  farms: "Farms",
  crops: "Crops",
  water: "Water",
  planting: "Planting Calendar",
  tasks: "Tasks",
  inventory: "Inventory",
  weather: "Weather",
  monitoring: "Monitoring",
  account: "Account",
  settings: "Settings",
  alerts: "Alerts",
  community: "Community",
  ecocoin: "EcoCoin",
  games: "Games",
  library: "Library",
  mrv: "MRV",
  news: "News",
  pilots: "Pilots",
  regional: "Regional",
  satellite: "Satellite",
  simulators: "Simulators",
  science: "Science",
  comparison: "Comparison",
  tourism: "Tourism",
  users: "Users",
  accounting: "Accounting",
  invoices: "Invoices",
  journal: "Journal",
  payments: "Payments",
  education: "Education",
  analytics: "Analytics",
  reports: "Reports",
  risks: "Risks",
  policies: "Policies",
  my: "My Simulations",
  new: "New",
  wizard: "Wizard",
  register: "Register",
  login: "Login",
  security: "Security",
  notifications: "Notifications",
  staking: "Staking",
  mining: "Mining",
  bioeconomy: "Bioeconomy",
  challenges: "Challenges",
  claim: "Claim",
  claims: "Claims",
  transparency: "Transparency",
  dashboard: "Dashboard",
  levels: "Levels",
  evidence: "Evidence",
  verify: "Verify",
  satellites: "Satellites",
  points: "Points",
  methodology: "Methodology",
  ledger: "Ledger",
  calculator: "Calculator",
  buffer: "Buffer",
  farm: "Farm Link",
  link: "Farm Link",
  timeseries: "Time Series",
  change: "Change Detection",
  fields: "Field Map",
  aquacrop: "AquaCrop",
  rothc: "RothC",
  methods: "Methods",
  irrigation: "Irrigation",
  soil: "Soil",
  map: "Map",
  rules: "Rules",
};

function getLabel(segment: string): string {
  // Check for dynamic segments (IDs)
  if (/^[a-f0-9-]{20,}$/.test(segment) || /^\d+$/.test(segment)) {
    return segment.slice(0, 8) + "...";
  }
  return ROUTE_LABELS[segment] || segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, " ");
}

export function Breadcrumb() {
  const { pathname } = useLocation();

  // Skip breadcrumb on home page
  if (pathname === "/" || pathname === "") return null;

  const segments: BreadcrumbSegment[] = [];
  const parts = pathname.split("/").filter(Boolean);

  let cumulativePath = "";
  for (const part of parts) {
    cumulativePath += "/" + part;
    segments.push({
      label: getLabel(part),
      path: cumulativePath,
    });
  }

  return (
    <nav aria-label="Breadcrumb" className="border-b bg-card/50 px-4 py-2 sm:px-6 lg:px-8">
      <ol className="flex flex-wrap items-center gap-1 text-sm text-muted-foreground">
        <li>
          <Link to="/" className="inline-flex items-center gap-1 hover:text-foreground transition-colors" aria-label="Home">
            <Home className="h-3.5 w-3.5" />
          </Link>
        </li>
        {segments.map((segment, idx) => (
          <li key={segment.path} className="flex items-center gap-1">
            <ChevronRight className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
            {idx === segments.length - 1 ? (
              <span className="font-medium text-foreground" aria-current="page">
                {segment.label}
              </span>
            ) : (
              <Link to={segment.path} className="hover:text-foreground transition-colors truncate max-w-[180px]">
                {segment.label}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}