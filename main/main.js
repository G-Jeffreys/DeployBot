const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const log = require('electron-log');
const WebSocketBridge = require('../bridge/websocket_bridge');

// Configure logging
log.transports.file.level = 'debug';
log.transports.console.level = 'debug';

// Global variables for process management
let mainWindow;
let pythonProcess;
let wsBridge;
// Better development mode detection
let isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

/**
 * Create the main application window with WebSocket communication setup
 */
function createWindow() {
  console.log('🚀 [MAIN] Creating DeployBot main window...');
  log.info('Creating main application window');

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
  });

  // Load the renderer
  if (isDev) {
    console.log('📱 [MAIN] Loading development server at http://localhost:3000');
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    console.log('📱 [MAIN] Loading production build from dist/index.html');
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    console.log('✅ [MAIN] Main window ready, showing application');
    log.info('Main window ready to show');
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    console.log('🔴 [MAIN] Main window closed');
    log.info('Main window closed');
    mainWindow = null;
  });

  // Setup IPC communication
  setupIPC();
  
  // Start Python backend with WebSocket server
  startPythonBackend();
  
  // Setup WebSocket bridge connection to backend
  setTimeout(() => {
    setupWebSocketBridge();
  }, 3000); // Wait 3 seconds for Python backend to start
}

/**
 * Setup WebSocket bridge connection to Python backend
 */
function setupWebSocketBridge() {
  console.log('🔌 [MAIN] Setting up WebSocket bridge connection to backend...');
  log.info('Setting up WebSocket bridge connection');
  
  // Create bridge instance
  wsBridge = new WebSocketBridge('ws://localhost:8765');
  
  // Set up event handlers
  wsBridge.on('connected', () => {
    console.log('✅ [MAIN] WebSocket bridge connected to backend');
    log.info('WebSocket bridge connected');
    
    // Send initial status check
    wsBridge.sendCommand('status', {});
  });
  
  wsBridge.on('disconnected', (data) => {
    console.log('🔴 [MAIN] WebSocket bridge disconnected:', data);
    log.info('WebSocket bridge disconnected', data);
  });
  
  wsBridge.on('error', (error) => {
    console.error('❌ [MAIN] WebSocket bridge error:', error);
    log.error('WebSocket bridge error', { error: error.message });
  });
  
  // Handle all message types and forward to renderer
  wsBridge.on('message', (message) => {
    console.log('📨 [MAIN] Received bridge message:', message);
    
    // Forward real-time updates to renderer
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('backend-update', message);
    }
  });
  
  // Handle specific event types
  wsBridge.on('system', (data) => {
    console.log('🔔 [MAIN] System event received:', data);
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('backend-update', { type: 'system', ...data });
    }
  });
  
  wsBridge.on('response', (data) => {
    console.log('📋 [MAIN] Command response received:', data);
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('backend-update', { type: 'response', ...data });
    }
  });
  
  wsBridge.on('deploy_detected', (data) => {
    console.log('🚀 [MAIN] Deploy detected event received:', data);
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('backend-update', { type: 'deploy_detected', data });
    }
  });
  
  wsBridge.on('task_selected', (data) => {
    console.log('🎯 [MAIN] Task selected event received:', data);
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('backend-update', { type: 'task_selected', data });
    }
  });
  
  // Connect to backend
  wsBridge.connect();
}

/**
 * Send command to backend via WebSocket bridge
 */
