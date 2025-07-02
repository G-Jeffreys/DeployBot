const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const log = require('electron-log');
const ProcessManager = require('./process_manager');

// Configure logging
log.transports.file.level = 'debug';
log.transports.console.level = 'debug';

// Global variables for process management
let mainWindow;
let processManager;
// Better development mode detection - only true if explicitly in development OR Vite server is running
let isDev = process.env.NODE_ENV === 'development' && process.argv.includes('--dev');

// Custom notification system
let notificationWindows = new Map(); // notification_id -> BrowserWindow
let notificationQueue = [];
let maxNotifications = 3;
let notificationSpacing = 10; // pixels between notifications

/**
 * Create the main application window with robust process management
 */
function createWindow() {
  console.log('🚀 [MAIN] Creating DeployBot main window...');
  log.info('Creating main application window');

  // Initialize process manager
  if (!processManager) {
    processManager = new ProcessManager();
    setupProcessManagerEventHandlers();
  }

  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
    },
    titleBarStyle: 'hiddenInset', // macOS style
    show: false, // Don't show until ready
    icon: path.join(__dirname, '../assets/icon.png')
  });

  // Load the renderer
  if (isDev) {
    console.log('📱 [MAIN] Loading React app from Vite development server');
    // Load from Vite dev server in development
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    console.log('📱 [MAIN] Loading production build from ../dist/index.html');
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    console.log('✅ [MAIN] Main window ready, showing application');
    log.info('Main window ready to show');
    mainWindow.show();
  });
  
  // Start comprehensive startup sequence
  console.log('🚀 [MAIN] Starting comprehensive backend startup sequence...');
  processManager.startComplete(isDev).then(success => {
    if (success) {
      console.log('✅ [MAIN] Backend startup sequence completed successfully');
    } else {
      console.error('❌ [MAIN] Backend startup sequence failed');
    }
  });

  // Handle window closed with comprehensive cleanup
  mainWindow.on('closed', () => {
    console.log('🔴 [MAIN] Main window closed');
    log.info('Main window closed');
    mainWindow = null;
    
    // Use process manager for comprehensive shutdown
    if (processManager) {
      processManager.shutdown().then(() => {
        console.log('✅ [MAIN] Process manager shutdown completed');
      }).catch(error => {
        console.error('❌ [MAIN] Error during process manager shutdown:', error);
      });
    }
  });

  // Setup IPC communication
  setupIPC();
}

/**
 * Create a custom notification window in the upper right corner
 */
