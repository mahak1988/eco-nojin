import React from 'react';

// کامپوننت مشترک نقشه برای جلوگیری از تکرار در ماژول‌های GIS، توپوگرافی و اکوتوریسم
export const MapViewer: React.FC<{ center?: [number, number] }> = ({ center = [35.6892, 51.3890] }) => {
  return (
    <div className="w-full h-96 bg-slate-100 rounded-lg flex items-center justify-center border border-slate-200">
      <span className="text-slate-500">Interactive Map Component (Leaflet/Mapbox)</span>
    </div>
  );
};
