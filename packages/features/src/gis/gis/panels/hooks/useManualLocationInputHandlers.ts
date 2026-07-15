import { useCallback } from 'react'

export function useManualLocationInputHandlers() {
  // TODO: منتقل کردن event handlers از ManualLocationInput

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
