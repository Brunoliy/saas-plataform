import apiClient from './api'
import { Proposal, ProposalCreate, ProposalUpdate, ProposalFilters } from '@/types/proposal'

export interface PaginatedProposals {
  items: Proposal[]
  total: number
  page: number
  size: number
  pages: number
}

export const proposalService = {
  async getProposals(filters?: ProposalFilters): Promise<PaginatedProposals> {
    const params = new URLSearchParams()

    if (filters?.project_id) params.append('project_id', filters.project_id)
    if (filters?.professional_id) params.append('professional_id', filters.professional_id)
    if (filters?.status_filter) params.append('status_filter', filters.status_filter)
    if (filters?.skip !== undefined) params.append('skip', String(filters.skip))
    if (filters?.limit !== undefined) params.append('limit', String(filters.limit))

    const response = await apiClient.get<PaginatedProposals>(`/proposals?${params.toString()}`)
    return response.data
  },

  async getProposalById(id: string): Promise<Proposal> {
    const response = await apiClient.get<Proposal>(`/proposals/${id}`)
    return response.data
  },

  async getProposalsByProfessional(professionalId: string, status?: string): Promise<Proposal[]> {
    const filters: ProposalFilters = {
      professional_id: professionalId,
      limit: 100,
    }

    if (status) {
      filters.status_filter = status as 'SUBMITTED' | 'ACCEPTED' | 'REJECTED'
    }

    const response = await this.getProposals(filters)
    return response.items
  },

  async createProposal(data: ProposalCreate): Promise<Proposal> {
    const response = await apiClient.post<Proposal>('/proposals', data)
    return response.data
  },

  async updateProposal(id: string, data: ProposalUpdate): Promise<Proposal> {
    const response = await apiClient.put<Proposal>(`/proposals/${id}`, data)
    return response.data
  },

  async deleteProposal(id: string): Promise<void> {
    await apiClient.delete(`/proposals/${id}`)
  },

  async acceptProposal(id: string): Promise<Proposal> {
    const response = await apiClient.post<Proposal>(`/proposals/${id}/accept`)
    return response.data
  },

  async rejectProposal(id: string): Promise<Proposal> {
    const response = await apiClient.post<Proposal>(`/proposals/${id}/reject`)
    return response.data
  },
}
