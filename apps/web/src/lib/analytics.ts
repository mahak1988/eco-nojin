// Analytics tracking system
export const analytics = {
  track: (event: string, properties?: Record<string, any>) => {
    if (typeof window === "undefined") return;
    
    const data = {
      event,
      properties,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };
    
    // Send to backend
    fetch("/api/v1/analytics/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).catch(err =>
);
    
    // Also log to console in development
    if (process.env.NODE_ENV === "development") {
    }
  },
  
  page: (name: string, properties?: Record<string, any>) => {
    analytics.track("page_view", { page: name, ...properties });
  },
  
  identify: (userId: string, traits?: Record<string, any>) => {
    analytics.track("identify", { userId, traits });
  },
};

// Hook for React components
export function useAnalytics() {
  return analytics;
}
