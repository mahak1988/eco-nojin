import apiClient from './api';
import type { SoilSample, SoilAnalysis } from '@/types';

export const createSoilSample = async (data: Partial<SoilSample>): Promise<SoilSample> => {
  const response = await apiClient.post<SoilSample>('/api/v1/soil/samples', data);
  return response.data;
};

export const getSoilSamples = async (): Promise<SoilSample[]> => {
  const response = await apiClient.get<SoilSample[]>('/api/v1/soil/samples');
  return response.data;
};

export const analyzeSample = async (sampleId: string, analysisType: string): Promise<SoilAnalysis> => {
  const response = await apiClient.post<SoilAnalysis>('/api/v1/soil/analyses', {
    sample_id: sampleId,
    analysis_type: analysisType,
  });
  return response.data;
};
