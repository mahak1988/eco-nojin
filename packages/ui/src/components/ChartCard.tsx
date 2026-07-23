"use client";
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, Legend, AreaChart, Area } from "recharts";

import { CHART, GIS, UI } from '@econojin/ui/lib/chart-colors';

export function ChartCard({ title, icon, data, chartType, xKey="name", yKey="value", colors=[CHART.blue,CHART.emerald,CHART.amber,"#ec4899"], badge, loading }) {
  if (loading) return <Card className="border-slate-800 bg-slate-900/50 animate-pulse"><CardHeader><div className="h-6 bg-slate-800 rounded w-32"/></CardHeader><CardContent><div className="h-48 bg-slate-800 rounded"/></CardContent></Card>;
  
  const common = <><XAxis dataKey={xKey} stroke={UI.textBody} fontSize={11} tickLine={false} axisLine={false}/><YAxis stroke={UI.textBody} fontSize={11} tickLine={false} axisLine={false}/><Tooltip contentStyle={{backgroundColor:GIS.background,border:"1px solid #1e293b",borderRadius:"12px",boxShadow:"0 10px 15px -3px rgba(0,0,0,0.5)"}} itemStyle={{color:UI.border}}/><Legend wrapperStyle={{color:UI.textMuted, fontSize:"12px"}}/></>;
  
  const renderChart = () => {
    switch(chartType) {
      case "line": return <ResponsiveContainer width="100%" height={220}><LineChart data={data}>{common}<Line type="monotone" dataKey={yKey} stroke={colors[0]} strokeWidth={3} dot={{r:4, fill:colors[0], strokeWidth:2, stroke:GIS.background}} activeDot={{r:6}}/></LineChart></ResponsiveContainer>;
      case "bar": return <ResponsiveContainer width="100%" height={220}><BarChart data={data}>{common}<Bar dataKey={yKey} fill={colors[0]} radius={[6,6,0,0]} maxBarSize={40}/></BarChart></ResponsiveContainer>;
      case "pie": return <ResponsiveContainer width="100%" height={220}><PieChart><Pie data={data} dataKey={yKey} nameKey={xKey} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={4} label>{data.map((_,i)=> <Cell key={i} fill={colors[i%colors.length]} stroke={GIS.background} strokeWidth={2}/>)}</Pie><Tooltip contentStyle={{backgroundColor:GIS.background,border:"1px solid #1e293b",borderRadius:"12px"}}/></PieChart></ResponsiveContainer>;
      case "area": return <ResponsiveContainer width="100%" height={220}><AreaChart data={data}>{common}<Area type="monotone" dataKey={yKey} stroke={colors[0]} strokeWidth={2} fill={`url(#grad)`} fillOpacity={0.2}/><defs><linearGradient id="grad" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={colors[0]} stopOpacity={0.3}/><stop offset="95%" stopColor={colors[0]} stopOpacity={0}/></linearGradient></defs></AreaChart></ResponsiveContainer>;
      default: return <div className="h-48 flex items-center justify-center text-slate-500">نمودار در دسترس نیست</div>;
    }
  };
  
  return (
    <motion.div initial={{opacity:0,y:15}} animate={{opacity:1,y:0}} transition={{duration:0.4}}>
      <Card className="border-slate-800 bg-slate-900/40 backdrop-blur-sm shadow-xl shadow-black/20">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl shadow-lg" style={{backgroundColor:colors[0]+"20", color:colors[0]}}>{icon}</div>
              <CardTitle className="text-base font-semibold text-slate-100">{title}</CardTitle>
            </div>
            {badge && <Badge variant={badge.variant} className="shadow-sm">{badge.label}</Badge>}
          </div>
        </CardHeader>
        <CardContent className="pt-2">{renderChart()}</CardContent>
      </Card>
    </motion.div>
  );
}
