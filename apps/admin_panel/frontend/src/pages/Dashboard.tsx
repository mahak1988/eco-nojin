import React from 'react';
import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  Settings, 
  FileText, 
  Activity, 
  Shield, 
  BookOpen, 
  Receipt, 
  CreditCard, 
  BarChart3,
  Brain,
  FileCode
} from 'lucide-react';
import CustomizableDashboard from '../components/CustomizableDashboard';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <CustomizableDashboard />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link 
          to="/users" 
          className="p-6 bg-card rounded-xl border shadow-sm hover:shadow-md transition-shadow flex items-center gap-4"
        >
          <div className="p-3 rounded-lg bg-blue-100 text-blue-600">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">مدیریت کاربران</h3>
            <p className="text-sm text-muted-foreground">مشاهده و مدیریت کاربران سیستم</p>
          </div>
        </Link>
        
        <Link 
          to="/settings" 
          className="p-6 bg-card rounded-xl border shadow-sm hover:shadow-md transition-shadow flex items-center gap-4"
        >
          <div className="p-3 rounded-lg bg-green-100 text-green-600">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">تنظیمات سیستم</h3>
            <p className="text-sm text-muted-foreground">پیکربندی تنظیمات سیستم</p>
          </div>
        </Link>
        
        <Link 
          to="/audit-logs" 
          className="p-6 bg-card rounded-xl border shadow-sm hover:shadow-md transition-shadow flex items-center gap-4"
        >
          <div className="p-3 rounded-lg bg-purple-100 text-purple-600">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">لاگ‌های حسابرسی</h3>
            <p className="text-sm text-muted-foreground">مشاهده فعالیت‌های سیستم</p>
          </div>
        </Link>
        
        <Link 
          to="/content-management" 
          className="p-6 bg-card rounded-xl border shadow-sm hover:shadow-md transition-shadow flex items-center gap-4"
        >
          <div className="p-3 rounded-lg bg-amber-100 text-amber-600">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">مدیریت محتوا</h3>
            <p className="text-sm text-muted-foreground">مدیریت صفحات، مقالات و محصولات</p>
          </div>
        </Link>
        
        <Link 
          to="/intelligent-analytics" 
          className="p-6 bg-card rounded-xl border shadow-sm hover:shadow-md transition-shadow flex items-center gap-4"
        >
          <div className="p-3 rounded-lg bg-indigo-100 text-indigo-600">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">تحلیل‌های هوشمند</h3>
            <p className="text-sm text-muted-foreground">تحلیل‌های پیشرفته با هوش مصنوعی</p>
          </div>
        </Link>
        
        <Link 
          to="/reports" 
          className="p-6 bg-card rounded-xl border shadow-sm hover:shadow-md transition-shadow flex items-center gap-4"
        >
          <div className="p-3 rounded-lg bg-emerald-100 text-emerald-600">
            <BarChart3 className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold">گزارش‌ها</h3>
            <p className="text-sm text-muted-foreground">گزارش‌های سیستم و عملکرد</p>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Dashboard;