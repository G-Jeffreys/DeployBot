import React, { useState, useEffect } from 'react'

const DeployStatus = ({ status, timerData }) => {
  // Remove mock timer simulation - we'll use real timer data from props
  console.log('🚀 [DEPLOY_STATUS] Rendering with status:', status, 'timerData:', timerData)

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
        
        {/* Timer and Progress for Active Deployments */}
        {(status === 'deploying' || timerData?.isActive) && timerData && (
          <div className="mt-1">
            <div className="text-xs text-gray-600 dark:text-gray-300">
              ⏰ {timerData.timeRemaining || 'Timer active'}
            </div>
            
            {/* Progress Bar */}
            <div className="w-32 h-1 bg-gray-200 dark:bg-gray-600 rounded-full mt-1">
              <div 
                className={`h-1 rounded-full transition-all duration-500 ${
                  timerData.remainingSeconds > 300 ? 'bg-green-500' : 'bg-yellow-500'
                }`}
                style={{ width: `${Math.max(0, Math.min(100, timerData.progressPercentage || 0))}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DeployStatus 