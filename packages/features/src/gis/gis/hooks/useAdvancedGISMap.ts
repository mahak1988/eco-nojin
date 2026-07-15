import { useState, useEffect } from 'react'

interface AdvancedGISMapState {
  loading: boolean
  error: Error | null
}

export function useAdvancedGISMap() {
  const [state, setState] = useState<AdvancedGISMapState>({
    loading: false,
    error: null,
  })

  // TODO: منتقل کردن state ها از AdvancedGISMap

  return {
    ...state,
  }
}
