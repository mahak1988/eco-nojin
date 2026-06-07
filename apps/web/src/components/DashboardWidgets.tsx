'use client';

import { useDashboardStats, useIoTStats, useEcoCoinStats } from '@/hooks/useApi';

export function DashboardWidgets() {
  const { data: dashboardStats, isLoading: dashboardLoading } = useDashboardStats();
  const { data: iotStats, isLoading: iotLoading } = useIoTStats();
  const { data: ecocoinStats, isLoading: ecocoinLoading } = useEcoCoinStats();

  if (dashboardLoading || iotLoading || ecocoinLoading) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-6">
      {/* Dashboard Stats */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Dashboard Overview</h3>
        {dashboardStats && (
          <div className="space-y-2">
            <p>Total Users: {dashboardStats.total_users}</p>
            <p>Active Users: {dashboardStats.active_users}</p>
            <p>Total Sensors: {dashboardStats.total_sensors}</p>
          </div>
        )}
      </div>

      {/* IoT Stats */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">IoT Sensors</h3>
        {iotStats && (
          <div className="space-y-2">
            <p>Total Sensors: {iotStats.total_sensors}</p>
            <p>Active Sensors: {iotStats.active_sensors}</p>
            <p>Avg Battery: {iotStats.avg_battery}%</p>
          </div>
        )}
      </div>

      {/* EcoCoin Stats */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">EcoCoin Impact</h3>
        {ecocoinStats && (
          <div className="space-y-2">
            <p>Wallets: {ecocoinStats.wallets_count}</p>
            <p>Carbon: {ecocoinStats.carbon_sequestered_tons} tons</p>
            <p>Water: {ecocoinStats.water_saved_liters} liters</p>
          </div>
        )}
      </div>
    </div>
  );
}
