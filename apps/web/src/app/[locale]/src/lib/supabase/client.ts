// Placeholder - Supabase not configured in this version
export const createClient = () => ({
  auth: {
    signInWithPassword: async () => ({ error: null, data: { user: null } }),
    signUp: async () => ({ error: null, data: { user: null } }),
    signOut: async () => ({ error: null }),
    getUser: async () => ({ data: { user: null } }),
  },
  from: () => ({
    select: () => ({ eq: () => ({ single: async () => null, maybeSingle: async () => null }) }),
    insert: () => ({ select: () => ({ single: async () => null }) }),
    update: () => ({ eq: () => ({ select: () => ({ single: async () => null }) }) }),
    delete: () => ({ eq: () => ({ single: async () => null }) }),
  }),
})
