import { useCallback } from 'react'

export function useChatHandlers() {
  // TODO: منتقل کردن event handlers از Chat

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
  }, [])

  return {
    handleSubmit,
  }
}
