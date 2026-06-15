import { apiClient } from '../core/instance';
import { SurveyProject } from '@econojin/types';

export const mappingApi = {
  getSurveys: () => apiClient.get<SurveyProject[]>('/mapping/surveys'),
  getSurveyById: (id: string) => apiClient.get<SurveyProject>(`/mapping/surveys/${id}`),
};
