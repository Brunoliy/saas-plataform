import { useState } from 'react'
import { Star } from 'lucide-react'
import { ReviewCreate } from '@/types/review'
import { toast } from 'react-hot-toast'

interface ReviewFormProps {
  projectId: string
  reviewedUserId: string
  reviewType: 'professional_to_client' | 'client_to_professional'
  onSubmit: (data: ReviewCreate) => Promise<void>
  onCancel?: () => void
}

export default function ReviewForm({
  projectId,
  reviewedUserId,
  reviewType,
  onSubmit,
  onCancel,
}: ReviewFormProps) {
  const [rating, setRating] = useState(0)
  const [hover, setHover] = useState(0)
  const [comment, setComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (rating === 0) {
      toast.error('Please select a rating')
      return
    }

    try {
      setIsSubmitting(true)
      await onSubmit({
        project_id: projectId,
        reviewed_id: reviewedUserId,
        rating,
        comment: comment.trim() || null,
        review_type: reviewType,
      })

      // Reset form
      setRating(0)
      setComment('')
      toast.success('Review submitted successfully!')
    } catch (error) {
      console.error('Failed to submit review:', error)
      toast.error('Failed to submit review')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Rating <span className="text-red-500">*</span>
        </label>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHover(star)}
              onMouseLeave={() => setHover(0)}
              className="p-1 transition-transform hover:scale-110"
            >
              <Star
                className={`w-8 h-8 ${
                  star <= (hover || rating)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
        </div>
        {rating > 0 && (
          <p className="text-sm text-gray-600 mt-1">
            {rating === 1 && 'Poor'}
            {rating === 2 && 'Fair'}
            {rating === 3 && 'Good'}
            {rating === 4 && 'Very Good'}
            {rating === 5 && 'Excellent'}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="comment" className="block text-sm font-medium text-gray-700 mb-1">
          Comment (Optional)
        </label>
        <textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={4}
          className="input"
          placeholder="Share your experience working on this project..."
          maxLength={1000}
        />
        <p className="text-xs text-gray-500 mt-1">
          {comment.length}/1000 characters
        </p>
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isSubmitting || rating === 0}
          className="btn btn-primary flex-1"
        >
          {isSubmitting ? 'Submitting...' : 'Submit Review'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="btn btn-secondary"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