function createNotificationWindow(notification) {
  console.log('🔔 [NOTIFICATION] Creating custom notification window:', notification.id);
  
  // Calculate position based on existing notifications
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize;
  
  const notificationWidth = 380;
  // Dynamic height based on notification type
  let notificationHeight = 160; // Default height
  
  if (notification.data?.type === 'unified_suggestion') {
    notificationHeight = 480; // Very tall for unified notifications with timer + task info + multiple buttons
  } else if (notification.data?.type === 'task_suggestion') {
    notificationHeight = 200; // Taller for task suggestions with tags
  }
  
  const marginRight = 20;
  const marginTop = 20;
  
  // Calculate Y position based on existing notifications with dynamic heights
  let yPosition = marginTop;
  if (notificationWindows.size > 0) {
    // Sum up heights of existing notifications
    for (const existingWindow of notificationWindows.values()) {
      if (!existingWindow.isDestroyed()) {
        yPosition += existingWindow.getBounds().height + notificationSpacing;
      }
    }
  }
  
  // Create notification window
  const notificationWindow = new BrowserWindow({
    width: notificationWidth,
    height: notificationHeight,
    x: screenWidth - notificationWidth - marginRight,
    y: yPosition,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    minimizable: false,
    maximizable: false,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js'),
    },
    backgroundColor: 'rgba(0, 0, 0, 0)', // Transparent background
    transparent: true,
    vibrancy: 'under-window', // macOS blur effect
    visualEffectState: 'active'
  });

  // Store window reference
  notificationWindows.set(notification.id, notificationWindow);

  // Load notification content
  // Always load from the static HTML file since notifications need to be self-contained
  notificationWindow.loadFile(path.join(__dirname, 'renderer/notification.html'), { 
    query: { id: notification.id } 
  });

  // Send notification data to window when ready
  notificationWindow.webContents.once('dom-ready', () => {
    console.log('🔔 [NOTIFICATION] DOM ready for notification window:', notification.id);
    console.log('🔔 [NOTIFICATION] Notification data to send:', JSON.stringify(notification, null, 2));
    
    setTimeout(() => {
      notificationWindow.webContents.send('notification-data', notification);
      console.log('🔔 [NOTIFICATION] Notification data sent to window');
      
      // Show with animation
      notificationWindow.show();
      console.log('🔔 [NOTIFICATION] Notification window shown');
      
      // Slide in animation
      notificationWindow.setOpacity(0);
      let opacity = 0;
      const fadeIn = setInterval(() => {
        // Check if window still exists before manipulating it
        if (notificationWindow.isDestroyed()) {
          clearInterval(fadeIn);
          return;
        }
        opacity += 0.1;
        notificationWindow.setOpacity(opacity);
        if (opacity >= 1) {
          clearInterval(fadeIn);
        }
      }, 30);
    }, 100);
  });

  // Notifications now persist until manually dismissed
  // No auto-dismiss timeout - user must explicitly close notifications

  // Handle window closed
  notificationWindow.on('closed', () => {
    console.log('🔔 [NOTIFICATION] Notification window closed:', notification.id);
    notificationWindows.delete(notification.id);
    repositionNotifications();
  });

  // Handle clicks
  notificationWindow.webContents.on('before-input-event', (event, input) => {
    if (input.type === 'keyDown' && input.key === 'Escape') {
      closeNotificationWindow(notification.id);
    }
  });

  console.log('✅ [NOTIFICATION] Custom notification window created successfully');
  return notificationWindow;
}

/**
 * Close a specific notification window with animation
 */
function closeNotificationWindow(notificationId) {
  const window = notificationWindows.get(notificationId);
  if (!window) return;

  console.log('🔔 [NOTIFICATION] Closing notification window:', notificationId);

  // Fade out animation
  let opacity = 1;
  const fadeOut = setInterval(() => {
    // Check if window still exists before manipulating it
    if (window.isDestroyed()) {
      clearInterval(fadeOut);
      return;
    }
    opacity -= 0.1;
    window.setOpacity(opacity);
    if (opacity <= 0) {
      clearInterval(fadeOut);
      if (!window.isDestroyed()) {
        window.close();
      }
    }
  }, 30);
}

/**
 * Reposition all notification windows after one is closed
 */
function repositionNotifications() {
  const windows = Array.from(notificationWindows.values());
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth } = primaryDisplay.workAreaSize;
  
  const notificationWidth = 380;
  const marginRight = 20;
  const marginTop = 20;

  let cumulativeY = marginTop;
  
  windows.forEach((window, index) => {
    // Check if window still exists before manipulating it
    if (window.isDestroyed()) {
      return;
    }
    
    // Get current window bounds to preserve height
    const currentBounds = window.getBounds();
    
    window.setBounds({
      x: screenWidth - notificationWidth - marginRight,
      y: cumulativeY,
      width: notificationWidth,
      height: currentBounds.height // Preserve the original height
    });
    
    // Update cumulative Y position for next window
    cumulativeY += currentBounds.height + notificationSpacing;
  });
}

/**
 * Handle notification from Python backend
 */
function showCustomNotification(notification) {
  console.log('🔔 [NOTIFICATION] Received notification request:', notification);
  
  // If we have too many notifications, close the oldest one
  if (notificationWindows.size >= maxNotifications) {
    const oldestId = notificationWindows.keys().next().value;
    closeNotificationWindow(oldestId);
  }

  // Create the notification window
  createNotificationWindow(notification);
}

