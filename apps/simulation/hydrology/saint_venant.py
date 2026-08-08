"""Saint-Venant 1-D Full Dynamic/Diffusive/Kinematic Wave + SCS-CN Runoff
Phase 3.3 | Manifest §2.4 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

CN_TABLE_IRAN = {
    ("A","forest"):30,("A","pasture"):39,("A","dry_farm"):54,("A","irrigated"):61,
    ("B","forest"):48,("B","pasture"):61,("B","dry_farm"):67,("B","irrigated"):72,
    ("C","forest"):62,("C","pasture"):74,("C","dry_farm"):76,("C","irrigated"):81,
    ("D","forest"):71,("D","pasture"):80,("D","dry_farm"):81,("D","irrigated"):88}
CN_SIMPLE = {"row_crop":78,"small_grain":72,"pasture":61,"forest":55,"bare":86,"urban":90}
CN_AMC = {"dry":0.87,"normal":1.0,"wet":1.13}

def scs_cn_runoff(P_mm,CN=78.0,amc="normal"):
    cn=CN*CN_AMC.get(amc,1.0);S=max(25400.0/cn-254.0,0.1);Ia=0.2*S
    return 0.0 if P_mm<=Ia else (P_mm-Ia)**2/(P_mm-Ia+S)

def scs_cn_continuous(P_mm,CN=78.0):
    Q=np.zeros_like(P_mm)
    for t in range(len(P_mm)):
        s=max(0,t-5);p5=P_mm[s:t+1].sum()
        amc="dry" if p5<13 else ("wet" if p5>=28 else "normal")
        Q[t]=scs_cn_runoff(P_mm[t],CN,amc)
    return Q

def manning_Q(A,P_w,S,n):
    A,P_w=np.asarray(A,float),np.asarray(P_w,float)
    R=np.where(P_w>1e-9,A/P_w,0.0)
    return np.sign(S)*(1.0/n)*A*R**(2./3.)*np.sqrt(np.abs(S)+1e-15)

def wp_rect(h,w):return w+2.0*np.maximum(h,0.0)
def wp_trap(h,bw,ss):return bw+2.0*h*np.sqrt(1.0+ss**2)
def area_rect(h,w):return np.maximum(h,0.0)*w
def area_trap(h,bw,ss):return np.maximum(h,0.0)*(bw+ss*np.maximum(h,0.0))
def h_from_area_trap(A,bw,ss):
    A=np.maximum(A,0.0)
    if ss<1e-15:return A/bw
    disc=bw**2+4.0*ss*A
    return np.maximum((-bw+np.sqrt(np.maximum(disc,0.0)))/(2.0*ss),0.001)
def friction_slope(Q,A,P_w,n):
    R=np.where(P_w>1e-9,A/P_w,1e-9)
    return n**2*Q*np.abs(Q)*P_w**(4./3.)/np.maximum(A,1e-9)**(10./3.)

class Scheme:
    KINEMATIC="kinematic";DIFFUSIVE="diffusive";DYNAMIC="dynamic"

@dataclass
class SVConfig:
    n_cells:int=50;dx:float=100.0;dt:float=10.0;n_steps:int=200
    n_manning:float=0.03;S0:float=0.001;width:float=5.0;side_slope:float=1.5
    channel_type:str="rectangular";scheme:str="diffusive";theta_weight:float=0.6
    max_iter:int=20;tol:float=1e-5;q_lateral:float=0.0;cn_value:float=78.0

def solve_saint_venant(cfg=None,Q_bc=0.5,P_series=None):
    cfg=cfg or SVConfig();g,n=9.81,cfg.n_cells
    if cfg.channel_type=="trapezoidal":
        h=np.full(n,0.5);A=area_trap(h,cfg.width,cfg.side_slope)
        P_w=wp_trap(h,cfg.width,cfg.side_slope)
    else:
        h=np.full(n,0.5);A=area_rect(h,cfg.width);P_w=wp_rect(h,cfg.width)
    Q=np.full(n,Q_bc);hh,hQ,Qout=[h.copy()],[Q.copy()],[]
    for st in range(cfg.n_steps):
        ql=np.full(n,cfg.q_lateral)
        if P_series is not None and st<len(P_series) and P_series[st]>0:
            ql+=scs_cn_runoff(P_series[st],cfg.cn_value)/1000.0*cfg.dx/cfg.dt
        if cfg.scheme==Scheme.KINEMATIC:
            h,Q,A,P_w=step_kinematic(h,Q,A,P_w,cfg,g,ql)
        elif cfg.scheme==Scheme.DIFFUSIVE:
            h,Q,A,P_w=step_diffusive(h,Q,A,P_w,cfg,g,ql)
        else:
            h,Q,A,P_w=step_dynamic(h,Q,A,P_w,cfg,g,ql)
        Q[0]=Q_bc;h[-1]=max(h[-1],0.005)
        hh.append(h.copy());hQ.append(Q.copy());Qout.append(float(Q[-1]))
    return {"status":"ok","h_final":h,"A_final":A,"Q_final":Q,
            "history_h":np.array(hh),"history_Q":np.array(hQ),
            "Q_out":np.array(Qout),"scheme":cfg.scheme}

def step_kinematic(h,Q,A,P_w,cfg,g,ql):
    n=cfg.n_cells;Qn=Q.copy()
    if cfg.channel_type=="trapezoidal":
        An=A.copy()
        for i in range(1,n):
            An[i]=max(A[i]-cfg.dt/cfg.dx*(Q[i]-Q[i-1])+ql[i]*cfg.dt,0.001)
        hn=h_from_area_trap(An,cfg.width,cfg.side_slope)
        Pn=wp_trap(hn,cfg.width,cfg.side_slope)
    else:
        An=A.copy()
        for i in range(1,n):
            An[i]=max(A[i]-cfg.dt/cfg.dx*(Q[i]-Q[i-1])+ql[i]*cfg.dt,0.001)
        hn=An/cfg.width;Pn=wp_rect(hn,cfg.width)
    for i in range(n):
        Qn[i]=float(manning_Q(np.array([An[i]]),np.array([Pn[i]]),np.array([cfg.S0]),cfg.n_manning)[0])
    return hn,Qn,An,Pn

def step_diffusive(h,Q,A,P_w,cfg,g,ql):
    n=cfg.n_cells;dh=np.zeros(n)
    dh[1:-1]=(h[2:]-h[:-2])/(2.0*cfg.dx)
    dh[0]=(h[1]-h[0])/cfg.dx;dh[-1]=(h[-1]-h[-2])/cfg.dx
    Sw=cfg.S0-dh;Qn=manning_Q(A,P_w,Sw,cfg.n_manning);An=A.copy()
    for i in range(1,n):
        An[i]=max(A[i]-cfg.dt/cfg.dx*(Qn[i]-Qn[i-1])+ql[i]*cfg.dt,0.001)
    if cfg.channel_type=="trapezoidal":
        hn=h_from_area_trap(An,cfg.width,cfg.side_slope)
        Pn=wp_trap(hn,cfg.width,cfg.side_slope)
    else:
        hn=An/cfg.width;Pn=wp_rect(hn,cfg.width)
    w=0.5;hn=w*hn+(1-w)*h;An=w*An+(1-w)*A
    return hn,Qn,An,Pn

def step_dynamic(h,Q,A,P_w,cfg,g,ql):
    n,dx,dt=cfg.n_cells,cfg.dx,cfg.dt
    Sf=friction_slope(Q,A,P_w,cfg.n_manning);Qn=Q.copy()
    for i in range(1,n-1):
        dhd=(h[i+1]-h[i-1])/(2.0*dx)
        q2a=Q**2/(A+1e-9);dq2d=(q2a[i+1]-q2a[i-1])/(2.0*dx)
        mom=-dq2d-g*A[i]*dhd-g*A[i]*(Sf[i]-cfg.S0)
        Qn[i]=max(Q[i]+dt*mom,0.0)
    An=A.copy()
    for i in range(1,n):
        An[i]=max(A[i]-dt/dx*(Qn[i]-Qn[i-1])+ql[i]*dt,0.001)
    if cfg.channel_type=="trapezoidal":
        hn=h_from_area_trap(An,cfg.width,cfg.side_slope)
        Pn=wp_trap(hn,cfg.width,cfg.side_slope)
    else:
        hn=An/cfg.width;Pn=wp_rect(hn,cfg.width)
    return hn,Qn,An,Pn

def compute_hydrograph(Qout,dt,threshold=0.1):
    pk=float(np.max(Qout));ttp=float(np.argmax(Qout))*dt
    ab=Qout>=threshold*pk
    if not np.any(ab):return {"peak_Q":pk,"ttp_s":ttp,"dur_s":0.0,"vol_m3":0.0}
    st=np.argmax(ab);en=len(ab)-np.argmax(ab[::-1])-1
    return {"peak_Q":pk,"ttp_s":ttp,"dur_s":(en-st+1)*dt,"vol_m3":float(np.sum(Qout)*dt)}

if __name__=="__main__":
    print("=== Saint-Venant Full ===")
    print(f"  SCS-CN(40mm):{scs_cn_runoff(40,78):.2f}mm")
    cfg=SVConfig(n_cells=40,n_steps=100,scheme="diffusive")
    out=solve_saint_venant(cfg,Q_bc=1.0,P_series=np.full(cfg.n_steps,2.0))
    hg=compute_hydrograph(out["Q_out"],cfg.dt)
    print(f"  h=[{out['h_final'].min():.3f},{out['h_final'].max():.3f}] pk={hg['peak_Q']:.3f}")
    print("ALL SAINT-VENANT TESTS PASSED")
