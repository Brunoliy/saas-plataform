import apiClient from './api';

export interface Skill {
  id: string;
  name: string;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProfessionalSkill {
  id: string;
  professional_id: string;
  skill_id: string;
  proficiency_level: number;
  years_experience: number | null;
  certified: boolean;
  skill?: Skill;
}

export interface ProfessionalSkillCreate {
  skill_id: string;
  proficiency_level: number;
  years_experience?: number | null;
  certified?: boolean;
}

export interface ProfessionalSkillUpdate {
  proficiency_level?: number;
  years_experience?: number | null;
  certified?: boolean;
}

export const skillService = {
  // Get all available skills
  async listSkills(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    search?: string;
  }): Promise<{ items: Skill[]; total: number }> {
    const response = await apiClient.get('/skills', { params });
    return response.data;
  },

  // Get skill categories
  async getCategories(): Promise<string[]> {
    const response = await apiClient.get('/skills/categories');
    return response.data;
  },

  // Create new skill
  async createSkill(data: { name: string; category: string }): Promise<Skill> {
    const response = await apiClient.post('/skills', data);
    return response.data;
  },

  // Professional Skills Management
  async getProfessionalSkills(professionalId: string): Promise<ProfessionalSkill[]> {
    const response = await apiClient.get(`/professionals/${professionalId}/skills`);
    return response.data;
  },

  async addProfessionalSkill(
    professionalId: string,
    data: ProfessionalSkillCreate
  ): Promise<ProfessionalSkill> {
    const response = await apiClient.post(
      `/professionals/${professionalId}/skills`,
      data
    );
    return response.data;
  },

  async updateProfessionalSkill(
    professionalId: string,
    skillId: string,
    data: ProfessionalSkillUpdate
  ): Promise<ProfessionalSkill> {
    const response = await apiClient.put(
      `/professionals/${professionalId}/skills/${skillId}`,
      data
    );
    return response.data;
  },

  async deleteProfessionalSkill(
    professionalId: string,
    skillId: string
  ): Promise<void> {
    await apiClient.delete(`/professionals/${professionalId}/skills/${skillId}`);
  },
};
