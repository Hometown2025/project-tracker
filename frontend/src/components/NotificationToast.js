import React, { useState, useEffect } from 'react';

const NotificationToast = ({ notification, onClose, duration = 5000 }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Fade in
    const timer1 = setTimeout(() => setIsVisible(true), 100);
    
    // Auto dismiss
    const timer2 = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300); // Wait for fade out animation
    }, duration);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [duration, onClose]);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'task_created': return '📋';
      case 'task_updated': return '✏️';
      case 'task_completed': return '✅';
      case 'project_created': return '🎯';
      case 'project_updated': return '🔄';
      case 'message_received': return '💬';
      default: return '🔔';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'task_completed': return 'border-l-green-500 bg-green-50';
      case 'task_created':
      case 'project_created': return 'border-l-blue-500 bg-blue-50';
      case 'message_received': return 'border-l-purple-500 bg-purple-50';
      default: return 'border-l-gray-500 bg-gray-50';
    }
  };

  if (!notification) return null;

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm w-full bg-white rounded-lg shadow-lg border-l-4 p-4 transform transition-all duration-300 ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      } ${getNotificationColor(notification.type)}`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl flex-shrink-0">
          {getNotificationIcon(notification.type)}
        </span>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 text-sm">
            {notification.title}
          </h4>
          <p className="text-gray-700 text-sm mt-1 break-words">
            {notification.message}
          </p>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
          }}
          className="text-gray-400 hover:text-gray-600 text-lg flex-shrink-0"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default NotificationToast;