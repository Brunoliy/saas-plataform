import { useParams } from 'react-router-dom'

const ProjectDetailPage = () => {
  const { id } = useParams()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Project Details</h1>
        <p className="mt-2 text-gray-600">
          Project ID: {id}
        </p>
      </div>

      <div className="card">
        <div className="card-content">
          <p className="text-gray-600">Project details not available.</p>
        </div>
      </div>
    </div>
  )
}

export default ProjectDetailPage 