import { useState, useEffect } from 'react'

interface SpectralIndicesState {
  // TODO: تعریف state ها
  loading: boolean
  error: Error | null
}

export function useSpectralIndices() {
  const [state, setState] = useState<SpectralIndicesState>({
    loading: false,
    error: null,
  })

  // TODO: منتقل کردن state ها و logic از SpectralIndices

  return {
    ...state,
    // TODO: export actions
  }
}
