/**
 * DeployBot Process Manager
 * 
 * Centralized process lifecycle management for robust frontend-backend coordination
 * Handles startup sequencing, health monitoring, cleanup, and recovery
 */

const { spawn } = require('child_process');
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs');
const { EventEmitter } = require('events');

class ProcessManager extends EventEmitter {
  constructor() {
    super();
    
    // Process state
    this.pythonProcess = null;
    this.wsConnection = null;
    this.isShuttingDown = false;
    this.startupSequenceActive = false;
    
    // Configuration
    this.config = {
      wsPort: 8765,
      wsHost: 'localhost',
      maxStartupAttempts: 5,
      maxConnectionAttempts: 10,
      startupTimeout: 30000, // 30 seconds
      connectionTimeout: 10000, // 10 seconds
      healthCheckInterval: 15000, // 15 seconds
      gracefulShutdownTimeout: 5000, // 5 seconds
      backendReadyCheckInterval: 1000, // 1 second
      maxBackendReadyWait: 20000 // 20 seconds
    };
    
    // State tracking
    this.state = {
      backend: 'stopped', // stopped, starting, running, error, stopping
      connection: 'disconnected', // disconnected, connecting, connected, error
      lastError: null,
      startupAttempt: 0,
      connectionAttempt: 0,
      startedAt: null,
      connectedAt: null
    };
    
    // Health monitoring
    this.healthCheckTimer = null;
    this.connectionTimer = null;
    this.startupTimer = null;
    
    console.log('🔧 [PROCESS_MANAGER] Process manager initialized');
  }

  /**
   * Get current WebSocket URL
   */
  getWebSocketUrl() {
    return `ws://${this.config.wsHost}:${this.config.wsPort}`;
  }

  /**
   * Get comprehensive system status
   */
  getStatus() {
    return {
      ...this.state,
      config: this.config,
      processId: this.pythonProcess?.pid || null,
      isConnected: this.state.connection === 'connected',
      isHealthy: this.state.backend === 'running' && this.state.connection === 'connected'
    };
  }

  /**
   * Comprehensive port cleanup - kills any processes using our WebSocket port
   */
  async cleanupPort() {
    console.log(`🧹 [PROCESS_MANAGER] Cleaning up port ${this.config.wsPort}...`);
    
    return new Promise((resolve) => {
      const { exec } = require('child_process');
      
      // Use lsof to find and kill processes on our port
      exec(`lsof -ti:${this.config.wsPort}`, (error, stdout) => {
        if (error || !stdout.trim()) {
          console.log(`✅ [PROCESS_MANAGER] Port ${this.config.wsPort} is clean`);
          resolve(true);
          return;
        }
        
        const pids = stdout.trim().split('\n').filter(pid => pid);
        console.log(`🔪 [PROCESS_MANAGER] Found ${pids.length} processes on port ${this.config.wsPort}: ${pids.join(', ')}`);
        
        // Kill all processes on the port
        exec(`kill -9 ${pids.join(' ')}`, (killError) => {
          if (killError) {
            console.warn(`⚠️ [PROCESS_MANAGER] Warning during port cleanup: ${killError.message}`);
          } else {
            console.log(`✅ [PROCESS_MANAGER] Killed ${pids.length} processes on port ${this.config.wsPort}`);
          }
          resolve(true);
        });
      });
    });
  }

  /**
   * Check if backend is ready to accept connections
   */
  async isBackendReady() {
    return new Promise((resolve) => {
      const testSocket = new WebSocket(this.getWebSocketUrl());
      
      const timeout = setTimeout(() => {
        testSocket.terminate();
        resolve(false);
      }, 2000); // 2 second timeout for ready check
      
      testSocket.on('open', () => {
        clearTimeout(timeout);
        testSocket.close();
        resolve(true);
      });
      
      testSocket.on('error', () => {
        clearTimeout(timeout);
        resolve(false);
      });
    });
  }

