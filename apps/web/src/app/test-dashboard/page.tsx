import { DashboardWidgets } from '@/components/DashboardWidgets';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <h1 className="text-4xl font-bold text-white mb-8 text-center">
        🚀 Econojin Dashboard Test
      </h1>
      <DashboardWidgets />
    </div>
  );
}
