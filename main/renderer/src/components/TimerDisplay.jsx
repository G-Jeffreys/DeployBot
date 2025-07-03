import React, { useState, useEffect } from 'react'

/**
 * TimerDisplay Component
 * 
 * Displays real deployment timer information from the backend
 * Connects to WebSocket updates for live timer data
 */
const TimerDisplay = ({ selectedProject, onTimerUpdate }) => {
  const [timerData, setTimerData] = useState(null)
  const [isActive, setIsActive] = useState(false)
  const [error, setError] = useState(null)

  // Timer status monitoring with auto-refresh - MEMORY LEAK FIX: Reduced frequency and better cleanup
  useEffect(() => {
    console.log('⏰ [TIMER_DISPLAY] Setting up timer monitoring for project:', selectedProject?.name || 'none')
    
    if (!selectedProject) {
      console.log('⏰ [TIMER_DISPLAY] No project selected, clearing timer data')
      setTimerData(null)
      setIsActive(false)
      return
    }

    let pollInterval = null

    const checkTimerStatus = async () => {
      try {
        console.log('⏰ [TIMER_DISPLAY] Checking timer status for project:', selectedProject.name)
        
        const response = await window.electronAPI?.timer.status(selectedProject.name)
        console.log('⏰ [TIMER_DISPLAY] Timer status response:', JSON.stringify(response, null, 2))
        
        // Handle WebSocket response structure
        const data = response?.data || response
        
        if (data && data.success) {
          const timerInfo = data.timer_info
          const wasActive = isActive
          
          if (timerInfo && timerInfo.status === 'running' && timerInfo.remaining_seconds > 0) {
            // Timer is active
            setTimerData(timerInfo)
            setIsActive(true)
            setError(null)
            
            // Notify parent about timer state change
            if (typeof onTimerUpdate === 'function') {
              onTimerUpdate({ 
                isActive: true, 
                ...timerInfo 
              })
            }
            
            if (!wasActive) {
              console.log('⏰ [TIMER_DISPLAY] Timer became active')
            }
          } else {
            // No active timer
            setTimerData(null)
            setIsActive(false)
            setError(null)
            
            // Notify parent about timer state change
            if (typeof onTimerUpdate === 'function') {
              onTimerUpdate({ isActive: false })
            }
            
            if (wasActive) {
              console.log('⏰ [TIMER_DISPLAY] Timer became inactive')
            }
          }
        } else {
          console.log('⚠️ [TIMER_DISPLAY] No timer data or failed response')
          setTimerData(null)
          setIsActive(false)
          
          if (typeof onTimerUpdate === 'function') {
            onTimerUpdate({ isActive: false })
          }
        }
      } catch (error) {
        console.error('❌ [TIMER_DISPLAY] Failed to get timer status:', error)
        setError(error.message)
        
        // Don't clear timer data on error, might be temporary connection issue
        if (!timerData) {
          setIsActive(false)
          if (typeof onTimerUpdate === 'function') {
            onTimerUpdate({ isActive: false })
          }
        }
      }
    }

    // Initial check
    checkTimerStatus()
    
    // MEMORY LEAK FIX: Reduced from 2 seconds to 3 seconds to reduce load
    if (selectedProject) {
      pollInterval = setInterval(checkTimerStatus, 3000)
    }

    return () => {
      console.log('🧹 [TIMER_DISPLAY] Cleaning up timer monitoring...')
      if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
      }
    }
  }, [selectedProject?.name, onTimerUpdate]) // Include onTimerUpdate in dependencies

  // Handle timer actions
  const handleStopTimer = async () => {
    if (!selectedProject || !timerData) return
    
    try {
      console.log('⏹️ [TIMER_DISPLAY] Stopping timer for project:', selectedProject.name)
      const response = await window.electronAPI?.timer.stop(selectedProject.name)
      console.log('⏹️ [TIMER_DISPLAY] Stop timer response:', response)
      
      // Clear timer data immediately for responsive UI
      setTimerData(null)
      setIsActive(false)
    } catch (error) {
      console.error('❌ [TIMER_DISPLAY] Failed to stop timer:', error)
      setError(error.message)
    }
  }

  const handleStartTimer = async () => {
    if (!selectedProject) return
    
    try {
      console.log('▶️ [TIMER_DISPLAY] Starting timer for project:', selectedProject.name)
      const response = await window.electronAPI?.timer.start(selectedProject.name, 1800) // 30 minutes default
      console.log('▶️ [TIMER_DISPLAY] Start timer response:', response)
      
      // Timer data will be updated by the polling mechanism
    } catch (error) {
      console.error('❌ [TIMER_DISPLAY] Failed to start timer:', error)
      setError(error.message)
    }
  }

  // Format time remaining display
  const formatTimeRemaining = (seconds) => {
    if (!seconds || seconds <= 0) return '00:00'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    
    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    } else {
      return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
  }

  // Get status color based on timer state
  const getStatusColor = () => {
    if (!timerData || !isActive) return 'text-gray-500'
    
    switch (timerData.status) {
      case 'running':
        return timerData.remainingSeconds > 300 ? 'text-green-600' : 'text-yellow-600' // Yellow if < 5 minutes
      case 'paused':
        return 'text-blue-600'
      case 'expired':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  // Get status icon
  const getStatusIcon = () => {
    if (!timerData || !isActive) return '⏰'
    
    switch (timerData.status) {
      case 'running':
        return timerData.remainingSeconds > 300 ? '⏰' : '⚠️'
      case 'paused':
        return '⏸️'
      case 'expired':
        return '⏰'
      default:
        return '⏰'
    }
  }

  // Don't render if no selected project
  if (!selectedProject) {
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
          <span>⏰</span>
          <span>Deploy Timer</span>
        </h3>
        
        {error && (
          <span className="text-xs text-red-500 bg-red-50 px-2 py-1 rounded">
            Error: {error}
          </span>
        )}
      </div>

      {/* Timer Display */}
      {isActive && timerData ? (
        <div className="space-y-3">
          {/* Main Timer Display */}
          <div className="text-center">
            <div className={`text-3xl font-bold ${getStatusColor()}`}>
              {getStatusIcon()} {timerData.timeRemaining || formatTimeRemaining(timerData.remainingSeconds)}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {timerData.status === 'running' ? 'Remaining' : 
               timerData.status === 'paused' ? 'Paused' : 'Timer Status'}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${
                timerData.remainingSeconds > 300 ? 'bg-green-500' : 'bg-yellow-500'
              }`}
              style={{ width: `${Math.max(0, Math.min(100, timerData.progressPercentage || 0))}%` }}
            />
          </div>

          {/* Timer Info */}
          <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <div className="flex justify-between">
              <span>Project:</span>
              <span className="font-medium">{timerData.projectName}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Duration:</span>
              <span>{formatTimeRemaining(timerData.totalDuration)}</span>
            </div>
            {timerData.deployCommand && (
              <div className="flex justify-between">
                <span>Deploy Command:</span>
                <span className="font-mono text-xs truncate max-w-24" title={timerData.deployCommand}>
                  {timerData.deployCommand}
                </span>
              </div>
            )}
          </div>

          {/* Timer Controls */}
          <div className="flex space-x-2">
            <button
              onClick={handleStopTimer}
              className="flex-1 px-3 py-2 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
            >
              ⏹️ Stop Timer
            </button>
          </div>
        </div>
      ) : (
        /* No Active Timer */
        <div className="text-center py-4">
          <div className="text-gray-400 dark:text-gray-500 text-4xl mb-2">⏰</div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            No active deployment timer
          </p>
          <button
            onClick={handleStartTimer}
            className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
          >
            ▶️ Start Timer
          </button>
        </div>
      )}
    </div>
  )
}

export default TimerDisplay 