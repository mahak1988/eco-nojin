'use client';

import { useDashboardStats, useIoTStats } from '@/hooks/useApiHooks';

export function DashboardExample() {
  const { data: dashboard, isLoading: dashboardLoading } = useDashboardStats();
  const { data: iot, isLoading: iotLoading } = useIoTStats();

  if (dashboardLoading || iotLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <pre>{JSON.stringify(dashboard, null, 2)}</pre>
      <h2>IoT Stats</h2>
      <pre>{JSON.stringify(iot, null, 2)}</pre>
    </div>
  );
}
