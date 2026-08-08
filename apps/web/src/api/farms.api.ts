import {http} from './http';
export const farmsApi={list:()=>http.get('/api/v1/farms'),get:(id:string)=>http.get(`/api/v1/farms/${id}`),create:(data:any)=>http.post('/api/v1/farms',data)};