  /**
   * Wait for backend to be ready with timeout
   */
  async waitForBackendReady() {
    console.log('⏳ [PROCESS_MANAGER] Waiting for backend to be ready...');
    const startTime = Date.now();
    
    while (Date.now() - startTime < this.config.maxBackendReadyWait) {
      if (await this.isBackendReady()) {
        console.log('✅ [PROCESS_MANAGER] Backend is ready to accept connections');
        return true;
      }
      
      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, this.config.backendReadyCheckInterval));
    }
    
    console.error('❌ [PROCESS_MANAGER] Backend did not become ready within timeout');
    return false;
  }

  /**
   * Start Python backend process with proper error handling and monitoring
   */
  async startBackend(isDev = false) {
    if (this.state.backend === 'starting' || this.state.backend === 'running') {
      console.log('⚠️ [PROCESS_MANAGER] Backend is already starting or running');
      return false;
    }
    
    this.state.backend = 'starting';
    this.state.startupAttempt++;
    this.emit('backend-state-changed', this.state.backend);
    
    console.log(`🚀 [PROCESS_MANAGER] Starting backend (attempt ${this.state.startupAttempt}/${this.config.maxStartupAttempts})...`);
    
    try {
      // Pre-startup cleanup
      await this.cleanupPort();
      
      // Determine Python script path and working directory
      let pythonScriptPath, workingDir;
      
      if (isDev && !__dirname.includes('app.asar')) {
        // Development mode
        pythonScriptPath = path.join(__dirname, '../backend/graph.py');
        workingDir = path.join(__dirname, '../backend');
        console.log('🔧 [PROCESS_MANAGER] Using development backend files');
      } else {
        // Production mode - extract to temp directory
        const tempDir = path.join(require('os').tmpdir(), 'deploybot-backend');
        
        if (!fs.existsSync(tempDir)) {
          fs.mkdirSync(tempDir, { recursive: true });
        }
        
        // Copy backend files
        const backendFiles = [
          'graph.py', 'logger.py', 'monitor.py', 'notification.py',
          'project_manager.py', 'redirect.py', 'tasks.py', 'timer.py',
          'deploy_wrapper_setup.py'
        ];
        
        for (const file of backendFiles) {
          const srcPath = path.join(__dirname, '../backend', file);
          const destPath = path.join(tempDir, file);
          
          if (fs.existsSync(srcPath)) {
            fs.copyFileSync(srcPath, destPath);
            console.log(`📄 [PROCESS_MANAGER] Copied ${file} to temp directory`);
          }
        }
        
        pythonScriptPath = path.join(tempDir, 'graph.py');
        workingDir = tempDir;
        console.log(`📦 [PROCESS_MANAGER] Using extracted backend files in: ${tempDir}`);
      }
      
      // Determine Python executable
      const pythonExecutable = path.join(__dirname, '../deploybot-env/bin/python3');
      console.log(`🐍 [PROCESS_MANAGER] Using Python executable: ${pythonExecutable}`);
      
      // Verify Python executable exists
      if (!fs.existsSync(pythonExecutable)) {
        throw new Error(`Python executable not found: ${pythonExecutable}`);
      }
      
      // Verify Python script exists
      if (!fs.existsSync(pythonScriptPath)) {
        throw new Error(`Python script not found: ${pythonScriptPath}`);
      }
      
      // Start Python process
      this.pythonProcess = spawn(pythonExecutable, [pythonScriptPath], {
        cwd: workingDir,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PATH: '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
          PYTHONUNBUFFERED: '1', // Ensure immediate output
          DEPLOYBOT_PROJECTS_ROOT: path.join(process.cwd(), 'projects') // Point to real projects directory
        }
      });
      
      console.log(`🐍 [PROCESS_MANAGER] Python process started with PID: ${this.pythonProcess.pid}`);
      this.state.startedAt = new Date().toISOString();
      
      // Set up process event handlers
      this.setupProcessHandlers();
      
      // Wait for backend to be ready
      const isReady = await this.waitForBackendReady();
      
      if (isReady) {
        this.state.backend = 'running';
        this.emit('backend-state-changed', this.state.backend);
        console.log('✅ [PROCESS_MANAGER] Backend started successfully');
        return true;
      } else {
        throw new Error('Backend did not become ready within timeout');
      }
      
    } catch (error) {
      console.error(`❌ [PROCESS_MANAGER] Failed to start backend: ${error.message}`);
      this.state.backend = 'error';
      this.state.lastError = error.message;
      this.emit('backend-state-changed', this.state.backend);
      
      // Cleanup on failure
      if (this.pythonProcess) {
        this.pythonProcess.kill('SIGKILL');
        this.pythonProcess = null;
      }
      
      return false;
    }
  }

  /**
   * Set up Python process event handlers
   */
  setupProcessHandlers() {
    if (!this.pythonProcess) return;
    
    // Handle stdout
    this.pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      console.log('🐍 [PYTHON_STDOUT]', output);
      this.emit('python-output', output);
    });
    
    // Handle stderr
    this.pythonProcess.stderr.on('data', (data) => {
      const error = data.toString().trim();
      console.error('🐍 [PYTHON_STDERR]', error);
      this.emit('python-error', error);
    });
    
    // Handle process exit
    this.pythonProcess.on('close', (code, signal) => {
      console.log(`🐍 [PROCESS_MANAGER] Python process exited with code: ${code}, signal: ${signal}`);
      
      const wasRunning = this.state.backend === 'running';
      this.state.backend = 'stopped';
      this.state.startedAt = null;
      this.pythonProcess = null;
      
      this.emit('backend-state-changed', this.state.backend);
      
      // Auto-restart if it was running and we're not shutting down
      if (wasRunning && !this.isShuttingDown && code !== 0) {
        console.log('🔄 [PROCESS_MANAGER] Backend crashed, scheduling restart...');
        setTimeout(() => {
          if (!this.isShuttingDown) {
            this.startBackend();
          }
        }, 3000);
      }
    });
    
    // Handle process error
    this.pythonProcess.on('error', (error) => {
      console.error('❌ [PROCESS_MANAGER] Python process error:', error);
      this.state.backend = 'error';
      this.state.lastError = error.message;
      this.emit('backend-state-changed', this.state.backend);
      this.emit('python-error', `Process error: ${error.message}`);
    });
  }

  /**
   * Connect to WebSocket with proper retry logic
   */
  async connectWebSocket() {
    if (this.state.connection === 'connecting' || this.state.connection === 'connected') {
      console.log('⚠️ [PROCESS_MANAGER] WebSocket is already connecting or connected');
      return false;
    }
    
    this.state.connection = 'connecting';
    this.state.connectionAttempt++;
    this.emit('connection-state-changed', this.state.connection);
    
    console.log(`🔌 [PROCESS_MANAGER] Connecting to WebSocket (attempt ${this.state.connectionAttempt}/${this.config.maxConnectionAttempts})...`);
    
    try {
      const wsUrl = this.getWebSocketUrl();
      this.wsConnection = new WebSocket(wsUrl);
      
      // Set up connection timeout
      const connectionTimeout = setTimeout(() => {
        if (this.wsConnection && this.wsConnection.readyState !== WebSocket.OPEN) {
          this.wsConnection.terminate();
          this.handleConnectionError(new Error('Connection timeout'));
        }
      }, this.config.connectionTimeout);
      
      // Handle successful connection
      this.wsConnection.on('open', () => {
        clearTimeout(connectionTimeout);
        console.log('✅ [PROCESS_MANAGER] WebSocket connected successfully');
        
        this.state.connection = 'connected';
        this.state.connectedAt = new Date().toISOString();
        this.state.connectionAttempt = 0; // Reset attempt counter
        
        this.emit('connection-state-changed', this.state.connection);
        this.startHealthMonitoring();
        
        // Send initial ping
        this.sendPing();
      });
      
      // Handle incoming messages
      this.wsConnection.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          console.log('📥 [PROCESS_MANAGER] WebSocket message:', message.type || 'unknown');
          this.emit('websocket-message', message);
        } catch (error) {
          console.error('❌ [PROCESS_MANAGER] Error parsing WebSocket message:', error);
        }
      });
      
      // Handle connection close
      this.wsConnection.on('close', (code, reason) => {
        clearTimeout(connectionTimeout);
        console.log(`🔌 [PROCESS_MANAGER] WebSocket connection closed: ${code} - ${reason}`);
        
        this.state.connection = 'disconnected';
        this.state.connectedAt = null;
        this.wsConnection = null;
        
        this.emit('connection-state-changed', this.state.connection);
        this.stopHealthMonitoring();
        
        // Auto-reconnect if not shutting down
        if (!this.isShuttingDown && this.state.backend === 'running') {
          this.scheduleReconnect();
        }
      });
      
      // Handle connection errors
      this.wsConnection.on('error', (error) => {
        clearTimeout(connectionTimeout);
        this.handleConnectionError(error);
      });
      
      return true;
      
    } catch (error) {
      console.error(`❌ [PROCESS_MANAGER] Failed to create WebSocket connection: ${error.message}`);
      this.handleConnectionError(error);
      return false;
    }
  }

  /**
   * Handle WebSocket connection errors
   */
  handleConnectionError(error) {
    console.error('❌ [PROCESS_MANAGER] WebSocket connection error:', error.message);
    
    this.state.connection = 'error';
    this.state.lastError = error.message;
    this.wsConnection = null;
    
    this.emit('connection-state-changed', this.state.connection);
    this.stopHealthMonitoring();
    
    // Schedule reconnect if not at max attempts
    if (!this.isShuttingDown && this.state.connectionAttempt < this.config.maxConnectionAttempts) {
      this.scheduleReconnect();
    }
  }

  /**
   * Schedule WebSocket reconnection with exponential backoff
   */
  scheduleReconnect() {
    const backoffDelay = Math.min(1000 * Math.pow(2, this.state.connectionAttempt - 1), 30000); // Max 30 seconds
    
    console.log(`🔄 [PROCESS_MANAGER] Scheduling WebSocket reconnect in ${backoffDelay}ms...`);
    
    this.connectionTimer = setTimeout(() => {
      if (!this.isShuttingDown) {
        this.connectWebSocket();
      }
    }, backoffDelay);
  }

  /**
   * Send ping message to backend
   */
  sendPing() {
    if (this.state.connection === 'connected' && this.wsConnection) {
      try {
        this.wsConnection.send(JSON.stringify({
          command: 'ping',
          data: { timestamp: new Date().toISOString() }
        }));
        console.log('📡 [PROCESS_MANAGER] Ping sent to backend');
      } catch (error) {
        console.error('❌ [PROCESS_MANAGER] Failed to send ping:', error);
      }
    }
  }

  /**
   * Send command to backend via WebSocket with proper response handling
   */
  async sendCommand(command, data = {}) {
    return new Promise((resolve, reject) => {
      if (this.state.connection !== 'connected' || !this.wsConnection) {
        reject(new Error('WebSocket not connected'));
        return;
      }
      
      try {
        const messageId = `${command}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        const message = {
          command,
          data,
          messageId,
          timestamp: new Date().toISOString()
        };
        
        // Set up response listener with timeout
        const timeout = setTimeout(() => {
          this.wsConnection.removeListener('message', responseListener);
          reject(new Error(`Command ${command} timed out after 10 seconds`));
        }, 10000);
        
        const responseListener = (data) => {
          try {
            const response = JSON.parse(data.toString());
            // Check if this is the response to our command
            if (response.messageId === messageId || (response.command === command && response.type === 'response')) {
              clearTimeout(timeout);
              this.wsConnection.removeListener('message', responseListener);
              console.log(`📥 [PROCESS_MANAGER] Response received for ${command}:`, JSON.stringify(response, null, 2));
              resolve(response);
            }
          } catch (error) {
            console.error('❌ [PROCESS_MANAGER] Error parsing response:', error);
          }
        };
        
        this.wsConnection.on('message', responseListener);
        
        this.wsConnection.send(JSON.stringify(message));
        console.log(`📤 [PROCESS_MANAGER] Command sent: ${command} (messageId: ${messageId})`);
        
      } catch (error) {
        console.error(`❌ [PROCESS_MANAGER] Failed to send command ${command}:`, error);
        reject(error);
      }
    });
  }

  /**
   * Start health monitoring
   */
  startHealthMonitoring() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }
    
    console.log('❤️ [PROCESS_MANAGER] Starting health monitoring...');
    
    this.healthCheckTimer = setInterval(() => {
      if (this.state.connection === 'connected') {
        this.sendPing();
      }
    }, this.config.healthCheckInterval);
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring() {
    if (this.healthCheckTimer) {
      console.log('❤️ [PROCESS_MANAGER] Stopping health monitoring...');
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }
  }

  /**
   * Complete startup sequence - starts backend and connects WebSocket
   */
  async startComplete(isDev = false) {
    if (this.startupSequenceActive) {
      console.log('⚠️ [PROCESS_MANAGER] Startup sequence already active');
      return false;
    }
    
    this.startupSequenceActive = true;
    this.isShuttingDown = false;
    
    console.log('🚀 [PROCESS_MANAGER] Starting complete startup sequence...');
    
    try {
      // Start backend
      const backendStarted = await this.startBackend(isDev);
      if (!backendStarted) {
        throw new Error('Failed to start backend');
      }
      
      // Connect WebSocket
      const wsConnected = await this.connectWebSocket();
      if (!wsConnected) {
        throw new Error('Failed to connect WebSocket');
      }
      
      console.log('✅ [PROCESS_MANAGER] Complete startup sequence successful');
      this.emit('startup-complete', this.getStatus());
      return true;
      
    } catch (error) {
      console.error(`❌ [PROCESS_MANAGER] Startup sequence failed: ${error.message}`);
      this.emit('startup-failed', error);
      return false;
    } finally {
      this.startupSequenceActive = false;
    }
  }

  /**
   * Comprehensive shutdown with proper cleanup order
   */
  async shutdown() {
    if (this.isShuttingDown) {
      console.log('⚠️ [PROCESS_MANAGER] Shutdown already in progress');
      return;
    }
    
    this.isShuttingDown = true;
    console.log('🛑 [PROCESS_MANAGER] Starting comprehensive shutdown...');
    
    // Clear all timers
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }
    
    if (this.connectionTimer) {
      clearTimeout(this.connectionTimer);
      this.connectionTimer = null;
    }
    
    if (this.startupTimer) {
      clearTimeout(this.startupTimer);
      this.startupTimer = null;
    }
    
    // Close WebSocket connection
    if (this.wsConnection) {
      console.log('🔌 [PROCESS_MANAGER] Closing WebSocket connection...');
      try {
        this.wsConnection.close();
      } catch (error) {
        console.warn('⚠️ [PROCESS_MANAGER] Warning closing WebSocket:', error.message);
      }
      this.wsConnection = null;
    }
    
    // Shutdown Python process
    if (this.pythonProcess) {
      console.log(`🐍 [PROCESS_MANAGER] Shutting down Python process (PID: ${this.pythonProcess.pid})...`);
      
      try {
        // First try graceful shutdown
        this.pythonProcess.kill('SIGTERM');
        
        // Wait for graceful shutdown or force kill
        const forceKillTimer = setTimeout(() => {
          if (this.pythonProcess && !this.pythonProcess.killed) {
            console.log('🔪 [PROCESS_MANAGER] Force killing Python process...');
            this.pythonProcess.kill('SIGKILL');
          }
        }, this.config.gracefulShutdownTimeout);
        
        // Clear timer if process exits gracefully
        this.pythonProcess.on('close', () => {
          clearTimeout(forceKillTimer);
        });
        
      } catch (error) {
        console.error('❌ [PROCESS_MANAGER] Error shutting down Python process:', error);
      }
      
      this.pythonProcess = null;
    }
    
    // Final port cleanup
    await this.cleanupPort();
    
    // Reset state
    this.state.backend = 'stopped';
    this.state.connection = 'disconnected';
    this.state.startedAt = null;
    this.state.connectedAt = null;
    
    console.log('✅ [PROCESS_MANAGER] Shutdown completed');
    this.emit('shutdown-complete');
  }

  /**
   * Emergency cleanup - forces cleanup of all resources
   */
  async emergencyCleanup() {
    console.log('🚨 [PROCESS_MANAGER] Emergency cleanup initiated...');
    
    // Force kill Python process
    if (this.pythonProcess) {
      try {
        this.pythonProcess.kill('SIGKILL');
      } catch (error) {
        console.warn('⚠️ [PROCESS_MANAGER] Warning during emergency Python cleanup:', error.message);
      }
      this.pythonProcess = null;
    }
    
    // Force close WebSocket
    if (this.wsConnection) {
      try {
        this.wsConnection.terminate();
      } catch (error) {
        console.warn('⚠️ [PROCESS_MANAGER] Warning during emergency WebSocket cleanup:', error.message);
      }
      this.wsConnection = null;
    }
    
    // Aggressive port cleanup
    await this.cleanupPort();
    
    // Clear all timers
    if (this.healthCheckTimer) clearInterval(this.healthCheckTimer);
    if (this.connectionTimer) clearTimeout(this.connectionTimer);
    if (this.startupTimer) clearTimeout(this.startupTimer);
    
    console.log('✅ [PROCESS_MANAGER] Emergency cleanup completed');
  }
}

module.exports = ProcessManager;