/**
 * Close all notification windows
 */
function closeAllNotifications() {
  console.log('🔔 [NOTIFICATION] Closing all notification windows');
  for (const notificationId of notificationWindows.keys()) {
    closeNotificationWindow(notificationId);
  }
}

/**
 * Set up event handlers for the process manager
 */
function setupProcessManagerEventHandlers() {
  if (!processManager) return;

  // Backend state changes
  processManager.on('backend-state-changed', (state) => {
    console.log(`🔄 [MAIN] Backend state changed: ${state}`);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-update', {
        type: 'system',
        event: 'backend_state_changed',
        message: `Backend state: ${state}`,
        data: { state, status: processManager.getStatus() }
      });
    }
  });

  // Connection state changes
  processManager.on('connection-state-changed', (state) => {
    console.log(`🔌 [MAIN] Connection state changed: ${state}`);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-update', {
        type: 'system',
        event: 'connection_state_changed',
        message: `Connection state: ${state}`,
        data: { state, status: processManager.getStatus() }
      });
    }
  });

  // Python output
  processManager.on('python-output', (output) => {
    console.log('🐍 [PYTHON_STDOUT]', output);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('python-output', output);
    }
  });

  // Python errors
  processManager.on('python-error', (error) => {
    console.error('🐍 [PYTHON_STDERR]', error);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('python-error', error);
    }
  });

  // WebSocket messages
  processManager.on('websocket-message', (message) => {
    console.log('📥 [MAIN] WebSocket message:', message.type || 'unknown');
    
    // Handle custom notifications from backend
    if (message.type === 'notification' && message.event === 'show_custom' && message.data?.notification) {
      console.log('🔔 [MAIN] Received custom notification from backend:', message.data.notification);
      showCustomNotification(message.data.notification);
    }
    
    // Forward all messages to renderer for other handling
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-update', message);
    }
  });

  // Startup events
  processManager.on('startup-complete', (status) => {
    console.log('✅ [MAIN] Startup sequence completed:', status);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-update', {
        type: 'system',
        event: 'startup_complete',
        message: 'Backend and connection established',
        data: status
      });
    }
  });

  processManager.on('startup-failed', (error) => {
    console.error('❌ [MAIN] Startup sequence failed:', error);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-update', {
        type: 'system',
        event: 'startup_failed',
        message: `Startup failed: ${error.message}`,
        data: { error: error.message }
      });
    }
  });
}

// WebSocket connection is now handled by ProcessManager

/**
 * Send command to Python backend via ProcessManager
 */
async function sendPythonCommand(command, data = {}) {
  console.log(`📤 [MAIN] Sending Python command: ${command}`, data);
  
  if (!processManager) {
    throw new Error('Process manager not initialized');
  }

  try {
    const response = await processManager.sendCommand(command, data);
    console.log('✅ [MAIN] Command sent successfully via process manager');
    return response;
  } catch (error) {
    console.error('❌ [MAIN] Error sending command via process manager:', error);
    throw error;
  }
}

/**
 * Setup Inter-Process Communication between renderer and main
 */
