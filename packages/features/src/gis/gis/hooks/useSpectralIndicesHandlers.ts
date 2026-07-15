import { useCallback } from 'react'

export function useSpectralIndicesHandlers() {
  // TODO: منتقل کردن event handlers از SpectralIndices

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    // TODO
  }, [])

  const handleChange = useCallback((e: React.ChangeEvent) => {
    // TODO
  }, [])

  return {
    handleSubmit,
    handleChange,
  }
}
