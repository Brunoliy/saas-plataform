import apiClient from './api'

export interface Recommendation {
  professional_id?: string
  professional_name?: string
  project_id?: string
  project_title?: string
  compatibility_score: number
  recommendation: string
  positive_factors?: Record<string, string>
  negative_factors?: Record<string, string>
  average_rating?: number
  total_reviews?: number
  budget?: number
  deadline?: string
}

export interface RecommendationsResponse {
  recommendations: Recommendation[]
  total: number
  message?: string
}

export interface ChatRequest {
  message: string
  context?: Record<string, unknown>
  user_type?: 'professional' | 'client'
}

export interface ChatResponse {
  response: string
  suggestions: string[]
  data?: Record<string, unknown>
}

const recommendationService = {
  // Get recommended projects for current professional
  async getRecommendedProjects(limit = 10): Promise<RecommendationsResponse> {
    const response = await apiClient.get<RecommendationsResponse>(
      `/recommendations/me/recommended-projects?limit=${limit}`
    )
    return response.data
  },

  // Get recommended professionals for a project
  async getRecommendedProfessionals(
    projectId: string,
    limit = 10
  ): Promise<RecommendationsResponse> {
    const response = await apiClient.get<RecommendationsResponse>(
      `/recommendations/projects/${projectId}/recommendations?limit=${limit}`
    )
    return response.data
  },

  // Get recommended projects for a professional
  async getProjectsForProfessional(
    professionalId: string,
    limit = 10
  ): Promise<RecommendationsResponse> {
    const response = await apiClient.get<RecommendationsResponse>(
      `/recommendations/professionals/${professionalId}/recommendations?limit=${limit}`
    )
    return response.data
  },

  // Calculate compatibility between project and professional
  async calculateCompatibility(
    projectId: string,
    professionalId: string
  ): Promise<{
    compatibility_score: number
    recommendation: string
    analysis: Record<string, unknown>
  }> {
    const response = await apiClient.get(
      `/recommendations/compatibility/${projectId}/${professionalId}`
    )
    return response.data
  },

  // Chat with AI
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/recommendations/chat', request)
    return response.data
  },
}

export default recommendationService
