import { useCallback } from 'react'

export function useInteractiveMapHandlers() {
  // TODO: منتقل کردن event handlers از InteractiveMap

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
