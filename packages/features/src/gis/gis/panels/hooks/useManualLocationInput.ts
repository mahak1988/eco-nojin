import { useState, useEffect } from 'react'

interface ManualLocationInputState {
  loading: boolean
  error: Error | null
}

export function useManualLocationInput() {
  const [state, setState] = useState<ManualLocationInputState>({
    loading: false,
    error: null,
  })

  // TODO: منتقل کردن state ها از ManualLocationInput

  return {
    ...state,
  }
}
