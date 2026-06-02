"""use client";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
export function GISونقشهCard({ title, value, icon, color }) {
  return (
    <motion.div whileHover={{ y: -5, scale: 1.01 }} transition={{ type: "spring", stiffness: 300 }}>
      <Card className="border-slate-800 bg-slate-900/40 backdrop-blur-sm shadow-lg relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-20 h-20 rounded-bl-full opacity-10 transition-opacity group-hover:opacity-20" style={{backgroundColor:color}}></div>
        <CardContent className="p-5 relative z-10 flex items-center gap-4">
          <div className="p-3 rounded-xl shadow-md" style={{ backgroundColor: color+"15", color: color }}>{icon}</div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</p>
            <p className="text-2xl font-bold text-slate-100 mt-1" style={{ color }}>{value}</p>
          </div>
        </CardContent>
    </Card>
    </motion.div>
  );
}
