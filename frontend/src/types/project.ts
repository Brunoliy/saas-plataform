export type ProjectStatus = 'OPEN' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'

export interface Project {
  id: string
  client_id: string
  client_user_id?: string | null  // User ID of the client who created the project
  title: string
  description: string
  budget: number | null
  deadline: string | null
  status: ProjectStatus
  selected_professional_id: string | null
  selected_professional_user_id?: string | null  // User ID of the selected professional
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  title: string
  description: string
  budget?: number | null
  deadline?: string | null
}

export interface ProjectUpdate {
  title?: string
  description?: string
  budget?: number | null
  deadline?: string | null
  status?: ProjectStatus
}

export interface ProjectFilters {
  status?: ProjectStatus
  client_id?: string
  professional_id?: string
  only_open?: boolean
  skip?: number
  limit?: number
}