function setupIPC() {
  console.log('🔗 [MAIN] Setting up IPC communication channels...');
  log.info('Setting up IPC communication');

  // Handle Python backend communication requests
  ipcMain.handle('python-command', async (event, command, data) => {
    console.log(`📞 [IPC] Python command received: ${command}`, data);
    log.info(`Python command received: ${command}`, { data });
    
    try {
      const response = await sendPythonCommand(command, data);
      console.log(`✅ [IPC] Python command completed: ${command}`, response);
      return response;
    } catch (error) {
      console.error(`❌ [IPC] Python command failed: ${command}`, error);
      return {
        success: false,
        error: error.message,
        command
      };
    }
  });

  // Handle project management
  ipcMain.handle('project-action', async (event, action, data) => {
    console.log(`📞 [IPC] Project action: ${action}`, data);
    log.info(`Project action: ${action}`, { projectData: data });
    
    try {
      let command;
      switch (action) {
        case 'create':
          command = 'project-create';
          break;
        case 'list':
          command = 'project-list';
          break;
        case 'open':
          command = 'project-load';
          break;
        case 'delete':
          command = 'project-delete';
          break;
        default:
          throw new Error(`Unknown project action: ${action}`);
      }
      
      const response = await sendPythonCommand(command, data);
      return response;
    } catch (error) {
      console.error(`❌ [IPC] Project action failed: ${action}`, error);
      return {
        success: false,
        error: error.message
      };
    }
  });

  // Handle log requests
  ipcMain.handle('get-logs', async (event, logType) => {
    console.log(`📞 [IPC] Log request: ${logType}`);
    log.info(`Log request: ${logType}`);
    
    try {
      // For now, we'll get logs via the Python backend
      // This could be enhanced to read log files directly
      const response = await sendPythonCommand('get-logs', { type: logType });
      return response;
    } catch (error) {
      console.error(`❌ [IPC] Failed to get logs: ${logType}`, error);
      return {
        success: false,
        error: error.message,
        logs: []
      };
    }
  });

  // Handle window focus requests
  ipcMain.handle('window-focus', async (event) => {
    console.log('🔍 [IPC] Window focus requested');
    log.info('Window focus requested');
    
    try {
      if (mainWindow && !mainWindow.isDestroyed()) {
        // Bring window to front and focus
        mainWindow.show();
        mainWindow.focus();
        
        // On macOS, also bring to front if minimized
        if (process.platform === 'darwin') {
          app.dock?.show();
        }
        
        console.log('✅ [IPC] Window focused successfully');
        log.info('Window focused successfully');
        
        return { success: true, message: 'Window focused' };
      } else {
        console.warn('⚠️ [IPC] Main window not available for focus');
        return { success: false, error: 'Window not available' };
      }
    } catch (error) {
      console.error('❌ [IPC] Failed to focus window:', error);
      log.error('Failed to focus window', { error: error.message });
      return { success: false, error: error.message };
    }
  });

  // Handle custom notification requests
  ipcMain.handle('show-notification', async (event, notification) => {
    console.log('🔔 [IPC] Custom notification request:', notification);
    log.info('Custom notification request', { notification });
    
    try {
      showCustomNotification(notification);
      return { success: true, message: 'Notification displayed' };
    } catch (error) {
      console.error('❌ [IPC] Failed to show notification:', error);
      return { success: false, error: error.message };
    }
  });

  // Handle notification action (click, dismiss, etc.)
  ipcMain.handle('notification-action', async (event, notificationId, action, data) => {
    console.log('🔔 [IPC] Notification action:', { notificationId, action, data });
    log.info('Notification action', { notificationId, action, data });
    
    try {
      if (action === 'dismiss') {
        closeNotificationWindow(notificationId);
        return { success: true, message: 'Notification dismissed' };
      } else if (action === 'click') {
        // Handle notification click - could open app, switch task, etc.
        console.log('🔔 [IPC] Notification clicked:', notificationId);
        
        // Send action back to Python backend for processing
        const response = await sendPythonCommand('notification-action', {
          notification_id: notificationId,
          action: action,
          data: data
        });
        
        // Close the notification after action
        closeNotificationWindow(notificationId);
        
        return response;
      } else {
        // Forward other actions to Python backend
        const response = await sendPythonCommand('notification-action', {
          notification_id: notificationId,
          action: action,
          data: data
        });
        return response;
      }
    } catch (error) {
      console.error('❌ [IPC] Failed to handle notification action:', error);
      return { success: false, error: error.message };
    }
  });

  // Note: Custom notification listening is handled in the main WebSocket message handler
}

