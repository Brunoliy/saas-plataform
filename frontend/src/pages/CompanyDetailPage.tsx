import { useEffect, useState, useCallback } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { clientService, ClientProfile } from '@/services/clientService'
import { projectService } from '@/services/projectService'
import { reviewService } from '@/services/reviewService'
import { Project } from '@/types/project'
import { Review, ReviewCreate } from '@/types/review'
import { toast } from 'react-hot-toast'
import { ArrowLeft, Star, Briefcase, Link as LinkIcon } from 'lucide-react'
import ReviewForm from '@/components/ReviewForm'
import ReviewList from '@/components/ReviewList'

const CompanyDetailPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [company, setCompany] = useState<ClientProfile | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [reviews, setReviews] = useState<Review[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingProjects, setIsLoadingProjects] = useState(true)
  const [isLoadingReviews, setIsLoadingReviews] = useState(true)
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)

  const loadCompany = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await clientService.getById(id!)
      setCompany(data)
    } catch (error) {
      console.error('Failed to load company:', error)
      toast.error('Failed to load company profile')
      navigate('/companies')
    } finally {
      setIsLoading(false)
    }
  }, [id, navigate])

  const loadProjects = useCallback(async () => {
    try {
      setIsLoadingProjects(true)
      const data = await projectService.getProjects({
        client_id: id!,
        limit: 100,
      })
      setProjects(data.items)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setIsLoadingProjects(false)
    }
  }, [id])

  const loadReviews = useCallback(async () => {
    try {
      setIsLoadingReviews(true)
      // Get reviews for company (where they were reviewed)
      const data = await reviewService.getReviews({
        reviewed_id: company?.user_id || id!,
        limit: 100,
      })
      setReviews(data.items)
    } catch (error) {
      console.error('Failed to load reviews:', error)
    } finally {
      setIsLoadingReviews(false)
    }
  }, [id, company])

  useEffect(() => {
    if (id) {
      loadCompany()
      loadProjects()
      loadReviews()
    }
  }, [id, loadCompany, loadProjects, loadReviews])

  const handleSubmitReview = async (reviewData: ReviewCreate) => {
    await reviewService.createReview(reviewData)
    setShowReviewForm(false)
    setSelectedProject(null)
    loadReviews()
    toast.success('Review submitted successfully!')
  }

  const canReviewCompany = (project: Project) => {
    if (!user || !company) return false

    // Must be completed
    if (project.status !== 'COMPLETED') return false

    // User must be the selected professional
    if (project.selected_professional_id !== user.id) return false

    // Check if already reviewed
    const alreadyReviewed = reviews.some(r => r.project_id === project.id && r.reviewer_id === user.id)
    return !alreadyReviewed
  }

  const handleReviewClick = (project: Project) => {
    setSelectedProject(project)
    setShowReviewForm(true)
  }

  const formatCurrency = (amount: number | null | undefined) => {
    if (!amount) return 'Not specified'
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(Number(amount))
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

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card">
          <div className="card-content">
            <p className="text-gray-600">Loading company profile...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!company) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card">
          <div className="card-content">
            <p className="text-gray-600">Company not found.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <Link
        to="/companies"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Companies
      </Link>

      {/* Company Header */}
      <div className="card mb-6">
        <div className="card-content">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-500 to-blue-600 flex items-center justify-center text-white text-2xl font-bold">
                {(company.company_name || 'C').charAt(0).toUpperCase()}
              </div>
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {company.company_name || 'Company'}
              </h1>

              {company.business_sector && (
                <p className="text-gray-600 mb-2">
                  <span className="font-medium">Sector:</span> {company.business_sector}
                </p>
              )}

              {company.description && (
                <p className="text-gray-700 mb-4">{company.description}</p>
              )}

              {company.bio && company.bio !== company.description && (
                <p className="text-gray-700 mb-4">{company.bio}</p>
              )}

              <div className="flex flex-wrap gap-4 text-sm">
                {company.average_rating && (
                  <div className="flex items-center gap-1 text-gray-600">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span>{Number(company.average_rating).toFixed(1)} ({company.total_reviews} reviews)</span>
                  </div>
                )}
              </div>

              {/* Links */}
              {company.links && company.links.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Links</h3>
                  <div className="flex flex-wrap gap-2">
                    {company.links.map((link) => (
                      <a
                        key={link.id}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                      >
                        <LinkIcon className="w-4 h-4" />
                        {link.label || link.platform}
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Projects Section */}
      <div className="card mb-6">
        <div className="card-header">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Briefcase className="w-5 h-5" />
            Projects
          </h2>
        </div>
        <div className="card-content">
          {isLoadingProjects ? (
            <p className="text-gray-600">Loading projects...</p>
          ) : projects.length === 0 ? (
            <p className="text-gray-600">No projects yet.</p>
          ) : (
            <div className="space-y-4">
              {projects.map((project) => (
                <div key={project.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all duration-200">
                  <div className="flex justify-between items-start mb-3">
                    <Link
                      to={`/projects/${project.id}`}
                      className="flex-1 group"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {project.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">{project.description}</p>
                      {project.budget && (
                        <p className="text-sm text-gray-600 mt-2">
                          Budget: {formatCurrency(project.budget)}
                        </p>
                      )}
                    </Link>
                    <div className="flex flex-col items-end gap-2 ml-4">
                      {getStatusBadge(project.status)}
                      {canReviewCompany(project) && (
                        <button
                          onClick={(e) => {
                            e.preventDefault()
                            e.stopPropagation()
                            handleReviewClick(project)
                          }}
                          className="btn btn-primary btn-sm whitespace-nowrap"
                        >
                          Leave Review
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Reviews Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-bold text-gray-900">Reviews</h2>
        </div>
        <div className="card-content">
          {/* Review Form */}
          {showReviewForm && selectedProject && company.user_id && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Review this Company</h3>
              <p className="text-sm text-gray-600 mb-4">
                Project: {selectedProject.title}
              </p>
              <ReviewForm
                projectId={selectedProject.id}
                reviewedUserId={company.user_id}
                reviewType="professional_to_client"
                onSubmit={handleSubmitReview}
                onCancel={() => {
                  setShowReviewForm(false)
                  setSelectedProject(null)
                }}
              />
            </div>
          )}

          {/* Review List */}
          <ReviewList reviews={reviews} isLoading={isLoadingReviews} />
        </div>
      </div>
    </div>
  )
}

export default CompanyDetailPage
