import React, { useState, useEffect } from 'react'

const TaskList = ({ project }) => {
  const [tasks, setTasks] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [taskStats, setTaskStats] = useState(null)

  console.log('📝 [TASK_LIST] Component mounted with project:', project?.name || 'none')

  // Load tasks when project changes
  useEffect(() => {
    console.log('📝 [TASK_LIST] useEffect triggered - project:', project?.name || 'none')
    
    if (project) {
      console.log('📝 [TASK_LIST] Loading tasks for project:', project.name)
      loadTasks()
    } else {
      console.log('📝 [TASK_LIST] No project selected, clearing tasks')
      setTasks([])
      setTaskStats(null)
    }
  }, [project])

  /**
   * Load tasks from the project's TODO.md file using real backend
   */
  const loadTasks = async () => {
    setIsLoading(true)
    setError(null)
    console.log('📝 [TASK_LIST] Loading tasks from backend for project:', project.path)
    
    try {
      // Get task suggestions from the sophisticated backend parser
      const response = await window.electronAPI?.tasks.getSuggestions(project.path, {
        project_name: project.name,
        load_all_tasks: true,
        include_completed: true
      })
      
      console.log('📝 [TASK_LIST] Backend response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response;
      
      if (data && data.success && data.task) {
        // If we got a single task, it means the TODO.md doesn't exist or is empty
        // Let's try to get the full project data which includes parsed tasks
        const projectResponse = await window.electronAPI?.project.open({ path: project.path })
        
        // Handle WebSocket response structure for project data
        const projectData = projectResponse?.data || projectResponse;
        
        if (projectData && projectData.success && projectData.project) {
          const fullProjectData = projectData.project
          console.log('📝 [TASK_LIST] Full project data:', JSON.stringify(fullProjectData, null, 2))
          
          if (fullProjectData.tasks && Array.isArray(fullProjectData.tasks)) {
            setTasks(fullProjectData.tasks)
            setTaskStats({
              total: fullProjectData.tasks.length,
              pending: fullProjectData.tasks.filter(t => !t.completed).length,
              completed: fullProjectData.tasks.filter(t => t.completed).length
            })
          } else {
            // No tasks found, set empty state
            setTasks([])
            setTaskStats({ total: 0, pending: 0, completed: 0 })
          }
        } else {
          throw new Error(projectData?.message || projectData?.error || 'Failed to load project data')
        }
      } else if (data && !data.success) {
        throw new Error(data?.message || data?.error || 'Failed to load tasks')
      } else {
        // Empty response, no tasks
        setTasks([])
        setTaskStats({ total: 0, pending: 0, completed: 0 })
      }
      
      console.log('✅ [TASK_LIST] Tasks loaded successfully')
    } catch (error) {
      console.error('❌ [TASK_LIST] Failed to load tasks:', error)
      console.error('❌ [TASK_LIST] Error details:', JSON.stringify(error, null, 2))
      setError(error.message)
      window.electronAPI?.utils.log('error', 'Failed to load tasks', error)
      
      // Set empty state on error
      setTasks([])
      setTaskStats({ total: 0, pending: 0, completed: 0 })
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Toggle task completion status
   */
  const toggleTask = async (taskId) => {
    console.log('📝 [TASK_LIST] Toggling task:', taskId)
    
    setTasks(prevTasks => 
      prevTasks.map(task => 
        task.id === taskId 
          ? { ...task, completed: !task.completed }
          : task
      )
    )
    
    // Update stats
    const updatedTasks = tasks.map(task => 
      task.id === taskId 
        ? { ...task, completed: !task.completed }
        : task
    )
    
    setTaskStats({
      total: updatedTasks.length,
      pending: updatedTasks.filter(t => !t.completed).length,
      completed: updatedTasks.filter(t => t.completed).length
    })
    
    window.electronAPI?.utils.log('info', 'Task toggled', { taskId })
  }

  /**
   * Open the associated app for a task using real redirection system
   */
  const openTaskApp = async (task) => {
    console.log('📝 [TASK_LIST] Opening app for task:', task.text, 'App:', task.app)
    
    try {
      // Use the sophisticated redirection system
      const context = {
        project_name: project.name,
        project_path: project.path,
        redirect_reason: 'manual_task_selection'
      }
      
      const response = await window.electronAPI?.tasks.redirectToTask(task, context)
      console.log('📝 [TASK_LIST] Redirection response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response;
      
      if (data && data.success) {
        console.log('✅ [TASK_LIST] Task redirection successful:', data)
        window.electronAPI?.utils.log('info', 'Task app opened successfully', { 
          task: task.text, 
          app: task.app,
          redirect_result: data.redirect_result 
        })
      } else {
        throw new Error(data?.message || data?.error || 'Redirection failed')
      }
    } catch (error) {
      console.error('❌ [TASK_LIST] Failed to open app:', error)
      console.error('❌ [TASK_LIST] Error details:', JSON.stringify(error, null, 2))
      window.electronAPI?.utils.log('error', 'Failed to open task app', error)
      
      // Fallback to simple app opening
      try {
        await window.electronAPI?.python.sendCommand('open-app', {
          app: task.app,
          task: task.text,
          tags: task.tags,
          project: project.name
        })
      } catch (fallbackError) {
        console.error('❌ [TASK_LIST] Fallback app opening also failed:', fallbackError)
      }
    }
  }

  /**
   * Get a smart task suggestion using the AI backend
   */
  const getTaskSuggestion = async () => {
    console.log('🎯 [TASK_LIST] Getting AI task suggestion...')
    setIsLoading(true)
    
    try {
      const context = {
        project_name: project.name,
        deploy_active: false, // Manual suggestion
        timer_duration: 1800,
        use_llm: true
      }
      
      const response = await window.electronAPI?.tasks.getSuggestions(project.path, context)
      console.log('🎯 [TASK_LIST] Task suggestion response:', JSON.stringify(response, null, 2))
      
      // Handle WebSocket response structure - data is nested under response.data
      const data = response?.data || response;
      
      if (data && data.success && data.task) {
        console.log('🎯 [TASK_LIST] AI suggested task:', data.task)
        
        // Highlight the suggested task in the UI
        const suggestedTask = data.task
        
        // Automatically open the suggested task
        if (confirm(`AI suggests: "${suggestedTask.text}"\nOpen in ${suggestedTask.app}?`)) {
          await openTaskApp(suggestedTask)
        }
      } else {
        console.warn('⚠️ [TASK_LIST] No task suggestion available')
        alert('No suitable task suggestions available for this project.')
      }
    } catch (error) {
      console.error('❌ [TASK_LIST] Failed to get task suggestion:', error)
      console.error('❌ [TASK_LIST] Error details:', JSON.stringify(error, null, 2))
      alert(`Failed to get task suggestion: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Test the task selection system
   */
  const testTaskSelection = async () => {
    console.log('🧪 [TASK_LIST] Testing task selection system...')
    
    try {
      const response = await window.electronAPI?.tasks.testSelection(project.name)
      console.log('🧪 [TASK_LIST] Task selection test result:', response)
      
      // Handle WebSocket response structure
      const data = response?.data || response;
      
      if (data && data.success) {
        alert(`Task selection test successful!\nSelected: ${data.selected_task?.text || 'No task'}\nApp: ${data.selected_task?.app || 'N/A'}`)
      } else {
        alert('Task selection test failed')
      }
    } catch (error) {
      console.error('❌ [TASK_LIST] Task selection test failed:', error)
      alert(`Test failed: ${error.message}`)
    }
  }

  /**
   * Get tag styling based on tag type
   */
  const getTagClass = (tag) => {
    const tagType = tag.replace('#', '')
    switch (tagType) {
      case 'short': return 'tag tag-short'
      case 'long': return 'tag tag-long'
      case 'code': case 'backend': return 'tag tag-code'
      case 'writing': case 'creative': return 'tag tag-writing'
      case 'research': return 'tag tag-research'
      case 'solo': return 'tag bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
      case 'collab': return 'tag bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100'
      default: return 'tag bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }
  }

  if (!project) {
    console.log('📝 [TASK_LIST] No project provided, rendering placeholder')
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-2">📂</div>
        <p className="text-gray-500 dark:text-gray-400">Select a project to view tasks</p>
      </div>
    )
  }

  console.log('📝 [TASK_LIST] Rendering TaskList for project:', project.name)

  return (
    <>
      <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            {taskStats && (
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {taskStats.pending} pending • {taskStats.completed} completed
              </div>
            )}
        </div>
        <div className="flex items-center space-x-2">
            <button
              onClick={getTaskSuggestion}
              className="btn-primary text-xs"
              disabled={isLoading || tasks.length === 0}
              title="Get AI task suggestion"
            >
              🎯 Suggest
            </button>
            <button
              onClick={testTaskSelection}
              className="btn-outline text-xs"
              disabled={isLoading}
              title="Test task selection system"
            >
              🧪 Test
            </button>
        </div>
      </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
              <span>❌</span>
              <span className="text-sm font-medium">Error loading tasks</span>
            </div>
            <p className="text-red-600 dark:text-red-400 text-sm mt-1">{error}</p>
            <button
              onClick={loadTasks}
              className="mt-2 text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 underline"
            >
              Try again
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">⏳</div>
            <p className="text-gray-500 dark:text-gray-400">Loading tasks from backend...</p>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📝</div>
            <p className="text-gray-500 dark:text-gray-400">No tasks found</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Add tasks to your TODO.md file in the project directory
            </p>
            <button
              onClick={loadTasks}
              className="mt-2 btn-outline text-sm"
            >
              🔄 Refresh
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <div
                key={task.id}
                className={`group p-4 border rounded-lg transition-all duration-200 hover:shadow-sm ${
                  task.completed
                    ? 'bg-gray-50 dark:bg-gray-700/50 border-gray-200 dark:border-gray-600'
                    : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 hover:border-deploybot-primary'
                }`}
              >
                <div className="flex items-start space-x-3">
                  {/* Checkbox */}
                  <button
                    onClick={() => toggleTask(task.id)}
                    className={`mt-1 w-5 h-5 rounded border-2 transition-colors duration-200 ${
                      task.completed
                        ? 'bg-deploybot-secondary border-deploybot-secondary text-white'
                        : 'border-gray-300 dark:border-gray-600 hover:border-deploybot-primary'
                    }`}
                  >
                    {task.completed && <span className="text-xs">✓</span>}
                  </button>

                  {/* Task Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className={`font-medium ${
                          task.completed
                            ? 'text-gray-500 dark:text-gray-400 line-through'
                            : 'text-gray-900 dark:text-white'
                        }`}>
                          {task.text}
                        </p>
                        
                        {/* Task metadata */}
                        {(task.priority || task.estimated_duration) && (
                          <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                            {task.priority && <span>Priority: {task.priority}/10</span>}
                            {task.priority && task.estimated_duration && <span> • </span>}
                            {task.estimated_duration && <span>~{task.estimated_duration}min</span>}
                          </div>
                        )}
                      </div>
                      
                      {/* Open App Button */}
                      {!task.completed && task.app && (
                        <button
                          onClick={() => openTaskApp(task)}
                          className="btn-outline text-xs ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                          title={`Open in ${task.app}`}
                        >
                          📱 {task.app}
                        </button>
                      )}
                    </div>

                    {/* Tags */}
                    {task.tags && task.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {task.tags.map((tag, index) => (
                          <span
                            key={index}
                            className={getTagClass(tag)}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
    </>
  )
}

export default TaskList 