import apiClient from './api'
import { Review, ReviewCreate, ReviewUpdate, ReviewType } from '@/types/review'

export interface PaginatedReviews {
  items: Review[]
  total: number
  page: number
  size: number
  pages: number
}

export interface UserRating {
  user_id: string
  average_rating: number
  total_reviews?: number
}

export const reviewService = {
  async createReview(data: ReviewCreate): Promise<Review> {
    const response = await apiClient.post<Review>('/reviews', data)
    return response.data
  },

  async getReviews(params?: {
    skip?: number
    limit?: number
    project_id?: string
    reviewer_id?: string
    reviewed_id?: string
    review_type?: ReviewType
  }): Promise<PaginatedReviews> {
    const queryParams = new URLSearchParams()
    if (params?.skip !== undefined) queryParams.append('skip', String(params.skip))
    if (params?.limit !== undefined) queryParams.append('limit', String(params.limit))
    if (params?.project_id) queryParams.append('project_id', params.project_id)
    if (params?.reviewer_id) queryParams.append('reviewer_id', params.reviewer_id)
    if (params?.reviewed_id) queryParams.append('reviewed_id', params.reviewed_id)
    if (params?.review_type) queryParams.append('review_type', params.review_type)

    const response = await apiClient.get<PaginatedReviews>(`/reviews?${queryParams.toString()}`)
    return response.data
  },

  async getReviewById(id: string): Promise<Review> {
    const response = await apiClient.get<Review>(`/reviews/${id}`)
    return response.data
  },

  async getUserRating(userId: string): Promise<UserRating> {
    const response = await apiClient.get<UserRating>(`/reviews/users/${userId}/rating`)
    return response.data
  },

  async updateReview(id: string, data: ReviewUpdate): Promise<Review> {
    const response = await apiClient.put<Review>(`/reviews/${id}`, data)
    return response.data
  },

  async deleteReview(id: string): Promise<void> {
    await apiClient.delete(`/reviews/${id}`)
  },
}
