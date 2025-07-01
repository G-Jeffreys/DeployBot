import React, { useEffect, useRef } from 'react'

const ActivityLog = ({ logs }) => {
  const logContainerRef = useRef(null)

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs])

  /**
   * Get log entry styling based on content
   */
  const getLogEntryClass = (logEntry) => {
    const entry = logEntry.toLowerCase()
    
    if (entry.includes('error') || entry.includes('failed')) {
      return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20'
    } else if (entry.includes('deploy') || entry.includes('monitoring')) {
      return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
    } else if (entry.includes('completed') || entry.includes('success')) {
      return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20'
    } else if (entry.includes('project') || entry.includes('opened')) {
      return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
    }
    
    return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50'
  }

  /**
   * Extract timestamp from log entry
   */
  const extractTimestamp = (logEntry) => {
    const timestampMatch = logEntry.match(/^\[(\d{1,2}:\d{2}:\d{2}(?:\s?[AP]M)?)\]/)
    return timestampMatch ? timestampMatch[1] : null
  }

  /**
   * Get log content without timestamp
   */
  const getLogContent = (logEntry) => {
    const timestampMatch = logEntry.match(/^\[[\d:APM\s]+\]\s*(.+)$/)
    return timestampMatch ? timestampMatch[1] : logEntry
  }

  /**
   * Clear all logs
   */
  const clearLogs = () => {
    console.log('📋 [ACTIVITY_LOG] Clearing activity logs...')
    // This would typically call a parent function to clear logs
    window.electronAPI?.utils.log('info', 'Activity logs cleared')
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            📋 Activity Log
          </h3>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {logs.length} entries
            </span>
            {logs.length > 0 && (
              <button
                onClick={clearLogs}
                className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                title="Clear logs"
              >
                🗑️
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Log Content */}
      <div 
        ref={logContainerRef}
        className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-2"
      >
        {logs.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400">
            <div className="text-4xl mb-2">📝</div>
            <p>No activity yet</p>
            <p className="text-sm mt-1">
              System events will appear here
            </p>
          </div>
        ) : (
          logs.map((logEntry, index) => {
            const timestamp = extractTimestamp(logEntry)
            const content = getLogContent(logEntry)
            
            return (
              <div
                key={index}
                className={`p-2 rounded text-xs font-mono border ${getLogEntryClass(logEntry)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {timestamp && (
                      <span className="text-gray-500 dark:text-gray-400 mr-2">
                        {timestamp}
                      </span>
                    )}
                    <span className="break-words">
                      {content}
                    </span>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Footer with Connection Status */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500 dark:text-gray-400">
            Real-time monitoring
          </span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-600 dark:text-green-400">
              Live
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ActivityLog 