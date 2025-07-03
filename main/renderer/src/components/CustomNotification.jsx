import React, { useState, useEffect } from 'react';

/**
 * CustomNotification Component
 * Displays a macOS-style notification with actions and animations
 */
const CustomNotification = ({ notification, onAction }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  const handleAction = async (action, data = {}) => {
    console.log('🔔 [NOTIFICATION] Action triggered:', action, data);
    
    // Handle task switching actions directly using the working path
    if (action === 'switch_now' || action === 'switch_to_task') {
      const task = notification.data?.task;
      const projectName = notification.data?.project_name;
      
      if (task && window.electronAPI && window.electronAPI.tasks) {
        console.log('🔀 [NOTIFICATION] Using working redirect path for task switch:', task);
        
        // Use the SAME working path as the "Suggest" button
        const context = {
          project_name: projectName,
          project_path: notification.data?.context?.project_path,
          redirect_reason: 'notification_task_switch'
        };
        
        try {
          const response = await window.electronAPI.tasks.redirectToTask(task, context);
          console.log('✅ [NOTIFICATION] Task redirection successful:', response);
        } catch (error) {
          console.error('❌ [NOTIFICATION] Task redirection failed:', error);
        }
      }
      
      // Add exit animation and close
      setIsVisible(false);
      setTimeout(() => {
        onAction('dismiss', {});
      }, 300);
      
    } else {
      // Handle other actions through normal notification system
      // Add exit animation
      setIsVisible(false);
      
      // Call action handler after animation
      // Use shorter delay for snooze actions since notification should dismiss immediately
      const delay = action.includes('snooze') ? 100 : 300;
      setTimeout(() => {
        onAction(action, data);
      }, delay);
    }
  };

  const handleDismiss = () => {
    handleAction('dismiss');
  };

  const handleClick = () => {
    if (notification.data?.type === 'task_suggestion') {
      // Handle task suggestion click
      handleAction('switch_now', { task: notification.data.task });
    } else {
      handleAction('click');
    }
  };

  const getNotificationIcon = () => {
    switch (notification.data?.type) {
      case 'deploy_detected':
        return '🚀';
      case 'task_suggestion':
        return '🎯';
      case 'timer_expiry':
        return '⏰';
      case 'deploy_completed':
        return '✅';
      case 'unified_suggestion':
        return '🎯⏰';
      default:
        return '🔔';
    }
  };

  const getNotificationColor = () => {
    switch (notification.data?.type) {
      case 'deploy_detected':
        return 'border-blue-400 bg-blue-50';
      case 'task_suggestion':
        return 'border-purple-400 bg-purple-50';
      case 'timer_expiry':
        return 'border-orange-400 bg-orange-50';
      case 'deploy_completed':
        return 'border-green-400 bg-green-50';
      case 'unified_suggestion':
        return 'border-indigo-400 bg-indigo-50';
      default:
        return 'border-gray-400 bg-gray-50';
    }
  };

  const formatTaskMessage = () => {
    // Handle unified suggestion notification
    if (notification.data?.type === 'unified_suggestion') {
      const { timer_info, task, project_name } = notification.data;
      
      return (
        <div className="space-y-1.5">
          {/* Timer status */}
          {timer_info && (
            <div className="p-1.5 bg-white bg-opacity-60 rounded-md">
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-orange-600">⏰</span>
                <span className="font-medium">
                  {timer_info.status === 'expired' 
                    ? `Timer expired for ${project_name}`
                    : timer_info.status === 'running'
                    ? `Timer: ${timer_info.time_remaining_formatted || 'running'} left`
                    : `Timer ${timer_info.status}`
                  }
                </span>
              </div>
            </div>
          )}
          
          {/* Task suggestion */}
          {task && (
            <div className="p-1.5 bg-white bg-opacity-60 rounded-md">
              <div className="flex items-center space-x-2 text-xs mb-1">
                <span className="text-purple-600">🎯</span>
                <span className="font-medium">Suggested Task:</span>
              </div>
              <p className="font-medium text-gray-900 mb-1 text-xs leading-tight">{task.text}</p>
              <div className="flex items-center space-x-1 text-xs text-gray-600 flex-wrap">
                <span className="px-1.5 py-0.5 bg-gray-200 rounded-full text-xs">
                  📱 {task.app || 'Unknown App'}
                </span>
                {task.estimated_duration && (
                  <span className="px-1.5 py-0.5 bg-gray-200 rounded-full text-xs">
                    ⏱️ ~{task.estimated_duration}min
                  </span>
                )}
                {task.tags && task.tags.length > 0 && (
                  <span className="px-1.5 py-0.5 bg-gray-200 rounded-full text-xs">
                    🏷️ {task.tags.slice(0, 2).join(' ')}
                  </span>
                )}
              </div>
            </div>
          )}
          
          {/* Show message if neither timer nor task */}
          {!timer_info && !task && (
            <p className="text-gray-900">{notification.message}</p>
          )}
        </div>
      );
    }
    
    // Handle task suggestion notification  
    if (notification.data?.type === 'task_suggestion' && notification.data?.task) {
      const task = notification.data.task;
      return (
        <div className="space-y-1">
          <p className="font-medium text-gray-900">{task.text}</p>
          <div className="flex items-center space-x-2 text-xs text-gray-600">
            <span className="px-2 py-1 bg-gray-200 rounded-full">
              📱 {task.app || 'Unknown App'}
            </span>
            {task.estimated_duration && (
              <span className="px-2 py-1 bg-gray-200 rounded-full">
                ⏱️ ~{task.estimated_duration}min
              </span>
            )}
            {task.tags && task.tags.length > 0 && (
              <span className="px-2 py-1 bg-gray-200 rounded-full">
                🏷️ {task.tags.slice(0, 2).join(' ')}
              </span>
            )}
          </div>
        </div>
      );
    }
    return <p className="text-gray-900">{notification.message}</p>;
  };

  const renderActionButtons = () => {
    const type = notification.data?.type;
    
    // Unified suggestion actions
    if (type === 'unified_suggestion') {
      const { task, timer_info } = notification.data;
      
      return (
        <div className="flex flex-wrap gap-1 justify-start">
          {/* Task-related actions */}
          {task && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleAction('switch_to_task', { task });
              }}
              className="px-2 py-0.5 bg-purple-600 text-white text-xs rounded-full hover:bg-purple-700 transition-colors duration-150 font-medium"
            >
              Switch
            </button>
          )}
          
          {/* Timer and New buttons removed - functionality was redundant */}
          
          {/* General actions */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('snooze', { snooze_minutes: 5 });
            }}
            className="px-2 py-0.5 bg-gray-600 text-white text-xs rounded-full hover:bg-gray-700 transition-colors duration-150 font-medium"
            style={{ display: 'none' }}
          >
            Snooze
          </button>
        </div>
      );
    }
    
    // Task suggestion actions
    if (type === 'task_suggestion') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('switch_now', { task: notification.data.task });
            }}
            className="px-3 py-1 bg-purple-600 text-white text-xs rounded-full hover:bg-purple-700 transition-colors duration-150 font-medium"
          >
            Switch Now
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('snooze_5min');
            }}
            className="px-3 py-1 bg-gray-600 text-white text-xs rounded-full hover:bg-gray-700 transition-colors duration-150 font-medium"
            style={{ display: 'none' }}
          >
            Snooze 5min
          </button>
        </div>
      );
    }
    
    // Deploy detection actions
    if (type === 'deploy_detected') {
      return (
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleAction('view_timer');
            }}
            className="px-3 py-1 bg-blue-600 text-white text-xs rounded-full hover:bg-blue-700 transition-colors duration-150 font-medium"
          >
            View Timer
          </button>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div 
      className={`
        fixed ${notification.data?.type === 'unified_suggestion' ? 'inset-x-0 top-0' : 'inset-0'} pointer-events-auto transition-all duration-300 ease-out
        ${isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'}
      `}
    >
      <div 
        className={`
          w-full ${notification.data?.type === 'unified_suggestion' ? '' : 'h-full'} ${notification.data?.type === 'unified_suggestion' ? 'p-3' : 'p-4'} rounded-xl border-2 shadow-2xl backdrop-blur-md
          ${getNotificationColor()}
          ${isHovered ? 'scale-105 shadow-3xl' : 'scale-100'}
          transition-all duration-200 ease-out cursor-pointer
          relative ${notification.data?.type === 'unified_suggestion' ? 'overflow-visible' : 'overflow-hidden'}
        `}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Background blur effect */}
        <div className="absolute inset-0 bg-white bg-opacity-80 backdrop-blur-sm rounded-xl"></div>
        
        {/* Content */}
        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getNotificationIcon()}</span>
              <h3 className="font-semibold text-gray-900 text-sm">
                {notification.title}
              </h3>
            </div>
            
            {/* Close button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDismiss();
              }}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-150 text-lg leading-none p-1"
              title="Dismiss"
            >
              ×
            </button>
          </div>

          {/* Message */}
          <div className={`text-sm ${notification.data?.type === 'unified_suggestion' ? 'mb-2' : 'mb-3'}`}>
            {formatTaskMessage()}
          </div>

          {/* Dynamic action buttons */}
          <div className="mt-2">
            {renderActionButtons()}
          </div>

          {/* Notifications now persist until manually dismissed */}
        </div>

        {/* Subtle gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white via-opacity-20 to-transparent opacity-30 animate-shimmer pointer-events-none"></div>
      </div>

      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        .animate-shimmer {
          animation: shimmer 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default CustomNotification; 