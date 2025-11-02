import { useEffect, useState, useCallback } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { professionalService, ProfessionalProfile } from '@/services/professionalService'
import { projectService } from '@/services/projectService'
import { proposalService } from '@/services/proposalService'
import { Project } from '@/types/project'
import { Proposal } from '@/types/proposal'
import StatCard from '@/components/StatCard'
import ProjectCard from '@/components/ProjectCard'
import ProposalCard from '@/components/ProposalCard'
import { Briefcase, FileText, TrendingUp, Star, Award } from 'lucide-react'
import { toast } from 'react-hot-toast'

interface DashboardStats {
  totalProjects: number
  activeProjects: number
  completedProjects: number
  totalProposals: number
  activeProposals: number
  acceptedProposals: number
  acceptanceRate: number
  averageRating: number
}

const DashboardPage = () => {
  const { user } = useAuthStore()
  const [professionalProfile, setProfessionalProfile] = useState<ProfessionalProfile | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboardData = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Fetch professional profile
      const profile = await professionalService.getMyProfile()
      setProfessionalProfile(profile)

      // Fetch projects and proposals in parallel
      const [projectsData, proposalsData] = await Promise.all([
        projectService.getProjectsByProfessional(profile.id),
        proposalService.getProposalsByProfessional(profile.id),
      ])

      setProjects(projectsData)
      setProposals(proposalsData)

      // Calculate statistics
      const calculatedStats = calculateStats(projectsData, proposalsData, profile)
      setStats(calculatedStats)

    } catch (error) {
      console.error('Failed to load dashboard data:', error)

      if (error && typeof error === 'object' && 'response' in error &&
          (error as { response?: { status?: number } }).response?.status === 404) {
        setError('Professional profile not found. Please create your profile first.')
      } else {
        setError('Failed to load dashboard data. Please try again.')
        toast.error('Failed to load dashboard data')
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (user?.account_type === 'professional') {
      loadDashboardData()
    } else {
      setIsLoading(false)
    }
  }, [user, loadDashboardData])

  const calculateStats = (
    projects: Project[],
    proposals: Proposal[],
    profile: ProfessionalProfile
  ): DashboardStats => {
    const activeProjects = projects.filter(p => p.status === 'IN_PROGRESS').length
    const completedProjects = projects.filter(p => p.status === 'COMPLETED').length
    const activeProposals = proposals.filter(p => p.status === 'SUBMITTED').length
    const acceptedProposals = proposals.filter(p => p.status === 'ACCEPTED').length

    const acceptanceRate = proposals.length > 0
      ? (acceptedProposals / proposals.length) * 100
      : 0

    return {
      totalProjects: projects.length,
      activeProjects,
      completedProjects,
      totalProposals: proposals.length,
      activeProposals,
      acceptedProposals,
      acceptanceRate,
      averageRating: profile.average_rating || 0,
    }
  }

  // Show message for non-professionals
  if (user?.account_type !== 'professional') {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
          <p className="text-gray-600">
            This dashboard is only available for professional accounts.
          </p>
        </div>
      </div>
    )
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md mx-auto">
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  const recentProjects = projects.slice(0, 3)
  const recentProposals = proposals.slice(0, 3)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.full_name}!
        </p>
      </div>

      {/* Statistics Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Projects"
            value={stats.totalProjects}
            icon={Briefcase}
            color="blue"
            description={`${stats.activeProjects} active`}
          />
          <StatCard
            title="Total Proposals"
            value={stats.totalProposals}
            icon={FileText}
            color="purple"
            description={`${stats.activeProposals} pending`}
          />
          <StatCard
            title="Acceptance Rate"
            value={`${stats.acceptanceRate.toFixed(0)}%`}
            icon={TrendingUp}
            color="green"
            description={`${stats.acceptedProposals} accepted`}
          />
          <StatCard
            title="Average Rating"
            value={stats.averageRating > 0 ? stats.averageRating.toFixed(1) : 'N/A'}
            icon={Star}
            color="orange"
            description={professionalProfile?.total_reviews ? `${professionalProfile.total_reviews} reviews` : 'No reviews yet'}
          />
        </div>
      )}

      {/* Projects and Proposals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Projects */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Recent Projects</h2>
            {projects.length > 3 && (
              <a href="/projects" className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </a>
            )}
          </div>

          <div className="space-y-4">
            {recentProjects.length > 0 ? (
              recentProjects.map(project => (
                <ProjectCard key={project.id} project={project} />
              ))
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No projects yet.</p>
                <p className="text-sm text-gray-500 mt-1">
                  Start applying to projects to see them here.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Proposals */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Recent Proposals</h2>
            {proposals.length > 3 && (
              <a href="/projects" className="text-sm text-primary-600 hover:text-primary-700">
                View all
              </a>
            )}
          </div>

          <div className="space-y-4">
            {recentProposals.length > 0 ? (
              recentProposals.map(proposal => (
                <ProposalCard key={proposal.id} proposal={proposal} />
              ))
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600">No proposals yet.</p>
                <p className="text-sm text-gray-500 mt-1">
                  Submit proposals to projects to see them here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Completed Projects Section */}
      {stats && stats.completedProjects > 0 && (
        <div className="mt-8">
          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
            <div className="flex items-center">
              <Award className="w-12 h-12 text-green-600 mr-4" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Great work! You've completed {stats.completedProjects} {stats.completedProjects === 1 ? 'project' : 'projects'}
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Keep up the excellent work and continue building your portfolio.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage 