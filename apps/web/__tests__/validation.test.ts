import { describe, it, expect } from 'vitest'
import { z } from 'zod'

const projectSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  status: z.enum(['active', 'archived', 'draft']),
})

describe('Project Validation', () => {
  it('should validate correct project data', () => {
    const result = projectSchema.safeParse({
      name: 'Test Project',
      description: 'Test description',
      status: 'active',
    })
    expect(result.success).toBe(true)
  })

  it('should reject invalid status', () => {
    const result = projectSchema.safeParse({
      name: 'Test',
      status: 'invalid',
    })
    expect(result.success).toBe(false)
  })

  it('should reject empty name', () => {
    const result = projectSchema.safeParse({
      name: '',
      status: 'active',
    })
    expect(result.success).toBe(false)
  })
})