import React, { useState, useEffect } from 'react'

// Global activity manager to prevent duplicate event handlers
let globalActivityManager = null
let globalActivities = []
let globalListeners = []

// Generate UUID for unique activity IDs
function generateUUID() {
  return 'xxxx-xxxx-4xxx-yxxx-xxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

function ActivityLog({ project }) {
  const [activities, setActivities] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const [filter, setFilter] = useState('all')

  console.log('📋 [ACTIVITY_LOG] Component rendering with project:', project?.name)

  // Initialize global activity manager once
  useEffect(() => {
    console.log('📋 [ACTIVITY_LOG] Initializing global activity manager...')
    
    if (!globalActivityManager) {
      console.log('📋 [ACTIVITY_LOG] Creating new global activity manager')
      
      globalActivityManager = {
        addActivity: (activity) => {
          console.log('📋 [ACTIVITY_LOG] Adding global activity:', activity.message)
          globalActivities = [activity, ...globalActivities.slice(0, 49)] // Keep max 50
          // Notify all listeners
          globalListeners.forEach(listener => {
            try {
              listener([...globalActivities])
            } catch (error) {
              console.error('📋 [ACTIVITY_LOG] Error notifying listener:', error)
            }
          })
        },
        
        registerListener: (listener) => {
          console.log('📋 [ACTIVITY_LOG] Registering new listener')
          globalListeners.push(listener)
          // Send current activities to new listener
          listener([...globalActivities])
          
          return () => {
            console.log('📋 [ACTIVITY_LOG] Unregistering listener')
            const index = globalListeners.indexOf(listener)
            if (index > -1) {
              globalListeners.splice(index, 1)
            }
          }
        },
        
        handleBackendUpdate: (data) => {
          console.log('📋 [ACTIVITY_LOG] Global backend update:', data.type, data.event || data.command)
          
          // Skip response events - they're handled by requesting components
          if (data.type === 'response') {
            return
          }
          
          // Create activity from backend event
          let activity = null
          
          if (data.type === 'activity' && data.activity) {
            // Direct activity data
            activity = {
              ...data.activity,
              id: data.activity.id || `activity-${generateUUID()}`
            }
          } else if (data.event) {
            // Convert event to activity
            activity = {
              id: `event-${generateUUID()}`,
              timestamp: data.timestamp || new Date().toISOString(),
              type: data.type || 'system',
              message: data.message || `${data.event} event occurred`,
              data: data.data || {},
              project: data.data?.project_name || 'Global',
              event: data.event
            }
          }
          
          if (activity) {
            globalActivityManager.addActivity(activity)
          }
        }
      }
      
      // Set up WebSocket listener (only once globally)
      if (window.electronAPI?.events?.onBackendUpdate) {
        console.log('📋 [ACTIVITY_LOG] Setting up global WebSocket listener')
        window.electronAPI.events.onBackendUpdate(globalActivityManager.handleBackendUpdate)
      } else {
        console.error('❌ [ACTIVITY_LOG] electronAPI.events.onBackendUpdate not available')
      }
      
      // Add initial activity
      globalActivityManager.addActivity({
        id: `startup-${generateUUID()}`,
        timestamp: new Date().toISOString(),
        type: 'system',
        message: 'DeployBot activity monitoring started',
        data: { component: 'ActivityLog' },
        project: 'System'
      })
    }
    
    // Register this component as a listener
    const unregister = globalActivityManager.registerListener(setActivities)
    
    return unregister
  }, []) // Empty dependency array - run only once
  
  // Connection status monitoring - REMOVED: Let App.jsx handle connection monitoring
  // to prevent redundant checks that cause project list refreshing
  useEffect(() => {
    console.log('📋 [ACTIVITY_LOG] Skipping redundant connection monitoring - App.jsx handles this')
    
    // Just set initial connected state without polling
    setIsConnected(true) // Assume connected until we know otherwise
  }, [])

  // Get activity icon based on type and event
  const getActivityIcon = (activity) => {
    switch (activity.type) {
      case 'deploy':
        switch (activity.event) {
          case 'detected': return '🚀'
          case 'started': return '⏳'
          case 'completed': return '✅'
          case 'failed': return '❌'
          default: return '📦'
        }
      case 'timer':
        switch (activity.event) {
          case 'started': return '⏰'
          case 'stopped': return '⏹️'
          case 'completed': return '⏰'
          default: return '⏱️'
        }
      case 'task':
        switch (activity.event) {
          case 'selected': return '🎯'
          case 'suggested': return '💡'
          case 'opened': return '📱'
          default: return '📝'
        }
      case 'project':
        switch (activity.event) {
          case 'created': return '📁'
          case 'loaded': return '📂'
          case 'deleted': return '🗑️'
          default: return '📁'
        }
      case 'monitoring':
        switch (activity.event) {
          case 'started': return '👁️'
          case 'stopped': return '💤'
          default: return '📊'
        }
      case 'system':
        return '⚙️'
      case 'error':
        return '❌'
      case 'warning':
        return '⚠️'
      default:
        return '📋'
    }
  }

  // Filter activities based on selected filter
  const filteredActivities = activities.filter(activity => {
    if (filter === 'all') return true
    return activity.type === filter
  })

  // Format timestamp for display
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  // Get unique activity types for filter options
  const availableTypes = [...new Set(activities.map(a => a.type))]

  console.log('📋 [ACTIVITY_LOG] Rendering with', activities.length, 'activities')

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">📋 Activity Log</h2>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-500">
            {filteredActivities.length} activities
          </span>
          
          {/* Filter dropdown */}
          {availableTypes.length > 1 && (
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-xs border border-gray-300 rounded px-2 py-1 bg-white"
            >
              <option value="all">All Types</option>
              {availableTypes.map(type => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          )}
          
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-500">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {filteredActivities.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No activities yet. Deploy something to see activity!</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredActivities.map((activity) => (
              <div key={activity.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">
                        {getActivityIcon(activity)}
                      </span>
                      
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        activity.type === 'deploy' ? 'bg-blue-100 text-blue-800' :
                        activity.type === 'timer' ? 'bg-yellow-100 text-yellow-800' :
                        activity.type === 'task' ? 'bg-green-100 text-green-800' :
                        activity.type === 'system' ? 'bg-gray-100 text-gray-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {activity.type}
                      </span>
                      
                      {activity.project && activity.project !== 'Global' && (
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {activity.project}
                        </span>
                      )}
                    </div>
                    
                    <p className="mt-1 text-sm text-gray-900">{activity.message}</p>
                    
                    {activity.data && Object.keys(activity.data).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                          View details
                        </summary>
                        <pre className="mt-1 text-xs text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(activity.data, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                  
                  <div className="text-xs text-gray-500 ml-4 flex-shrink-0">
                    {formatTimestamp(activity.timestamp)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ActivityLog 