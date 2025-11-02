import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { professionalService, ProfessionalProfile } from '@/services/professionalService'

const ProfessionalsPage = () => {
  const [items, setItems] = useState<ProfessionalProfile[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await professionalService.list({ skip: 0, limit: 20 })
        setItems(data.items)
      } catch (e) {
        setError('Failed to load professionals')
        console.error(e)
      } finally {
        setIsLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Professionals</h1>
        <p className="mt-2 text-gray-600">Find the perfect professional for your project</p>
      </div>

      {isLoading ? (
        <div className="text-gray-600">Loading...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : items.length === 0 ? (
        <div className="card"><div className="card-content"><p className="text-gray-600">No professionals available.</p></div></div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((p) => (
            <Link key={p.id} to={`/professionals/${p.id}`} className="card hover:shadow-lg transition-shadow">
              <div className="card-content">
                <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors">{p.title}</h3>
                {p.bio && <p className="mt-2 text-gray-700 line-clamp-3">{p.bio}</p>}
                <div className="mt-3 flex items-center justify-between text-sm">
                  {p.hourly_rate != null && (
                    <p className="text-gray-600">R$ {Number(p.hourly_rate).toFixed(2)}/hour</p>
                  )}
                  {p.average_rating != null && (
                    <p className="text-yellow-600 font-medium">
                      ⭐ {Number(p.average_rating).toFixed(1)}
                    </p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProfessionalsPage 