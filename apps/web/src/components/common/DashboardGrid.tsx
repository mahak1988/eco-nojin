import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BarChart3, TrendingUp, Activity, Leaf } from "lucide-react"

interface DashboardCardProps {
  title: string
  value: string | number
  description?: string
  icon?: React.ReactNode
  trend?: "up" | "down" | "neutral"
  trendValue?: string
  className?: string
}

function DashboardCard({
  title,
  value,
  description,
  icon,
  trend,
  trendValue,
  className,
}: DashboardCardProps) {
  return (
    <Card className={cn("overflow-hidden transition-all hover:shadow-lg", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
        {trend && trendValue && (
          <div className="flex items-center mt-2">
            {trend === "up" && <TrendingUp className="h-3 w-3 text-green-500 mr-1" />}
            {trend === "down" && <TrendingUp className="h-3 w-3 text-red-500 mr-1 rotate-180" />}
            <span
              className={cn(
                "text-xs font-medium",
                trend === "up" && "text-green-500",
                trend === "down" && "text-red-500",
                trend === "neutral" && "text-muted-foreground",
              )}
            >
              {trendValue}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

interface DashboardGridProps {
  cards: Omit<DashboardCardProps, "className">[]
  columns?: 1 | 2 | 3 | 4
}

function DashboardGrid({ cards, columns = 4 }: DashboardGridProps) {
  return (
    <div
      className={cn(
        "grid gap-4",
        columns === 1 && "grid-cols-1",
        columns === 2 && "grid-cols-1 md:grid-cols-2",
        columns === 3 && "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
        columns === 4 && "grid-cols-1 md:grid-cols-2 lg:grid-cols-4",
      )}
    >
      {cards.map((card, index) => (
        <DashboardCard key={index} {...card} />
      ))}
    </div>
  )
}

// Predefined dashboard cards for EcoNojin project
const defaultEcoCards: Omit<DashboardCardProps, "className">[] = [
  {
    title: "کشاورزان فعال",
    value: "1,245",
    description: "در ماه جاری",
    icon: <Leaf className="h-4 w-4 text-green-500" />,
    trend: "up",
    trendValue: "+12% نسبت به ماه قبل",
  },
  {
    title: "زمین های ثبت شده",
    value: "856",
    description: "هکتار مشوق‌شده",
    icon: <Activity className="h-4 w-4 text-blue-500" />,
    trend: "up",
    trendValue: "+8% رشد",
  },
  {
    title: "داده‌های MRV",
    value: "12,432",
    description: "رکورد در سامانه",
    icon: <BarChart3 className="h-4 w-4 text-purple-500" />,
    trend: "neutral",
    trendValue: "به‌روزرسانی امروز",
  },
  {
    title: "تصمیم‌گیری هوشمند",
    value: "98%",
    description: "دقت پیش‌بینی",
    icon: <Activity className="h-4 w-4 text-orange-500" />,
    trend: "up",
    trendValue: "+2% بهبود",
  },
]

function EcoDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">داشبورد کشاورزی هوشمند</h2>
        <p className="text-muted-foreground">
          خلاصه‌ای از عملکرد و داده‌های پروژه‌های کشاورزی محیط‌زیست
        </p>
      </div>
      <DashboardGrid cards={defaultEcoCards} />
    </div>
  )
}

export { DashboardCard, DashboardGrid, EcoDashboard, type DashboardCardProps, type DashboardGridProps }