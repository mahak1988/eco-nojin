// Placeholder - Supabase not configured in this version
// برای فعال‌سازی: ۱. نصب @supabase/supabase-js  ۲. تنظیم متغیرهای محیطی

export type SupabaseClient = {
  auth: {
    signInWithPassword: (params: { email: string; password: string }) => Promise<{ error: any; data: { user: any } }>
    signUp: (params: { email: string; password: string }) => Promise<{ error: any; data: { user: any } }>
    signOut: () => Promise<{ error: any }>
    getUser: () => Promise<{ data: { user: any } }>
  }
  from: (table: string) => {
    select: (columns?: string) => {
      eq: (key: string, value: any) => {
        single: () => Promise<any>
        maybeSingle: () => Promise<any>
      }
    }
    insert: (data: any) => { select: (columns?: string) => { single: () => Promise<any> } }
    update: (data: any) => { eq: (key: string, value: any) => { select: (columns?: string) => { single: () => Promise<any> } } }
    delete: () => { eq: (key: string, value: any) => { single: () => Promise<any> } }
  }
}

export const createClient = (): SupabaseClient => ({
  auth: {
    signInWithPassword: async () => ({ error: null, data: { user: null } }),
    signUp: async () => ({ error: null, data: { user: null } }),
    signOut: async () => ({ error: null }),
    getUser: async () => ({ data: { user: null } }),
  },
  from: (table: string) => ({
    select: (columns?: string) => ({
      eq: (key: string, value: any) => ({
        single: async () => null,
        maybeSingle: async () => null,
      }),
    }),
    insert: (data: any) => ({
      select: (columns?: string) => ({ single: async () => null }),
    }),
    update: (data: any) => ({
      eq: (key: string, value: any) => ({ select: (columns?: string) => ({ single: async () => null }) }),
    }),
    delete: () => ({ eq: (key: string, value: any) => ({ single: async () => null }) }),
  }),
})

export const supabase = createClient()
