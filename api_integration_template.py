from pathlib import Path

print("🔌 Creating API integration templates...")

frontend_path = Path('apps/web')

# Create API hooks template
hooks_content = """import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api-client';

// Dashboard
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => api.getDashboardStats(),
    staleTime: 5 * 60 * 1000,
  });
}

// IoT
export function useIoTStats() {
  return useQuery({
    queryKey: ['iot', 'stats'],
    queryFn: () => api.getIoTStats(),
    staleTime: 30 * 1000,
  });
}

// EcoCoin
export function useMyWallet() {
  return useQuery({
    queryKey: ['ecocoin', 'wallet'],
    queryFn: () => api.getMyWallet(),
  });
}

export function useTransferTokens() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => api.transferTokens(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ecocoin', 'wallet'] });
    },
  });
}

// Academy
export function useAcademyStats() {
  return useQuery({
    queryKey: ['academy', 'stats'],
    queryFn: () => api.getAcademyStats(),
  });
}

// Add more hooks as needed...
"""

hooks_path = frontend_path / 'src/hooks/useApiHooks.ts'
hooks_path.write_text(hooks_content, encoding='utf-8')
print(f"✅ Created {hooks_path}")

# Create example component
example_content = """'use client';

import { useDashboardStats, useIoTStats } from '@/hooks/useApiHooks';

export function DashboardExample() {
  const { data: dashboard, isLoading: dashboardLoading } = useDashboardStats();
  const { data: iot, isLoading: iotLoading } = useIoTStats();

  if (dashboardLoading || iotLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <pre>{JSON.stringify(dashboard, null, 2)}</pre>
      <h2>IoT Stats</h2>
      <pre>{JSON.stringify(iot, null, 2)}</pre>
    </div>
  );
}
"""

example_path = frontend_path / 'src/components/DashboardExample.tsx'
example_path.write_text(example_content, encoding='utf-8')
print(f"✅ Created {example_path}")

print("\n✅ API integration templates created!")
print("\n📋 Next steps:")
print("1. Import hooks in your components")
print("2. Use the data in your UI")
print("3. Add error handling")
print("4. Add loading states")
