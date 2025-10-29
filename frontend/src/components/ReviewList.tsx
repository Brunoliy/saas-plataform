import { Star } from 'lucide-react'
import { Review } from '@/types/review'

interface ReviewListProps {
  reviews: Review[]
  isLoading?: boolean
}

export default function ReviewList({ reviews, isLoading }: ReviewListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  if (reviews.length === 0) {
    return (
      <div className="text-center py-8">
        <Star className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">No reviews yet</p>
        <p className="text-sm text-gray-500 mt-1">
          Be the first to leave a review!
        </p>
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return 'text-green-600'
    if (rating >= 3) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <div key={review.id} className="border border-gray-200 rounded-lg p-4">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`w-5 h-5 ${
                    star <= review.rating
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              ))}
              <span className={`ml-2 font-semibold ${getRatingColor(review.rating)}`}>
                {review.rating}.0
              </span>
            </div>
            <span className="text-xs text-gray-500">
              {formatDate(review.created_at)}
            </span>
          </div>

          {review.comment && (
            <p className="text-sm text-gray-700 mt-2 whitespace-pre-wrap">
              {review.comment}
            </p>
          )}

          <div className="mt-3 pt-3 border-t border-gray-100">
            <span className="text-xs text-gray-500 capitalize">
              {review.review_type.replace('_', ' ')}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
