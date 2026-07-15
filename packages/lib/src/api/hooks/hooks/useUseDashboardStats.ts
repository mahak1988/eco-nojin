import { useQuery } from '@tanstack/react-query'

export function useuseDashboardStats() {
  return useQuery({
    queryKey: ['usedashboardstats'],
    queryFn: async () => {
      // TODO: منتقل کردن fetch logic از useDashboardStats
      const response = await fetch('/api/usedashboardstats')
      return response.json()
    },
  })
}
