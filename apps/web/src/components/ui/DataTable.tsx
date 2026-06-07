"use client";
import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Filter, ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from "lucide-react";

export function DataTable({data,columns,searchKeys=[],pageSize=10,emptyMessage="داده‌ای یافت نشد",onRowClick}){
  const [searchQuery,setSearchQuery]=useState("");
  const [sortKey,setSortKey]=useState(null);
  const [sortAsc,setSortAsc]=useState(true);
  const [page,setPage]=useState(1);
  
  const filtered=useMemo(()=>{
    let r=[...data];
    if(searchQuery) r=r.filter(row=>searchKeys.some(k=>String(row[k]).toLowerCase().includes(searchQuery.toLowerCase())));
    if(sortKey) r.sort((a,b)=>{const av=a[sortKey],bv=b[sortKey];return av<bv?(sortAsc?-1:1):av>bv?(sortAsc?1:-1):0;});
    return r;
  },[data,searchQuery,sortKey,sortAsc]);
  
  const paginated=filtered.slice((page-1)*pageSize,page*pageSize);
  const totalPages=Math.ceil(filtered.length/pageSize);
  
  return (
    <Card className="border-slate-800 bg-slate-900/40 backdrop-blur-sm shadow-xl shadow-black/20">
      <CardContent className="p-5">
        {searchKeys.length>0 && <div className="mb-5 relative max-w-sm"><Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500"/><Input placeholder="جستجو در جدول..." className="pr-10 bg-slate-950/50 border-slate-800 focus:border-slate-600 transition-colors" value={searchQuery} onChange={e=>{setSearchQuery(e.target.value);setPage(1);}}/></div>}
        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-sm text-right">
            <thead><tr className="bg-slate-950/80 border-b border-slate-800">{columns.map(col=><th key={String(col.key)} className="px-5 py-3.5 font-semibold text-slate-300 cursor-pointer hover:text-slate-100 transition-colors" onClick={()=>col.sortable&&setSortKey(col.key)}><div className="flex items-center gap-1.5">{col.title}{col.sortable&&sortKey===col.key&&(sortAsc?<ChevronUp className="h-3.5 w-3.5"/>:<ChevronDown className="h-3.5 w-3.5"/>)}</div></th>)}</tr></thead>
            <tbody><AnimatePresence mode="popLayout">{paginated.map((row,idx)=><motion.tr key={row.id} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} transition={{delay:idx*0.03}} className={`border-b border-slate-800/50 last:border-0 hover:bg-slate-800/30 transition-colors ${onRowClick?"cursor-pointer":""}`} onClick={()=>onRowClick?.(row)}>{columns.map(col=><td key={String(col.key)} className="px-5 py-3.5 text-slate-400" style={{width:col.width}}>{col.render?col.render(row[col.key],row):row[col.key]}</td>)}</motion.tr>)}</AnimatePresence></tbody>
          </table>
        </div>
        {paginated.length===0 && <div className="text-center py-16 text-slate-500"><Filter className="h-12 w-12 mx-auto mb-4 opacity-30"/><p className="text-sm">{emptyMessage}</p></div>}
        {totalPages>1 && <div className="flex items-center justify-between mt-5 pt-4 border-t border-slate-800"><p className="text-xs text-slate-500">صفحه {page} از {totalPages}</p><div className="flex gap-2"><Button variant="outline" size="sm" className="border-slate-800 hover:bg-slate-800" onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page===1}><ChevronRight className="h-3.5 w-3.5 ml-1"/>قبلی</Button><Button variant="outline" size="sm" className="border-slate-800 hover:bg-slate-800" onClick={()=>setPage(p=>Math.min(totalPages,p+1))} disabled={page===totalPages}>بعدی <ChevronLeft className="h-3.5 w-3.5 mr-1"/></Button></div></div>}
      </CardContent>
    </Card>
  );
}
