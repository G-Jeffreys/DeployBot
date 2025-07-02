const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
console.log('🔗 [PRELOAD] Setting up secure context bridge...');

contextBridge.exposeInMainWorld('electronAPI', {
  // Python backend communication
  python: {
    sendCommand: (command, data) => {
      console.log(`📡 [PRELOAD] Sending Python command: ${command}`, data);
      return ipcRenderer.invoke('python-command', command, data);
    },
    
    onOutput: (callback) => {
      console.log('📡 [PRELOAD] Registering Python output listener');
      ipcRenderer.on('python-output', (_event, data) => callback(data));
    },
    
    onError: (callback) => {
      console.log('📡 [PRELOAD] Registering Python error listener');
      ipcRenderer.on('python-error', (_event, error) => callback(error));
    },
  },

  // Project management
  project: {
    create: (projectData) => {
      console.log('📁 [PRELOAD] Creating project:', projectData);
      return ipcRenderer.invoke('python-command', 'project-create', projectData);
    },
    
    open: (projectData) => {
      console.log('📁 [PRELOAD] Opening project:', projectData);
      return ipcRenderer.invoke('python-command', 'project-load', { path: projectData.path });
    },
    
    delete: (projectData) => {
      console.log('📁 [PRELOAD] Deleting project:', projectData);
      return ipcRenderer.invoke('python-command', 'project-delete', { path: projectData.path, name: projectData.name });
    },
    
    list: () => {
      console.log('📁 [PRELOAD] Listing projects');
      return ipcRenderer.invoke('python-command', 'project-list', {});
    },
  },

  // Task management - NEW
  tasks: {
    getSuggestions: (projectPath, context = {}) => {
      console.log('🎯 [PRELOAD] Getting task suggestions:', projectPath);
      return ipcRenderer.invoke('python-command', 'get-task-suggestions', { project_path: projectPath, context });
    },
    
    redirectToTask: (task, context = {}) => {
      console.log('🔀 [PRELOAD] Redirecting to task:', task);
      return ipcRenderer.invoke('python-command', 'redirect-to-task', { task, context });
    },
    
    testSelection: (projectName) => {
      console.log('🧪 [PRELOAD] Testing task selection:', projectName);
      return ipcRenderer.invoke('python-command', 'test-task-selection', { projectName });
    },
  },

  // Deploy monitoring - NEW
  monitoring: {
    start: () => {
      console.log('🚀 [PRELOAD] Starting deploy monitoring');
      return ipcRenderer.invoke('python-command', 'start-monitoring', {});
    },
    
    stop: () => {
      console.log('🛑 [PRELOAD] Stopping deploy monitoring');
      return ipcRenderer.invoke('python-command', 'stop-monitoring', {});
    },
    
    status: () => {
      console.log('📊 [PRELOAD] Checking monitoring status');
      return ipcRenderer.invoke('python-command', 'check-monitor', {});
    },
    
    simulateDeploy: (projectName, command = 'test deploy') => {
      console.log('🧪 [PRELOAD] Simulating deploy event:', projectName, command);
      return ipcRenderer.invoke('python-command', 'simulate-deploy', { project_name: projectName, command });
    },
  },

  // Timer management - NEW  
  timer: {
    start: (projectName, durationSeconds = 1800, deployCommand = null) => {
      console.log('⏰ [PRELOAD] Starting timer:', projectName, durationSeconds);
      return ipcRenderer.invoke('python-command', 'timer-start', { 
        project_name: projectName, 
        duration_seconds: durationSeconds,
        deploy_command: deployCommand 
      });
    },
    
    stop: (projectName) => {
      console.log('⏹️ [PRELOAD] Stopping timer:', projectName);
      return ipcRenderer.invoke('python-command', 'timer-stop', { project_name: projectName });
    },
    
    status: (projectName) => {
      console.log('📊 [PRELOAD] Getting timer status:', projectName);
      return ipcRenderer.invoke('python-command', 'timer-status', { project_name: projectName });
    },
  },

  // Deploy wrapper management - NEW
  wrapper: {
    status: () => {
      console.log('🔧 [PRELOAD] Checking wrapper status');
      return ipcRenderer.invoke('python-command', 'wrapper-status', {});
    },
    
    install: () => {
      console.log('📥 [PRELOAD] Installing deploy wrapper');
      return ipcRenderer.invoke('python-command', 'wrapper-install', {});
    },
    
    uninstall: () => {
      console.log('🗑️ [PRELOAD] Uninstalling deploy wrapper');
      return ipcRenderer.invoke('python-command', 'wrapper-uninstall', {});
    },
  },

  // Testing utilities - NEW
  testing: {
    week3Workflow: (projectName) => {
      console.log('🧪 [PRELOAD] Testing Week 3 workflow:', projectName);
      return ipcRenderer.invoke('python-command', 'test-week3-workflow', { project_name: projectName });
    },
    
    pythonBackend: () => {
      console.log('🐍 [PRELOAD] Testing Python backend');
      return ipcRenderer.invoke('python-command', 'ping', {});
    },
  },

  // Window management - NEW
  window: {
    focus: () => {
      console.log('🔍 [PRELOAD] Requesting window focus');
      return ipcRenderer.invoke('window-focus');
    },
  },

  // Real-time WebSocket events - NEW
  events: {
    onBackendUpdate: (callback) => {
      console.log('📡 [PRELOAD] Registering backend update listener');
      ipcRenderer.on('backend-update', (_event, data) => callback(data));
    },
    
    removeBackendUpdateListener: (callback) => {
      console.log('📡 [PRELOAD] Removing backend update listener');
      ipcRenderer.removeListener('backend-update', callback);
    },
  },

  // Logging and monitoring
  logs: {
    get: (logType) => {
      console.log(`📋 [PRELOAD] Requesting logs: ${logType}`);
      return ipcRenderer.invoke('get-logs', logType);
    },
  },

  // Utility functions
  utils: {
    log: (level, message, data) => {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] [RENDERER-${level.toUpperCase()}] ${message}`, data || '');
    },
    
    isProduction: () => process.env.NODE_ENV === 'production',
    isDevelopment: () => process.env.NODE_ENV === 'development',
  },

  // WebSocket communication (for future direct WS connection from renderer)
  websocket: {
    connect: (url) => {
      console.log(`🔌 [PRELOAD] WebSocket connection requested: ${url}`);
      // This will be implemented when we need direct WS from renderer
      return Promise.resolve({ connected: false, message: 'Not implemented yet' });
    },
  },

  // Deploy monitoring - KEPT FOR BACKWARD COMPATIBILITY
  deploy: {
    startMonitoring: () => {
      console.log('🚀 [PRELOAD] Starting deploy monitoring (legacy)');
      return ipcRenderer.invoke('python-command', 'start-monitoring', {});
    },
    
    stopMonitoring: () => {
      console.log('🛑 [PRELOAD] Stopping deploy monitoring (legacy)');
      return ipcRenderer.invoke('python-command', 'stop-monitoring', {});
    },
    
    status: (projectPath) => {
      console.log('📊 [PRELOAD] Checking deploy status for project:', projectPath);
      return ipcRenderer.invoke('python-command', 'check-monitor', {});
    },
  },

  // Custom notifications - NEW
  notifications: {
    show: (notification) => {
      console.log('🔔 [PRELOAD] Showing custom notification:', notification);
      return ipcRenderer.invoke('show-notification', notification);
    },
    
    action: (notificationId, action, data = {}) => {
      console.log('🔔 [PRELOAD] Notification action:', { notificationId, action, data });
      return ipcRenderer.invoke('notification-action', notificationId, action, data);
    },
  },

  // For notification windows specifically
  notificationAction: (notificationId, action, data = {}) => {
    console.log('🔔 [PRELOAD] Direct notification action:', { notificationId, action, data });
    return ipcRenderer.invoke('notification-action', notificationId, action, data);
  },

  // IPC Renderer for notification windows
  ipcRenderer: {
    on: (channel, callback) => {
      console.log('📡 [PRELOAD] Registering IPC listener:', channel);
      ipcRenderer.on(channel, callback);
    },
    
    removeListener: (channel, callback) => {
      console.log('📡 [PRELOAD] Removing IPC listener:', channel);
      ipcRenderer.removeListener(channel, callback);
    },
  },
});

// Remove any existing listeners to prevent memory leaks
ipcRenderer.removeAllListeners('python-output');
ipcRenderer.removeAllListeners('python-error');
ipcRenderer.removeAllListeners('backend-update');

console.log('✅ [PRELOAD] Context bridge setup complete - electronAPI exposed to renderer');

// Log when the preload script is loaded
window.addEventListener('DOMContentLoaded', () => {
  console.log('🎉 [PRELOAD] DOM loaded - DeployBot renderer ready for initialization');
}); 