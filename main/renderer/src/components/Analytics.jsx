import React, { useState, useEffect } from 'react'

/**
 * Analytics Dashboard Component
 * 
 * 📊 PHASE 2: Comprehensive productivity analytics dashboard
 * Features:
 * - Productivity overview with time saved metrics
 * - Deploy session analytics and patterns  
 * - Task suggestion performance analytics
 * - Real-time data via WebSocket integration
 * - Multiple view modes and date range filtering
 */
const Analytics = ({ selectedProject }) => {
  console.log('📊 [ANALYTICS] Component rendering for project:', selectedProject?.name || 'none')

  // Component state
  const [activeTab, setActiveTab] = useState('overview') // overview | deploy | tasks | patterns
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dateRange, setDateRange] = useState(30) // days
  
  // Analytics data state
  const [overviewData, setOverviewData] = useState(null)
  const [deployAnalytics, setDeployAnalytics] = useState(null)
  const [taskAnalytics, setTaskAnalytics] = useState(null)
  const [currentSession, setCurrentSession] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  console.log('📊 [ANALYTICS] Current state:', { 
    activeTab, 
    dateRange, 
    hasOverviewData: !!overviewData,
    hasDeployData: !!deployAnalytics,
    selectedProject: selectedProject?.name 
  })

  // Load analytics data when component mounts or project changes
  useEffect(() => {
    if (selectedProject) {
      console.log('📊 [ANALYTICS] Loading analytics for project:', selectedProject.name)
      loadAllAnalytics()
    } else {
      console.log('📊 [ANALYTICS] No project selected, clearing data')
      clearAnalyticsData()
    }
  }, [selectedProject, dateRange, refreshTrigger])

  // Real-time session monitoring
  useEffect(() => {
    if (selectedProject) {
      loadCurrentSession()
      
      // Set up periodic refresh for current session
      const sessionInterval = setInterval(loadCurrentSession, 10000) // Every 10 seconds
      
      return () => {
        clearInterval(sessionInterval)
      }
    }
  }, [selectedProject])

  /**
   * Load all analytics data
   */
  const loadAllAnalytics = async () => {
    console.log('📊 [ANALYTICS] Loading all analytics data...')
    setIsLoading(true)
    setError(null)

    try {
      // Load data in parallel for better performance
      await Promise.all([
        loadProductivityOverview(),
        loadDeployAnalytics(),
        loadTaskAnalytics(),
        loadCurrentSession()
      ])
      
      console.log('✅ [ANALYTICS] All analytics data loaded successfully')
    } catch (error) {
      console.error('❌ [ANALYTICS] Failed to load analytics:', error)
      setError(error.message)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Load productivity overview data
   */
  const loadProductivityOverview = async () => {
    try {
      console.log('📊 [ANALYTICS] Loading productivity overview...')
      
      const response = await window.electronAPI?.python.sendCommand('get-productivity-overview', {
        last_n_days: dateRange
      })
      
      console.log('📊 [ANALYTICS] Productivity overview response:', response)
      
      // Handle WebSocket response structure
      const data = response?.data || response
      
      if (data?.success) {
        setOverviewData(data.overview)
        console.log('✅ [ANALYTICS] Productivity overview loaded')
      } else {
        throw new Error(data?.message || 'Failed to load productivity overview')
      }
    } catch (error) {
      console.error('❌ [ANALYTICS] Failed to load productivity overview:', error)
      throw error
    }
  }

  /**
   * Load deploy analytics for current project
   */
  const loadDeployAnalytics = async () => {
    try {
      console.log('📊 [ANALYTICS] Loading deploy analytics...')
      
      const response = await window.electronAPI?.python.sendCommand('get-deploy-analytics', {
        project_name: selectedProject.name,
        last_n_days: dateRange
      })
      
      console.log('📊 [ANALYTICS] Deploy analytics response:', response)
      
      // Handle WebSocket response structure
      const data = response?.data || response
      
      if (data?.success) {
        setDeployAnalytics(data.analytics)
        console.log('✅ [ANALYTICS] Deploy analytics loaded')
      } else {
        throw new Error(data?.message || 'Failed to load deploy analytics')
      }
    } catch (error) {
      console.error('❌ [ANALYTICS] Failed to load deploy analytics:', error)
      throw error
    }
  }

  /**
   * Load task analytics for current project
   */
  const loadTaskAnalytics = async () => {
    try {
      console.log('📊 [ANALYTICS] Loading task analytics...')
      
      const response = await window.electronAPI?.python.sendCommand('get-task-analytics', {
        project_name: selectedProject.name,
        last_n_days: dateRange
      })
      
      console.log('📊 [ANALYTICS] Task analytics response:', response)
      
      // Handle WebSocket response structure
      const data = response?.data || response
      
      if (data?.success) {
        setTaskAnalytics(data.analytics)
        console.log('✅ [ANALYTICS] Task analytics loaded')
      } else {
        throw new Error(data?.message || 'Failed to load task analytics')
      }
    } catch (error) {
      console.error('❌ [ANALYTICS] Failed to load task analytics:', error)
      throw error
    }
  }

  /**
   * Load current active session
   */
  const loadCurrentSession = async () => {
    try {
      const response = await window.electronAPI?.python.sendCommand('get-session-status', {
        project_name: selectedProject.name
      })
      
      // Handle WebSocket response structure
      const data = response?.data || response
      
      if (data?.success) {
        setCurrentSession(data.session)
        console.log('📊 [ANALYTICS] Current session loaded:', data.session?.session_id || 'none')
      }
    } catch (error) {
      console.warn('⚠️ [ANALYTICS] Failed to load current session:', error)
      // Don't throw - this is non-critical
    }
  }

  /**
   * Clear all analytics data
   */
  const clearAnalyticsData = () => {
    setOverviewData(null)
    setDeployAnalytics(null)
    setTaskAnalytics(null)
    setCurrentSession(null)
  }

  /**
   * Handle manual refresh
   */
  const handleRefresh = () => {
    console.log('🔄 [ANALYTICS] Manual refresh triggered')
    setRefreshTrigger(prev => prev + 1)
  }

  /**
   * Format duration in minutes to human readable
   */
  const formatDuration = (minutes) => {
    if (!minutes || minutes === 0) return '0 min'
    if (minutes < 60) return `${Math.round(minutes)} min`
    const hours = Math.floor(minutes / 60)
    const mins = Math.round(minutes % 60)
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }

  /**
   * Format percentage for display
   */
  const formatPercentage = (value) => {
    return `${Math.round(value || 0)}%`
  }

  /**
   * Get status indicator based on current session
   */
  const getSessionStatus = () => {
    if (!currentSession) {
      return { icon: '💤', text: 'No Active Session', color: 'text-gray-500' }
    }
    
    if (currentSession.session_status === 'active') {
      return { 
        icon: '🚀', 
        text: `Deploy Active (${formatDuration((Date.now() - new Date(currentSession.session_start)) / 1000 / 60)})`, 
        color: 'text-green-600' 
      }
    }
    
    return { icon: '✅', text: 'Session Complete', color: 'text-blue-600' }
  }

  // Show project selection prompt if no project
  if (!selectedProject) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            📊 Analytics Dashboard
          </h2>
        </div>
        
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Select a Project
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Choose a project from the sidebar to view productivity analytics
          </p>
        </div>
      </div>
    )
  }

  const sessionStatus = getSessionStatus()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            📊 Analytics Dashboard
          </h2>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {selectedProject.name} • Last {dateRange} days
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Current Session Status */}
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-lg bg-gray-50 dark:bg-gray-800 ${sessionStatus.color}`}>
            <span>{sessionStatus.icon}</span>
            <span className="text-sm font-medium">{sessionStatus.text}</span>
          </div>
          
          {/* Date Range Selector */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(Number(e.target.value))}
            className="form-select text-sm"
            disabled={isLoading}
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          
          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="btn-outline"
            title="Refresh analytics data"
          >
            {isLoading ? '🔄' : '🔄'} Refresh
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
            <span>❌</span>
            <span className="font-medium">Error Loading Analytics</span>
          </div>
          <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
          <button
            onClick={handleRefresh}
            className="mt-2 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 underline"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-gray-500 dark:text-gray-400">Loading analytics data...</p>
        </div>
      )}

      {/* Analytics Content */}
      {!isLoading && !error && (
        <>
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', label: '📈 Overview', icon: '📈' },
                { id: 'deploy', label: '🚀 Deploy Analytics', icon: '🚀' },
                { id: 'tasks', label: '🎯 Task Performance', icon: '🎯' },
                { id: 'patterns', label: '📊 Patterns', icon: '📊' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-6">
            {activeTab === 'overview' && (
              <ProductivityOverview 
                overviewData={overviewData}
                deployAnalytics={deployAnalytics}
                currentSession={currentSession}
                dateRange={dateRange}
                formatDuration={formatDuration}
                formatPercentage={formatPercentage}
              />
            )}
            
            {activeTab === 'deploy' && (
              <DeployAnalytics 
                deployAnalytics={deployAnalytics}
                currentSession={currentSession}
                dateRange={dateRange}
                formatDuration={formatDuration}
                formatPercentage={formatPercentage}
              />
            )}
            
            {activeTab === 'tasks' && (
              <TaskAnalytics 
                taskAnalytics={taskAnalytics}
                dateRange={dateRange}
              />
            )}
            
            {activeTab === 'patterns' && (
              <DeployPatterns 
                deployAnalytics={deployAnalytics}
                dateRange={dateRange}
                formatDuration={formatDuration}
                formatPercentage={formatPercentage}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}

/**
 * Productivity Overview Tab Component
 */
const ProductivityOverview = ({ overviewData, deployAnalytics, currentSession, dateRange, formatDuration, formatPercentage }) => {
  console.log('📈 [PRODUCTIVITY_OVERVIEW] Rendering with data:', { hasOverview: !!overviewData, hasDeploy: !!deployAnalytics })

  // Quick stats cards
  const stats = [
    {
      title: 'Total Time Saved',
      value: formatDuration(overviewData?.total_time_saved_minutes || deployAnalytics?.total_time_saved_minutes || 0),
      icon: '⏰',
      description: 'Time recovered through productivity redirections',
      color: 'text-green-600'
    },
    {
      title: 'Deploy Sessions',
      value: deployAnalytics?.total_sessions || 0,
      icon: '🚀',
      description: `Deployment sessions in last ${dateRange} days`,
      color: 'text-blue-600'
    },
    {
      title: 'Switch Rate',
      value: formatPercentage(deployAnalytics?.switch_button_usage_rate || 0),
      icon: '🔀',
      description: 'Percentage of sessions where you switched to tasks',
      color: 'text-purple-600'
    },
    {
      title: 'Productivity Score',
      value: `${Math.round((deployAnalytics?.avg_productivity_score || 0) * 100)}%`,
      icon: '📊',
      description: 'Overall productivity engagement score',
      color: 'text-orange-600'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="text-2xl mr-3">{stat.icon}</div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.title}</p>
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{stat.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Current Session Card */}
      {currentSession && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🚀 Current Deploy Session
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Deploy Command</p>
              <p className="text-sm text-gray-900 dark:text-white font-mono bg-white dark:bg-gray-800 px-2 py-1 rounded mt-1">
                {currentSession.deploy_command}
              </p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Timer Duration</p>
              <p className="text-sm text-gray-900 dark:text-white">
                {formatDuration(currentSession.timer_duration_seconds / 60)} (Cloud propagation time)
              </p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Switch Status</p>
              <p className="text-sm">
                {currentSession.switch_button_pressed ? (
                  <span className="text-green-600 dark:text-green-400">✅ Switched to task</span>
                ) : (
                  <span className="text-gray-500 dark:text-gray-400">⏳ Waiting for switch</span>
                )}
              </p>
            </div>
          </div>
          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Tasks Activity</p>
              <p className="text-sm text-gray-900 dark:text-white">
                {currentSession.tasks_suggested} suggested • {currentSession.tasks_accepted} accepted
              </p>
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Session Started</p>
              <p className="text-sm text-gray-900 dark:text-white">
                {new Date(currentSession.session_start).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Project Summary */}
      {deployAnalytics && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            📊 Project Summary ({dateRange} days)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Deploy Activity</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Total Deployments</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{deployAnalytics.total_deploys}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Avg per Day</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{deployAnalytics.avg_deploys_per_day?.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Avg Time Saved per Session</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatDuration(deployAnalytics.avg_time_saved_per_session_minutes)}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Productivity Metrics</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatPercentage(deployAnalytics.productivity_improvement_rate)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Switch Success Rate</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {formatPercentage(deployAnalytics.switch_button_usage_rate * 100)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* No Data State */}
      {!deployAnalytics && !currentSession && (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            No Analytics Data Yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Start a deployment to begin tracking productivity analytics
          </p>
        </div>
      )}
    </div>
  )
}

/**
 * Deploy Analytics Tab Component
 */
const DeployAnalytics = ({ deployAnalytics, currentSession, dateRange, formatDuration, formatPercentage }) => {
  console.log('🚀 [DEPLOY_ANALYTICS] Rendering with data:', !!deployAnalytics)

  if (!deployAnalytics) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">🚀</div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No Deploy Data
        </h3>
        <p className="text-gray-500 dark:text-gray-400">
          No deployment sessions found in the last {dateRange} days
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Deploy Commands Analysis */}
      {deployAnalytics.most_common_commands && deployAnalytics.most_common_commands.length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🛠️ Most Common Deploy Commands
          </h3>
          
          <div className="space-y-3">
            {deployAnalytics.most_common_commands.map(([command, count], index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <span className="font-mono text-sm bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    {command}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">{count} times</span>
                  <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                    <div 
                      className="h-2 bg-blue-600 rounded-full"
                      style={{ width: `${(count / deployAnalytics.most_common_commands[0][1]) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Time of Day Patterns */}
      {deployAnalytics.deploy_time_patterns && Object.keys(deployAnalytics.deploy_time_patterns).length > 0 && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🕐 Deploy Time Patterns
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(deployAnalytics.deploy_time_patterns).map(([timeOfDay, count]) => {
              const icons = {
                morning: '🌅',
                afternoon: '☀️', 
                evening: '🌆',
                night: '🌙'
              }
              
              return (
                <div key={timeOfDay} className="text-center">
                  <div className="text-2xl mb-2">{icons[timeOfDay] || '🕐'}</div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">{timeOfDay}</p>
                  <p className="text-lg font-bold text-blue-600">{count}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">deploys</p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Deploy Frequency */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📈 Deploy Frequency Analysis
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{deployAnalytics.total_deploys}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Deploys</p>
          </div>
          
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">{deployAnalytics.avg_deploys_per_day?.toFixed(1)}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Avg per Day</p>
          </div>
          
          <div className="text-center">
            <p className="text-2xl font-bold text-purple-600">{deployAnalytics.total_sessions}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Sessions</p>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Task Analytics Tab Component  
 */
const TaskAnalytics = ({ taskAnalytics, dateRange }) => {
  console.log('🎯 [TASK_ANALYTICS] Rendering with data:', !!taskAnalytics)

  return (
    <div className="space-y-6">
      {/* Coming Soon Placeholder */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          🎯 Task Performance Analytics
        </h3>
        
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🚧</div>
          <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Coming Soon
          </h4>
          <p className="text-gray-500 dark:text-gray-400">
            Detailed task suggestion and acceptance analytics will be available in the next update
          </p>
        </div>
      </div>
    </div>
  )
}

/**
 * Deploy Patterns Tab Component
 */
const DeployPatterns = ({ deployAnalytics, dateRange, formatDuration, formatPercentage }) => {
  console.log('📊 [DEPLOY_PATTERNS] Rendering with data:', !!deployAnalytics)

  if (!deployAnalytics) {
    return (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📊</div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No Pattern Data
        </h3>
        <p className="text-gray-500 dark:text-gray-400">
          No deployment patterns found in the last {dateRange} days
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Productivity Trends */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📈 Productivity Trends
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">Switch Rate Trend</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Current Rate</span>
                <span className="text-lg font-bold text-blue-600">
                  {Math.round((deployAnalytics.switch_button_usage_rate || 0) * 100)}%
                </span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div 
                  className="h-2 bg-blue-600 rounded-full"
                  style={{ width: `${(deployAnalytics.switch_button_usage_rate || 0) * 100}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Percentage of sessions where you switched to productive tasks
              </p>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">Time Savings Efficiency</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">Avg per Session</span>
                <span className="text-lg font-bold text-green-600">
                  {Math.round(deployAnalytics.avg_time_saved_per_session_minutes || 0)} min
                </span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div 
                  className="h-2 bg-green-600 rounded-full"
                  style={{ width: `${Math.min(100, (deployAnalytics.avg_time_saved_per_session_minutes || 0) / 30 * 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Average time saved per deployment session
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Weekly Pattern Analysis */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          📅 Weekly Deploy Pattern
        </h3>
        
        <div className="text-center py-8">
          <div className="text-4xl mb-4">📊</div>
          <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Advanced Patterns Coming Soon
          </h4>
          <p className="text-gray-500 dark:text-gray-400">
            Weekly trends, deployment success rates, and predictive analytics will be available soon
          </p>
        </div>
      </div>
    </div>
  )
}

export default Analytics 