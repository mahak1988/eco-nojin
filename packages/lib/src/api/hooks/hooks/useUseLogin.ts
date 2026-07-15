import { useQuery } from '@tanstack/react-query'

export function useuseLogin() {
  return useQuery({
    queryKey: ['uselogin'],
    queryFn: async () => {
      // TODO: منتقل کردن fetch logic از useLogin
      const response = await fetch('/api/uselogin')
      return response.json()
    },
  })
}