/**
 * Setup global shortcuts for DeployBot
 */
function setupGlobalShortcuts() {
  console.log('⌨️ [MAIN] Registering global shortcuts...');
  log.info('Registering global shortcuts');

  // Register global shortcut to show/hide DeployBot (Cmd+Shift+D on macOS)
  const shortcutRegistered = globalShortcut.register('CommandOrControl+Shift+D', () => {
    console.log('⌨️ [MAIN] Global shortcut triggered - toggling DeployBot visibility');
    log.info('Global shortcut triggered');
    
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

  if (shortcutRegistered) {
    console.log('✅ [MAIN] Global shortcut Cmd+Shift+D registered successfully');
    log.info('Global shortcut registered successfully');
  } else {
    console.error('❌ [MAIN] Failed to register global shortcut');
    log.error('Failed to register global shortcut');
  }
}

/**
 * Application event handlers
 */

// App ready event
app.whenReady().then(() => {
  console.log('🎉 [MAIN] DeployBot application is ready!');
  log.info('DeployBot application ready');
  
  createWindow();
  setupGlobalShortcuts();

  app.on('activate', () => {
    console.log('🔄 [MAIN] App activated (macOS dock click)');
    log.info('App activated');
    
    if (BrowserWindow.getAllWindows().length === 0) {
      console.log('🔄 [MAIN] Recreating window on activate...');
      createWindow();
    }
  });
});

// All windows closed
app.on('window-all-closed', () => {
  console.log('🛑 [MAIN] All windows closed');
  log.info('All windows closed');
  
  // Mark app as quitting to prevent reconnections
  app.isQuiting = true;
  
  // Use process manager for comprehensive cleanup
  if (processManager) {
    processManager.shutdown().then(() => {
      console.log('✅ [MAIN] Process manager shutdown completed on app quit');
    }).catch(error => {
      console.error('❌ [MAIN] Error during process manager shutdown on quit:', error);
    });
  }
  
  // Unregister global shortcuts
  globalShortcut.unregisterAll();
  console.log('⌨️ [MAIN] Global shortcuts unregistered');
  log.info('Global shortcuts unregistered');
  
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// App before quit
app.on('before-quit', () => {
  console.log('🛑 [MAIN] Application shutting down...');
  log.info('Application shutting down');
  
  // Mark as quitting
  app.isQuiting = true;
  
  // Use process manager for shutdown
  if (processManager) {
    console.log('🧹 [MAIN] Initiating process manager shutdown...');
    processManager.shutdown();
  }
  
  // Unregister global shortcuts
  globalShortcut.unregisterAll();
  console.log('⌨️ [MAIN] Global shortcuts unregistered');
  log.info('Global shortcuts unregistered');
});

// Handle certificate errors for development
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});

// Handle unexpected errors
process.on('uncaughtException', (error) => {
  console.error('❌ [MAIN] Uncaught exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ [MAIN] Unhandled rejection at:', promise, 'reason:', reason);
});

// Handle process termination signals
process.on('SIGINT', () => {
  console.log('🛑 [MAIN] SIGINT received, cleaning up...');
  cleanup();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 [MAIN] SIGTERM received, cleaning up...');
  cleanup();
  process.exit(0);
});

/**
 * Comprehensive cleanup function
 */
function cleanup() {
  console.log('🧹 [MAIN] Starting comprehensive cleanup...');
  
  if (processManager) {
    // Use emergency cleanup for immediate shutdown
    processManager.emergencyCleanup().then(() => {
      console.log('✅ [MAIN] Emergency cleanup completed');
    }).catch(error => {
      console.error('❌ [MAIN] Error during emergency cleanup:', error);
    });
  }
  
  console.log('🧹 [MAIN] Cleanup completed');
}

console.log('🚀 [MAIN] DeployBot main process initialized');
log.info('DeployBot main process initialized'); 