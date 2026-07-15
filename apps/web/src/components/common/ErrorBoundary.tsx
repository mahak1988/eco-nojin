/**
 * ============================================================================
 *  ErrorBoundary — functional error boundary (class is required by React)
 * ============================================================================
 *
 *  i18n: fallback UI uses useLanguage() for translated strings.
 *        Note: the fallback must be rendered by a child of the boundary,
 *        not by the boundary itself (the boundary is a class and can't
 *        use hooks). We delegate to <ErrorFallback />.
 * ============================================================================
 */

import { Component, type ErrorInfo, type ReactNode } from "react";

import { ErrorFallback } from "@/components/common/ErrorFallback";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
  onError?: (error: Error, info: ErrorInfo) => void;
  onReset?: () => void;
}

interface ErrorBoundaryState {
  error: Error | null;
}

// ---------------------------------------------------------------------------
// ErrorBoundary (class is required — React limitation)
// ---------------------------------------------------------------------------

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  override state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  override componentDidCatch(error: Error, info: ErrorInfo): void {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.error("[ErrorBoundary]", error, info.componentStack);
    }
    this.props.onError?.(error, info);
  }

  private readonly reset = (): void => {
    this.props.onReset?.();
    this.setState({ error: null });
  };

  override render(): ReactNode {
    const { error } = this.state;
    const { children, fallback } = this.props;

    if (error) {
      if (fallback) return fallback(error, this.reset);
      return <ErrorFallback error={error} reset={this.reset} />;
    }

    return children;
  }
}
