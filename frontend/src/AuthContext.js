import React, { createContext, useContext, useState, useEffect } from 'react';
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

  useEffect(() => {
    checkAuth();
  }, []);

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

    // Clear local storage and state
    localStorage.removeItem('session_token');
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    delete axios.defaults.headers.common['Authorization'];
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
    login,
    logout,
    isAdmin,
    canEdit,
    canCreate,
    canDelete,
    hasProjectAccess
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};