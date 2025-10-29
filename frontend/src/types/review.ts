export type ReviewType = 'professional_to_client' | 'client_to_professional'

export interface Review {
  id: string
  project_id: string
  reviewer_id: string
  reviewed_id: string
  rating: number
  comment: string | null
  review_type: ReviewType
  created_at: string
  updated_at: string
}

export interface ReviewCreate {
  project_id: string
  reviewed_id: string
  rating: number
  comment?: string | null
  review_type: ReviewType
}

export interface ReviewUpdate {
  rating?: number
  comment?: string | null
}
