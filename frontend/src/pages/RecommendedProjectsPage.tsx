import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-hot-toast'
import recommendationService, { Recommendation } from '@/services/recommendationService'
import { Sparkles, TrendingUp, AlertCircle, DollarSign, Calendar, MessageCircle } from 'lucide-react'

const RecommendedProjectsPage = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showChat, setShowChat] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setIsLoading(true)
      const data = await recommendationService.getRecommendedProjects(10)
      setRecommendations(data.recommendations)
    } catch (error) {
      console.error('Failed to load recommendations:', error)
      toast.error('Failed to load recommended projects')
    } finally {
      setIsLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 65) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (score >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-gray-600 bg-gray-50 border-gray-200'
  }

  const getScoreBadge = (score: number) => {
    if (score >= 80) return { text: 'Excellent Match', color: 'bg-green-500' }
    if (score >= 65) return { text: 'Good Match', color: 'bg-blue-500' }
    if (score >= 50) return { text: 'Moderate Match', color: 'bg-yellow-500' }
    return { text: 'Low Match', color: 'bg-gray-500' }
  }

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-8 w-8 text-purple-600" />
              <h1 className="text-3xl font-bold text-gray-900">AI Recommended Projects</h1>
            </div>
            <p className="text-gray-600">
              Projects matched to your skills and experience using our AI algorithm
            </p>
          </div>
          <button
            onClick={() => setShowChat(!showChat)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <MessageCircle className="h-5 w-5" />
            Ask AI
          </button>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length === 0 ? (
        <div className="card">
          <div className="card-content text-center py-12">
            <Sparkles className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No recommendations yet</h3>
            <p className="text-gray-600 mb-4">
              Complete your profile and add skills to get personalized project recommendations!
            </p>
            <button
              onClick={() => navigate('/profile')}
              className="btn btn-primary"
            >
              Complete Profile
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {recommendations.map((rec, index) => {
            const scoreBadge = getScoreBadge(rec.compatibility_score)
            const positiveFactors = rec.positive_factors ? Object.values(rec.positive_factors) : []
            const negativeFactors = rec.negative_factors ? Object.values(rec.negative_factors) : []

            return (
              <div
                key={rec.project_id || index}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className="card-content">
                  {/* Header with Score */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold text-gray-900">
                          {rec.project_title || 'Untitled Project'}
                        </h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium text-white ${scoreBadge.color}`}>
                          {scoreBadge.text}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{rec.recommendation}</p>
                    </div>
                    <div className={`ml-4 px-4 py-3 rounded-lg border-2 ${getScoreColor(rec.compatibility_score)}`}>
                      <div className="text-center">
                        <div className="text-3xl font-bold">
                          {rec.compatibility_score.toFixed(0)}%
                        </div>
                        <div className="text-xs font-medium mt-1">Match</div>
                      </div>
                    </div>
                  </div>

                  {/* Project Details */}
                  <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
                    {rec.budget && (
                      <div className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        ${rec.budget.toLocaleString()}
                      </div>
                    )}
                    {rec.deadline && (
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Due: {new Date(rec.deadline).toLocaleDateString()}
                      </div>
                    )}
                  </div>

                  {/* Positive Factors */}
                  {positiveFactors.length > 0 && (
                    <div className="mb-3">
                      <div className="flex items-center gap-2 text-green-700 font-medium mb-2 text-sm">
                        <TrendingUp className="h-4 w-4" />
                        Why it's a great match:
                      </div>
                      <ul className="space-y-1">
                        {positiveFactors.slice(0, 3).map((factor, i) => (
                          <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="text-green-500 mt-0.5">✓</span>
                            <span>{factor}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Negative Factors */}
                  {negativeFactors.length > 0 && (
                    <div className="mb-4">
                      <div className="flex items-center gap-2 text-orange-700 font-medium mb-2 text-sm">
                        <AlertCircle className="h-4 w-4" />
                        Things to consider:
                      </div>
                      <ul className="space-y-1">
                        {negativeFactors.slice(0, 2).map((factor, i) => (
                          <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="text-orange-500 mt-0.5">!</span>
                            <span>{factor}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => navigate(`/projects/${rec.project_id}`)}
                      className="btn btn-primary flex-1"
                    >
                      View Project & Apply
                    </button>
                    <button
                      onClick={() => {
                        // TODO: Open chat with context about this project
                        setShowChat(true)
                      }}
                      className="btn btn-secondary"
                    >
                      <MessageCircle className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Chat Sidebar (placeholder) */}
      {showChat && (
        <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold">AI Assistant</h3>
            <button onClick={() => setShowChat(false)} className="text-gray-500 hover:text-gray-700">
              ✕
            </button>
          </div>
          <p className="text-sm text-gray-600">Chat component coming soon...</p>
        </div>
      )}
    </div>
  )
}

export default RecommendedProjectsPage
