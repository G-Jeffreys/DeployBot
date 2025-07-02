const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const log = require('electron-log');
const WebSocket = require('ws');

// Configure logging
log.transports.file.level = 'debug';
log.transports.console.level = 'debug';

// Global variables for process management
let mainWindow;
let pythonProcess;
let wsConnection;
let connectionAttempts = 0;
const maxConnectionAttempts = 10;
// Better development mode detection
let isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

/**
 * Create the main application window with WebSocket communication setup
 */
function createWindow() {
  console.log('🚀 [MAIN] Creating DeployBot main window...');
  log.info('Creating main application window');
  
  // Very early debug file
  const fs = require('fs');
  const debugPath1 = path.join(require('os').tmpdir(), 'deploybot-debug.txt');
  fs.writeFileSync(debugPath1, `createWindow started at ${new Date().toISOString()}\n`, { flag: 'a' });

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
    console.log('📱 [MAIN] Loading development server at http://localhost:3000');
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
  
  // Start Python backend immediately after creating window
  console.log('🚀 [MAIN] Starting Python backend immediately...');
  
  // Debug logging right before calling startPythonBackend
  const fs2 = require('fs');
  const debugPath2 = path.join(require('os').tmpdir(), 'deploybot-debug.txt');
  fs2.writeFileSync(debugPath2, `About to call startPythonBackend at ${new Date().toISOString()}\n`, { flag: 'a' });
  
  startPythonBackend();

  // Handle window closed
  mainWindow.on('closed', () => {
    console.log('🔴 [MAIN] Main window closed');
    log.info('Main window closed');
    mainWindow = null;
    
    // Cleanup Python process and WebSocket
    if (pythonProcess) {
      console.log('🐍 [MAIN] Forcefully terminating existing Python process...', pythonProcess.pid);
      try {
        // First try graceful termination
        pythonProcess.kill('SIGTERM');
        
        // If still running after 2 seconds, force kill
        setTimeout(() => {
          if (pythonProcess && !pythonProcess.killed) {
            console.log('🐍 [MAIN] Force killing Python process with SIGKILL...', pythonProcess.pid);
            pythonProcess.kill('SIGKILL');
          }
        }, 2000);
      } catch (error) {
        console.error('❌ [MAIN] Error killing Python process:', error);
      }
      pythonProcess = null;
    }
    
    // Also kill any orphaned Python processes by port
    try {
      console.log('🧹 [MAIN] Cleaning up any processes on port 8765...');
      require('child_process').exec('lsof -ti:8765 | xargs kill -9', (error) => {
        if (error && !error.message.includes('No such process')) {
          console.warn('⚠️ [MAIN] Port cleanup warning:', error.message);
        } else {
          console.log('✅ [MAIN] Port 8765 cleanup completed');
        }
      });
    } catch (error) {
      console.warn('⚠️ [MAIN] Port cleanup failed:', error);
    }
    
    if (wsConnection) {
      console.log('🔌 [MAIN] Closing WebSocket connection...');
      wsConnection.close();
      wsConnection = null;
    }
    
    // Cleanup temp directory (if created in packaged mode)
    if (!isDev) {
      const tempDir = path.join(require('os').tmpdir(), 'deploybot-backend');
      try {
        const fs = require('fs');
        if (fs.existsSync(tempDir)) {
          fs.rmSync(tempDir, { recursive: true, force: true });
          console.log('🧹 [MAIN] Cleaned up temp backend directory');
        }
      } catch (error) {
        console.error('❌ [MAIN] Failed to cleanup temp directory:', error);
      }
    }
  });

  // Setup IPC communication
  setupIPC();
}

/**
 * Start the Python backend process
 */
