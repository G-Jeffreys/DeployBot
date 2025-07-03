import React, { useState, useEffect, useCallback } from 'react'

// Import all functional components
import ProjectSelector from './components/ProjectSelector'
import TaskList from './components/TaskList'
import DeployStatus from './components/DeployStatus'
import TimerDisplay from './components/TimerDisplay'
import ActivityLog from './components/ActivityLog'
import TestPythonConnection from './components/TestPythonConnection'
import Analytics from './components/Analytics'

function App() {
  console.log('🚀 [APP] DeployBot App component starting...')
  
  // Check if this is a notification window
  const urlParams = new URLSearchParams(window.location.search);
  const isNotificationWindow = urlParams.has('id') || window.location.pathname.includes('notification');
  
  // If this is a notification window, render notification content
  if (isNotificationWindow) {
    console.log('🔔 [APP] Notification window detected - delegating to notification handler')
    
    // Import and render the notification app
    const NotificationApp = React.lazy(() => import('./NotificationApp'))
    
    return (
      <React.Suspense fallback={
        <div className="p-4 bg-white rounded-lg shadow-lg">
          <div className="animate-pulse">Loading notification...</div>
        </div>
      }>
        <NotificationApp />
      </React.Suspense>
    )
  }

  // Main application state
  const [selectedProject, setSelectedProject] = useState(null)
  const [deployStatus, setDeployStatus] = useState('idle')
  const [timerData, setTimerData] = useState(null)
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [backendStatus, setBackendStatus] = useState('disconnected')
  const [appError, setAppError] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  
  // 📊 PHASE 2: Analytics dashboard navigation state
  const [activeView, setActiveView] = useState('tasks') // 'tasks' or 'analytics'

  console.log('🔄 [APP] Current state:', { 
    selectedProject: selectedProject?.name, 
    deployStatus, 
    isBackendConnected, 
    backendStatus,
    activeView  // 📊 PHASE 2: Include analytics view state
  })

  // Connection monitoring - MEMORY LEAK FIX: Reduced frequency and better cleanup
  useEffect(() => {
    console.log('🔗 [APP] Setting up connection monitoring...')
    
    let connectionCheckInterval
    let mounted = true  // Track if component is still mounted

    const checkConnection = async () => {
      if (!mounted) return  // Don't proceed if component is unmounted
      
      try {
        const response = await window.electronAPI?.backend.ping()
        const isConnectedNow = response && response.data && response.data.success

        if (!mounted) return  // Check again after async operation

        // Use functional form to avoid stale closure issues
        setIsBackendConnected(currentConnected => {
          if (isConnectedNow !== currentConnected) {
            console.log('🔄 [APP] Connection state changed:', isConnectedNow ? 'connected' : 'disconnected')
            setBackendStatus(isConnectedNow ? 'connected' : 'disconnected')
            
            if (isConnectedNow) {
              setAppError(null)
            }
          }
          return isConnectedNow
        })

        // Set loading to false after first successful check (regardless of result)
        setIsLoading(false)

      } catch (error) {
        if (!mounted) return
        
        console.error('❌ [APP] Connection check failed:', error)
        setIsBackendConnected(false)
        setBackendStatus('error')
        setIsLoading(false)  // Always set loading to false even on error
        setAppError(`Connection failed: ${error.message}`)
      }
    }

    // Initial connection check
    checkConnection()

    // Set up periodic connection monitoring with MUCH longer interval
    connectionCheckInterval = setInterval(checkConnection, 10000) // Check every 10 seconds

    return () => {
      console.log('🧹 [APP] Cleaning up connection monitoring...')
      mounted = false  // Mark as unmounted
      if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval)
      }
    }
  }, [])  // Empty dependency array - run once on mount only

  // Deploy status monitoring - MEMORY LEAK FIX: Reduced frequency and better cleanup
  useEffect(() => {
    console.log('📦 [APP] Setting up deploy status monitoring...')
    
    if (!isBackendConnected || !selectedProject) {
      console.log('📦 [APP] Skipping deploy monitoring - no backend or project')
      return
    }

    let deployCheckInterval = null

    const checkDeployStatus = async () => {
      try {
        console.log('📦 [APP] Checking deploy status for project:', selectedProject.name)
        
        const response = await window.electronAPI?.deploy.status(selectedProject.path)
        console.log('📦 [APP] Deploy status response:', JSON.stringify(response, null, 2))
        
        // Handle WebSocket response structure
        const data = response?.data || response
        
        if (data && data.success) {
          // Check if monitoring is active and if our project is being monitored
          const isMonitoring = data.monitoring_active || false
          const monitoredProjects = data.monitored_projects || []
          const isProjectMonitored = monitoredProjects.some(p => 
            p.name === selectedProject.name || p.path === selectedProject.path
          )
          
          // Set status based on monitoring state
          const newStatus = isMonitoring && isProjectMonitored ? 'monitoring' : 'idle'
          setDeployStatus(newStatus)
        }
      } catch (error) {
        console.error('❌ [APP] Failed to check deploy status:', error)
        // Don't update status on error to avoid flickering
      }
    }

    // Initial check
    checkDeployStatus()
    
    // MEMORY LEAK FIX: Reduced from 3 seconds to 5 seconds to reduce load
    deployCheckInterval = setInterval(checkDeployStatus, 5000)

    return () => {
      console.log('🧹 [APP] Cleaning up deploy status monitoring...')
      if (deployCheckInterval) {
        clearInterval(deployCheckInterval)
        deployCheckInterval = null
      }
    }
  }, [isBackendConnected, selectedProject?.path]) // Removed deployStatus from dependencies

  // Handle project selection
  const handleProjectSelect = (project) => {
    console.log('📁 [APP] Project selected:', project?.name || 'none')
    setSelectedProject(project)
    
    // Reset deploy status when changing projects
    if (project) {
      setDeployStatus('idle')
      console.log('📁 [APP] Reset deploy status to idle for new project')
    }
  }

  // Handle timer updates from TimerDisplay - memoized to prevent infinite re-renders
  const handleTimerUpdate = useCallback((newTimerData) => {
    console.log('⏰ [APP] Timer update received:', newTimerData?.isActive ? 'active' : 'inactive')
    setTimerData(newTimerData)
  }, []) // Empty dependency array since setTimerData is stable

  // 📊 PHASE 2: Handle view navigation
  const handleViewChange = (view) => {
    console.log('📊 [APP] Switching to view:', view)
    setActiveView(view)
  }

  // Get connection status display
  const getConnectionStatus = () => {
    if (isBackendConnected) {
      return { 
        icon: '🟢', 
        text: 'Connected', 
        color: 'text-green-600 dark:text-green-400' 
      }
    } else {
      switch (backendStatus) {
        case 'connecting':
          return { 
            icon: '🟡', 
            text: backendStatus, 
            color: 'text-yellow-600 dark:text-yellow-400' 
          }
        case 'failed':
        case 'error':
          return { 
            icon: '🔴', 
            text: 'Failed', 
            color: 'text-red-600 dark:text-red-400' 
          }
        default:
          return { 
            icon: '🔴', 
            text: 'Disconnected', 
            color: 'text-red-600 dark:text-red-400' 
          }
      }
    }
  }

  const connectionStatus = getConnectionStatus()

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Starting DeployBot...
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            Connecting to backend services
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                🚀 DeployBot
              </h1>
              
              {/* 📊 PHASE 2: View Navigation */}
              <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => handleViewChange('tasks')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    activeView === 'tasks'
                      ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  📝 Tasks
                </button>
                <button
                  onClick={() => handleViewChange('analytics')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    activeView === 'analytics'
                      ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  📊 Analytics
                </button>
              </div>
              
              {/* Deploy Status */}
              <DeployStatus status={deployStatus} timerData={timerData} />
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <span className="text-sm">{connectionStatus.icon}</span>
                <span className={`text-sm font-medium ${connectionStatus.color}`}>
                  {connectionStatus.text}
                </span>
              </div>
              
              {/* Selected Project */}
              {selectedProject && (
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  📁 {selectedProject.name}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Error Display */}
      {appError && (
        <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 m-4 rounded">
          <div className="flex items-center">
            <span className="text-red-500 text-lg mr-2">❌</span>
            <div>
              <h3 className="text-red-800 dark:text-red-200 font-medium">Connection Error</h3>
              <p className="text-red-700 dark:text-red-300 text-sm mt-1">{appError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Project Selection & Timer */}
          <div className="lg:col-span-3 space-y-6">
            {/* Project Selector */}
            <ProjectSelector 
              selectedProject={selectedProject}
              onProjectSelect={handleProjectSelect}
              isBackendConnected={isBackendConnected}
              backendStatus={backendStatus}
            />
            
            {/* Timer Display */}
            <TimerDisplay 
              selectedProject={selectedProject}
              onTimerUpdate={handleTimerUpdate}
            />
            
            {/* Backend Connection Test */}
            <div style={{ display: 'none' }}>
              <TestPythonConnection />
            </div>
          </div>

          {/* Center - Dynamic Content Based on Active View */}
          <div className="lg:col-span-9">
            {/* 📊 PHASE 2: Conditional rendering based on active view */}
            {activeView === 'tasks' && (
              <TaskList project={selectedProject} />
            )}
            
            {activeView === 'analytics' && (
              <Analytics selectedProject={selectedProject} />
            )}
          </div>

          {/* Right Sidebar - Activity Log */}
          <div className="lg:col-span-3" style={{ display: 'none' }}>
            <ActivityLog project={selectedProject} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-8">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <div>
              DeployBot v1.0.0 - Intelligent Deployment Assistant
              {/* 📊 PHASE 2: Analytics status indicator */}
              {activeView === 'analytics' && selectedProject && (
                <span className="ml-2 text-blue-600 dark:text-blue-400">
                  • Analytics: {selectedProject.name}
                </span>
              )}
            </div>
            <div>
              {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App 