"""use client";
import { motion, useSpring, useTransform } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { useEffect } from "react";

export function AnimatedStatCard({title,value,suffix="",prefix="",icon,color,trend}){
  const spring=useSpring(0,{damping:25,stiffness:150});
  const display=useTransform(spring,v=>prefix+Math.round(v).toLocaleString("fa-IR")+suffix);
  useEffect(()=>{spring.set(value);},[value,spring]);
  return (
    <motion.div whileHover={{y:-5, scale:1.01}} transition={{type:"spring",stiffness:300}}>
      <Card className="border-slate-800 bg-slate-900/40 backdrop-blur-sm shadow-lg shadow-black/10 relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-24 h-24 rounded-bl-full opacity-10 transition-opacity group-hover:opacity-20" style={{backgroundColor:color}}></div>
        <CardContent className="p-5 relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
              <motion.p className="text-2xl font-bold mt-2 text-slate-100" style={{color}}>{display}</motion.p>
              {trend && <div className={"flex items-center gap-1.5 mt-2 text-xs font-medium "+(trend.positive!==false?"text-emerald-400":"text-rose-400")}>
                <span className="bg-slate-950/50 px-1.5 py-0.5 rounded">{trend.positive!==false?"↑":"↓"} {Math.abs(trend.value).toLocaleString("fa-IR")}{trend.suffix||"%"}</span>
                <span className="text-slate-500">{trend.label}</span>
              </div>}
            </div>
            <motion.div className="p-3 rounded-xl shadow-lg" style={{backgroundColor:color+"15", color:color}} whileHover={{scale:1.1, rotate:5}} transition={{type:"spring",stiffness:400}}>{icon}</motion.div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