function startPythonBackend() {
  console.log('🐍 [MAIN] Starting Python backend...');
  log.info('Starting Python backend process');
  
  // First, ensure port 8765 is clear
  try {
    console.log('🧹 [MAIN] Checking for existing processes on port 8765...');
    require('child_process').execSync('lsof -ti:8765 | xargs kill -9', { timeout: 5000 });
    console.log('✅ [MAIN] Cleaned up existing processes on port 8765');
  } catch (error) {
    // This is expected if no processes are on the port
    console.log('✅ [MAIN] Port 8765 is clear (no existing processes)');
  }
  
  // Create a debug file to confirm this function is called
  const fs3 = require('fs');
  const debugPath3 = path.join(require('os').tmpdir(), 'deploybot-debug.txt');
  fs3.writeFileSync(debugPath3, `startPythonBackend called at ${new Date().toISOString()}\n`, { flag: 'a' });

  try {
    let pythonScriptPath;
    let workingDir;
    
    // Check if we're in development or packaged mode
    console.log(`🔍 [MAIN] isDev: ${isDev}, __dirname: ${__dirname}`);
    
    // Force packaged mode for testing
    const forcePackagedMode = __dirname.includes('app.asar');
    console.log(`🔍 [MAIN] forcePackagedMode: ${forcePackagedMode}`);
    
    if (isDev && !forcePackagedMode) {
      // Development mode: use source files
      pythonScriptPath = path.join(__dirname, '../backend/graph.py');
      workingDir = path.join(__dirname, '../backend');
      console.log('🔧 [MAIN] Using development backend files');
    } else {
      // Packaged mode: extract Python files from ASAR to temp directory
      const tempDir = path.join(require('os').tmpdir(), 'deploybot-backend');
      const fs = require('fs');
      
      console.log('📦 [MAIN] Extracting Python backend from package...');
      
      // Create temp directory if it doesn't exist
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }
      
      // Copy Python files from ASAR to temp directory
      const asarPath = path.join(__dirname, '../backend');
      const files = ['graph.py', 'logger.py', 'monitor.py', 'notification.py', 'project_manager.py', 'redirect.py', 'tasks.py', 'timer.py', 'deploybot_main.py'];
      
      for (const file of files) {
        const srcPath = path.join(asarPath, file);
        const destPath = path.join(tempDir, file);
        try {
          if (fs.existsSync(srcPath)) {
            fs.copyFileSync(srcPath, destPath);
            console.log(`📄 [MAIN] Copied ${file} to temp directory`);
          }
        } catch (error) {
          console.error(`❌ [MAIN] Failed to copy ${file}:`, error);
        }
      }
      
      pythonScriptPath = path.join(tempDir, 'graph.py');
      workingDir = tempDir;
      console.log(`📦 [MAIN] Using extracted backend files in: ${tempDir}`);
    }
    
    console.log(`🐍 [MAIN] Starting Python script: ${pythonScriptPath}`);
    
    // Use full path to python3 to avoid PATH issues in packaged app
    // Always use the deploybot virtual environment Python
    const pythonExecutable = path.join(__dirname, '../deploybot-env/bin/python3');
    console.log(`🐍 [MAIN] Using Python executable: ${pythonExecutable}`);
    
    // Start Python process
    pythonProcess = spawn(pythonExecutable, [pythonScriptPath], {
      cwd: workingDir,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin' }
    });

    console.log('🐍 [MAIN] Python process started with PID:', pythonProcess.pid);

    // Handle Python output
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      console.log('🐍 [PYTHON_STDOUT]', output);
      
      // Forward Python output to renderer
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('python-output', output);
      }
    });

    // Handle Python errors
    pythonProcess.stderr.on('data', (data) => {
      const error = data.toString().trim();
      console.error('🐍 [PYTHON_STDERR]', error);
      
      // Forward Python errors to renderer
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('python-error', error);
      }
    });

    // Handle Python process exit
    pythonProcess.on('close', (code) => {
      console.log(`🐍 [MAIN] Python process exited with code: ${code}`);
      pythonProcess = null;
      
      // Restart Python if it exits unexpectedly (and we're not shutting down)
      if (code !== 0 && !app.isQuiting && mainWindow && !mainWindow.isDestroyed()) {
        console.log('🔄 [MAIN] Restarting Python backend after unexpected exit...');
        setTimeout(() => startPythonBackend(), 3000);
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('❌ [MAIN] Python process error:', error);
      pythonProcess = null;
      
      // Forward error to renderer
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('python-error', `Python process error: ${error.message}`);
      }
    });

    // Wait a moment then connect to WebSocket
    setTimeout(() => {
      connectToWebSocket();
    }, 2000);

  } catch (error) {
    console.error('❌ [MAIN] Failed to start Python backend:', error);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('python-error', `Failed to start Python backend: ${error.message}`);
    }
  }
}

/**
 * Connect to the Python WebSocket server
 */
function connectToWebSocket() {
  const wsUrl = 'ws://localhost:8765';
  console.log(`🔌 [MAIN] Connecting to WebSocket: ${wsUrl} (attempt ${connectionAttempts + 1}/${maxConnectionAttempts})`);
  
  try {
    wsConnection = new WebSocket(wsUrl);

    wsConnection.on('open', () => {
      console.log('✅ [MAIN] WebSocket connection established');
      connectionAttempts = 0;
      
      // Send a ping to test the connection (with a small delay to ensure connection is ready)
      setTimeout(() => {
        if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
          try {
            wsConnection.send(JSON.stringify({
              command: 'ping',
              data: { timestamp: new Date().toISOString() }
            }));
            console.log('📡 [MAIN] Initial ping sent to backend');
          } catch (error) {
            console.error('❌ [MAIN] Failed to send initial ping:', error);
          }
        }
      }, 100);
      
      // Notify renderer that backend is connected
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend-update', {
          type: 'system',
          event: 'backend_connected',
          message: 'Backend connection established',
          data: { connected: true }
        });
      }
    });

    wsConnection.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        console.log('📡 [MAIN] WebSocket message received:', message);
        
        // Forward all backend messages to renderer as real-time updates
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('backend-update', message);
        }
      } catch (error) {
        console.error('❌ [MAIN] Failed to parse WebSocket message:', error);
      }
    });

    wsConnection.on('close', (code, reason) => {
      console.log(`🔌 [MAIN] WebSocket connection closed: ${code} - ${reason}`);
      wsConnection = null;
      
      // Notify renderer about disconnection
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend-update', {
          type: 'system',
          event: 'backend_disconnected',
          message: 'Backend connection lost',
          data: { connected: false, code, reason: reason.toString() }
        });
      }
      
      // Attempt to reconnect if not shutting down
      if (!app.isQuiting && connectionAttempts < maxConnectionAttempts) {
        connectionAttempts++;
        console.log(`🔄 [MAIN] Attempting to reconnect WebSocket in 3 seconds... (${connectionAttempts}/${maxConnectionAttempts})`);
        setTimeout(() => connectToWebSocket(), 3000);
      } else if (connectionAttempts >= maxConnectionAttempts) {
        console.error('❌ [MAIN] Max WebSocket connection attempts reached');
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.webContents.send('backend-update', {
            type: 'system',
            event: 'backend_connection_failed',
            message: 'Failed to connect to backend after multiple attempts',
            data: { connected: false, attempts: connectionAttempts }
          });
        }
      }
    });

    wsConnection.on('error', (error) => {
      console.error('❌ [MAIN] WebSocket error:', error);
      
      // Notify renderer about connection error
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('backend-update', {
          type: 'system',
          event: 'backend_error',
          message: `Backend connection error: ${error.message}`,
          data: { connected: false, error: error.message }
        });
      }
    });

  } catch (error) {
    console.error('❌ [MAIN] Failed to create WebSocket connection:', error);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-update', {
        type: 'system',
        event: 'backend_connection_failed',
        message: `Failed to create WebSocket connection: ${error.message}`,
        data: { connected: false, error: error.message }
      });
    }
  }
}

