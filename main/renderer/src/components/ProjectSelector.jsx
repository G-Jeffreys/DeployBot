import React, { useState, useEffect } from 'react'

const ProjectSelector = ({ selectedProject, onProjectSelect }) => {
  const [projects, setProjects] = useState([])
  const [isCreating, setIsCreating] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')

  // Load projects on component mount
  useEffect(() => {
    console.log('📁 [PROJECT_SELECTOR] Component initializing...')
    loadProjects()
  }, [])

  /**
   * Load available projects from the backend
   */
  const loadProjects = async () => {
    console.log('📁 [PROJECT_SELECTOR] Loading projects...')
    
    try {
      const response = await window.electronAPI?.project.list()
      console.log('📁 [PROJECT_SELECTOR] Projects loaded:', response)
      
      if (response && response.success && response.projects) {
        // Use real data from backend
        setProjects(response.projects)
        console.log('✅ [PROJECT_SELECTOR] Projects set from backend:', response.projects)
      } else {
        // Fallback to empty array if no projects or error
        console.warn('⚠️ [PROJECT_SELECTOR] No projects returned from backend, using empty list')
        setProjects([])
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to load projects:', error)
      window.electronAPI?.utils.log('error', 'Failed to load projects', error)
      
      // Set empty projects on error
      setProjects([])
    }
  }

  /**
   * Create a new project
   */
  const handleCreateProject = async () => {
    if (!newProjectName.trim()) {
      console.warn('⚠️ [PROJECT_SELECTOR] Project name is empty')
      return
    }

    console.log('📁 [PROJECT_SELECTOR] Creating new project:', newProjectName)
    
    try {
      const projectData = {
        name: newProjectName.trim(),
        backend_services: [],
        description: `Project created via DeployBot UI`
      }
      
      const response = await window.electronAPI?.project.create(projectData)
      console.log('📁 [PROJECT_SELECTOR] Project creation response:', response)
      
      if (response && response.success && response.project) {
        // Use the project data returned from backend
        setProjects(prev => [...prev, response.project])
        setNewProjectName('')
        setIsCreating(false)
        
        console.log('✅ [PROJECT_SELECTOR] Project created successfully:', response.project)
        window.electronAPI?.utils.log('info', 'Project created', response.project)
      } else {
        throw new Error(response?.message || 'Failed to create project')
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to create project:', error)
      window.electronAPI?.utils.log('error', 'Failed to create project', error)
      alert(`Failed to create project: ${error.message}`)
    }
  }

  /**
   * Delete a project
   */
  const handleDeleteProject = async (project) => {
    console.log('📁 [PROJECT_SELECTOR] Deleting project:', project)
    
    if (!confirm(`Are you sure you want to delete "${project.name}"?`)) {
      return
    }
    
    try {
      const response = await window.electronAPI?.project.delete({ path: project.path, name: project.name })
      console.log('📁 [PROJECT_SELECTOR] Project deletion response:', response)
      
      if (response && response.success) {
        setProjects(prev => prev.filter(p => p.path !== project.path))
        
        // Deselect if this was the selected project
        if (selectedProject?.path === project.path) {
          onProjectSelect(null)
        }
        
        console.log('✅ [PROJECT_SELECTOR] Project deleted successfully')
        window.electronAPI?.utils.log('info', 'Project deleted', project)
      } else {
        throw new Error(response?.message || 'Failed to delete project')
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to delete project:', error)
      window.electronAPI?.utils.log('error', 'Failed to delete project', error)
      alert(`Failed to delete project: ${error.message}`)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Projects
        </h3>
        <button
          onClick={() => setIsCreating(true)}
          className="btn-primary text-sm"
          disabled={isCreating}
        >
          ➕ New
        </button>
      </div>

      {/* Create Project Form */}
      {isCreating && (
        <div className="card">
          <div className="card-body space-y-3">
            <h4 className="font-medium text-gray-900 dark:text-white">
              Create New Project
            </h4>
            <div>
              <label className="form-label">Project Name</label>
              <input
                type="text"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                placeholder="My Awesome Project"
                className="form-input"
                autoFocus
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateProject()
                  } else if (e.key === 'Escape') {
                    setIsCreating(false)
                    setNewProjectName('')
                  }
                }}
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleCreateProject}
                className="btn-primary text-sm"
                disabled={!newProjectName.trim()}
              >
                Create
              </button>
              <button
                onClick={() => {
                  setIsCreating(false)
                  setNewProjectName('')
                }}
                className="btn-outline text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Project List */}
      <div className="space-y-2">
        {projects.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <div className="text-4xl mb-2">📂</div>
            <p>No projects yet</p>
            <p className="text-sm">Create your first project to get started</p>
          </div>
        ) : (
          projects.map((project) => (
            <div
              key={project.path}
              className={`card cursor-pointer transition-all duration-200 hover:shadow-md ${
                selectedProject?.path === project.path
                  ? 'ring-2 ring-deploybot-primary bg-blue-50 dark:bg-blue-900/20'
                  : ''
              }`}
              onClick={async () => {
                console.log('📁 [PROJECT_SELECTOR] Project clicked:', project)
                
                try {
                  // Load the project via backend to get full details
                  const response = await window.electronAPI?.project.open(project.path)
                  console.log('📁 [PROJECT_SELECTOR] Project load response:', response)
                  
                  if (response && response.success && response.project) {
                    onProjectSelect(response.project)
                  } else {
                    // Fallback to current project data
                    onProjectSelect(project)
                  }
                } catch (error) {
                  console.error('❌ [PROJECT_SELECTOR] Failed to load project:', error)
                  // Fallback to current project data
                  onProjectSelect(project)
                }
              }}
            >
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {project.name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {project.path}
                    </p>
                    {project.backendServices && project.backendServices.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {project.backendServices.map((service) => (
                          <span
                            key={service}
                            className="tag tag-code text-xs"
                          >
                            {service}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteProject(project)
                    }}
                    className="text-red-500 hover:text-red-700 text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete project"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Project Statistics */}
      {projects.length > 0 && (
        <div className="text-sm text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p>{projects.length} project{projects.length !== 1 ? 's' : ''} total</p>
        </div>
      )}
    </div>
  )
}

export default ProjectSelector 