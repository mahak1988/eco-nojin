import { AlertTriangle, RefreshCw, WifiOff, ShieldAlert, Ban } from "lucide-react";

type ErrorType = "network" | "unauthorized" | "forbidden" | "not_found" | "server" | "validation" | "generic";

interface ApiErrorDisplayProps {
  type?: ErrorType;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

const ERROR_CONFIG: Record<ErrorType, { icon: typeof AlertTriangle; title: string; action?: string }> = {
  network: { icon: WifiOff, title: "Network Error", action: "Retry" },
  unauthorized: { icon: ShieldAlert, title: "Session Expired", action: "Sign In" },
  forbidden: { icon: Ban, title: "Access Denied" },
  not_found: { icon: AlertTriangle, title: "Not Found" },
  server: { icon: AlertTriangle, title: "Server Error", action: "Retry" },
  validation: { icon: AlertTriangle, title: "Validation Error" },
  generic: { icon: AlertTriangle, title: "Something went wrong", action: "Retry" },
};

export function ApiErrorDisplay({ type = "generic", message, onRetry, className = "" }: ApiErrorDisplayProps) {
  const config = ERROR_CONFIG[type];
  const Icon = config.icon;

  return (
    <div className={`flex flex-col items-center justify-center rounded-lg border border-destructive/20 bg-destructive/5 p-8 text-center ${className}`}>
      <Icon className="mb-3 h-10 w-10 text-destructive/70" />
      <h3 className="mb-1 text-lg font-semibold text-foreground">{config.title}</h3>
      {message && <p className="mb-4 max-w-md text-sm text-muted-foreground">{message}</p>}
      {config.action && onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          {config.action}
        </button>
      )}
    </div>
  );
}

export function getErrorType(status: number): ErrorType {
  if (status === 0 || !status) return "network";
  switch (status) {
    case 401: return "unauthorized";
    case 403: return "forbidden";
    case 404: return "not_found";
    case 422: return "validation";
    case 500: case 502: case 503: return "server";
    default: return "generic";
  }
}