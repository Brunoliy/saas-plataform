import apiClient from './api'
import { Project, ProjectCreate, ProjectUpdate, ProjectFilters } from '@/types/project'

export interface PaginatedProjects {
  items: Project[]
  total: number
  page: number
  size: number
  pages: number
}

export const projectService = {
  async getProjects(filters?: ProjectFilters): Promise<PaginatedProjects> {
    const params = new URLSearchParams()

    // Backend expects 'status_filter' not 'status'
    if (filters?.status) params.append('status_filter', filters.status)
    if (filters?.client_id) params.append('client_id', filters.client_id)
    if (filters?.professional_id) params.append('professional_id', filters.professional_id)
    if (filters?.only_open !== undefined) params.append('only_open', String(filters.only_open))
    if (filters?.skip !== undefined) params.append('skip', String(filters.skip))
    if (filters?.limit !== undefined) params.append('limit', String(filters.limit))

    const response = await apiClient.get<PaginatedProjects>(`/projects?${params.toString()}`)
    return response.data
  },

  async getProjectById(id: string): Promise<Project> {
    const response = await apiClient.get<Project>(`/projects/${id}`)
    return response.data
  },

  async getProjectsByProfessional(professionalId: string, status?: string): Promise<Project[]> {
    const filters: ProjectFilters = {
      professional_id: professionalId,
      limit: 100,
    }

    const response = await this.getProjects(filters)

    // Filter by status if provided
    if (status) {
      return response.items.filter(p => p.status === status)
    }

    return response.items
  },

  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await apiClient.post<Project>('/projects', data)
    return response.data
  },

  async updateProject(id: string, data: ProjectUpdate): Promise<Project> {
    const response = await apiClient.put<Project>(`/projects/${id}`, data)
    return response.data
  },

  async deleteProject(id: string): Promise<void> {
    await apiClient.delete(`/projects/${id}`)
  },

  async completeProject(id: string): Promise<Project> {
    const response = await apiClient.patch<Project>(`/projects/${id}/complete`)
    return response.data
  },

  async cancelProject(id: string): Promise<Project> {
    const response = await apiClient.patch<Project>(`/projects/${id}/cancel`)
    return response.data
  },
}
