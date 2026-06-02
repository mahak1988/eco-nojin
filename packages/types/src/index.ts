export type UserRole = 'admin' | 'manager' | 'member'

export interface Tenant {
  id: string
  name: string
  slug: string
}

export interface AppUser {
  id: string
  email: string
  role: UserRole
  tenantId: string
}
