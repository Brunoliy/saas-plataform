import { Link } from 'react-router-dom'
import { X } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

interface MobileMenuProps {
  isOpen: boolean
  onClose: () => void
}

const MobileMenu = ({ isOpen, onClose }: MobileMenuProps) => {
  const { isAuthenticated, user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    onClose()
  }

  const handleLinkClick = () => {
    onClose()
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
        onClick={onClose}
      />

      {/* Menu */}
      <div className="fixed top-0 right-0 bottom-0 w-64 bg-white shadow-xl z-50 md:hidden transform transition-transform duration-300 ease-in-out">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <span className="text-lg font-bold text-primary-600">Menu</span>
            <button
              onClick={onClose}
              className="p-2 rounded-md text-gray-600 hover:bg-gray-100"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-4">
            <div className="space-y-1 px-3">
              <Link
                to="/"
                onClick={handleLinkClick}
                className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
              >
                Home
              </Link>

              {isAuthenticated && (
                <>
                  <Link
                    to="/dashboard"
                    onClick={handleLinkClick}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/projects"
                    onClick={handleLinkClick}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                  >
                    Projects
                  </Link>
                  <Link
                    to="/professionals"
                    onClick={handleLinkClick}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                  >
                    Professionals
                  </Link>
                  {user?.account_type === 'professional' && (
                    <Link
                      to="/recommended-projects"
                      onClick={handleLinkClick}
                      className="block px-3 py-2 rounded-md text-base font-medium text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                    >
                      ✨ AI Recommendations
                    </Link>
                  )}
                  <Link
                    to="/companies"
                    onClick={handleLinkClick}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                  >
                    Companies
                  </Link>
                  {user?.account_type === 'admin' && (
                    <Link
                      to="/users"
                      onClick={handleLinkClick}
                      className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                    >
                      Users
                    </Link>
                  )}
                  <Link
                    to="/profile"
                    onClick={handleLinkClick}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-primary-600 hover:bg-gray-50"
                  >
                    Profile
                  </Link>
                </>
              )}
            </div>
          </nav>

          {/* Footer Actions */}
          <div className="border-t border-gray-200 p-4 space-y-2">
            {isAuthenticated ? (
              <>
                {user && (
                  <div className="px-3 py-2 mb-2">
                    <p className="text-xs text-gray-500">Logged in as</p>
                    <p className="text-sm font-medium text-gray-900 truncate">{user.email}</p>
                  </div>
                )}
                <button
                  onClick={handleLogout}
                  className="w-full btn btn-outline btn-sm"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={handleLinkClick}
                  className="block w-full text-center px-4 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-300"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  onClick={handleLinkClick}
                  className="block w-full text-center btn btn-primary btn-sm"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default MobileMenu
