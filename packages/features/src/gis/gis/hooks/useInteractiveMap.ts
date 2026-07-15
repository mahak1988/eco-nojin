import { useState, useEffect } from 'react'

interface InteractiveMapState {
  loading: boolean
  error: Error | null
}

export function useInteractiveMap() {
  const [state, setState] = useState<InteractiveMapState>({
    loading: false,
    error: null,
  })

  // TODO: منتقل کردن state ها از InteractiveMap

  return {
    ...state,
  }
}
