import React, { useState, useEffect } from 'react'

const DeployStatus = ({ status }) => {
  const [timeRemaining, setTimeRemaining] = useState(null)
  const [progress, setProgress] = useState(0)

  // Simulate timer countdown when deploying
  useEffect(() => {
    let interval = null
    
    if (status === 'deploying') {
      console.log('🚀 [DEPLOY_STATUS] Starting deploy timer simulation...')
      const startTime = Date.now()
      const duration = 5000 // 5 seconds for demo
      
      interval = setInterval(() => {
        const elapsed = Date.now() - startTime
        const remaining = Math.max(0, duration - elapsed)
        const progressPercent = Math.min(100, (elapsed / duration) * 100)
        
        setTimeRemaining(Math.ceil(remaining / 1000))
        setProgress(progressPercent)
        
        if (remaining <= 0) {
          console.log('✅ [DEPLOY_STATUS] Deploy timer completed')
          clearInterval(interval)
        }
      }, 100)
    } else {
      setTimeRemaining(null)
      setProgress(0)
    }

    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [status])

  /**
   * Get status display information
   */
  const getStatusInfo = () => {
    switch (status) {
      case 'idle':
        return {
          icon: '😴',
          text: 'Idle',
          color: 'text-gray-500 dark:text-gray-400',
          bgColor: 'bg-gray-100 dark:bg-gray-700'
        }
      case 'deploying':
        return {
          icon: '🚀',
          text: 'Deploying',
          color: 'text-yellow-800 dark:text-yellow-200',
          bgColor: 'bg-yellow-100 dark:bg-yellow-800/30'
        }
      case 'completed':
        return {
          icon: '✅',
          text: 'Completed',
          color: 'text-green-800 dark:text-green-200',
          bgColor: 'bg-green-100 dark:bg-green-800/30'
        }
      case 'error':
        return {
          icon: '❌',
          text: 'Error',
          color: 'text-red-800 dark:text-red-200',
          bgColor: 'bg-red-100 dark:bg-red-800/30'
        }
      default:
        return {
          icon: '❓',
          text: 'Unknown',
          color: 'text-gray-500 dark:text-gray-400',
          bgColor: 'bg-gray-100 dark:bg-gray-700'
        }
    }
  }

  const statusInfo = getStatusInfo()

  return (
    <div className={`inline-flex items-center px-3 py-2 rounded-lg ${statusInfo.bgColor}`}>
      <span className="text-lg mr-2">{statusInfo.icon}</span>
      
      <div className="flex flex-col">
        <span className={`text-sm font-medium ${statusInfo.color}`}>
          {statusInfo.text}
        </span>
        
        {/* Timer and Progress for Deploying Status */}
        {status === 'deploying' && (
          <div className="mt-1">
            {timeRemaining !== null && (
              <div className="text-xs text-gray-600 dark:text-gray-300">
                {timeRemaining}s remaining
              </div>
            )}
            
            {/* Progress Bar */}
            <div className="w-24 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mt-1">
              <div 
                className="h-1 bg-yellow-500 rounded-full transition-all duration-200"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DeployStatus 