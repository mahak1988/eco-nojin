import { apiClient } from '../core/instance';

export interface LogFrameIndicator {
  indicator_id: string;
  name: string;
  level: 'impact' | 'outcome' | 'output';
  sdg_targets: string[];
  baseline_value: number;
  target_value: number;
  current_value: number;
}

export const logframeApi = {
  getOverview: () => apiClient.get('/api/logframe/overview'),
  getIndicatorsBySDG: (sdgNumber: string) =>
    apiClient.get<LogFrameIndicator[]>('/api/logframe/sdg/' + sdgNumber),
  getGEFCoreIndicators: () => apiClient.get('/api/logframe/gef/core-indicators'),
};
