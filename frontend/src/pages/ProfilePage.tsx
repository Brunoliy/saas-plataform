import { useEffect, useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { professionalService, ProfessionalProfile } from '@/services/professionalService'
import { toast } from 'react-hot-toast'
import SocialLinks from '@/components/SocialLinks'

const ProfilePage = () => {
  const { user } = useAuthStore()
  const [professionalProfile, setProfessionalProfile] = useState<ProfessionalProfile | null>(null)
  const [bio, setBio] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (user?.account_type === 'professional') {
      loadProfessionalProfile()
    }
  }, [user])

  const loadProfessionalProfile = async () => {
    try {
      setIsLoading(true)
      const profile = await professionalService.getMyProfile()
      setProfessionalProfile(profile)
      setBio(profile.bio || '')
    } catch (error: any) {
      console.error('Failed to load professional profile:', error)
      // If 404, profile doesn't exist yet - that's ok, we'll show create button
      if (error.response?.status !== 404) {
        toast.error('Failed to load professional profile')
      }
      setProfessionalProfile(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateProfile = async () => {
    try {
      setIsSaving(true)
      const enteredTitle = window.prompt('Enter your professional title (e.g., Full-Stack Developer):', 'Professional') || 'Professional'
      const newProfile = await professionalService.createProfile({ title: enteredTitle, bio: '' })
      setProfessionalProfile(newProfile)
      setBio('')
      toast.success('Professional profile created!')
    } catch (error) {
      console.error('Failed to create profile:', error)
      toast.error('Failed to create profile')
    } finally {
      setIsSaving(false)
    }
  }

  const handleSaveBio = async () => {
    try {
      setIsSaving(true)
      const updated = await professionalService.updateMyProfile({ bio })
      setProfessionalProfile(updated)
      setIsEditing(false)
      toast.success('Bio updated successfully!')
    } catch (error) {
      console.error('Failed to update bio:', error)
      toast.error('Failed to update bio')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setBio(professionalProfile?.bio || '')
    setIsEditing(false)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <p className="mt-2 text-gray-600">
          Manage your account settings
        </p>
      </div>

      <div className="space-y-6">
        {/* Account Information */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <p className="mt-1 text-sm text-gray-900">{user?.full_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Account Type</label>
                <p className="mt-1 text-sm text-gray-900 capitalize">{user?.account_type}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Professional Profile Section */}
        {user?.account_type === 'professional' && (
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Professional Profile</h3>
            </div>
            <div className="card-content">
              {isLoading ? (
                <p className="text-sm text-gray-600">Loading profile...</p>
              ) : professionalProfile ? (
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium text-gray-700">About You</label>
                      {!isEditing && (
                        <button
                          onClick={() => setIsEditing(true)}
                          className="text-sm text-primary-600 hover:text-primary-700"
                        >
                          Edit
                        </button>
                      )}
                    </div>
                    {isEditing ? (
                      <div className="space-y-2">
                        <textarea
                          value={bio}
                          onChange={(e) => setBio(e.target.value)}
                          rows={6}
                          className="input"
                          placeholder="Tell us about yourself, your experience, and what makes you unique..."
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={handleSaveBio}
                            disabled={isSaving}
                            className="btn btn-primary text-sm"
                          >
                            {isSaving ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            onClick={handleCancel}
                            disabled={isSaving}
                            className="btn btn-secondary text-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                        {professionalProfile.bio || 'No bio added yet. Click Edit to add one.'}
                      </p>
                    )}
                  </div>

                  {/* Social Links Section */}
                  <div className="pt-4 border-t border-gray-200">
                    <SocialLinks
                      professionalId={professionalProfile.id}
                      links={professionalProfile.links || []}
                      onLinksUpdate={loadProfessionalProfile}
                      isOwner={true}
                    />
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-sm text-gray-600 mb-4">
                    You don't have a professional profile yet. Create one to start showcasing your skills and experience!
                  </p>
                  <button
                    onClick={handleCreateProfile}
                    disabled={isSaving}
                    className="btn btn-primary"
                  >
                    {isSaving ? 'Creating...' : 'Create Professional Profile'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProfilePage 