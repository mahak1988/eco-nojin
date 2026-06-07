// API Client Usage Examples
import api from './api-client';

// Dashboard
export async function getDashboardData() {
  const [stats, iotStats, ecocoinStats] = await Promise.all([
    api.getDashboardStats(),
    api.getIoTStats(),
    api.getEcoCoinStats()
  ]);
  
  return { stats, iotStats, ecocoinStats };
}

// Academy
export async function getAcademyData() {
  const [stats, courses] = await Promise.all([
    api.getAcademyStats(),
    api.getCourses()
  ]);
  
  return { stats, courses };
}

// Financial
export async function getFinancialData() {
  const dashboard = await api.getFinancialDashboard();
  return dashboard;
}

// Maintenance
export async function getMaintenanceData() {
  const stats = await api.getMaintenanceStats();
  return stats;
}

// MRV
export async function getMRVData() {
  const stats = await api.getMRVStats();
  return stats;
}

// Drought
export async function getDroughtData() {
  const stats = await api.getDroughtStats();
  return stats;
}

// Scientific
export async function getScientificData() {
  const thresholds = await api.getThresholds();
  return thresholds;
}
