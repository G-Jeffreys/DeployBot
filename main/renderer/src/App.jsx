import React, { useState, useEffect } from 'react'

// Components
import ProjectSelector from './components/ProjectSelector'
import TaskList from './components/TaskList'
import DeployStatus from './components/DeployStatus'
import ActivityLog from './components/ActivityLog'
import TestPythonConnection from './components/TestPythonConnection'

function App() {
  // Application state
  const [selectedProject, setSelectedProject] = useState(null)
  const [pythonStatus, setPythonStatus] = useState('connecting')
  const [deployStatus, setDeployStatus] = useState('idle')
  const [logs, setLogs] = useState([])

  // Log application initialization
  useEffect(() => {
    console.log('🎉 [APP] DeployBot App component initializing...')
    window.electronAPI?.utils.log('info', 'App component mounted')
    
    initializeApp()
    setupPythonListeners()
    
    return () => {
      console.log('🔴 [APP] App component cleaning up...')
      window.electronAPI?.utils.log('info', 'App component unmounting')
    }
  }, [])

  /**
   * Initialize the application and load initial data
   */
  const initializeApp = async () => {
    console.log('🚀 [APP] Initializing DeployBot application...')
    
    try {
      // Test Python connection
      const pythonResponse = await window.electronAPI?.python.sendCommand('ping', {})
      console.log('🐍 [APP] Python connection test:', pythonResponse)
      setPythonStatus('connected')
      
      // Load available projects
      const projectsResponse = await window.electronAPI?.project.list()
      console.log('📁 [APP] Available projects:', projectsResponse)
      
      // Load recent logs
      const logsResponse = await window.electronAPI?.logs.get('recent')
      console.log('📋 [APP] Recent logs:', logsResponse)
      if (logsResponse?.logs) {
        setLogs(logsResponse.logs)
      }
      
      console.log('✅ [APP] Application initialization complete')
    } catch (error) {
      console.error('❌ [APP] Application initialization failed:', error)
      setPythonStatus('error')
    }
  }

  /**
   * Setup listeners for Python backend communication
   */
  const setupPythonListeners = () => {
    console.log('📡 [APP] Setting up Python communication listeners...')
    
    // Listen for Python output
    window.electronAPI?.python.onOutput((output) => {
      console.log('🐍 [APP] Python output received:', output)
      window.electronAPI?.utils.log('info', 'Python output', output)
      
      // Update application state based on Python output
      if (output.includes('DEPLOY_DETECTED')) {
        setDeployStatus('deploying')
        addLog('Deploy detected - starting timer')
      } else if (output.includes('TASK_SELECTED')) {
        addLog('Alternative task selected')
      } else if (output.includes('REDIRECT_COMPLETE')) {
        addLog('Successfully redirected to task')
      }
    })
    
    // Listen for Python errors
    window.electronAPI?.python.onError((error) => {
      console.error('🐍 [APP] Python error received:', error)
      window.electronAPI?.utils.log('error', 'Python error', error)
      setPythonStatus('error')
      addLog(`Python error: ${error}`)
    })
    
    console.log('✅ [APP] Python listeners setup complete')
  }

  /**
   * Add a new log entry to the activity log
   */
  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString()
    const logEntry = `[${timestamp}] ${message}`
    console.log(`📋 [APP] Adding log: ${logEntry}`)
    
    setLogs(prevLogs => [logEntry, ...prevLogs.slice(0, 9)]) // Keep last 10 logs
  }

  /**
   * Handle project selection
   */
  const handleProjectSelect = async (project) => {
    console.log('📁 [APP] Project selected:', project)
    window.electronAPI?.utils.log('info', 'Project selected', project)
    
    setSelectedProject(project)
    addLog(`Opened project: ${project?.name || 'Unknown'}`)
    
    // Start deploy monitoring for this project
    if (project) {
      try {
        await window.electronAPI?.deploy.startMonitoring()
        console.log('🚀 [APP] Deploy monitoring started for project:', project.name)
        addLog('Deploy monitoring started')
      } catch (error) {
        console.error('❌ [APP] Failed to start deploy monitoring:', error)
        addLog('Failed to start deploy monitoring')
      }
    }
  }

  /**
   * Handle deploy detection test
   */
  const handleTestDeploy = () => {
    console.log('🧪 [APP] Testing deploy detection...')
    window.electronAPI?.utils.log('info', 'Testing deploy detection')
    
    setDeployStatus('deploying')
    addLog('Simulating deploy detection...')
    
    // Simulate deploy process
    setTimeout(() => {
      setDeployStatus('completed')
      addLog('Deploy simulation completed')
      
      setTimeout(() => {
        setDeployStatus('idle')
      }, 3000)
    }, 5000)
  }

  return (
    <div className="min-h-screen bg-deploybot-light dark:bg-deploybot-dark">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-deploybot-primary">
                🤖 DeployBot
              </h1>
              <div className={`status-${pythonStatus === 'connected' ? 'online' : 'offline'}`}>
                {pythonStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <DeployStatus status={deployStatus} />
              <button
                onClick={handleTestDeploy}
                className="btn-outline"
                disabled={deployStatus === 'deploying'}
              >
                🧪 Test Deploy
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-screen pt-16">
        {/* Sidebar */}
        <aside className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 overflow-y-auto scrollbar-thin">
          <div className="p-6">
            <ProjectSelector 
              selectedProject={selectedProject}
              onProjectSelect={handleProjectSelect}
            />
          </div>
        </aside>

        {/* Main Panel */}
        <main className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="p-6">
            {selectedProject ? (
              <div className="space-y-6">
                {/* Project Header */}
                <div className="card">
                  <div className="card-header">
                    <h2 className="text-xl font-semibold">
                      📁 {selectedProject.name}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {selectedProject.path}
                    </p>
                  </div>
                </div>

                {/* Task List */}
                <TaskList project={selectedProject} />

                {/* Python Connection Test */}
                <TestPythonConnection />
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📂</div>
                <h2 className="text-2xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  No Project Selected
                </h2>
                <p className="text-gray-500 dark:text-gray-500">
                  Select or create a project from the sidebar to get started
                </p>
              </div>
            )}
          </div>
        </main>

        {/* Activity Log Panel */}
        <aside className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700">
          <ActivityLog logs={logs} />
        </aside>
      </div>
    </div>
  )
}

export default App 