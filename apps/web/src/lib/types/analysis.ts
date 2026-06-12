export interface Analysis {
  id: string;
  name: string;
  type: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisResult {
  id: string;
  analysisId: string;
  data: any;
  createdAt: string;
}