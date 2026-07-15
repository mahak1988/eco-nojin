import { useQuery } from '@tanstack/react-query'

export function uselandSoilWaterClient() {
  return useQuery({
    queryKey: ['landsoilwaterclient'],
    queryFn: async () => {
      // TODO: منتقل کردن fetch logic از landSoilWaterClient
      const response = await fetch('/api/landsoilwaterclient')
      return response.json()
    },
  })
}
