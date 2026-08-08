import {http} from './http';
export const regionalApi={getRegions:()=>http.get('/api/v1/regional'),getClimateZones:()=>http.get('/api/v1/regional/climate-zones'),getRegionalForecast:(regionId:string)=>http.get(`/api/v1/regional/${regionId}/forecast`)};
