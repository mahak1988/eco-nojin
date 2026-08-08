import {http} from './http';
export const ecocoinApi={getBalance:(address?:string)=>http.get(address?`/api/v1/ecocoin/balance/${address}`:'/api/v1/ecocoin/balance'),getMetrics:()=>http.get('/api/v1/ecocoin/metrics'),stake:(amount:number,durationDays:number)=>http.post('/api/v1/ecocoin/stake',{amount,durationDays})};
