// توپوگرافی و برداشت نقشه
export interface SurveyProject {
  id: string;
  name: string;
  coordinates: number[][];
  status: 'active' | 'completed';
}

export interface DEMFile {
  id: string;
  url: string;
  resolution: number;
}
