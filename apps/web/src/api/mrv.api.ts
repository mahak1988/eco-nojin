import {http} from './http';
export const mrvApi={listProjects:()=>http.get('/api/v1/mrv/projects'),getProject:(id:string)=>http.get(`/api/v1/mrv/projects/${id}`),createProject:(data:any)=>http.post('/api/v1/mrv/projects',data),qualityCheckV2:(projectId:string)=>http.post('/api/v1/mrv/quality-v2',{projectId})};
