import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const WS_URL = BACKEND_URL.replace(/^http/, 'ws');

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
  const wsRef = useRef(null);

  useEffect(() => {
    checkAuth();
  }, []);

  // WebSocket connection management
  const connectWebSocket = (userId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`${WS_URL}/ws/${userId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      if (data.type === 'notification') {
        // Add notification to state
        setNotifications(prev => [data.data, ...prev.slice(0, 49)]); // Keep last 50 notifications
        
        // Show browser notification if permitted
        if (Notification.permission === 'granted') {
          new Notification(data.data.title, {
            body: data.data.message,
            icon: '/favicon.ico'
          });
        }
      } else if (data.type === 'message') {
        // Handle incoming message
        setUnreadMessages(prev => prev + 1);
        
        // Show browser notification
        if (Notification.permission === 'granted') {
          new Notification('New Message', {
            body: `New message in ${data.data.conversation_title}`,
            icon: '/favicon.ico'
          });
        }
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds if user is still authenticated
      if (isAuthenticated) {
        setTimeout(() => {
          if (isAuthenticated && user) {
            connectWebSocket(user.id);
          }
        }, 5000);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    wsRef.current = ws;
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
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
        
        // Connect WebSocket
        connectWebSocket(response.data.id);
        
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

      // Connect WebSocket
      connectWebSocket(userData.id);
      
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

    // Disconnect WebSocket
    disconnectWebSocket();

    // Clear local storage and state
    localStorage.removeItem('session_token');
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    setNotifications([]);
    setUnreadMessages(0);
    delete axios.defaults.headers.common['Authorization'];
  };

  const clearNotifications = () => {
    setNotifications([]);
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