import React, { useState } from 'react';
import { useAuth } from '../AuthContext';

const NotificationPanel = ({ isOpen, onClose }) => {
  const { notifications, clearNotifications } = useAuth();

  if (!isOpen) return null;

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

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

  const getPriorityColor = (type) => {
    switch (type) {
      case 'task_completed': return 'text-green-600';
      case 'task_created':
      case 'project_created': return 'text-blue-600';
      case 'message_received': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-end">
      <div className="w-96 bg-white h-full shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-purple-600 text-white p-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-xl">🔔</span>
            <h2 className="text-lg font-semibold">Notifications</h2>
          </div>
          <div className="flex items-center gap-2">
            {notifications.length > 0 && (
              <button
                onClick={clearNotifications}
                className="text-white hover:text-purple-200 text-sm underline"
              >
                Clear All
              </button>
            )}
            <button
              onClick={onClose}
              className="text-white hover:text-purple-200 text-xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <span className="text-4xl mb-2">🔔</span>
              <p className="text-lg font-medium">No notifications yet</p>
              <p className="text-sm">You'll see real-time updates here</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {notifications.map((notification, index) => (
                <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">
                      {getNotificationIcon(notification.type)}
                    </span>
                    <div className="flex-1 min-w-0">
                      <h3 className={`font-medium text-sm ${getPriorityColor(notification.type)}`}>
                        {notification.title}
                      </h3>
                      <p className="text-gray-700 text-sm mt-1 break-words">
                        {notification.message}
                      </p>
                      <p className="text-gray-400 text-xs mt-2">
                        {formatTime(notification.created_at)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationPanel;