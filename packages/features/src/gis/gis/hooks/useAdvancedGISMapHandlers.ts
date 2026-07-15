import { useCallback } from 'react'

export function useAdvancedGISMapHandlers() {
  // TODO: منتقل کردن event handlers از AdvancedGISMap

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
