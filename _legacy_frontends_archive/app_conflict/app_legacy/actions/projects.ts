'use server'

import { createClient } from '@/lib/supabase/server'
import { revalidatePath } from 'next/cache'
import { z } from 'zod'

const projectSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().optional(),
  status: z.enum(['active', 'archived', 'draft']).default('draft'),
})

export async function createProject(formData: FormData) {
  const supabase = await createClient()
  
  const validatedData = projectSchema.parse({
    name: formData.get('name'),
    description: formData.get('description'),
    status: formData.get('status'),
  })

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  const { data: profile } = await supabase
    .from('profiles')
    .select('tenant_id')
    .eq('id', user.id)
    .single()

  const { error } = await supabase
    .from('projects')
    .insert({
      ...validatedData,
      tenant_id: profile!.tenant_id,
      created_by: user.id,
    })

  if (error) throw error

  revalidatePath('/projects')
  return { success: true }
}

export async function updateProject(id: string, formData: FormData) {
  const supabase = await createClient()
  
  const validatedData = projectSchema.parse({
    name: formData.get('name'),
    description: formData.get('description'),
    status: formData.get('status'),
  })

  const { error } = await supabase
    .from('projects')
    .update(validatedData)
    .eq('id', id)

  if (error) throw error

  revalidatePath(`/projects/${id}`)
  revalidatePath('/projects')
  return { success: true }
}

export async function deleteProject(id: string) {
  const supabase = await createClient()
  
  const { error } = await supabase
    .from('projects')
    .delete()
    .eq('id', id)

  if (error) throw error

  revalidatePath('/projects')
  return { success: true }
}