async function sendBridgeCommand(command, data, timeout = 10000) {
  if (!wsBridge) {
    throw new Error('WebSocket bridge not initialized');
  }
  
  console.log(`📡 [MAIN] Sending bridge command: ${command}`, data);
  
  try {
    const response = await wsBridge.sendCommand(command, data);
    console.log(`📨 [MAIN] Bridge command response for ${command}:`, response);
    return response;
  } catch (error) {
    console.error(`❌ [MAIN] Bridge command failed: ${command}`, error);
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
    console.log(`📡 [MAIN] Received Python command: ${command}`, data);
    log.info(`Python command received: ${command}`, { data });
    
    try {
      const response = await sendBridgeCommand(command, data);
      return response;
    } catch (error) {
      console.error(`❌ [MAIN] Python command failed: ${command}`, error);
      return { success: false, error: error.message };
    }
  });

  // Handle project management
  ipcMain.handle('project-action', async (event, action, projectData) => {
    console.log(`📁 [MAIN] Project action: ${action}`, projectData);
    log.info(`Project action: ${action}`, { projectData });
    
    try {
      // Map project actions to backend commands
      const commandMap = {
        'create': 'project-create',
        'list': 'project-list',
        'delete': 'project-delete',
        'open': 'project-load'
      };
      
      const command = commandMap[action];
      if (!command) {
        throw new Error(`Unknown project action: ${action}`);
      }
      
      const response = await sendBridgeCommand(command, projectData);
      return response;
    } catch (error) {
      console.error(`❌ [MAIN] Project action failed: ${action}`, error);
      return { success: false, error: error.message };
    }
  });

  // Handle log requests
  ipcMain.handle('get-logs', async (event, logType) => {
    console.log(`📋 [MAIN] Log request: ${logType}`);
    log.info(`Log request: ${logType}`);
    
    try {
      const response = await sendBridgeCommand('get-logs', { logType });
      return response;
    } catch (error) {
      console.error(`❌ [MAIN] Log request failed: ${logType}`, error);
      return { success: false, error: error.message };
    }
  });
}

/**
 * Start the Python backend with LangGraph and WebSocket server
 */
function startPythonBackend() {
  console.log('🐍 [MAIN] Starting Python LangGraph backend...');
  log.info('Starting Python backend process');

  const pythonScript = path.join(__dirname, '../langgraph/graph.py');
  // Use virtual environment Python interpreter
  const pythonPath = path.join(__dirname, '../deploybot-env/bin/python');
  
  console.log(`🐍 [MAIN] Using Python interpreter: ${pythonPath}`);
  log.info(`Using Python interpreter: ${pythonPath}`);
  
  pythonProcess = spawn(pythonPath, [pythonScript], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    console.log(`🐍 [PYTHON] ${output}`);
    log.info(`Python stdout: ${output}`);
    
    // Forward Python output to renderer if needed
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('python-output', output);
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    const error = data.toString().trim();
    console.error(`🐍 [PYTHON ERROR] ${error}`);
    log.error(`Python stderr: ${error}`);
    
    // Forward Python errors to renderer
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('python-error', error);
    }
  });

  pythonProcess.on('close', (code) => {
    console.log(`🐍 [PYTHON] Process exited with code ${code}`);
    log.info(`Python process exited with code: ${code}`);
  });

  pythonProcess.on('error', (error) => {
    console.error(`🐍 [PYTHON ERROR] Failed to start process:`, error);
    log.error('Failed to start Python process', { error: error.message });
  });
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
      createWindow();
    }
  });
});

// All windows closed
app.on('window-all-closed', () => {
  console.log('🔴 [MAIN] All windows closed');
  log.info('All windows closed');
  
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// App before quit
app.on('before-quit', () => {
  console.log('🛑 [MAIN] Application shutting down...');
  log.info('Application shutting down');
  
  // Cleanup WebSocket bridge connection
  if (wsBridge) {
    console.log('🔌 [MAIN] Disconnecting WebSocket bridge...');
    log.info('Disconnecting WebSocket bridge');
    wsBridge.disconnect();
  }
  
  // Cleanup Python process
  if (pythonProcess) {
    console.log('🐍 [MAIN] Terminating Python backend process...');
    log.info('Terminating Python process');
    pythonProcess.kill();
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

console.log('🚀 [MAIN] DeployBot main process initialized');
log.info('DeployBot main process initialized'); 