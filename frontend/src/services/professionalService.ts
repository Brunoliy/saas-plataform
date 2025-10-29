import apiClient from './api';

export interface ProfessionalLink {
  id: string;
  professional_id: string;
  platform: string;
  url: string;
  label: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfessionalLinkCreate {
  platform: string;
  url: string;
  label?: string | null;
}

export interface ProfessionalLinkUpdate {
  platform?: string;
  url?: string;
  label?: string | null;
}

export interface ProfessionalProfile {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  bio: string | null;
  hourly_rate: number | null;
  average_rating: number | null;
  total_reviews: number;
  links: ProfessionalLink[];
  created_at: string;
  updated_at: string;
}

export interface ProfessionalProfileCreate {
  bio?: string | null;
}

export interface ProfessionalProfileUpdate {
  title?: string;
  description?: string | null;
  bio?: string | null;
  hourly_rate?: number | null;
}

export const professionalService = {
  async createProfile(data: ProfessionalProfileCreate): Promise<ProfessionalProfile> {
    const response = await apiClient.post<ProfessionalProfile>('/professionals', data);
    return response.data;
  },

  async getMyProfile(): Promise<ProfessionalProfile> {
    const response = await apiClient.get<ProfessionalProfile>('/professionals/me');
    return response.data;
  },

  async updateMyProfile(data: ProfessionalProfileUpdate): Promise<ProfessionalProfile> {
    const response = await apiClient.put<ProfessionalProfile>('/professionals/me', data);
    return response.data;
  },

  async getProfileById(id: string): Promise<ProfessionalProfile> {
    const response = await apiClient.get<ProfessionalProfile>(`/professionals/${id}`);
    return response.data;
  },

  // Social Links
  async addLink(professionalId: string, data: ProfessionalLinkCreate): Promise<ProfessionalLink> {
    const response = await apiClient.post<ProfessionalLink>(`/professionals/${professionalId}/links`, data);
    return response.data;
  },

  async updateLink(professionalId: string, linkId: string, data: ProfessionalLinkUpdate): Promise<ProfessionalLink> {
    const response = await apiClient.put<ProfessionalLink>(`/professionals/${professionalId}/links/${linkId}`, data);
    return response.data;
  },

  async deleteLink(professionalId: string, linkId: string): Promise<void> {
    await apiClient.delete(`/professionals/${professionalId}/links/${linkId}`);
  },
};
