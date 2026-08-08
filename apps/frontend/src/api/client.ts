const BASE='http://localhost:8000/api/v1';
export async function apiGet<T=any>(path:string):Promise<T>{const r=await fetch(BASE+path);if(!r.ok)throw new Error(`API ${r.status}`);return r.json();}
export async function apiPost<T=any>(path:string,body:any):Promise<T>{const r=await fetch(BASE+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok)throw new Error(`API ${r.status}`);return r.json();}
export const endpoints={science:{status:()=>apiGet('/science/status'),aquacrop:(p:any)=>apiPost('/science/aquacrop-advanced',p),rothc:(p:any)=>apiPost('/science/rothc',p)},farms:{list:()=>apiGet('/farms')},satellite:{ndvi:()=>apiGet('/satellite/ndvi')},simulation:{run:(model:string,p:any)=>apiPost(`/simulation/${model}`,p)}};
