import React, { useState, useEffect } from 'react'

const TaskList = ({ project }) => {
  const [tasks, setTasks] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  // Load tasks when project changes
  useEffect(() => {
    if (project) {
      console.log('📝 [TASK_LIST] Loading tasks for project:', project.name)
      loadTasks()
    }
  }, [project])

  /**
   * Load tasks from the project's TODO.md file
   */
  const loadTasks = async () => {
    setIsLoading(true)
    console.log('📝 [TASK_LIST] Loading tasks from TODO.md...')
    
    try {
      // For now, we'll use mock data that demonstrates the task structure
      const mockTasks = [
        {
          id: 1,
          text: 'Write script for product video',
          tags: ['#short', '#creative', '#solo'],
          completed: false,
          app: 'Notion'
        },
        {
          id: 2,
          text: 'Review Firebase rules',
          tags: ['#research', '#backend'],
          completed: false,
          app: 'VSCode'
        },
        {
          id: 3,
          text: 'Update documentation',
          tags: ['#writing', '#long'],
          completed: true,
          app: 'Bear'
        },
        {
          id: 4,
          text: 'Design new feature mockups',
          tags: ['#creative', '#short', '#solo'],
          completed: false,
          app: 'Figma'
        }
      ]
      
      setTasks(mockTasks)
      console.log('✅ [TASK_LIST] Tasks loaded:', mockTasks)
    } catch (error) {
      console.error('❌ [TASK_LIST] Failed to load tasks:', error)
      window.electronAPI?.utils.log('error', 'Failed to load tasks', error)
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
    
    window.electronAPI?.utils.log('info', 'Task toggled', { taskId })
  }

  /**
   * Open the associated app for a task
   */
  const openTaskApp = async (task) => {
    console.log('📝 [TASK_LIST] Opening app for task:', task.text, 'App:', task.app)
    
    try {
      // This would eventually trigger the redirection logic
      await window.electronAPI?.python.sendCommand('open-app', {
        app: task.app,
        task: task.text,
        tags: task.tags
      })
      
      window.electronAPI?.utils.log('info', 'Task app opened', { task: task.text, app: task.app })
    } catch (error) {
      console.error('❌ [TASK_LIST] Failed to open app:', error)
      window.electronAPI?.utils.log('error', 'Failed to open task app', error)
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
      default: return 'tag bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }
  }

  if (!project) {
    return null
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            📝 Tasks
          </h3>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {tasks.filter(t => !t.completed).length} pending • {tasks.filter(t => t.completed).length} completed
          </div>
        </div>
      </div>

      <div className="card-body">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">⏳</div>
            <p className="text-gray-500 dark:text-gray-400">Loading tasks...</p>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📝</div>
            <p className="text-gray-500 dark:text-gray-400">No tasks found</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Add tasks to your TODO.md file
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <div
                key={task.id}
                className={`p-4 border rounded-lg transition-all duration-200 hover:shadow-sm ${
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
                      <p className={`font-medium ${
                        task.completed
                          ? 'text-gray-500 dark:text-gray-400 line-through'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {task.text}
                      </p>
                      
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

                    {/* App Association */}
                    {task.app && (
                      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                        📱 Opens in {task.app}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Task Statistics */}
        {tasks.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-semibold text-deploybot-primary">
                  {tasks.length}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Total Tasks
                </div>
              </div>
              <div>
                <div className="text-lg font-semibold text-deploybot-accent">
                  {tasks.filter(t => !t.completed).length}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Pending
                </div>
              </div>
              <div>
                <div className="text-lg font-semibold text-deploybot-secondary">
                  {Math.round((tasks.filter(t => t.completed).length / tasks.length) * 100)}%
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Complete
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TaskList 