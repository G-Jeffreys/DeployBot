/**
 * WebSocket Bridge for DeployBot
 * 
 * This module handles WebSocket communication between the Electron main process
 * and the Python LangGraph backend. It provides a clean interface for sending
 * commands and receiving real-time updates.
 */

const WebSocket = require('ws');
const log = require('electron-log');

class WebSocketBridge {
  constructor(url = 'ws://localhost:8765') {
    this.url = url;
    this.ws = null;
    this.isConnected = false;
    this.reconnectInterval = 5000; // 5 seconds
    this.reconnectTimer = null;
    this.messageQueue = [];
    this.eventHandlers = {};
    
    console.log('🔌 [WS_BRIDGE] WebSocket bridge initialized', { url: this.url });
    log.info('WebSocket bridge initialized', { url: this.url });
  }

  /**
   * Connect to the Python WebSocket server
   */
  async connect() {
    console.log('🔌 [WS_BRIDGE] Attempting to connect to Python backend...');
    log.info('Attempting WebSocket connection');

    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.on('open', () => {
        console.log('✅ [WS_BRIDGE] Connected to Python backend successfully');
        log.info('WebSocket connected successfully');
        
        this.isConnected = true;
        this.clearReconnectTimer();
        this.processMessageQueue();
        this.emit('connected');
      });

      this.ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          console.log('📥 [WS_BRIDGE] Message received from Python:', message);
          log.debug('WebSocket message received', { type: message.type });
          
          this.handleMessage(message);
        } catch (error) {
          console.error('❌ [WS_BRIDGE] Error parsing message:', error);
          log.error('Error parsing WebSocket message', { error: error.message });
        }
      });

      this.ws.on('close', (code, reason) => {
        console.log('🔴 [WS_BRIDGE] Connection closed', { code, reason: reason.toString() });
        log.info('WebSocket connection closed', { code, reason: reason.toString() });
        
        this.isConnected = false;
        this.ws = null;
        this.emit('disconnected', { code, reason: reason.toString() });
        this.scheduleReconnect();
      });

      this.ws.on('error', (error) => {
        console.error('❌ [WS_BRIDGE] WebSocket error:', error);
        log.error('WebSocket error', { error: error.message });
        
        this.emit('error', error);
      });

    } catch (error) {
      console.error('❌ [WS_BRIDGE] Failed to create WebSocket connection:', error);
      log.error('Failed to create WebSocket connection', { error: error.message });
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect() {
    console.log('🔴 [WS_BRIDGE] Disconnecting from Python backend...');
    log.info('Disconnecting WebSocket');
    
    this.clearReconnectTimer();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.isConnected = false;
    this.emit('disconnected', { code: 1000, reason: 'Manual disconnect' });
  }

  /**
   * Send a command to the Python backend
   */
  async sendCommand(command, data = {}) {
    console.log('📤 [WS_BRIDGE] Sending command to Python:', { command, data });
    log.info('Sending WebSocket command', { command });

    const message = {
      command,
      data,
      timestamp: new Date().toISOString(),
      id: this.generateMessageId()
    };

    if (this.isConnected && this.ws) {
      try {
        this.ws.send(JSON.stringify(message));
        console.log('✅ [WS_BRIDGE] Command sent successfully');
        
        // For now, return a success response immediately
        // In a full implementation, we'd wait for the actual response
        return {
          success: true,
          message: 'Command sent to Python backend',
          commandId: message.id
        };
      } catch (error) {
        console.error('❌ [WS_BRIDGE] Failed to send command:', error);
        log.error('Failed to send WebSocket command', { command, error: error.message });
        throw error;
      }
    } else {
      console.warn('⚠️ [WS_BRIDGE] Not connected, queueing message...');
      log.warn('WebSocket not connected, queueing message', { command });
      
      this.messageQueue.push(message);
      
      // Try to reconnect if not already attempting
      if (!this.reconnectTimer) {
        this.connect();
      }
      
      return {
        success: false,
        message: 'Not connected to Python backend, message queued',
        queued: true
      };
    }
  }

  /**
   * Handle incoming messages from Python backend
   */
  handleMessage(message) {
    const { type, event, data, command } = message;
    
    switch (type) {
      case 'system':
        console.log('🔔 [WS_BRIDGE] System event received:', event, data);
        this.emit('system', { event, data });
        break;
        
      case 'response':
        console.log('📋 [WS_BRIDGE] Command response received:', command, data);
        this.emit('response', { command, data });
        break;
        
      case 'error':
        console.error('❌ [WS_BRIDGE] Error message received:', message);
        this.emit('error', new Error(message.message || 'Unknown Python error'));
        break;
        
      case 'deploy_detected':
        console.log('🚀 [WS_BRIDGE] Deploy detected event received:', data);
        this.emit('deploy_detected', data);
        break;
        
      case 'task_selected':
        console.log('🎯 [WS_BRIDGE] Task selected event received:', data);
        this.emit('task_selected', data);
        break;
        
      default:
        console.log('📝 [WS_BRIDGE] Unknown message type received:', type, message);
        this.emit('message', message);
    }
  }

  /**
   * Register event handler
   */
  on(event, handler) {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = [];
    }
    this.eventHandlers[event].push(handler);
    
    console.log(`📡 [WS_BRIDGE] Event handler registered for: ${event}`);
  }

  /**
   * Remove event handler
   */
  off(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event] = this.eventHandlers[event].filter(h => h !== handler);
    }
  }

  /**
   * Emit event to registered handlers
   */
  emit(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`❌ [WS_BRIDGE] Error in event handler for ${event}:`, error);
          log.error('Error in WebSocket event handler', { event, error: error.message });
        }
      });
    }
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnect() {
    if (this.reconnectTimer) {
      return; // Already scheduled
    }
    
    console.log(`⏰ [WS_BRIDGE] Scheduling reconnect in ${this.reconnectInterval}ms...`);
    log.info('Scheduling WebSocket reconnect', { interval: this.reconnectInterval });
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      console.log('🔄 [WS_BRIDGE] Attempting reconnect...');
      this.connect();
    }, this.reconnectInterval);
  }

  /**
   * Clear reconnection timer
   */
  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
      console.log('⏹️ [WS_BRIDGE] Reconnect timer cleared');
    }
  }

  /**
   * Process queued messages after reconnection
   */
  processMessageQueue() {
    if (this.messageQueue.length === 0) {
      return;
    }
    
    console.log(`📤 [WS_BRIDGE] Processing ${this.messageQueue.length} queued messages...`);
    log.info('Processing queued WebSocket messages', { count: this.messageQueue.length });
    
    const queue = this.messageQueue.slice(); // Copy array
    this.messageQueue = []; // Clear original
    
    queue.forEach(message => {
      try {
        this.ws.send(JSON.stringify(message));
        console.log('✅ [WS_BRIDGE] Queued message sent:', message.command);
      } catch (error) {
        console.error('❌ [WS_BRIDGE] Failed to send queued message:', error);
        this.messageQueue.push(message); // Re-queue on failure
      }
    });
  }

  /**
   * Generate unique message ID
   */
  generateMessageId() {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get connection status
   */
  getStatus() {
    return {
      connected: this.isConnected,
      url: this.url,
      queuedMessages: this.messageQueue.length,
      hasReconnectTimer: !!this.reconnectTimer
    };
  }
}

module.exports = WebSocketBridge; 