import { apiClient } from './api'

export interface ClientLink {
  id: string
  client_id: string
  platform: string
  url: string
  label: string | null
  created_at: string
  updated_at: string
}

export interface ClientProfile {
  id: string
  user_id: string
  company_name?: string | null
  business_sector?: string | null
  description?: string | null
  bio?: string | null
  average_rating?: number | null
  total_reviews: number
  links?: ClientLink[]
  created_at: string
  updated_at: string
}

export interface ClientProfileCreate {
  company_name?: string | null
  business_sector?: string | null
}

export interface ClientProfileUpdate extends ClientProfileCreate {}

export const clientService = {
  async list(params?: { skip?: number; limit?: number; business_sector?: string }) {
    const response = await apiClient.get('/clients', { params })
    return response.data as { items: ClientProfile[]; total: number; page: number; size: number; pages: number }
  },

  async getById(id: string): Promise<ClientProfile> {
    const response = await apiClient.get<ClientProfile>(`/clients/${id}`)
    return response.data
  },

  async createProfile(data: ClientProfileCreate): Promise<ClientProfile> {
    const response = await apiClient.post<ClientProfile>('/clients', data)
    return response.data
  },

  async getMyProfile(): Promise<ClientProfile> {
    const response = await apiClient.get<ClientProfile>('/clients/me')
    return response.data
  },

  async updateMyProfile(data: ClientProfileUpdate): Promise<ClientProfile> {
    const response = await apiClient.put<ClientProfile>('/clients/me', data)
    return response.data
  },
}


