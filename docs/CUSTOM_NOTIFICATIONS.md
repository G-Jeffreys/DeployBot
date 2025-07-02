# Custom Notification System

## Overview

DeployBot now features a custom notification system that creates floating notification windows in the upper right corner of your screen, similar to macOS notifications but with full customization and interaction capabilities. This system replaces the problematic system notifications with a reliable, cross-platform solution.

## Architecture

### Components

1. **Electron Main Process** (`main/main.js`)
   - Creates custom notification windows
   - Manages window positioning and animations
   - Handles IPC communication between windows

2. **React Notification Component** (`main/renderer/src/components/CustomNotification.jsx`)
   - Renders the notification UI with macOS-style design
   - Handles user interactions and animations
   - Displays task-specific information

3. **Notification App** (`main/renderer/src/NotificationApp.jsx`)
   - Standalone app for notification windows
   - Routes to the custom notification component

4. **Python Backend Integration** (`backend/notification.py`)
   - Sends notifications via WebSocket to main process
   - Maintains compatibility with existing notification API

5. **Fallback HTML** (`main/renderer/notification.html`)
   - Production fallback when React isn't available
   - Pure HTML/CSS/JS implementation

## Features

### Visual Design
- **macOS-style appearance** with blur effects and shadows
- **Color-coded notifications** by type (deploy, task suggestion, timer, etc.)
- **Smooth animations** for entrance/exit
- **Responsive hover effects**
- **Auto-positioning** with smart stacking

### Interaction
- **Clickable actions** (Switch Now, Snooze, View Timer, etc.)
- **Auto-dismiss** after 10 seconds
- **Manual dismiss** via close button or escape key
- **Task-specific context** with app icons and duration estimates

### Types of Notifications

#### 1. Task Suggestions 🎯
```javascript
{
  type: 'task_suggestion',
  title: '🎯 Task Suggestion',
  message: 'Switch to: Write documentation',
  data: {
    task: {
      text: 'Write documentation for custom notifications',
      app: 'Bear',
      tags: ['#writing', '#docs'],
      estimated_duration: 30
    }
  },
  actions: ['Switch Now', 'Snooze 5min', 'Dismiss']
}
```

#### 2. Deploy Detection 🚀
```javascript
{
  type: 'deploy_detected',
  title: '🚀 Deploy Detected',
  message: 'Deployment started: firebase deploy',
  actions: ['View Timer', 'Dismiss']
}
```

#### 3. Timer Expiry ⏰
```javascript
{
  type: 'timer_expiry',
  title: '⏰ Timer Expired',
  message: 'Deploy timer finished for MyProject',
  actions: ['View Project', 'Dismiss']
}
```

#### 4. Deploy Completed ✅
```javascript
{
  type: 'deploy_completed',
  title: '✅ Deploy Complete',
  message: 'Deployment finished successfully',
  actions: ['View Logs', 'Dismiss']
}
```

## API Usage

### From Python Backend
```python
# Send custom notification
await notification_manager.notify_task_suggestion(
    project_name="MyProject",
    task={
        "text": "Write unit tests",
        "app": "VSCode",
        "tags": ["#code", "#testing"],
        "estimated_duration": 45
    },
    context={
        "deploy_active": True,
        "timer_duration": 1800
    }
)
```

### From Renderer Process
```javascript
// Show custom notification manually
const notification = {
  id: `notification_${Date.now()}`,
  title: '🎯 Custom Notification',
  message: 'This is a test notification',
  data: { type: 'task_suggestion' }
}

const response = await window.electronAPI.notifications.show(notification)
```

### Handle Notification Actions
```javascript
// In notification component
const handleAction = async (action, data) => {
  await window.electronAPI.notificationAction(
    notification.id, 
    action, 
    data
  )
}
```

## Configuration

### Window Properties
- **Size**: 380px wide, dynamic height (160px default, 200px for task suggestions, 320px for unified notifications)
- **Position**: Upper right corner with 20px margins
- **Stacking**: Up to 3 notifications with 10px spacing, accounting for dynamic heights
- **Persistence**: 10 seconds auto-dismiss
- **Transparency**: Full transparency with blur effects

### Customization
The notification system supports various customization options:

```javascript
// In main.js
const notificationWidth = 380
// Dynamic height based on type:
// - Default: 160px
// - Task suggestions: 200px  
// - Unified notifications: 320px
const maxNotifications = 3
const notificationSpacing = 10
```

## Testing

### Manual Testing
Use the test button in the Python Backend Testing component:

1. Open DeployBot
2. Navigate to Testing tab
3. Click "🔔 Test Notification"
4. Observe the custom notification in the upper right corner

### Programmatic Testing
```javascript
// Test task suggestion notification
const testNotification = {
  id: `test_${Date.now()}`,
  title: '🎯 Test Task Suggestion',
  data: {
    type: 'task_suggestion',
    task: {
      text: 'Complete notification system testing',
      app: 'Bear',
      estimated_duration: 15
    }
  }
}

await window.electronAPI.notifications.show(testNotification)
```

## Integration with Existing System

The custom notification system is designed to work alongside the existing notification preferences:

```python
# In notification.py
self.preferences = {
    "system_notifications_enabled": True,  # Fallback to system notifications
    "in_app_modals_enabled": True,         # Additional in-app notifications
    "custom_notifications_enabled": True,  # Our new system (always enabled)
}
```

### Notification Flow
1. **Custom notification** is sent first (primary method)
2. **System notification** as fallback (if enabled)
3. **In-app modal** for additional context (if enabled)

## Troubleshooting

### Common Issues

#### Notifications Not Appearing
- Check that the main window is running
- Verify WebSocket connection to Python backend
- Look for errors in the main process console

#### Styling Issues
- Ensure Tailwind CSS is loaded properly
- Check for CSS conflicts in custom styles
- Verify transparency and blur support

#### Action Handling Problems
- Confirm IPC handlers are registered
- Check notification ID consistency
- Verify Python backend response handling

### Debug Logging
The system includes comprehensive logging:

```javascript
// Enable debug logging
console.log('🔔 [NOTIFICATION] Custom notification received:', data)
console.log('🔔 [IPC] Notification action:', { notificationId, action, data })
```

## Future Enhancements

### Planned Features
- [ ] Sound notifications with custom audio files
- [ ] Notification history and replay
- [ ] Rich media support (images, progress bars)
- [ ] Multi-monitor positioning
- [ ] Notification templates and themes
- [ ] Batch notification management

### Performance Optimizations
- [ ] Notification pooling to reduce window creation overhead
- [ ] Memory cleanup for dismissed notifications
- [ ] Lazy loading for notification components

## Benefits Over System Notifications

1. **Reliability**: No dependency on macOS notification permissions
2. **Customization**: Full control over appearance and behavior
3. **Interaction**: Rich interactive elements and actions
4. **Consistency**: Identical behavior across all platforms
5. **Integration**: Seamless integration with DeployBot's workflow
6. **Debugging**: Complete visibility into notification lifecycle

## Conclusion

The custom notification system provides a robust, reliable alternative to system notifications while maintaining the familiar macOS aesthetic and improving upon the user experience with better interactions and task-specific context. 