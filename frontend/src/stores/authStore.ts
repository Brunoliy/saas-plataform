import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface User {
  id: string
  email: string
  full_name: string
  account_type: 'professional' | 'client'
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (user: User, token: string) => void
  logout: () => void
  updateUser: (user: User) => void
  loginDemo: (accountType: 'client' | 'professional') => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user: User, token: string) =>
        set({ user, token, isAuthenticated: true }),
      logout: () =>
        set({ user: null, token: null, isAuthenticated: false }),
      updateUser: (user: User) =>
        set({ user }),
      loginDemo: (accountType: 'client' | 'professional') => {
        const demoUser: User = {
          id: 'demo-' + accountType,
          email: accountType === 'client' ? 'cliente@demo.com' : 'profissional@demo.com',
          full_name: accountType === 'client' ? 'Cliente Demo' : 'Profissional Demo',
          account_type: accountType
        };
        set({ user: demoUser, token: 'demo-token', isAuthenticated: true });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
) 