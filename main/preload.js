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
      return ipcRenderer.invoke('project-action', 'create', projectData);
    },
    
    open: (projectPath) => {
      console.log('📁 [PRELOAD] Opening project:', projectPath);
      return ipcRenderer.invoke('project-action', 'open', { path: projectPath });
    },
    
    delete: (projectPath) => {
      console.log('📁 [PRELOAD] Deleting project:', projectPath);
      return ipcRenderer.invoke('project-action', 'delete', { path: projectPath });
    },
    
    list: () => {
      console.log('📁 [PRELOAD] Listing projects');
      return ipcRenderer.invoke('project-action', 'list', {});
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

  // Deploy monitoring
  deploy: {
    startMonitoring: () => {
      console.log('🚀 [PRELOAD] Starting deploy monitoring');
      return ipcRenderer.invoke('python-command', 'start-monitoring', {});
    },
    
    stopMonitoring: () => {
      console.log('🛑 [PRELOAD] Stopping deploy monitoring');
      return ipcRenderer.invoke('python-command', 'stop-monitoring', {});
    },
  },
});

// Remove any existing listeners to prevent memory leaks
ipcRenderer.removeAllListeners('python-output');
ipcRenderer.removeAllListeners('python-error');

console.log('✅ [PRELOAD] Context bridge setup complete - electronAPI exposed to renderer');

// Log when the preload script is loaded
window.addEventListener('DOMContentLoaded', () => {
  console.log('🎉 [PRELOAD] DOM loaded - DeployBot renderer ready for initialization');
}); 