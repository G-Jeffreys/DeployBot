import React, { useState, useEffect } from 'react'
import DirectoryPicker from './DirectoryPicker'
import CustomDirectoryManager from './CustomDirectoryManager'

const ProjectSelector = ({ selectedProject, onProjectSelect, isBackendConnected, backendStatus }) => {
  const [projects, setProjects] = useState([])
  const [isCreating, setIsCreating] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [customDirectory, setCustomDirectory] = useState('')
  const [useCustomDirectory, setUseCustomDirectory] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showDirectoryManager, setShowDirectoryManager] = useState(false)

  // Load projects when backend becomes connected - FIXED infinite loop
  useEffect(() => {
    console.log('📁 [PROJECT_SELECTOR] Component initializing...', { isBackendConnected, backendStatus })
    
    // Only load on meaningful status changes, not every minor fluctuation
    if (isBackendConnected && backendStatus === 'connected') {
      console.log('📁 [PROJECT_SELECTOR] Backend is connected, loading projects...')
      
      // Debounce project loading to prevent rapid successive calls
      const loadTimeout = setTimeout(() => {
        loadProjects()
      }, 500) // Wait 500ms for status to stabilize
      
      return () => clearTimeout(loadTimeout)
    } else {
      console.log('📁 [PROJECT_SELECTOR] Waiting for backend connection...', { isBackendConnected, backendStatus })
    }
  }, [isBackendConnected, backendStatus]) // Fixed: Use separate dependencies

  /**
   * Load projects from backend
   */
  const loadProjects = async () => {
    console.log('📁 [PROJECT_SELECTOR] Loading projects from backend...')
    setIsLoading(true)
    setError(null) // Clear any previous errors
    
    // Don't try to load if backend isn't connected
    if (!isBackendConnected || backendStatus !== 'connected') {
      console.log('📁 [PROJECT_SELECTOR] Backend not connected, skipping project load')
      setIsLoading(false)
      setError('Waiting for backend connection...')
      return
    }
    
    try {
      // Since we know backend is connected, use fewer retries
      let retries = 2
      let response = null
      let lastError = null
      
      while (retries > 0) {
        try {
          response = await window.electronAPI?.project.list()
          break // Success, exit retry loop
        } catch (error) {
          lastError = error
          if (error.message?.includes('WebSocket not connected') && retries > 1) {
            console.log(`📁 [PROJECT_SELECTOR] Temporary connection issue, retrying... (${retries} attempts left)`)
            setError(`🔄 Retrying... (${3 - retries}/2)`)
            await new Promise(resolve => setTimeout(resolve, 500)) // Shorter delay since backend should be ready
            retries--
            continue
          }
          throw lastError
        }
      }
      
      console.log('📁 [PROJECT_SELECTOR] Backend project list response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response
      
      if (data && data.success) {
        if (data.projects && Array.isArray(data.projects)) {
          // Use real project data from backend
          setProjects(data.projects)
          console.log('✅ [PROJECT_SELECTOR] Loaded projects from backend:', data.projects.length, 'projects')
          
          // Auto-select first project if none selected
          if (!selectedProject && data.projects.length > 0) {
            const firstProject = data.projects[0]
            console.log('📁 [PROJECT_SELECTOR] Auto-selecting first project:', firstProject.name)
            onProjectSelect(firstProject)
          }
        } else {
          console.log('📁 [PROJECT_SELECTOR] No projects found in response')
          setProjects([])
        }
      } else {
        throw new Error(data?.message || data?.error || 'Failed to load projects')
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to load projects:', error)
      console.error('❌ [PROJECT_SELECTOR] Error details:', JSON.stringify(error, null, 2))
      setError(error.message)
      window.electronAPI?.utils.log('error', 'Failed to load projects', error)
    } finally {
      setIsLoading(false)
      // Clear connecting status after loading completes
      if (error && error.includes('🔄 Connecting')) {
        setError(null)
      }
    }
  }

  /**
   * Create a new project using real backend with custom directory support
   */
  const handleCreateProject = async () => {
    if (!newProjectName.trim()) {
      console.warn('⚠️ [PROJECT_SELECTOR] Project name is empty')
      return
    }

    console.log('📁 [PROJECT_SELECTOR] Creating new project via backend:', {
      name: newProjectName,
      useCustomDirectory,
      customDirectory
    })
    setIsLoading(true)
    
    try {
      const projectData = {
        name: newProjectName.trim(),
        backend_services: [],
        description: `Project created via DeployBot UI on ${new Date().toLocaleDateString()}`
      }

      // Add custom directory if specified
      if (useCustomDirectory && customDirectory && customDirectory.trim()) {
        projectData.custom_directory = customDirectory.trim()
        console.log('📂 [PROJECT_SELECTOR] Using custom directory:', customDirectory.trim())
      }
      
      const response = await window.electronAPI?.project.create(projectData)
      console.log('📁 [PROJECT_SELECTOR] Project creation response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response
      
      if (data && data.success && data.project) {
        // Add the new project to the list
        setProjects(prev => [data.project, ...prev])
        
        // Reset form state
        setNewProjectName('')
        setCustomDirectory('')
        setUseCustomDirectory(false)
        setIsCreating(false)
        
        console.log('✅ [PROJECT_SELECTOR] Project created successfully:', data.project)
        window.electronAPI?.utils.log('info', 'Project created successfully', data.project)
        
        // Automatically select the newly created project
        await handleProjectClick(data.project)
      } else {
        throw new Error(data?.message || data?.error || response?.message || response?.error || 'Failed to create project')
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to create project:', error)
      console.error('❌ [PROJECT_SELECTOR] Error details:', JSON.stringify(error, null, 2))
      setError(error.message)
      window.electronAPI?.utils.log('error', 'Failed to create project', error)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Delete a project using real backend
   */
  const handleDeleteProject = async (project) => {
    console.log('📁 [PROJECT_SELECTOR] Deleting project via backend:', project)
    
    if (!confirm(`Are you sure you want to delete "${project.name}"?\n\nThis will permanently remove all project data including:\n• TODO.md tasks\n• Activity logs\n• Configuration\n\nThis action cannot be undone.`)) {
      return
    }
    
    setIsLoading(true)
    
    try {
      const response = await window.electronAPI?.project.delete({ 
        path: project.path, 
        name: project.name 
      })
      console.log('📁 [PROJECT_SELECTOR] Project deletion response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response
      
      if (data && data.success) {
        // Remove project from list
        setProjects(prev => prev.filter(p => p.path !== project.path))
        
        // Deselect if this was the selected project
        if (selectedProject?.path === project.path) {
          onProjectSelect(null)
        }
        
        console.log('✅ [PROJECT_SELECTOR] Project deleted successfully')
        window.electronAPI?.utils.log('info', 'Project deleted successfully', project)
      } else {
        throw new Error(data?.message || data?.error || response?.message || response?.error || 'Failed to delete project')
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to delete project:', error)
      console.error('❌ [PROJECT_SELECTOR] Error details:', JSON.stringify(error, null, 2))
      setError(error.message)
      window.electronAPI?.utils.log('error', 'Failed to delete project', error)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Handle project selection with full backend loading
   */
  const handleProjectClick = async (project) => {
    console.log('📁 [PROJECT_SELECTOR] Project clicked, loading full data:', project)
    setIsLoading(true)
    
    try {
      // Load the complete project data from backend
      const response = await window.electronAPI?.project.open({ path: project.path })
      console.log('📁 [PROJECT_SELECTOR] Full project load response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response
      
      if (data && data.success && data.project) {
        const fullProjectData = data.project
        console.log('✅ [PROJECT_SELECTOR] Full project data loaded:', fullProjectData)
        
        // Start monitoring for this project
        try {
          const monitorResponse = await window.electronAPI?.monitoring.start()
          console.log('🚀 [PROJECT_SELECTOR] Deploy monitoring started:', JSON.stringify(monitorResponse, null, 2))
        } catch (monitorError) {
          console.warn('⚠️ [PROJECT_SELECTOR] Failed to start monitoring:', monitorError)
          // Don't block project selection if monitoring fails
        }
        
        // Pass the complete project data to parent
        onProjectSelect(fullProjectData)
        window.electronAPI?.utils.log('info', 'Project selected and loaded', fullProjectData)
      } else {
        throw new Error(data?.message || data?.error || response?.message || response?.error || 'Failed to load project data')
      }
    } catch (error) {
      console.error('❌ [PROJECT_SELECTOR] Failed to load project:', error)
      console.error('❌ [PROJECT_SELECTOR] Error details:', JSON.stringify(error, null, 2))
      setError(error.message)
      window.electronAPI?.utils.log('error', 'Failed to load project', error)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Refresh projects list
   */
  const handleRefresh = () => {
    console.log('🔄 [PROJECT_SELECTOR] Refreshing projects list...', { isBackendConnected, backendStatus })
    if (isBackendConnected && backendStatus === 'connected') {
      loadProjects()
    } else {
      console.log('📁 [PROJECT_SELECTOR] Backend not connected, cannot refresh projects')
      setError('Backend is not connected. Please wait for connection to be established.')
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Projects
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowDirectoryManager(true)}
            className="btn-outline text-xs"
            disabled={isLoading}
            title="Manage custom directories"
          >
            🗂️
          </button>
          <button
            onClick={handleRefresh}
            className="btn-outline text-xs"
            disabled={isLoading}
            title={isBackendConnected ? "Refresh projects" : "Backend not connected"}
          >
            🔄
          </button>
          <button
            onClick={() => setIsCreating(true)}
            className="btn-primary text-sm"
            disabled={isCreating || isLoading}
          >
            ➕ New
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
            <span>❌</span>
            <span className="text-sm font-medium">Error</span>
          </div>
          <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
          <button
            onClick={() => setError(null)}
            className="mt-2 text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Create Project Form */}
      {isCreating && (
        <div className="card">
          <div className="card-body space-y-4">
            <h4 className="font-medium text-gray-900 dark:text-white">
              Create New Project
            </h4>
            
            {/* Project Name */}
            <div>
              <label className="form-label">Project Name</label>
              <input
                type="text"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                placeholder="My Awesome Project"
                className="form-input"
                autoFocus
                disabled={isLoading}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !isLoading && !useCustomDirectory) {
                    handleCreateProject()
                  } else if (e.key === 'Escape') {
                    setIsCreating(false)
                    setNewProjectName('')
                    setCustomDirectory('')
                    setUseCustomDirectory(false)
                  }
                }}
              />
            </div>

            {/* Custom Directory Option */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="useCustomDirectory"
                  checked={useCustomDirectory}
                  onChange={(e) => setUseCustomDirectory(e.target.checked)}
                  className="form-checkbox"
                  disabled={isLoading}
                />
                <label htmlFor="useCustomDirectory" className="form-label text-sm mb-0">
                  Use custom directory
                </label>
              </div>
              
              {useCustomDirectory && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                  <DirectoryPicker
                    value={customDirectory}
                    onChange={setCustomDirectory}
                    label=""
                    placeholder="Choose where to store this project..."
                    disabled={isLoading}
                    showValidation={true}
                    className="mb-0"
                  />
                  
                  <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                    💡 Project will be created in the selected directory instead of the default location
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-2">
              <button
                onClick={handleCreateProject}
                className="btn-primary text-sm"
                disabled={
                  !newProjectName.trim() || 
                  isLoading || 
                  (useCustomDirectory && (!customDirectory || !customDirectory.trim()))
                }
              >
                {isLoading ? '⏳ Creating...' : 'Create Project'}
              </button>
              <button
                onClick={() => {
                  setIsCreating(false)
                  setNewProjectName('')
                  setCustomDirectory('')
                  setUseCustomDirectory(false)
                }}
                className="btn-outline text-sm"
                disabled={isLoading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {(isLoading && !isCreating) || (!isBackendConnected) ? (
        <div className="text-center py-4">
          <div className="text-2xl mb-2">
            {!isBackendConnected ? '🔄' : '⏳'}
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {!isBackendConnected 
              ? `Waiting for backend connection... (${backendStatus})`
              : 'Loading projects...'
            }
          </p>
        </div>
      ) : null}

      {/* Project List */}
      <div className="space-y-2">
        {!isLoading && projects.length === 0 ? (
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
              onClick={() => !isLoading && handleProjectClick(project)}
            >
              <div className="card-body py-3 px-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900 dark:text-white truncate">
                      📁 {project.name}
                    </h4>
                    
                    {/* Project metadata */}
                    <div className="mt-1 text-xs text-gray-500 dark:text-gray-400 space-y-1">
                      <div className="flex items-center flex-wrap gap-2">
                        {project.taskCount ? (
                          <span>{project.taskCount} tasks</span>
                        ) : project.task_count ? (
                          <span>{project.task_count} tasks</span>
                        ) : project.tasks ? (
                          <span>{project.tasks.length} tasks</span>
                        ) : (
                          <span>No tasks</span>
                        )}
                        
                        {project.created_at && (
                          <>
                            <span>•</span>
                            <span>Created {new Date(project.created_at).toLocaleDateString()}</span>
                          </>
                        )}
                        
                        {project.last_deploy && (
                          <>
                            <span>•</span>
                            <span>Last deploy: {new Date(project.last_deploy).toLocaleDateString()}</span>
                          </>
                        )}
                      </div>

                      {/* Custom directory location info */}
                      {project.path && (
                        <div className="flex items-center space-x-1 text-blue-600 dark:text-blue-400">
                          <span>📍</span>
                          <span className="truncate font-mono">
                            {project.path.includes('DeployBot/projects') 
                              ? 'Default location' 
                              : `Custom: ${project.path.split('/').slice(-2).join('/')}`
                            }
                          </span>
                          {!project.path.includes('DeployBot/projects') && (
                            <span className="inline-flex items-center px-1 py-0.5 rounded text-xs bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100">
                              Custom
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Backend services */}
                    {project.backend_services && project.backend_services.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {project.backend_services.map((service, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded text-xs bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100"
                          >
                            {service}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Delete Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDeleteProject(project)
                    }}
                    className="ml-2 p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete project"
                    disabled={isLoading}
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Backend Status */}
      <div className="text-xs text-gray-500 dark:text-gray-400 text-center pt-2 border-t border-gray-200 dark:border-gray-700">
        {!isBackendConnected ? (
          <span>🔄 Backend: {backendStatus}</span>
        ) : projects.length > 0 ? (
          <span>✅ {projects.length} project{projects.length !== 1 ? 's' : ''} loaded from backend</span>
        ) : !isLoading ? (
          <span>📡 Connected to backend • No projects found</span>
        ) : (
          <span>🔄 Loading from backend...</span>
        )}
      </div>

      {/* Custom Directory Manager Modal */}
      <CustomDirectoryManager
        isOpen={showDirectoryManager}
        onClose={() => setShowDirectoryManager(false)}
        onRefreshProjects={handleRefresh}
      />
    </div>
  )
}

export default ProjectSelector 