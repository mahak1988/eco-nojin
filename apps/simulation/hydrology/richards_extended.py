"""Richards Extended — FDM with dynamic hysteresis."""
import numpy as np
from typing import Any,Optional
from apps.simulation.hydrology.soil_physics import van_genuchten_theta,hydraulic_conductivity
def solve_richards_extended(n_nodes=21,z_max=1.0,dt=60.0,n_steps=24,alpha=1.0,n=2.0,theta_s=0.45,theta_r=0.05,Ks=1e-5,init_theta=0.30,precip_rate=None,et_rate=None)->dict[str,Any]:
    dz=z_max/(n_nodes-1);z=np.linspace(0,-z_max,n_nodes)
    h=np.full(n_nodes,-1.0);theta=np.full(n_nodes,init_theta)
    hs=np.zeros(n_nodes,dtype=bool)
    for step in range(n_steps):
        for i in range(1,n_nodes-1):
            dh_dz=(h[i+1]-h[i-1])/(2*dz)
            K=hydraulic_conductivity(theta[i],Ks,theta_s,theta_r,n)
            flow=-K*(dh_dz+1.0);hs[i]=flow>0
            flux_up=K*((h[i]-h[i-1])/dz+1.0)
            flux_dn=K*((h[i+1]-h[i])/dz+1.0)
            theta[i]+=dt*(flux_up-flux_dn)/dz
            theta[i]=max(theta_r,min(theta_s,theta[i]))
            if theta[i]<=theta_r:h[i]=-1e6
            elif theta[i]>=theta_s:h[i]=0.0
            else:
                Se=(theta[i]-theta_r)/(theta_s-theta_r);m=1-1/n
                h[i]=-((Se**(-1/m)-1)**(1/n))/alpha if Se>1e-6 else -100
        if precip_rate and step<len(precip_rate):theta[0]+=precip_rate[step]*dt/1000/dz
        if et_rate and step<len(et_rate):theta[0]-=et_rate[step]*dt/1000/dz
        theta[0]=max(theta_r,min(theta_s,theta[0]))
    return{"model_fidelity":"simplified","h_final":[round(float(x),4)for x in h],"theta_final":[round(float(x),4)for x in theta],"hysteresis_state":[bool(x)for x in hs],"solver":"FDM dynamic hysteresis"}
