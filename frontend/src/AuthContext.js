import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('session_token'));
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    checkAuth();
  }, []);

  // Start polling when authenticated
  useEffect(() => {
    if (isAuthenticated && token) {
      startPolling();
    } else {
      stopPolling();
    }
  }, [isAuthenticated, token]);

  // Polling for notifications and messages
  const startPolling = () => {
    if (pollIntervalRef.current) return; // Already polling
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const currentToken = localStorage.getItem('session_token');
        if (!currentToken) return;
        
        // Poll for notifications
        const notificationsResponse = await axios.get(`${API}/notifications/poll`, {
          headers: { Authorization: `Bearer ${currentToken}` }
        });
        
        // Update notifications if there are new ones
        if (notificationsResponse.data.length > 0) {
          setNotifications(prev => {
            const newNotifications = notificationsResponse.data.filter(newNotif => 
              !prev.some(existingNotif => existingNotif.id === newNotif.id)
            );
            
            // Show browser notification for new notifications
            newNotifications.forEach(notification => {
              if (Notification.permission === 'granted') {
                new Notification(notification.title, {
                  body: notification.message,
                  icon: '/favicon.ico'
                });
              }
            });
            
            return [...newNotifications, ...prev.slice(0, 49)]; // Keep last 50
          });
        }
        
        // Poll for unread messages
        const messagesResponse = await axios.get(`${API}/messages/poll`, {
          headers: { Authorization: `Bearer ${currentToken}` }
        });
        
        setUnreadMessages(messagesResponse.data.unread_count);
        
      } catch (error) {
        console.error('Polling error:', error);
        if (error.response?.status === 401) {
          // Token expired, logout
          logout();
        }
      }
    }, 3000); // Poll every 3 seconds
  };

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  // Request notification permission
  const requestNotificationPermission = () => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  };

  const checkAuth = async () => {
    const storedToken = localStorage.getItem('session_token');
    if (storedToken) {
      try {
        const response = await axios.get(`${API}/auth/me`, {
          headers: { Authorization: `Bearer ${storedToken}` }
        });
        
        setUser(response.data);
        setToken(storedToken);
        setIsAuthenticated(true);
        
        // Set default axios header
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        
        // Start polling for notifications
        startPolling();
        
        // Request notification permission
        requestNotificationPermission();
        
      } catch (error) {
        // Token is invalid, remove it
        localStorage.removeItem('session_token');
        setUser(null);
        setToken(null);
        setIsAuthenticated(false);
        delete axios.defaults.headers.common['Authorization'];
      }
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });

      const { session_token, user: userData } = response.data;
      
      // Store token
      localStorage.setItem('session_token', session_token);
      setToken(session_token);
      setUser(userData);
      setIsAuthenticated(true);

      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${session_token}`;

      // Start polling for notifications
      startPolling();
      
      // Request notification permission
      requestNotificationPermission();

      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      return { success: false, error: message };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${API}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.log('Logout API call failed, but continuing with local logout');
    }

    // Stop polling
    stopPolling();

    // Clear local storage and state
    localStorage.removeItem('session_token');
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    setNotifications([]);
    setUnreadMessages(0);
    delete axios.defaults.headers.common['Authorization'];
  };

  const clearNotifications = async () => {
    try {
      await axios.post(`${API}/notifications/mark-read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications([]);
    } catch (error) {
      console.error('Error clearing notifications:', error);
    }
  };

  const markMessagesAsRead = () => {
    setUnreadMessages(0);
  };

  const isAdmin = () => {
    return user?.role === 'admin';
  };

  const canEdit = () => {
    return isAdmin();
  };

  const canCreate = () => {
    return isAdmin();
  };

  const canDelete = () => {
    return isAdmin();
  };

  const hasProjectAccess = (projectId) => {
    if (isAdmin()) return true;
    return user?.assigned_projects?.includes(projectId) || false;
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated,
    notifications,
    unreadMessages,
    login,
    logout,
    isAdmin,
    canEdit,
    canCreate,
    canDelete,
    hasProjectAccess,
    clearNotifications,
    markMessagesAsRead
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};