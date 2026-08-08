import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, Lightbulb, BarChart3, Activity, Target, Zap, Shield, Users, Database, Server } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@econojin/ui';
import { Badge } from '@econojin/ui';
import { Button } from '@econojin/ui';
import { Skeleton } from '@econojin/ui';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@econojin/ui';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  LineChart, Line, AreaChart, Area
} from 'recharts';
import { useTheme } from '../contexts/ThemeContext';

// Types for intelligent analytics
interface Recommendation {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  confidence: number; // 0-1
  suggestedAction: string;
  createdAt: string;
}

interface Alert {
  id: string;
  type: 'error' | 'warning' | 'info';
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  timestamp: string;
  actionRequired: boolean;
  patternScore: number; // 0-1
}

interface Prediction {
  metric: string;
  currentValue: number;
  predictedValue: number;
  changePercentage: number;
  confidence: number; // 0-1
}

interface Insight {
  id: string;
  title: string;
  description: string;
  category: string;
  impact: 'high' | 'medium' | 'low';
  trend: 'increasing' | 'decreasing' | 'stable';
}

interface AnalyticsSummary {
  totalRecommendations: number;
  activeAlerts: number;
  predictedImprovements: number;
  confidenceScore: number;
}

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkIn: number;
  networkOut: number;
  uptime: number;
}

