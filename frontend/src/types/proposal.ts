export type ProposalStatus = 'SUBMITTED' | 'ACCEPTED' | 'REJECTED'

export interface Proposal {
  id: string
  project_id: string
  professional_id: string
  proposed_amount: number
  estimated_days: number | null
  description: string
  status: ProposalStatus
  ai_score: number | null
  created_at: string
  updated_at: string
  project?: {
    id: string
    title: string
    status: string
  }
}

export interface ProposalCreate {
  project_id: string
  proposed_amount: number
  estimated_days?: number | null
  description: string
}

export interface ProposalUpdate {
  proposed_amount?: number
  estimated_days?: number | null
  description?: string
}

export interface ProposalFilters {
  project_id?: string
  professional_id?: string
  status_filter?: ProposalStatus
  skip?: number
  limit?: number
}
