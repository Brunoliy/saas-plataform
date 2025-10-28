import apiClient from './api';

export interface ProfessionalProfile {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  bio: string | null;
  hourly_rate: number | null;
  average_rating: number | null;
  total_reviews: number;
  created_at: string;
  updated_at: string;
}

export interface ProfessionalProfileUpdate {
  title?: string;
  description?: string | null;
  bio?: string | null;
  hourly_rate?: number | null;
}

export const professionalService = {
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
};
