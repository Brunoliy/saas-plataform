import { useState } from 'react'
import { Github, Linkedin, Twitter, Globe, Link as LinkIcon, Trash2, Edit2, X, Check } from 'lucide-react'
import { ProfessionalLink, ProfessionalLinkCreate, professionalService } from '@/services/professionalService'
import { toast } from 'react-hot-toast'

interface SocialLinksProps {
  professionalId: string
  links: ProfessionalLink[]
  onLinksUpdate: () => void
  isOwner: boolean
}

const platformIcons: Record<string, React.ReactNode> = {
  github: <Github className="w-5 h-5" />,
  linkedin: <Linkedin className="w-5 h-5" />,
  twitter: <Twitter className="w-5 h-5" />,
  portfolio: <Globe className="w-5 h-5" />,
  other: <LinkIcon className="w-5 h-5" />,
}

const platformLabels: Record<string, string> = {
  github: 'GitHub',
  linkedin: 'LinkedIn',
  twitter: 'Twitter',
  portfolio: 'Portfolio',
  other: 'Other',
}

export default function SocialLinks({ professionalId, links, onLinksUpdate, isOwner }: SocialLinksProps) {
  const [isAdding, setIsAdding] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [newLink, setNewLink] = useState<ProfessionalLinkCreate>({
    platform: 'github',
    url: '',
    label: null,
  })
  const [editLink, setEditLink] = useState<ProfessionalLinkCreate>({
    platform: 'github',
    url: '',
    label: null,
  })
  const [isSaving, setIsSaving] = useState(false)

  const handleAddLink = async () => {
    if (!newLink.url.trim()) {
      toast.error('Please enter a URL')
      return
    }

    try {
      setIsSaving(true)
      await professionalService.addLink(professionalId, newLink)
      toast.success('Link added successfully!')
      setNewLink({ platform: 'github', url: '', label: null })
      setIsAdding(false)
      onLinksUpdate()
    } catch (error) {
      console.error('Failed to add link:', error)
      toast.error('Failed to add link')
    } finally {
      setIsSaving(false)
    }
  }

  const handleUpdateLink = async (linkId: string) => {
    if (!editLink.url.trim()) {
      toast.error('Please enter a URL')
      return
    }

    try {
      setIsSaving(true)
      await professionalService.updateLink(professionalId, linkId, editLink)
      toast.success('Link updated successfully!')
      setEditingId(null)
      onLinksUpdate()
    } catch (error) {
      console.error('Failed to update link:', error)
      toast.error('Failed to update link')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteLink = async (linkId: string) => {
    if (!confirm('Are you sure you want to delete this link?')) {
      return
    }

    try {
      await professionalService.deleteLink(professionalId, linkId)
      toast.success('Link deleted successfully!')
      onLinksUpdate()
    } catch (error) {
      console.error('Failed to delete link:', error)
      toast.error('Failed to delete link')
    }
  }

  const startEdit = (link: ProfessionalLink) => {
    setEditingId(link.id)
    setEditLink({
      platform: link.platform,
      url: link.url,
      label: link.label,
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditLink({ platform: 'github', url: '', label: null })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h4 className="text-sm font-medium text-gray-700">Social Links</h4>
        {isOwner && !isAdding && (
          <button
            onClick={() => setIsAdding(true)}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            Add Link
          </button>
        )}
      </div>

      {/* Add New Link Form */}
      {isAdding && (
        <div className="border border-gray-200 rounded-md p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
              <select
                value={newLink.platform}
                onChange={(e) => setNewLink({ ...newLink, platform: e.target.value })}
                className="input text-sm"
              >
                <option value="github">GitHub</option>
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">Twitter</option>
                <option value="portfolio">Portfolio</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Label (Optional)</label>
              <input
                type="text"
                value={newLink.label || ''}
                onChange={(e) => setNewLink({ ...newLink, label: e.target.value })}
                className="input text-sm"
                placeholder="Custom label"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
            <input
              type="url"
              value={newLink.url}
              onChange={(e) => setNewLink({ ...newLink, url: e.target.value })}
              className="input text-sm"
              placeholder="https://..."
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleAddLink}
              disabled={isSaving}
              className="btn btn-primary text-sm"
            >
              {isSaving ? 'Adding...' : 'Add'}
            </button>
            <button
              onClick={() => {
                setIsAdding(false)
                setNewLink({ platform: 'github', url: '', label: null })
              }}
              disabled={isSaving}
              className="btn btn-secondary text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Links List */}
      <div className="space-y-2">
        {links.length === 0 && !isAdding && (
          <p className="text-sm text-gray-500">No social links added yet.</p>
        )}

        {links.map((link) => (
          <div key={link.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-md">
            {editingId === link.id ? (
              <div className="flex-1 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <select
                      value={editLink.platform}
                      onChange={(e) => setEditLink({ ...editLink, platform: e.target.value })}
                      className="input text-sm"
                    >
                      <option value="github">GitHub</option>
                      <option value="linkedin">LinkedIn</option>
                      <option value="twitter">Twitter</option>
                      <option value="portfolio">Portfolio</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <input
                      type="text"
                      value={editLink.label || ''}
                      onChange={(e) => setEditLink({ ...editLink, label: e.target.value })}
                      className="input text-sm"
                      placeholder="Custom label"
                    />
                  </div>
                </div>
                <input
                  type="url"
                  value={editLink.url}
                  onChange={(e) => setEditLink({ ...editLink, url: e.target.value })}
                  className="input text-sm"
                  placeholder="https://..."
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => handleUpdateLink(link.id)}
                    disabled={isSaving}
                    className="btn btn-primary text-sm flex items-center gap-1"
                  >
                    <Check className="w-4 h-4" />
                    Save
                  </button>
                  <button
                    onClick={cancelEdit}
                    disabled={isSaving}
                    className="btn btn-secondary text-sm flex items-center gap-1"
                  >
                    <X className="w-4 h-4" />
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-3 flex-1">
                  <div className="text-gray-600">
                    {platformIcons[link.platform] || platformIcons.other}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {link.label || platformLabels[link.platform] || 'Link'}
                    </div>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-700 truncate block"
                    >
                      {link.url}
                    </a>
                  </div>
                </div>
                {isOwner && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => startEdit(link)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteLink(link.id)}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