const IntelligentAnalyticsDashboard: React.FC = () => {
  const { themeColors } = useTheme();
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data initialization
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      
      // Simulate API calls with mock data
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Mock summary
      const mockSummary: AnalyticsSummary = {
        totalRecommendations: 12,
        activeAlerts: 5,
        predictedImprovements: 18,
        confidenceScore: 0.87
      };
      
      // Mock recommendations
      const mockRecommendations: Recommendation[] = [
        {
          id: 'rec_001',
          title: 'بهینه سازی عملکرد پایگاه داده',
          description: 'تحلیل هوشمند نشان می‌دهد که عملکرد پایگاه داده نیاز به بهینه سازی دارد',
          category: 'performance',
          priority: 'high',
          confidence: 0.92,
          suggestedAction: 'index_optimization',
          createdAt: '2023-06-15T10:30:00Z'
        },
        {
          id: 'rec_002',
          title: 'افزایش امنیت سیستم',
          description: 'شناسایی نقاط ضعف امنیتی که نیاز به توجه دارند',
          category: 'security',
          priority: 'medium',
          confidence: 0.78,
          suggestedAction: 'security_audit',
          createdAt: '2023-06-14T14:20:00Z'
        },
        {
          id: 'rec_003',
          title: 'بهبود تجربه کاربری',
          description: 'تحلیل رفتار کاربران نشان می‌دهد که برخی بخش‌ها نیاز به بهبود دارند',
          category: 'ux',
          priority: 'medium',
          confidence: 0.85,
          suggestedAction: 'ui_enhancement',
          createdAt: '2023-06-13T09:15:00Z'
        },
        {
          id: 'rec_004',
          title: 'بهینه سازی تصاویر',
          description: 'تصاویر بارگذاری شده می‌توانند فشرده‌سازی شوند تا عملکرد بهبود یابد',
          category: 'performance',
          priority: 'low',
          confidence: 0.65,
          suggestedAction: 'image_optimization',
          createdAt: '2023-06-12T16:45:00Z'
        }
      ];
      
      // Mock alerts
      const mockAlerts: Alert[] = [
        {
          id: 'alert_001',
          type: 'error',
          title: 'تاخیر بالا در پایگاه داده',
          description: 'تاخیر در پرس و جوهای پایگاه داده بیش از حد مجاز است',
          severity: 'high',
          timestamp: '2023-06-15T10:30:00Z',
          actionRequired: true,
          patternScore: 0.91
        },
        {
          id: 'alert_002',
          type: 'warning',
          title: 'فعالیت غیرمعمول ورود',
          description: 'تعداد زیادی تلاش ورود ناموفق در مدت کوتاهی',
          severity: 'medium',
          timestamp: '2023-06-15T09:45:00Z',
          actionRequired: true,
          patternScore: 0.78
        },
        {
          id: 'alert_003',
          type: 'warning',
          title: 'فضای دیسک در حال پر شدن',
          description: 'ظرفیت دیسک به 85% رسیده است',
          severity: 'medium',
          timestamp: '2023-06-15T08:20:00Z',
          actionRequired: true,
          patternScore: 0.82
        },
        {
          id: 'alert_004',
          type: 'info',
          title: 'کاربران جدید زیادی',
          description: 'افزایش ۲۵٪ در ثبت نام کاربران جدید',
          severity: 'low',
          timestamp: '2023-06-14T17:30:00Z',
          actionRequired: false,
          patternScore: 0.65
        }
      ];
      
      // Mock predictions
      const mockPredictions: Prediction[] = [
        {
          metric: 'کاربران فعال',
          currentValue: 8500,
          predictedValue: 9750,
          changePercentage: 14.7,
          confidence: 0.89
        },
        {
          metric: 'درخواست‌های API',
          currentValue: 12500,
          predictedValue: 14200,
          changePercentage: 13.6,
          confidence: 0.82
        },
        {
          metric: 'میزان مصرف حافظه',
          currentValue: 68,
          predictedValue: 75,
          changePercentage: 10.3,
          confidence: 0.76
        },
        {
          metric: 'حجم ترافیک',
          currentValue: 2.4,
          predictedValue: 2.8,
          changePercentage: 16.7,
          confidence: 0.91
        }
      ];
      
      // Mock insights
      const mockInsights: Insight[] = [
        {
          id: 'ins_001',
          title: 'افزایش ترافیک از موبایل',
          description: '۶۵٪ از کاربران از دستگاه‌های موبایل استفاده می‌کنند',
          category: 'traffic',
          impact: 'high',
          trend: 'increasing'
        },
        {
          id: 'ins_002',
          title: 'کاربران بیشتر در ساعات کاری',
          description: '۷۰٪ فعالیت کاربران در ساعات ۹ تا ۱۷ است',
          category: 'behavior',
          impact: 'medium',
          trend: 'stable'
        },
        {
          id: 'ins_003',
          title: 'افزایش محتوای بلاگ',
          description: 'محتوای بلاگ ۳۵٪ در ماه گذشته افزایش یافته است',
          category: 'content',
          impact: 'medium',
          trend: 'increasing'
        }
      ];
      
      // Mock system metrics
      const mockSystemMetrics: SystemMetrics = {
        cpuUsage: 65,
        memoryUsage: 72,
        diskUsage: 85,
        networkIn: 1.2,
        networkOut: 0.8,
        uptime: 99.9
      };
      
      setSummary(mockSummary);
      setRecommendations(mockRecommendations);
      setAlerts(mockAlerts);
      setPredictions(mockPredictions);
      setInsights(mockInsights);
      setSystemMetrics(mockSystemMetrics);
      setLoading(false);
    };
    
    loadData();
  }, []);

  // Priority badge component
  const PriorityBadge: React.FC<{ priority: 'high' | 'medium' | 'low' }> = ({ priority }) => {
    const priorityClasses = {
      high: 'bg-destructive text-destructive-foreground',
      medium: 'bg-yellow-500 text-yellow-900',
      low: 'bg-green-500 text-green-900'
    };
    
    return (
      <Badge className={priorityClasses[priority]}>
        {priority === 'high' ? 'بالا' : priority === 'medium' ? 'متوسط' : 'کم'}
      </Badge>
    );
  };

  // Severity badge component
  const SeverityBadge: React.FC<{ severity: 'high' | 'medium' | 'low' }> = ({ severity }) => {
    const severityClasses = {
      high: 'bg-destructive text-destructive-foreground',
      medium: 'bg-yellow-500 text-yellow-900',
      low: 'bg-green-500 text-green-900'
    };
    
    return (
      <Badge className={severityClasses[severity]}>
        {severity === 'high' ? 'بالا' : severity === 'medium' ? 'متوسط' : 'کم'}
      </Badge>
    );
  };

  // Type badge component
  const TypeBadge: React.FC<{ type: 'error' | 'warning' | 'info' }> = ({ type }) => {
    const typeClasses = {
      error: 'bg-destructive text-destructive-foreground',
      warning: 'bg-yellow-500 text-yellow-900',
      info: 'bg-blue-500 text-blue-900'
    };
    
    return (
      <Badge className={typeClasses[type]}>
        {type === 'error' ? 'خطا' : type === 'warning' ? 'هشدار' : 'اطلاعات'}
      </Badge>
    );
  };

  // Impact badge component
  const ImpactBadge: React.FC<{ impact: 'high' | 'medium' | 'low' }> = ({ impact }) => {
    const impactClasses = {
      high: 'bg-red-500 text-red-900',
      medium: 'bg-yellow-500 text-yellow-900',
      low: 'bg-green-500 text-green-900'
    };
    
    return (
      <Badge className={impactClasses[impact]}>
        {impact === 'high' ? 'بالا' : impact === 'medium' ? 'متوسط' : 'کم'}
      </Badge>
    );
  };

  // Trend indicator component
  const TrendIndicator: React.FC<{ trend: 'increasing' | 'decreasing' | 'stable' }> = ({ trend }) => {
    const trendConfig = {
      increasing: { icon: TrendingUp, color: 'text-green-500', text: 'افزایش' },
      decreasing: { icon: TrendingUp, color: 'text-red-500 rotate-180', text: 'کاهش' },
      stable: { icon: Target, color: 'text-blue-500', text: 'ثابت' }
    };

    const config = trendConfig[trend];
    return (
      <div className={`flex items-center gap-1 ${config.color}`}>
        <config.icon className="w-4 h-4" />
        <span className="text-xs">{config.text}</span>
      </div>
    );
  };

  // Confidence indicator component
  const ConfidenceIndicator: React.FC<{ confidence: number }> = ({ confidence }) => {
    const percentage = Math.round(confidence * 100);
    const color = confidence > 0.8 ? 'text-green-500' : confidence > 0.6 ? 'text-yellow-500' : 'text-red-500';
    
    return (
      <div className="flex items-center gap-2">
        <div className="w-16 bg-muted rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${color.replace('text-', 'bg-')}`} 
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className={`text-sm font-medium ${color}`}>{percentage}%</span>
      </div>
    );
  };

  // System metrics charts
  const systemChartData = systemMetrics ? [
    { name: 'CPU', usage: systemMetrics.cpuUsage },
    { name: 'حافظه', usage: systemMetrics.memoryUsage },
    { name: 'دیسک', usage: systemMetrics.diskUsage },
  ] : [];

  const trafficData = [
    { name: 'شنبه', traffic: 4000 },
    { name: 'یکشنبه', traffic: 3000 },
    { name: 'دوشنبه', traffic: 2000 },
    { name: 'سه‌شنبه', traffic: 2780 },
    { name: 'چهارشنبه', traffic: 1890 },
    { name: 'پنجشنبه', traffic: 2390 },
    { name: 'جمعه', traffic: 3490 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <Brain className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">داشبورد تحلیلی هوشمند</h1>
            <p className="text-muted-foreground">
              تحلیل‌ها و بینش‌های هوشمند سیستم با استفاده از هوش مصنوعی
            </p>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">نمای کلی</TabsTrigger>
          <TabsTrigger value="recommendations">توصیه‌ها</TabsTrigger>
          <TabsTrigger value="alerts">هشدارها</TabsTrigger>
          <TabsTrigger value="predictions">پیش‌بینی‌ها</TabsTrigger>
          <TabsTrigger value="insights">بینش‌ها</TabsTrigger>
          <TabsTrigger value="metrics">معیارها</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">توصیه‌های فعال</CardTitle>
                <Lightbulb className="w-5 h-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {loading ? '--' : summary?.totalRecommendations}
                </div>
                <p className="text-xs text-muted-foreground">توصیه‌های هوشمند</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">هشدارهای فعال</CardTitle>
                <AlertTriangle className="w-5 h-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {loading ? '--' : summary?.activeAlerts}
                </div>
                <p className="text-xs text-muted-foreground">هشدارهای هوشمند</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">بهبودهای پیش‌بینی شده</CardTitle>
                <TrendingUp className="w-5 h-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {loading ? '--' : summary?.predictedImprovements}
                </div>
                <p className="text-xs text-muted-foreground">بهبودهای احتمالی</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">دقت پیش‌بینی</CardTitle>
                <Target className="w-5 h-5 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {loading ? '--%' : `${Math.round((summary?.confidenceScore || 0) * 100)}%`}
                </div>
                <p className="text-xs text-muted-foreground">اطمینان از داده‌ها</p>
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  ترافیک سیستم
                </CardTitle>
                <CardDescription>
                  تحلیل ترافیک در طول هفته
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-64 w-full" />
                ) : (
                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={trafficData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="name" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip
                        contentStyle={{
                          borderRadius: '8px',
                          border: '1px solid hsl(var(--border))',
                          background: 'hsl(var(--card))',
                        }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="traffic" 
                        stroke={themeColors.primary} 
                        fill={themeColors.primary + '40'} 
                        strokeWidth={2} 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="w-5 h-5" />
                  معیارهای سیستم
                </CardTitle>
                <CardDescription>
                  وضعیت منابع سیستم
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-64 w-full" />
                ) : (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={systemChartData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="name" className="text-xs" />
                      <YAxis className="text-xs" />
                      <Tooltip
                        contentStyle={{
                          borderRadius: '8px',
                          border: '1px solid hsl(var(--border))',
                          background: 'hsl(var(--card))',
                        }}
                      />
                      <Bar dataKey="usage" fill={themeColors.primary} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Top Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                توصیه‌های اولویت‌دار
              </CardTitle>
              <CardDescription>
                توصیه‌های هوشمند با بالاترین اولویت
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-3">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : (
                <div className="space-y-4">
                  {recommendations.slice(0, 3).map((rec) => (
                    <div key={rec.id} className="flex items-start gap-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0 pt-1">
                        <PriorityBadge priority={rec.priority} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium">{rec.title}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
                        <div className="mt-2 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">{rec.category}</Badge>
                            <ConfidenceIndicator confidence={rec.confidence} />
                          </div>
                          <Button variant="outline" size="sm">بررسی</Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                تمام توصیه‌های هوشمند
              </CardTitle>
              <CardDescription>
                لیست کامل توصیه‌های هوشمند بر اساس تحلیل داده‌ها
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-20 w-full" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {recommendations.map((rec) => (
                    <div key={rec.id} className="flex items-start gap-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0 pt-1">
                        <PriorityBadge priority={rec.priority} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-lg">{rec.title}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
                        <div className="mt-3 flex items-center justify-between flex-wrap gap-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary">{rec.category}</Badge>
                            <span className="text-xs text-muted-foreground">
                              {new Date(rec.createdAt).toLocaleDateString('fa-IR')}
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <ConfidenceIndicator confidence={rec.confidence} />
                            <Button variant="outline">بررسی</Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                هشدارهای هوشمند
              </CardTitle>
              <CardDescription>
                لیست کامل هشدارهای هوشمند سیستم
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} className="h-20 w-full" />
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="flex items-start gap-4 p-4 border rounded-lg">
                      <div className="flex-shrink-0 pt-1">
                        <TypeBadge type={alert.type} />
                        <SeverityBadge severity={alert.severity as any} {...({className: "mt-2"} as any)} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-lg">{alert.title}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{alert.description}</p>
                        <div className="mt-3 flex items-center justify-between flex-wrap gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">
                              {new Date(alert.timestamp).toLocaleTimeString('fa-IR')}
                            </span>
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <Target className="w-3 h-3" />
                              <span>دقت: {Math.round(alert.patternScore * 100)}%</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {alert.actionRequired ? (
                              <Badge variant="default" className="bg-destructive text-destructive-foreground">
                                نیازمند اقدام
                              </Badge>
                            ) : (
                              <Badge variant="outline">اطلاع‌رسانی</Badge>
                            )}
                            <Button 
                              variant={alert.actionRequired ? "default" : "outline"}
                              className={alert.actionRequired ? "bg-destructive text-destructive-foreground hover:bg-destructive hover:text-destructive-foreground" : ""}
                            >
                              {alert.actionRequired ? 'اقدام فوری' : 'مشاهده'}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="predictions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                پیش‌بینی‌های هوشمند
              </CardTitle>
              <CardDescription>
                پیش‌بینی‌های سیستم برای دوره آینده
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  <Skeleton className="h-48 w-full" />
                  <Skeleton className="h-48 w-full" />
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {predictions.map((pred, idx) => (
                      <Card key={idx}>
                        <CardHeader>
                          <CardTitle className="text-lg">{pred.metric}</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-muted-foreground">مقدار فعلی</span>
                            <span className="font-medium">
                              {typeof pred.currentValue === 'number' ? pred.currentValue.toLocaleString() : pred.currentValue}
                              {pred.metric.includes('مصرف') ? '%' : pred.metric.includes('ترافیک') ? 'GB' : ''}
                            </span>
                          </div>
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-sm text-muted-foreground">پیش‌بینی</span>
                            <span className="font-medium text-primary">
                              {typeof pred.predictedValue === 'number' ? pred.predictedValue.toLocaleString() : pred.predictedValue}
                              {pred.metric.includes('مصرف') ? '%' : pred.metric.includes('ترافیک') ? 'GB' : ''}
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">تغییر</span>
                            <div className={`flex items-center gap-1 ${pred.changePercentage > 0 ? 'text-red-500' : 'text-green-500'}`}>
                              <TrendingUp className={`w-4 h-4 ${pred.changePercentage < 0 ? 'rotate-180' : ''}`} />
                              <span>{Math.abs(pred.changePercentage)}%</span>
                            </div>
                          </div>
                          <div className="mt-3">
                            <ConfidenceIndicator confidence={pred.confidence} />
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>نمودار پیش‌بینی ترافیک</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={trafficData}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                          <XAxis dataKey="name" className="text-xs" />
                          <YAxis className="text-xs" />
                          <Tooltip
                            contentStyle={{
                              borderRadius: '8px',
                              border: '1px solid hsl(var(--border))',
                              background: 'hsl(var(--card))',
                            }}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="traffic" 
                            stroke={themeColors.primary} 
                            strokeWidth={2} 
                            dot={{ r: 4 }} 
                            activeDot={{ r: 6 }} 
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="insights">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                بینش‌های هوشمند
              </CardTitle>
              <CardDescription>
                بینش‌های تحلیلی از داده‌های سیستم
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  <Skeleton className="h-32 w-full" />
                  <Skeleton className="h-32 w-full" />
                  <Skeleton className="h-32 w-full" />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {insights.map((insight) => (
                    <Card key={insight.id}>
                      <CardHeader>
                        <CardTitle className="text-lg">{insight.title}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <ImpactBadge impact={insight.impact} />
                            <TrendIndicator trend={insight.trend} />
                          </div>
                          <Badge variant="secondary">{insight.category}</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                معیارهای سیستم
              </CardTitle>
              <CardDescription>
                نمای کلی از معیارهای عملکرد سیستم
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  <Skeleton className="h-48 w-full" />
                </div>
              ) : systemMetrics ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>CPU</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">میزان مصرف</span>
                        <span className="font-medium">{systemMetrics.cpuUsage}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2.5">
                        <div 
                          className="bg-primary h-2.5 rounded-full" 
                          style={{ width: `${systemMetrics.cpuUsage}%` }}
                        />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>حافظه</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">میزان مصرف</span>
                        <span className="font-medium">{systemMetrics.memoryUsage}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2.5">
                        <div 
                          className="bg-blue-500 h-2.5 rounded-full" 
                          style={{ width: `${systemMetrics.memoryUsage}%` }}
                        />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>دیسک</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">میزان مصرف</span>
                        <span className="font-medium">{systemMetrics.diskUsage}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2.5">
                        <div 
                          className={systemMetrics.diskUsage > 80 ? "bg-red-500 h-2.5 rounded-full" : "bg-green-500 h-2.5 rounded-full"} 
                          style={{ width: `${systemMetrics.diskUsage}%` }}
                        />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>ترافیک ورودی</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">GB/ساعت</span>
                        <span className="font-medium">{systemMetrics.networkIn} GB</span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>ترافیک خروجی</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">GB/ساعت</span>
                        <span className="font-medium">{systemMetrics.networkOut} GB</span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>آپتایم</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">درصد</span>
                        <span className="font-medium">{systemMetrics.uptime}%</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  معیارهای سیستم در دسترس نیست
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default IntelligentAnalyticsDashboard;