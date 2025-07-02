import React, { useState, useEffect } from 'react'

// Components
import ProjectSelector from './components/ProjectSelector'
import TaskList from './components/TaskList'
import DeployStatus from './components/DeployStatus'
import ActivityLog from './components/ActivityLog'
import TestPythonConnection from './components/TestPythonConnection'
import TimerDisplay from './components/TimerDisplay'

function App() {
  // Application state
  const [selectedProject, setSelectedProject] = useState(null)
  const [deployStatus, setDeployStatus] = useState(null)
  const [isBackendConnected, setIsBackendConnected] = useState(false)
  const [backendStatus, setBackendStatus] = useState('connecting')
  const [lastActivity, setLastActivity] = useState(null)
  const [timerData, setTimerData] = useState(null)

  // Set up backend connection monitoring
  useEffect(() => {
    console.log('🚀 [APP] Setting up backend connection monitoring...')
    
    // Test backend connection on startup
    testBackendConnection()
    
    // Set up periodic connection checks
    const connectionInterval = setInterval(() => {
      if (backendStatus === 'disconnected' || backendStatus === 'failed') {
        testBackendConnection()
      }
    }, 10000) // Check every 10 seconds if disconnected
    
    // Cleanup on unmount
    return () => {
      console.log('🧹 [APP] Cleaning up backend connection monitoring...')
      clearInterval(connectionInterval)
    }
  }, [backendStatus])

  // Event handlers are now managed globally by ActivityLog component
  // App component focuses on connection management and routing

  /**
   * Test backend connection
   */
  const testBackendConnection = async () => {
    console.log('🔍 [APP] Testing backend connection...')
    setBackendStatus('connecting')
    
    try {
      // Wait a moment for backend to be ready if this is initial startup
      console.log('🔍 [APP] Waiting for backend to initialize...')
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const response = await window.electronAPI?.testing.pythonBackend()
      console.log('🔍 [APP] Backend test response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response
      
      if (data && data.success) {
        setIsBackendConnected(true)
        setBackendStatus('connected')
        console.log('✅ [APP] Backend connection test successful')
        console.log('✅ [APP] Backend is now connected and ready')
      } else {
        console.warn('⚠️ [APP] Backend test response was not successful:', data)
        throw new Error(data?.message || data?.error || response?.message || response?.error || 'Backend test failed')
      }
    } catch (error) {
      console.error('❌ [APP] Backend connection test failed:', error)
      console.error('❌ [APP] Error details:', JSON.stringify(error, null, 2))
      setIsBackendConnected(false)
      
      // Set appropriate status based on error type
      if (error.message?.includes('WebSocket not connected') || error.message?.includes('connection')) {
        setBackendStatus('connecting')
        console.log('🔄 [APP] Will retry backend connection in 3 seconds...')
        setTimeout(() => {
          testBackendConnection()
        }, 3000)
      } else {
      setBackendStatus('error')
      }
    }
  }

  /**
   * Handle project selection
   */
  const handleProjectSelect = async (project) => {
    console.log('📁 [APP] Project selected:', project)
    setSelectedProject(project)
    
    // Clear deploy status when switching projects
    setDeployStatus(null)
    
    if (project) {
      window.electronAPI?.utils.log('info', 'Project selected in UI', { 
        name: project.name, 
        path: project.path 
      })
    }
  }

  /**
   * Get connection status display info
   */
  const getConnectionStatus = () => {
    switch (backendStatus) {
      case 'connected':
        return { icon: '✅', text: 'Connected', color: 'text-green-600' }
      case 'connecting':
        return { icon: '🔄', text: 'Connecting...', color: 'text-yellow-600' }
      case 'disconnected':
        return { icon: '🔴', text: 'Disconnected', color: 'text-red-600' }
      case 'error':
        return { icon: '❌', text: 'Error', color: 'text-red-600' }
      case 'failed':
        return { icon: '💥', text: 'Failed', color: 'text-red-600' }
      default:
        return { icon: '❓', text: 'Unknown', color: 'text-gray-600' }
    }
  }

  const connectionStatus = getConnectionStatus()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="text-2xl">🤖</div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  DeployBot
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Deploy Detection & Task Redirection
                </p>
              </div>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center space-x-4">
              {/* Backend Connection Status */}
              <div className={`flex items-center space-x-2 text-sm ${connectionStatus.color}`}>
                <span className="text-lg">{connectionStatus.icon}</span>
                <span className="hidden sm:inline">Backend: {connectionStatus.text}</span>
              </div>
              
              {/* Selected Project */}
              {selectedProject && (
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                  <span>📁</span>
                  <span className="hidden sm:inline">
                    {selectedProject.name}
                  </span>
                </div>
              )}
              
              {/* Deploy Status Indicator */}
              {deployStatus?.isActive && (
                <div className="flex items-center space-x-2 text-sm text-blue-600 dark:text-blue-400">
                  <span className="animate-pulse">🚀</span>
                  <span className="hidden sm:inline">Deploy Active</span>
                </div>
              )}
              
              {/* Timer Status in Header - Prominent Display */}
              {timerData?.isActive && (
                <div className="flex items-center space-x-2 text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 px-3 py-1 rounded-full">
                  <span className="animate-pulse">⏰</span>
                  <span className="font-bold">{timerData.timeRemaining}</span>
                  <span className="hidden sm:inline text-xs">remaining</span>
                </div>
              )}
              
              {/* Last Activity */}
              {lastActivity && (
                <div className="text-xs text-gray-500 dark:text-gray-400 max-w-xs truncate">
                  Last: {lastActivity.message}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Backend Connection Warning */}
        {!isBackendConnected && (
          <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-yellow-600 dark:text-yellow-400 text-lg">⚠️</span>
              <div>
                <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Backend Connection Issue
                </h3>
                <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  The Python backend is not connected. Some features may not work properly.
                </p>
                <button
                  onClick={testBackendConnection}
                  className="mt-2 text-sm bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-1 rounded"
                >
                  🔄 Retry Connection
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Project Selection */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <div className="card-body">
                <ProjectSelector
                  selectedProject={selectedProject}
                  onProjectSelect={handleProjectSelect}
                />
              </div>
            </div>
          </div>

          {/* Middle Column - Timer, Deploy Status and Tasks */}
          <div className="lg:col-span-1 space-y-6">
            {/* Prominent Timer Display */}
            <TimerDisplay 
              selectedProject={selectedProject}
              onTimerUpdate={setTimerData}
            />

            {/* Deploy Status */}
            <DeployStatus
              status={
                deployStatus?.isActive 
                  ? 'deploying'
                  : deployStatus?.event === 'completed' 
                    ? 'completed'
                    : deployStatus?.event === 'failed'
                      ? 'error'
                      : 'idle'
              }
              timerData={timerData}
            />

            {/* Task List */}
            <div className="card">
              <div className="card-header">
                <h3 className="text-lg font-semibold">📝 Tasks</h3>
              </div>
              <div className="card-body">
                {(() => {
                  try {
                    console.log('🔍 [APP] Rendering TaskList component with project:', selectedProject?.name || 'none')
                    return <TaskList project={selectedProject} />
                  } catch (error) {
                    console.error('❌ [APP] TaskList component error:', error)
                    return (
                      <div className="text-center py-8">
                        <div className="text-4xl mb-2">❌</div>
                        <p className="text-red-600 dark:text-red-400">Error loading tasks</p>
                        <p className="text-sm text-gray-500 mt-1">{error.message}</p>
                      </div>
                    )
                  }
                })()}
              </div>
            </div>
          </div>

          {/* Right Column - Activity Log and Connection Test */}
          <div className="lg:col-span-1 space-y-6">
            {/* Activity Log */}
            <ActivityLog
              project={selectedProject}
            />

            {/* Backend Connection Test (Development) */}
            {window.electronAPI?.utils.isDevelopment() && (
              <div className="card">
                <div className="card-header">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    🔧 Development Tools
                  </h3>
                </div>
                <div className="card-body">
                  <TestPythonConnection />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
            <div>
              DeployBot v1.0.0 - Week 4 Implementation
            </div>
            <div className="flex items-center space-x-4">
              <span>Backend: {connectionStatus.text}</span>
              {selectedProject && (
                <span>Project: {selectedProject.name}</span>
              )}
              <span>
                {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App 