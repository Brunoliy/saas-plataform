import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import { Plus, X, Star } from 'lucide-react'
import { skillService, Skill, ProfessionalSkill } from '@/services/skillService'

interface ProfessionalSkillsManagerProps {
  professionalId: string
}

const ProfessionalSkillsManager = ({ professionalId }: ProfessionalSkillsManagerProps) => {
  const [skills, setSkills] = useState<Skill[]>([])
  const [professionalSkills, setProfessionalSkills] = useState<ProfessionalSkill[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAdding, setIsAdding] = useState(false)
  const [selectedSkillId, setSelectedSkillId] = useState('')
  const [proficiency, setProficiency] = useState(3)
  const [yearsExp, setYearsExp] = useState<number | ''>('')
  const [certified, setCertified] = useState(false)

  useEffect(() => {
    loadData()
  }, [professionalId])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const [allSkills, profSkills] = await Promise.all([
        skillService.listSkills({ limit: 100 }),
        skillService.getProfessionalSkills(professionalId)
      ])
      setSkills(allSkills.items)
      setProfessionalSkills(profSkills)
    } catch (error) {
      console.error('Failed to load skills:', error)
      toast.error('Failed to load skills')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedSkillId) {
      toast.error('Please select a skill')
      return
    }

    try {
      setIsAdding(true)
      const newSkill = await skillService.addProfessionalSkill(professionalId, {
        skill_id: selectedSkillId,
        proficiency_level: proficiency,
        years_experience: yearsExp === '' ? null : Number(yearsExp),
        certified
      })
      setProfessionalSkills([...professionalSkills, newSkill])
      setSelectedSkillId('')
      setProficiency(3)
      setYearsExp('')
      setCertified(false)
      toast.success('Skill added successfully!')
    } catch (error) {
      console.error('Failed to add skill:', error)
      toast.error('Failed to add skill')
    } finally {
      setIsAdding(false)
    }
  }

  const handleRemoveSkill = async (skillId: string) => {
    if (!confirm('Remove this skill?')) return

    try {
      await skillService.deleteProfessionalSkill(professionalId, skillId)
      setProfessionalSkills(professionalSkills.filter(s => s.id !== skillId))
      toast.success('Skill removed')
    } catch (error) {
      console.error('Failed to remove skill:', error)
      toast.error('Failed to remove skill')
    }
  }

  const availableSkills = skills.filter(
    skill => !professionalSkills.some(ps => ps.skill_id === skill.id)
  )

  if (isLoading) {
    return <div className="text-center py-4">Loading skills...</div>
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Skills</h3>

      {/* Current Skills */}
      <div className="space-y-2">
        {professionalSkills.length === 0 ? (
          <p className="text-sm text-gray-500">No skills added yet. Add your first skill below!</p>
        ) : (
          professionalSkills.map((ps) => (
            <div
              key={ps.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">{ps.skill?.name}</span>
                  {ps.certified && (
                    <span className="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                      Certified
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-4 h-4 ${
                          i < ps.proficiency_level
                            ? 'text-yellow-400 fill-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  {ps.years_experience && (
                    <span>{ps.years_experience} years</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleRemoveSkill(ps.id)}
                className="p-1 text-red-600 hover:bg-red-50 rounded"
                title="Remove skill"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Add New Skill Form */}
      <form onSubmit={handleAddSkill} className="space-y-3 border-t pt-4">
        <h4 className="text-sm font-medium text-gray-700">Add New Skill</h4>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Skill
          </label>
          <select
            value={selectedSkillId}
            onChange={(e) => setSelectedSkillId(e.target.value)}
            className="input w-full"
            required
          >
            <option value="">Select a skill...</option>
            {availableSkills.map((skill) => (
              <option key={skill.id} value={skill.id}>
                {skill.name} ({skill.category})
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Proficiency Level
            </label>
            <select
              value={proficiency}
              onChange={(e) => setProficiency(Number(e.target.value))}
              className="input w-full"
            >
              <option value={1}>1 - Beginner</option>
              <option value={2}>2 - Elementary</option>
              <option value={3}>3 - Intermediate</option>
              <option value={4}>4 - Advanced</option>
              <option value={5}>5 - Expert</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Years Experience
            </label>
            <input
              type="number"
              min="0"
              max="50"
              value={yearsExp}
              onChange={(e) => setYearsExp(e.target.value === '' ? '' : Number(e.target.value))}
              className="input w-full"
              placeholder="Optional"
            />
          </div>

          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={certified}
                onChange={(e) => setCertified(e.target.checked)}
                className="w-4 h-4 text-primary-600 rounded"
              />
              <span className="text-sm font-medium text-gray-700">Certified</span>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={isAdding || !selectedSkillId}
          className="btn btn-primary btn-sm w-full sm:w-auto"
        >
          <Plus className="w-4 h-4 mr-1" />
          {isAdding ? 'Adding...' : 'Add Skill'}
        </button>
      </form>
    </div>
  )
}

export default ProfessionalSkillsManager
