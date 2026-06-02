import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number, decimals = 2): string {
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(decimals) + 'M';
  }
  if (num >= 1_000) {
    return (num / 1_000).toFixed(decimals) + 'K';
  }
  return num.toFixed(decimals);
}

export function formatUSD(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
}

export function shortenAddress(address: string, chars = 4): string {
  if (!address) return '';
  return `${address.slice(0, chars + 2)}...${address.slice(-chars)}`;
}

export function getCarbonColor(tons: number): string {
  if (tons >= 1000) return 'text-purple-600';
  if (tons >= 100) return 'text-blue-600';
  if (tons >= 10) return 'text-green-600';
  return 'text-yellow-600';
}

export function getActivityIcon(activityType: string): string {
  const icons: Record<string, string> = {
    tree_planting: '🌳',
    soil_regeneration: '🌱',
    agroforestry: '🌾',
    mangrove_planting: '🌊',
    wetland_restoration: '💧',
    grassland_restoration: '🌿',
    urban_greening: '🏙️',
  };
  return icons[activityType] || '🌍';
}

export function getActivityLabel(activityType: string): string {
  const labels: Record<string, string> = {
    tree_planting: 'Tree Planting',
    soil_regeneration: 'Soil Regeneration',
    agroforestry: 'Agroforestry',
    mangrove_planting: 'Mangrove Planting',
    wetland_restoration: 'Wetland Restoration',
    grassland_restoration: 'Grassland Restoration',
    urban_greening: 'Urban Greening',
  };
  return labels[activityType] || activityType;
}

export function calculateCO2Equivalent(
  trees: number,
  years: number = 10
): { cars: number; flights: number; homes: number } {
  const tonsCO2 = trees * 0.022 * years; // 22 kg/tree/year
  
  return {
    cars: Math.round(tonsCO2 / 4.6), // 4.6 tons/car/year
    flights: Math.round(tonsCO2 / 0.9), // 0.9 tons/flight NYC-LA
    homes: Math.round(tonsCO2 / 7.5), // 7.5 tons/home/year
  };
}
