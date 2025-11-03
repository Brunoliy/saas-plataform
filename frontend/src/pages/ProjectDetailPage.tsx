import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { projectService } from '@/services/projectService'
import { reviewService } from '@/services/reviewService'
import { proposalService } from '@/services/proposalService'
import { professionalService } from '@/services/professionalService'
import { Project } from '@/types/project'
import { Review, ReviewCreate } from '@/types/review'
import { toast } from 'react-hot-toast'
import { ArrowLeft, Briefcase, Calendar, DollarSign, User, Send } from 'lucide-react'
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
  const [showProposalForm, setShowProposalForm] = useState(false)
  const [proposalDescription, setProposalDescription] = useState('')
  const [proposalAmount, setProposalAmount] = useState('')
  const [proposalDays, setProposalDays] = useState('')
  const [isSubmittingProposal, setIsSubmittingProposal] = useState(false)
  const [hasApplied, setHasApplied] = useState(false)

  const checkIfApplied = useCallback(async () => {
    if (!user || !id) return

    try {
      const professionalProfile = await professionalService.getMyProfile()
      if (professionalProfile) {
        const proposals = await proposalService.getProposals({
          project_id: id,
          professional_id: professionalProfile.id,
          limit: 1,
        })
        setHasApplied(proposals.items.length > 0)
      }
    } catch (error) {
      // User might not have a professional profile
      console.log('Could not check proposal status:', error)
    }
  }, [id, user])

  const loadProject = useCallback(async () => {
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
  }, [id, navigate])

  const loadReviews = useCallback(async () => {
    try {
      setIsLoadingReviews(true)
      const data = await reviewService.getReviews({ project_id: id!, limit: 100 })
      setReviews(data.items)
    } catch (error) {
      console.error('Failed to load reviews:', error)
    } finally {
      setIsLoadingReviews(false)
    }
  }, [id])

  useEffect(() => {
    if (id) {
      loadProject()
      loadReviews()
      checkIfApplied()
    }
  }, [id, loadProject, loadReviews, checkIfApplied])

  const handleSubmitReview = async (reviewData: ReviewCreate) => {
    await reviewService.createReview(reviewData)
    setShowReviewForm(false)
    loadReviews()
  }

  const handleSubmitProposal = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!proposalAmount || !proposalDescription) {
      toast.error('Please fill in all required fields')
      return
    }

    try {
      setIsSubmittingProposal(true)
      await proposalService.createProposal({
        project_id: id!,
        proposed_amount: Number(proposalAmount),
        estimated_days: proposalDays ? Number(proposalDays) : undefined,
        description: proposalDescription,
      })

      toast.success('Proposal submitted successfully!')
      setShowProposalForm(false)
      setProposalDescription('')
      setProposalAmount('')
      setProposalDays('')
      setHasApplied(true)
    } catch (error) {
      console.error('Failed to submit proposal:', error)
      const errorMessage = (error && typeof error === 'object' && 'response' in error &&
        (error as { response?: { data?: { detail?: string } } }).response?.data?.detail) ||
        'Failed to submit proposal'
      toast.error(String(errorMessage))
    } finally {
      setIsSubmittingProposal(false)
    }
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

  // Check if professional can apply to project
  const canApplyToProject = () => {
    if (!project || !user) return false

    // Project must be OPEN
    if (project.status !== 'OPEN') return false

    // User must not be the project owner
    if (project.client_user_id === user.id) return false

    // User must not have already applied
    if (hasApplied) return false

    return true
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

      {/* Apply to Project Section */}
      {canApplyToProject() && (
        <div className="card mb-6">
          <div className="card-header">
            <h2 className="text-xl font-bold text-gray-900">Apply to this Project</h2>
          </div>
          <div className="card-content">
            {!showProposalForm ? (
              <div className="text-center py-4">
                <p className="text-gray-600 mb-4">
                  Interested in this project? Submit a proposal to get started!
                </p>
                <button
                  onClick={() => setShowProposalForm(true)}
                  className="btn btn-primary inline-flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Submit Proposal
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmitProposal} className="space-y-4">
                <div>
                  <label htmlFor="proposalAmount" className="block text-sm font-medium text-gray-700 mb-1">
                    Proposed Amount (BRL) <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="proposalAmount"
                    type="number"
                    step="0.01"
                    min="0"
                    value={proposalAmount}
                    onChange={(e) => setProposalAmount(e.target.value)}
                    className="input"
                    placeholder="10000.00"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="proposalDays" className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Days
                  </label>
                  <input
                    id="proposalDays"
                    type="number"
                    min="1"
                    value={proposalDays}
                    onChange={(e) => setProposalDays(e.target.value)}
                    className="input"
                    placeholder="30"
                  />
                </div>

                <div>
                  <label htmlFor="proposalDescription" className="block text-sm font-medium text-gray-700 mb-1">
                    Proposal Description <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="proposalDescription"
                    value={proposalDescription}
                    onChange={(e) => setProposalDescription(e.target.value)}
                    rows={6}
                    className="input"
                    placeholder="Explain your approach to this project, relevant experience, and why you're the best fit..."
                    required
                    maxLength={2000}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {proposalDescription.length}/2000 characters
                  </p>
                </div>

                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={isSubmittingProposal}
                    className="btn btn-primary flex-1"
                  >
                    {isSubmittingProposal ? 'Submitting...' : 'Submit Proposal'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowProposalForm(false)
                      setProposalDescription('')
                      setProposalAmount('')
                      setProposalDays('')
                    }}
                    disabled={isSubmittingProposal}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {hasApplied && !canApplyToProject() && project.status === 'OPEN' && (
        <div className="card mb-6">
          <div className="card-content">
            <div className="text-center py-4">
              <p className="text-green-600 font-medium">
                You have already submitted a proposal for this project
              </p>
              <p className="text-sm text-gray-600 mt-1">
                The client will review your proposal and get back to you.
              </p>
            </div>
          </div>
        </div>
      )}

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