/**
 * Send command to Python backend via WebSocket
 */
async function sendPythonCommand(command, data = {}) {
  console.log(`📡 [MAIN] Sending command to Python: ${command}`, data);
  
  return new Promise((resolve, reject) => {
    if (!wsConnection || wsConnection.readyState !== WebSocket.OPEN) {
      const error = 'WebSocket not connected to Python backend';
      console.error('❌ [MAIN]', error);
      reject(new Error(error));
      return;
    }

    const messageId = Date.now().toString();
    const message = {
      command,
      data,
      messageId,
      timestamp: new Date().toISOString()
    };

    // Set up response handler
    const responseHandler = (data) => {
      try {
        const response = JSON.parse(data.toString());
        if (response.messageId === messageId || response.command === command) {
          wsConnection.removeListener('message', responseHandler);
          
          console.log(`✅ [MAIN] Command response received: ${command}`, response);
          resolve(response);
        }
      } catch (error) {
        console.error('❌ [MAIN] Failed to parse command response:', error);
        wsConnection.removeListener('message', responseHandler);
        reject(error);
      }
    };

    // Listen for response
    wsConnection.on('message', responseHandler);

    // Send the command
    wsConnection.send(JSON.stringify(message));
    
    // Set timeout for response
    setTimeout(() => {
      wsConnection.removeListener('message', responseHandler);
      reject(new Error(`Command timeout: ${command}`));
    }, 30000); // 30 second timeout
  });
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
  
  // Cleanup Python process
  if (pythonProcess) {
    console.log('🐍 [MAIN] Terminating Python backend process on app quit...');
    try {
      pythonProcess.kill('SIGKILL'); // Force kill on app quit
    } catch (error) {
      console.error('❌ [MAIN] Error killing Python process on quit:', error);
    }
  }
  
  // Also kill any processes on port 8765
  try {
    require('child_process').exec('lsof -ti:8765 | xargs kill -9', () => {
      console.log('🧹 [MAIN] Port cleanup on app quit completed');
    });
  } catch (error) {
    console.warn('⚠️ [MAIN] Port cleanup on quit failed:', error);
  }
  
  // Cleanup WebSocket
  if (wsConnection) {
    console.log('🔌 [MAIN] Closing WebSocket on app quit...');
    wsConnection.close();
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
  
  // Cleanup WebSocket connection
  if (wsConnection) {
    console.log('🔌 [MAIN] Disconnecting WebSocket connection...');
    log.info('Disconnecting WebSocket connection');
    wsConnection.close();
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
  
  // Kill Python process
  if (pythonProcess) {
    try {
      pythonProcess.kill('SIGKILL');
      console.log('✅ [MAIN] Python process terminated');
    } catch (error) {
      console.error('❌ [MAIN] Error terminating Python process:', error);
    }
  }
  
  // Kill any processes on port 8765
  try {
    require('child_process').execSync('lsof -ti:8765 | xargs kill -9', { timeout: 5000 });
    console.log('✅ [MAIN] Port 8765 cleanup completed');
  } catch (error) {
    // This is expected if no processes are on the port
    console.log('🧹 [MAIN] Port cleanup completed (no processes found)');
  }
  
  // Close WebSocket
  if (wsConnection) {
    try {
      wsConnection.close();
      console.log('✅ [MAIN] WebSocket closed');
    } catch (error) {
      console.error('❌ [MAIN] Error closing WebSocket:', error);
    }
  }
  
  console.log('🧹 [MAIN] Cleanup completed');
}

console.log('🚀 [MAIN] DeployBot main process initialized');
log.info('DeployBot main process initialized'); 