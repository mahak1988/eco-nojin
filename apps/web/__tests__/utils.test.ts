import { describe, it, expect } from 'vitest'
import { cn } from '@/lib/utils'

describe('cn utility function', () => {
  it('should merge class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar')
    expect(cn('foo', false && 'bar', 'baz')).toBe('foo baz')
    expect(cn('px-2', 'py-1', 'p-4')).toBe('p-4')
  })

  it('should handle conditional classes', () => {
    const isActive = true
    expect(cn('base', isActive && 'active')).toBe('base active')
  })
})