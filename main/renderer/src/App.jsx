import React, { useState, useEffect, useCallback } from 'react'

// Import all functional components
import ProjectSelector from './components/ProjectSelector'
import TaskList from './components/TaskList'
import DeployStatus from './components/DeployStatus'
import TimerDisplay from './components/TimerDisplay'
import ActivityLog from './components/ActivityLog'
import TestPythonConnection from './components/TestPythonConnection'

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

  console.log('🔄 [APP] Current state:', { 
    selectedProject: selectedProject?.name, 
    deployStatus, 
    isBackendConnected, 
    backendStatus 
  })

  // Backend connection monitoring and initialization
  useEffect(() => {
    console.log('🔗 [APP] Setting up backend connection monitoring...')
    let connectionCheckInterval = null
    let retryAttempts = 0
    const maxRetries = 10

    const checkConnection = async () => {
      try {
        console.log('🔍 [APP] Checking backend connection...')
        
        // Use the ping command to test backend connectivity
        const response = await window.electronAPI?.python.sendCommand('ping', { 
          timestamp: new Date().toISOString() 
        })
        
        console.log('🔍 [APP] Backend ping response:', JSON.stringify(response, null, 2))
        
        // Handle WebSocket response structure
        const data = response?.data || response
        
        if (data && data.success) {
          console.log('✅ [APP] Backend connection successful')
          setIsBackendConnected(true)
          setBackendStatus('connected')
          setAppError(null)
          retryAttempts = 0
          
          // Load initial data when first connected
          setIsLoading(false)
        } else {
          throw new Error(data?.error || data?.message || 'Backend ping failed')
        }
      } catch (error) {
        console.error('❌ [APP] Backend connection check failed:', error)
        
        retryAttempts++
        if (retryAttempts <= maxRetries) {
          console.log(`🔄 [APP] Connection attempt ${retryAttempts}/${maxRetries} failed, will retry...`)
          setBackendStatus(`connecting (${retryAttempts}/${maxRetries})`)
          setIsBackendConnected(false)
        } else {
          console.error(`💀 [APP] Max connection retries (${maxRetries}) reached`)
          setBackendStatus('failed')
          setIsBackendConnected(false)
          setAppError(`Backend connection failed after ${maxRetries} attempts. Please check if the Python backend is running.`)
        }
      }
    }

    // Initial connection check
    checkConnection()
    
    // Set up periodic connection monitoring
    connectionCheckInterval = setInterval(checkConnection, 5000) // Check every 5 seconds
    
    // Set up event listeners for backend state changes
    if (window.electronAPI?.events?.onBackendStateChange) {
      console.log('🔗 [APP] Setting up backend state change listener')
      
      const handleBackendStateChange = (state) => {
        console.log('🔄 [APP] Backend state changed:', state)
        
        switch (state) {
          case 'connected':
            setIsBackendConnected(true)
            setBackendStatus('connected')
            setAppError(null)
            break
          case 'disconnected':
            setIsBackendConnected(false)
            setBackendStatus('disconnected')
            break
          case 'connecting':
            setIsBackendConnected(false)
            setBackendStatus('connecting')
            break
          case 'error':
            setIsBackendConnected(false)
            setBackendStatus('error')
            setAppError('Backend connection error')
            break
          default:
            console.warn('🤔 [APP] Unknown backend state:', state)
        }
      }
      
      window.electronAPI.events.onBackendStateChange(handleBackendStateChange)
    }

    // Cleanup function
    return () => {
      console.log('🧹 [APP] Cleaning up connection monitoring...')
      if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval)
      }
    }
  }, []) // Only run once on mount

  // Deploy status monitoring
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
    
    // Periodic checks
    deployCheckInterval = setInterval(checkDeployStatus, 3000)

    return () => {
      console.log('🧹 [APP] Cleaning up deploy status monitoring...')
      if (deployCheckInterval) {
        clearInterval(deployCheckInterval)
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
            <TestPythonConnection />
          </div>

          {/* Center - Task List */}
          <div className="lg:col-span-6">
            <TaskList project={selectedProject} />
          </div>

          {/* Right Sidebar - Activity Log */}
          <div className="lg:col-span-3">
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