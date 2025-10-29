import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { projectService } from '@/services/projectService'
import { reviewService } from '@/services/reviewService'
import { Project } from '@/types/project'
import { Review, ReviewCreate } from '@/types/review'
import { toast } from 'react-hot-toast'
import { ArrowLeft, Briefcase, Calendar, DollarSign, User } from 'lucide-react'
import ReviewForm from '@/components/ReviewForm'
import ReviewList from '@/components/ReviewList'

const ProjectDetailPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [project, setProject] = useState<Project | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingReviews, setIsLoadingReviews] = useState(true)
  const [showReviewForm, setShowReviewForm] = useState(false)

  useEffect(() => {
    if (id) {
      loadProject()
      loadReviews()
    }
  }, [id])

  const loadProject = async () => {
    try {
      setIsLoading(true)
      const data = await projectService.getProjectById(id!)
      setProject(data)
    } catch (error) {
      console.error('Failed to load project:', error)
      toast.error('Failed to load project')
      navigate('/projects')
    } finally {
      setIsLoading(false)
    }
  }

  const loadReviews = async () => {
    try {
      setIsLoadingReviews(true)
      const data = await reviewService.getReviews({ project_id: id!, limit: 100 })
      setReviews(data.items)
    } catch (error) {
      console.error('Failed to load reviews:', error)
    } finally {
      setIsLoadingReviews(false)
    }
  }

  const handleSubmitReview = async (reviewData: ReviewCreate) => {
    await reviewService.createReview(reviewData)
    setShowReviewForm(false)
    loadReviews()
  }

  const formatCurrency = (amount: number | null) => {
    if (!amount) return 'Not specified'
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(amount)
  }

  const formatDate = (date: string | null) => {
    if (!date) return 'Not set'
    return new Date(date).toLocaleDateString('pt-BR')
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      OPEN: 'bg-green-100 text-green-800',
      IN_PROGRESS: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    }
    return (
      <span className={`px-3 py-1 text-sm font-medium rounded-full ${badges[status]}`}>
        {status.replace('_', ' ')}
      </span>
    )
  }

  // Check if user can leave a review
  const canLeaveReview = () => {
    if (!project || !user) return false

    // Project must be completed
    if (project.status !== 'COMPLETED') return false

    // User must be either the client or the selected professional
    const isClient = project.client_id === user.id
    const isProfessional = project.selected_professional_id === user.id

    if (!isClient && !isProfessional) return false

    // Check if user already left a review
    const userAlreadyReviewed = reviews.some(r => r.reviewer_id === user.id)
    if (userAlreadyReviewed) return false

    return true
  }

  const getReviewType = (): 'professional_to_client' | 'client_to_professional' | null => {
    if (!project || !user) return null

    if (project.client_id === user.id) {
      return 'client_to_professional'
    } else if (project.selected_professional_id === user.id) {
      return 'professional_to_client'
    }

    return null
  }

  const getReviewedUserId = (): string | null => {
    if (!project || !user) return null

    if (project.client_id === user.id) {
      // Client is reviewing the professional
      return project.selected_professional_id
    } else if (project.selected_professional_id === user.id) {
      // Professional is reviewing the client
      return project.client_id
    }

    return null
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card">
          <div className="card-content">
            <p className="text-gray-600">Loading project...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card">
          <div className="card-content">
            <p className="text-gray-600">Project not found.</p>
          </div>
        </div>
      </div>
    )
  }

  const isOwner = user?.id === project.client_id

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <Link
        to="/projects"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Projects
      </Link>

      {/* Project Header */}
      <div className="card mb-6">
        <div className="card-header flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Briefcase className="w-6 h-6 text-gray-600" />
              <h1 className="text-3xl font-bold text-gray-900">{project.title}</h1>
            </div>
            {getStatusBadge(project.status)}
          </div>
          {isOwner && (
            <Link
              to={`/projects/${project.id}/edit`}
              className="btn btn-secondary btn-sm"
            >
              Edit Project
            </Link>
          )}
        </div>

        <div className="card-content space-y-4">
          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
            <p className="text-gray-900 whitespace-pre-wrap">{project.description}</p>
          </div>

          {/* Project Details */}
          <div className="grid md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
            {project.budget && (
              <div className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Budget</p>
                  <p className="font-semibold">{formatCurrency(project.budget)}</p>
                </div>
              </div>
            )}

            {project.deadline && (
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Deadline</p>
                  <p className="font-semibold">{formatDate(project.deadline)}</p>
                </div>
              </div>
            )}

            <div className="flex items-center gap-2">
              <User className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-sm text-gray-600">Created</p>
                <p className="font-semibold">{formatDate(project.created_at)}</p>
              </div>
            </div>

            {project.selected_professional_id && (
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="text-sm text-gray-600">Assigned Professional</p>
                  <p className="font-semibold">Assigned</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-900">Reviews</h2>
          {canLeaveReview() && !showReviewForm && (
            <button
              onClick={() => setShowReviewForm(true)}
              className="btn btn-primary btn-sm"
            >
              Leave a Review
            </button>
          )}
        </div>

        <div className="card-content">
          {/* Review Form */}
          {showReviewForm && canLeaveReview() && getReviewType() && getReviewedUserId() && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">
                {getReviewType() === 'client_to_professional'
                  ? 'Review the Professional'
                  : 'Review the Client'}
              </h3>
              <ReviewForm
                projectId={project.id}
                reviewedUserId={getReviewedUserId()!}
                reviewType={getReviewType()!}
                onSubmit={handleSubmitReview}
                onCancel={() => setShowReviewForm(false)}
              />
            </div>
          )}

          {/* Project must be completed for reviews */}
          {project.status !== 'COMPLETED' && reviews.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-600">
                Reviews will be available once this project is completed.
              </p>
            </div>
          )}

          {/* Review List */}
          <ReviewList reviews={reviews} isLoading={isLoadingReviews} />
        </div>
      </div>
    </div>
  )
}

export default ProjectDetailPage
