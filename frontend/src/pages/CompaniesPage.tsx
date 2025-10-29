import { useEffect, useState } from 'react'
import { clientService, ClientProfile } from '@/services/clientService'

const CompaniesPage = () => {
  const [items, setItems] = useState<ClientProfile[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await clientService.list({ skip: 0, limit: 20 })
        setItems(data.items)
      } catch (e: any) {
        setError('Failed to load companies')
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
        <h1 className="text-3xl font-bold text-gray-900">Companies</h1>
        <p className="mt-2 text-gray-600">Browse companies posting projects</p>
      </div>

      {isLoading ? (
        <div className="text-gray-600">Loading...</div>
      ) : error ? (
        <div className="text-red-600">{error}</div>
      ) : items.length === 0 ? (
        <div className="card"><div className="card-content"><p className="text-gray-600">No companies available.</p></div></div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((c) => (
            <div key={c.id} className="card">
              <div className="card-content">
                <h3 className="text-lg font-semibold text-gray-900">{c.company_name || 'Company'}</h3>
                {c.business_sector && (
                  <p className="mt-2 text-gray-700 text-sm">Sector: {c.business_sector}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CompaniesPage


