import { Link } from 'react-router-dom'
import { Calendar, DollarSign, Briefcase } from 'lucide-react'
import { Project } from '@/types/project'

interface ProjectCardProps {
  project: Project
}

const statusColors = {
  OPEN: 'bg-blue-100 text-blue-800',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
  COMPLETED: 'bg-green-100 text-green-800',
  CANCELLED: 'bg-red-100 text-red-800',
}

const statusLabels = {
  OPEN: 'Open',
  IN_PROGRESS: 'In Progress',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
}

export default function ProjectCard({ project }: ProjectCardProps) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No deadline'
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const formatBudget = (budget: number | null) => {
    if (!budget) return 'Not specified'
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(budget)
  }

  return (
    <Link
      to={`/projects/${project.id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">{project.title}</h3>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[project.status]}`}>
          {statusLabels[project.status]}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4 line-clamp-2">{project.description}</p>

      <div className="space-y-2">
        <div className="flex items-center text-sm text-gray-500">
          <DollarSign className="w-4 h-4 mr-2" />
          <span>{formatBudget(project.budget)}</span>
        </div>

        <div className="flex items-center text-sm text-gray-500">
          <Calendar className="w-4 h-4 mr-2" />
          <span>{formatDate(project.deadline)}</span>
        </div>

        <div className="flex items-center text-sm text-gray-500">
          <Briefcase className="w-4 h-4 mr-2" />
          <span>Project ID: {project.id.slice(0, 8)}...</span>
        </div>
      </div>
    </Link>
  )
}
