import apiClient from './api';
import type { CarbonProject, CarbonStock } from '@/types';

export const createProject = async (data: Partial<CarbonProject>): Promise<CarbonProject> => {
  const response = await apiClient.post<CarbonProject>('/api/v1/carbon/projects', data);
  return response.data;
};

export const getProjects = async (): Promise<CarbonProject[]> => {
  const response = await apiClient.get<CarbonProject[]>('/api/v1/carbon/projects');
  return response.data;
};

export const calculateStock = async (data: Partial<CarbonStock>): Promise<CarbonStock> => {
  const response = await apiClient.post<CarbonStock>('/api/v1/carbon/stocks/calculate', data);
  return response.data;
};
