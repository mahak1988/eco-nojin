import {http} from './http';
export const satelliteApi={getLayers:()=>http.get('/api/v1/satellite/layers'),getNdvi:(bbox?:string)=>http.get('/api/v1/satellite/ndvi',{params:{bbox}}),getEt:(bbox?:string)=>http.get('/api/v1/satellite/et',{params:{bbox}})};
