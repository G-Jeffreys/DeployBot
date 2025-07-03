import React, { useState, useEffect } from 'react'

/**
 * CustomDirectoryManager Component
 * 
 * Provides management interface for the custom directory system:
 * - View all project-directory mappings
 * - Migrate existing projects to new system
 * - Manage and update project locations
 * - System status and diagnostics
 */
const CustomDirectoryManager = ({ isOpen, onClose, onRefreshProjects }) => {
  console.log('🗂️ [CUSTOM_DIRECTORY_MANAGER] Component rendering, isOpen:', isOpen)

  // Component state
  const [projectMappings, setProjectMappings] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isMigrating, setIsMigrating] = useState(false)
  const [error, setError] = useState(null)
  const [migrationResult, setMigrationResult] = useState(null)
  const [activeTab, setActiveTab] = useState('mappings') // 'mappings' | 'migration' | 'diagnostics'

  // Load project mappings when component opens
  useEffect(() => {
    if (isOpen) {
      console.log('🗂️ [CUSTOM_DIRECTORY_MANAGER] Component opened, loading mappings...')
      loadProjectMappings()
    }
  }, [isOpen])

  /**
   * Load current project-directory mappings
   */
  const loadProjectMappings = async () => {
    console.log('🗂️ [CUSTOM_DIRECTORY_MANAGER] Loading project mappings...')
    setIsLoading(true)
    setError(null)

    try {
      const response = await window.electronAPI?.project.listProjectMappings()
      console.log('🗂️ [CUSTOM_DIRECTORY_MANAGER] Mappings response:', response)

      // Handle WebSocket response structure
      const data = response?.data || response

      if (data && data.success) {
        setProjectMappings(data.mappings || [])
        console.log('✅ [CUSTOM_DIRECTORY_MANAGER] Loaded', data.mappings?.length || 0, 'mappings')
      } else {
        throw new Error(data?.message || data?.error || 'Failed to load mappings')
      }
    } catch (error) {
      console.error('❌ [CUSTOM_DIRECTORY_MANAGER] Failed to load mappings:', error)
      setError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Migrate existing projects to the new directory system
   */
  const handleMigrateProjects = async () => {
    console.log('🔄 [CUSTOM_DIRECTORY_MANAGER] Starting project migration...')
    setIsMigrating(true)
    setError(null)
    setMigrationResult(null)

    try {
      const response = await window.electronAPI?.project.migrateExistingProjects()
      console.log('🔄 [CUSTOM_DIRECTORY_MANAGER] Migration response:', response)

      // Handle WebSocket response structure
      const data = response?.data || response

      if (data && data.success) {
        setMigrationResult(data.migration_result)
        console.log('✅ [CUSTOM_DIRECTORY_MANAGER] Migration completed:', data.migration_result)
        
        // Reload mappings to show updated data
        await loadProjectMappings()
        
        // Notify parent to refresh project list
        if (onRefreshProjects) {
          onRefreshProjects()
        }
      } else {
        throw new Error(data?.message || data?.error || 'Migration failed')
      }
    } catch (error) {
      console.error('❌ [CUSTOM_DIRECTORY_MANAGER] Migration failed:', error)
      setError(error.message)
    } finally {
      setIsMigrating(false)
    }
  }

  /**
   * Resolve project path for display
   */
  const resolveProjectPath = async (projectName) => {
    try {
      const response = await window.electronAPI?.project.resolveProjectPath(projectName)
      const data = response?.data || response
      
      if (data && data.success) {
        return data.resolved_path
      }
    } catch (error) {
      console.warn('⚠️ [CUSTOM_DIRECTORY_MANAGER] Failed to resolve path for:', projectName)
    }
    return 'Unknown location'
  }

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return 'Invalid date'
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            🗂️ Custom Directory Manager
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('mappings')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'mappings'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            📋 Project Mappings
          </button>
          <button
            onClick={() => setActiveTab('migration')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'migration'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            🔄 Migration
          </button>
          <button
            onClick={() => setActiveTab('diagnostics')}
            className={`px-6 py-3 text-sm font-medium ${
              activeTab === 'diagnostics'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            🔍 Diagnostics
          </button>
        </div>

        {/* Content */}
        <div className="p-6 max-h-[60vh] overflow-y-auto">
          {/* Error Display */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
                <span>❌</span>
                <span className="font-medium">Error</span>
              </div>
              <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Project Mappings Tab */}
          {activeTab === 'mappings' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Project Directory Mappings
                </h3>
                <button
                  onClick={loadProjectMappings}
                  disabled={isLoading}
                  className="btn-outline text-sm"
                >
                  {isLoading ? '🔄 Loading...' : '🔄 Refresh'}
                </button>
              </div>

              {isLoading ? (
                <div className="text-center py-8">
                  <div className="text-2xl mb-2">⏳</div>
                  <p className="text-gray-500 dark:text-gray-400">Loading mappings...</p>
                </div>
              ) : projectMappings.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">📂</div>
                  <p className="text-gray-500 dark:text-gray-400">No project mappings found</p>
                  <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
                    Run migration to register existing projects
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {projectMappings.map((mapping, index) => (
                    <div key={index} className="card border border-gray-200 dark:border-gray-700">
                      <div className="card-body">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              📁 {mapping.project_name}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              📍 {mapping.custom_directory}
                            </p>
                            
                            {/* Mapping metadata */}
                            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 space-y-1">
                              <div>🕒 Added: {formatDate(mapping.created_at)}</div>
                              {mapping.migrated_from && (
                                <div>🔄 Migrated from: {mapping.migrated_from}</div>
                              )}
                            </div>
                          </div>

                          {/* Status indicator */}
                          <div className="flex items-center space-x-2">
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
                              ✅ Active
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Migration Tab */}
          {activeTab === 'migration' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                Project Migration
              </h3>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">💡</span>
                  <div>
                    <h4 className="font-medium text-blue-900 dark:text-blue-100">
                      About Migration
                    </h4>
                    <p className="text-blue-800 dark:text-blue-200 text-sm mt-1">
                      Migration registers existing projects in the default <code>DeployBot/projects</code> directory 
                      with the new custom directory system. This is safe and doesn't move any files.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <button
                  onClick={handleMigrateProjects}
                  disabled={isMigrating}
                  className="btn-primary"
                >
                  {isMigrating ? '🔄 Migrating...' : '🔄 Migrate Existing Projects'}
                </button>
                
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  This process is safe and reversible
                </span>
              </div>

              {/* Migration Result */}
              {migrationResult && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <span>✅</span>
                    <h4 className="font-medium text-green-900 dark:text-green-100">
                      Migration Completed
                    </h4>
                  </div>
                  
                  <div className="text-green-800 dark:text-green-200 text-sm space-y-1">
                    <div>📊 Projects processed: {migrationResult.processed_count || 0}</div>
                    <div>📁 Projects registered: {migrationResult.registered_count || 0}</div>
                    <div>⏭️ Projects skipped: {migrationResult.skipped_count || 0}</div>
                    
                    {migrationResult.registered_projects && migrationResult.registered_projects.length > 0 && (
                      <div className="mt-2">
                        <div>✅ Registered projects:</div>
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          {migrationResult.registered_projects.map((project, index) => (
                            <li key={index}>{project}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Diagnostics Tab */}
          {activeTab === 'diagnostics' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                System Diagnostics
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* System Status */}
                <div className="card border border-gray-200 dark:border-gray-700">
                  <div className="card-body">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                      📊 System Status
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Custom Directory System:</span>
                        <span className="text-green-600 dark:text-green-400">✅ Active</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Project Mappings:</span>
                        <span>{projectMappings.length} registered</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Backend Integration:</span>
                        <span className="text-green-600 dark:text-green-400">✅ Connected</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Directory Info */}
                <div className="card border border-gray-200 dark:border-gray-700">
                  <div className="card-body">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                      📂 Directory Info
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div>
                        <div className="text-gray-600 dark:text-gray-400">Default Directory:</div>
                        <div className="font-mono text-xs">~/DeployBot/projects</div>
                      </div>
                      <div>
                        <div className="text-gray-600 dark:text-gray-400">Mapping File:</div>
                        <div className="font-mono text-xs">~/.deploybot/project_mappings.json</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* API Test Section */}
              <div className="card border border-gray-200 dark:border-gray-700">
                <div className="card-body">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                    🧪 API Tests
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <button 
                      onClick={loadProjectMappings}
                      className="btn-outline text-sm"
                      disabled={isLoading}
                    >
                      📋 Test Mappings API
                    </button>
                    <button 
                      onClick={() => window.electronAPI?.project.validateCustomDirectory('/tmp')}
                      className="btn-outline text-sm"
                    >
                      ✅ Test Validation API
                    </button>
                    <button 
                      onClick={() => window.electronAPI?.fileSystem.selectDirectory()}
                      className="btn-outline text-sm"
                    >
                      📂 Test Directory Dialog
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Custom Directory System v2.0 - Enhanced project management
          </div>
          <button
            onClick={onClose}
            className="btn-outline"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default CustomDirectoryManager 