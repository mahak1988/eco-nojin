export type Json = string | number | boolean | null | { [key: string]: Json } | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          role: 'admin' | 'manager' | 'member'
          created_at: string
        }
        Insert: {
          id?: string
          email: string
          role?: 'admin' | 'manager' | 'member'
        }
        Update: {
          email?: string
          role?: 'admin' | 'manager' | 'member'
        }
      }
      tenants: {
        Row: {
          id: string
          name: string
          slug: string
          created_at: string | null
        }
        Insert: {
          id?: string
          name: string
          slug: string
        }
        Update: {
          name?: string
          slug?: string
        }
      }
      profiles: {
        Row: {
          id: string
          tenant_id: string
          email: string
          full_name: string
          role: 'admin' | 'manager' | 'member'
          created_at: string | null
        }
        Insert: {
          id: string
          tenant_id: string
          email: string
          full_name: string
          role?: 'admin' | 'manager' | 'member'
        }
        Update: {
          tenant_id?: string
          email?: string
          full_name?: string
          role?: 'admin' | 'manager' | 'member'
        }
      }
      projects: {
        Row: {
          id: string
          name: string
          description: string | null
          status: string
          tenant_id: string
          created_at: string | null
        }
        Insert: {
          id?: string
          name: string
          description?: string | null
          status?: string
          tenant_id: string
        }
        Update: {
          name?: string
          description?: string | null
          status?: string
          tenant_id?: string
        }
      }
      tasks: {
        Row: {
          id: string
          project_id: string
          title: string
          status: string
          due_date: string | null
          created_at: string | null
        }
        Insert: {
          id?: string
          project_id: string
          title: string
          status?: string
          due_date?: string | null
        }
        Update: {
          project_id?: string
          title?: string
          status?: string
          due_date?: string | null
        }
      }
    }
    Views: {}
    Functions: {}
  }
}
