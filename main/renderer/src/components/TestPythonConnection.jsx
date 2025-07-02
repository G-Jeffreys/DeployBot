import React, { useState } from 'react'

const TestPythonConnection = () => {
  const [testResults, setTestResults] = useState([])
  const [isRunning, setIsRunning] = useState(false)

  /**
   * Run a series of Python backend tests
   */
  const runTests = async () => {
    console.log('🧪 [TEST_PYTHON] Starting Python backend tests...')
    setIsRunning(true)
    setTestResults([])

    const tests = [
      {
        name: 'Python Backend Ping',
        command: 'ping',
        data: { timestamp: Date.now() }
      },
      {
        name: 'LangGraph Status',
        command: 'status',
        data: {}
      },
      {
        name: 'Deploy Monitor Check',
        command: 'check-monitor',
        data: {}
      },
      {
        name: 'Task Selection Test',
        command: 'test-task-selection',
        data: { projectName: 'TestProject' }
      }
    ]

    for (const test of tests) {
      try {
        console.log(`🧪 [TEST_PYTHON] Running test: ${test.name}`)
        
        const startTime = Date.now()
        const response = await window.electronAPI?.python.sendCommand(test.command, test.data)
        const duration = Date.now() - startTime

        const result = {
          ...test,
          success: response?.success !== false,
          response,
          duration,
          timestamp: new Date().toLocaleTimeString()
        }

        setTestResults(prev => [...prev, result])
        console.log(`✅ [TEST_PYTHON] Test completed: ${test.name}`, result)

        // Add a small delay between tests
        await new Promise(resolve => setTimeout(resolve, 500))
        
      } catch (error) {
        console.error(`❌ [TEST_PYTHON] Test failed: ${test.name}`, error)
        
        const result = {
          ...test,
          success: false,
          error: error.message,
          timestamp: new Date().toLocaleTimeString()
        }

        setTestResults(prev => [...prev, result])
      }
    }

    setIsRunning(false)
    console.log('🧪 [TEST_PYTHON] All tests completed')
    window.electronAPI?.utils.log('info', 'Python backend tests completed')
  }

  /**
   * Clear test results
   */
  const clearResults = () => {
    console.log('🧪 [TEST_PYTHON] Clearing test results...')
    setTestResults([])
  }

  /**
   * Test unified notification system
   */
  const testUnifiedNotification = async () => {
    console.log('🔔 [TEST] Testing unified notification system...')
    
    try {
      setIsRunning(true)
      
      // Create a test unified notification
      const testNotification = {
        id: `test_unified_notification_${Date.now()}`,
        title: '🎯⏰ Task & Timer Update',
        message: 'This is a test of the unified notification system',
        data: {
          type: 'unified_suggestion',
          project_name: 'TestProject',
          timer_info: {
            status: 'running',
            time_remaining_formatted: '22:15',
            duration_seconds: 1800
          },
          task: {
            text: 'Write documentation for unified notifications',
            app: 'Bear',
            tags: ['#writing', '#docs'],
            estimated_duration: 25
          },
          context: {
            deploy_active: true,
            timer_duration: 1800
          },
          has_timer: true,
          has_task: true
        },
        actions: ['Switch to Task', 'Start New Timer', 'View Timer', 'Snooze', 'Dismiss'],
        timestamp: new Date().toISOString()
      }
      
      // Show the unified notification
      const response = await window.electronAPI?.notifications.show(testNotification)
      console.log('🔔 [TEST] Unified notification response:', response)
      
      const result = {
        name: 'Unified Notification Test',
        command: 'show-unified-notification',
        data: testNotification,
        success: response?.success === true,
        response,
        timestamp: new Date().toLocaleTimeString()
      }

      setTestResults(prev => [...prev, result])
      
      if (!response?.success) {
        throw new Error(response?.error || 'Failed to show unified notification')
      }
      
    } catch (error) {
      console.error('❌ [TEST] Unified notification test failed:', error)
      
      const result = {
        name: 'Unified Notification Test',
        command: 'show-unified-notification',
        data: {},
        success: false,
        error: error.message,
        timestamp: new Date().toLocaleTimeString()
      }

      setTestResults(prev => [...prev, result])
    } finally {
      setIsRunning(false)
    }
  }

  /**
   * Test custom notification system
   */
  const testCustomNotification = async () => {
    console.log('🔔 [TEST] Testing custom notification system...')
    
    try {
      setIsRunning(true)
      
      // Create a test notification
      const testNotification = {
        id: `test_notification_${Date.now()}`,
        title: '🎯 Test Task Suggestion',
        message: 'This is a test of the custom notification system',
        data: {
          type: 'task_suggestion',
          project_name: 'TestProject',
          task: {
            text: 'Write documentation for custom notifications',
            app: 'Bear',
            tags: ['#writing', '#docs'],
            estimated_duration: 30
          },
          context: {
            deploy_active: true,
            timer_duration: 1800
          }
        },
        actions: ['Switch Now', 'Snooze 5min', 'Dismiss'],
        timestamp: new Date().toISOString()
      }
      
      // Show the custom notification
      const response = await window.electronAPI?.notifications.show(testNotification)
      console.log('🔔 [TEST] Custom notification response:', response)
      
      const result = {
        name: 'Custom Notification Test',
        command: 'show-notification',
        data: testNotification,
        success: response?.success === true,
        response,
        timestamp: new Date().toLocaleTimeString()
      }

      setTestResults(prev => [...prev, result])
      
      if (!response?.success) {
        throw new Error(response?.error || 'Failed to show notification')
      }
      
    } catch (error) {
      console.error('❌ [TEST] Custom notification test failed:', error)
      
      const result = {
        name: 'Custom Notification Test',
        command: 'show-notification',
        data: {},
        success: false,
        error: error.message,
        timestamp: new Date().toLocaleTimeString()
      }

      setTestResults(prev => [...prev, result])
    } finally {
      setIsRunning(false)
    }
  }

  /**
   * Test individual command
   */
  const testCommand = async (command, data = {}) => {
    console.log(`🧪 [TEST_PYTHON] Testing individual command: ${command}`)
    
    try {
      setIsRunning(true)
      const response = await window.electronAPI?.python.sendCommand(command, data)
      
      const result = {
        name: `Manual Test: ${command}`,
        command,
        data,
        success: response?.success !== false,
        response,
        timestamp: new Date().toLocaleTimeString()
      }

      setTestResults(prev => [...prev, result])
      console.log(`✅ [TEST_PYTHON] Manual test completed: ${command}`, result)
      
    } catch (error) {
      console.error(`❌ [TEST_PYTHON] Manual test failed: ${command}`, error)
      
      const result = {
        name: `Manual Test: ${command}`,
        command,
        data,
        success: false,
        error: error.message,
        timestamp: new Date().toLocaleTimeString()
      }

      setTestResults(prev => [...prev, result])
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            🧪 Python Backend Testing
          </h3>
          <div className="space-x-2">
            <button
              onClick={runTests}
              className="btn-primary text-sm"
              disabled={isRunning}
            >
              {isRunning ? '⏳ Running...' : '▶️ Run Tests'}
            </button>
            {testResults.length > 0 && (
              <button
                onClick={clearResults}
                className="btn-outline text-sm"
                disabled={isRunning}
              >
                🗑️ Clear
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="card-body">
        {/* Quick Test Buttons */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Quick Tests:
          </h4>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => testCommand('ping')}
              className="btn-outline text-xs"
              disabled={isRunning}
            >
              📡 Ping
            </button>
            <button
              onClick={() => testCommand('status')}
              className="btn-outline text-xs"
              disabled={isRunning}
            >
              📊 Status
            </button>
            <button
              onClick={() => testCommand('start-monitoring')}
              className="btn-outline text-xs"
              disabled={isRunning}
            >
              🚀 Start Monitor
            </button>
            <button
              onClick={() => testCommand('stop-monitoring')}
              className="btn-outline text-xs"
              disabled={isRunning}
            >
              🛑 Stop Monitor
            </button>
            <button
              onClick={testCustomNotification}
              className="btn-outline text-xs"
              disabled={isRunning}
            >
              🔔 Test Notification
            </button>
            <button
              onClick={testUnifiedNotification}
              className="btn-outline text-xs"
              disabled={isRunning}
            >
              🎯⏰ Test Unified
            </button>
          </div>
        </div>

        {/* Test Results */}
        {testResults.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <div className="text-4xl mb-2">🧪</div>
            <p>No tests run yet</p>
            <p className="text-sm mt-1">
              Run tests to verify Python backend connectivity
            </p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-thin">
            {testResults.map((result, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${
                  result.success
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                    : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">
                        {result.success ? '✅' : '❌'}
                      </span>
                      <h5 className="font-medium text-gray-900 dark:text-white">
                        {result.name}
                      </h5>
                      {result.duration && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          ({result.duration}ms)
                        </span>
                      )}
                    </div>
                    
                    <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                      <span className="font-mono bg-gray-100 dark:bg-gray-700 px-1 rounded">
                        {result.command}
                      </span>
                      <span className="ml-2 text-xs">
                        {result.timestamp}
                      </span>
                    </div>

                    {/* Response or Error */}
                    {result.response && (
                      <div className="mt-2">
                        <details className="text-xs">
                          <summary className="cursor-pointer text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
                            Response Data
                          </summary>
                          <pre className="mt-1 p-2 bg-gray-100 dark:bg-gray-700 rounded font-mono text-xs overflow-x-auto">
                            {JSON.stringify(result.response, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}

                    {result.error && (
                      <div className="mt-2 text-xs text-red-600 dark:text-red-400 font-mono bg-red-100 dark:bg-red-900/30 p-2 rounded">
                        {result.error}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Summary */}
        {testResults.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">
                Test Summary:
              </span>
              <div className="space-x-4">
                <span className="text-green-600 dark:text-green-400">
                  ✅ {testResults.filter(r => r.success).length} passed
                </span>
                <span className="text-red-600 dark:text-red-400">
                  ❌ {testResults.filter(r => !r.success).length} failed
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TestPythonConnection 