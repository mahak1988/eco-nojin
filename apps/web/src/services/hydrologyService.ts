import apiClient from './api';
import type { Watershed, Simulation } from '@/types';

export const createWatershed = async (data: Partial<Watershed>): Promise<Watershed> => {
  const response = await apiClient.post<Watershed>('/api/v1/hydrology/watersheds', data);
  return response.data;
};

export const getWatersheds = async (): Promise<Watershed[]> => {
  const response = await apiClient.get<Watershed[]>('/api/v1/hydrology/watersheds');
  return response.data;
};

export const createSimulation = async (data: Partial<Simulation>): Promise<Simulation> => {
  const response = await apiClient.post<Simulation>('/api/v1/hydrology/simulations', data);
  return response.data;
};

export const getSimulations = async (): Promise<Simulation[]> => {
  const response = await apiClient.get<Simulation[]>('/api/v1/hydrology/simulations');
  return response.data;
};

export const runSimulation = async (id: string): Promise<Simulation> => {
  const response = await apiClient.post<Simulation>(`/api/v1/hydrology/simulations/${id}/run`);
  return response.data;
};
