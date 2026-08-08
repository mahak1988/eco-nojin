import {http} from './http';
export const contentApi={getNews:(page?:number)=>http.get('/api/v1/content/news',{params:{page}}),getPolicies:()=>http.get('/api/v1/content/policies'),getMethodology:(modelId:string)=>http.get(`/api/v1/content/methodology/${modelId}`)};
