import { useAuthStore } from '@/stores/authStore'

const DashboardPage = () => {
  const { user } = useAuthStore()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.full_name}!
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Recent Projects</h3>
          </div>
          <div className="card-content">
            <p className="text-gray-600">No projects yet.</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Active Proposals</h3>
          </div>
          <div className="card-content">
            <p className="text-gray-600">No active proposals.</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Statistics</h3>
          </div>
          <div className="card-content">
            <p className="text-gray-600">No statistics available.</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage 