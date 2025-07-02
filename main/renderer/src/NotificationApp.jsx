import React, { useState, useEffect } from 'react';
import CustomNotification from './components/CustomNotification';

/**
 * NotificationApp - Standalone app for notification windows
 * This runs in separate windows created by the main process
 */
const NotificationApp = () => {
  const [notification, setNotification] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    console.log('🔔 [NOTIFICATION_APP] Notification app initialized');
    
    // Listen for notification data from main process
    const handleNotificationData = (event, notificationData) => {
      console.log('🔔 [NOTIFICATION_APP] Received notification data:', notificationData);
      setNotification(notificationData);
      setIsReady(true);
    };

    // Register IPC listener
    if (window.electronAPI?.ipcRenderer) {
      window.electronAPI.ipcRenderer.on('notification-data', handleNotificationData);
    }

    // Cleanup listener on unmount
    return () => {
      if (window.electronAPI?.ipcRenderer) {
        window.electronAPI.ipcRenderer.removeListener('notification-data', handleNotificationData);
      }
    };
  }, []);

  const handleNotificationAction = async (action, data = {}) => {
    console.log('🔔 [NOTIFICATION_APP] Handling action:', action, data);

    try {
      // Send action to main process
      const response = await window.electronAPI?.notificationAction(
        notification.id, 
        action, 
        data
      );
      
      console.log('🔔 [NOTIFICATION_APP] Action response:', response);
      
      // Close window after action (main process will handle this)
      if (action === 'dismiss') {
        window.close();
      }
    } catch (error) {
      console.error('❌ [NOTIFICATION_APP] Failed to handle action:', error);
      // Close window anyway on error
      window.close();
    }
  };

  // Show loading state until notification data is received
  if (!isReady || !notification) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-transparent">
        <div className="text-gray-500 text-sm">Loading notification...</div>
      </div>
    );
  }

  return (
    <div className="w-full h-full overflow-hidden bg-transparent">
      <CustomNotification 
        notification={notification}
        onAction={handleNotificationAction}
      />
    </div>
  );
};

export default NotificationApp; 