import { Link } from 'react-router-dom'
import { DollarSign, Clock, FileText, Star } from 'lucide-react'
import { Proposal } from '@/types/proposal'

interface ProposalCardProps {
  proposal: Proposal
}

const statusColors = {
  SUBMITTED: 'bg-blue-100 text-blue-800',
  ACCEPTED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
}

const statusLabels = {
  SUBMITTED: 'Submitted',
  ACCEPTED: 'Accepted',
  REJECTED: 'Rejected',
}

export default function ProposalCard({ proposal }: ProposalCardProps) {
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  return (
    <Link
      to={`/projects/${proposal.project_id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
            {proposal.project?.title || `Project ${proposal.project_id.slice(0, 8)}...`}
          </h3>
          <p className="text-xs text-gray-500 mt-1">Submitted {formatDate(proposal.created_at)}</p>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[proposal.status]}`}>
          {statusLabels[proposal.status]}
        </span>
      </div>

      <p className="text-sm text-gray-600 mb-4 line-clamp-2">{proposal.description}</p>

      <div className="space-y-2">
        <div className="flex items-center text-sm text-gray-700 font-medium">
          <DollarSign className="w-4 h-4 mr-2 text-green-600" />
          <span>{formatAmount(proposal.proposed_amount)}</span>
        </div>

        {proposal.estimated_days && (
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="w-4 h-4 mr-2" />
            <span>{proposal.estimated_days} days</span>
          </div>
        )}

        {proposal.ai_score !== null && (
          <div className="flex items-center text-sm text-gray-500">
            <Star className="w-4 h-4 mr-2 text-yellow-500" />
            <span>AI Score: {proposal.ai_score.toFixed(1)}</span>
          </div>
        )}

        <div className="flex items-center text-sm text-gray-500">
          <FileText className="w-4 h-4 mr-2" />
          <span>Proposal ID: {proposal.id.slice(0, 8)}...</span>
        </div>
      </div>
    </Link>
  )
}
