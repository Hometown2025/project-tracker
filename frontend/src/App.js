import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { AuthProvider, useAuth } from "./AuthContext";
import LoginPage from "./LoginPage";
import AdminPanel from "./AdminPanel";
import Components from "./Components";
import NotificationToast from "./components/NotificationToast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Main App Component (wrapped with auth)
const AppContent = () => {
  const { user, isAuthenticated, loading, logout, isAdmin, notifications } = useAuth();
  const [currentView, setCurrentView] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [ideas, setIdeas] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [appLoading, setAppLoading] = useState(false);
  const [activeToasts, setActiveToasts] = useState([]);

  // Fetch data functions
  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const fetchTasks = async (projectId = null) => {
    try {
      let url = `${API}/tasks`;
      if (projectId) url += `?project_id=${projectId}`;
      const response = await axios.get(url);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const fetchIdeas = async (projectId = null) => {
    try {
      let url = `${API}/ideas`;
      if (projectId) url += `?project_id=${projectId}`;
      const response = await axios.get(url);
      setIdeas(response.data);
    } catch (error) {
      console.error('Error fetching ideas:', error);
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      if (error.response?.status === 401) {
        logout();
      }
    }
  };

  const refreshData = () => {
    fetchProjects();
    fetchDashboardStats();
    fetchTasks();
    fetchIdeas();
  };

  // Handle new notifications for toasts
  useEffect(() => {
    if (notifications.length > 0) {
      const latestNotification = notifications[0];
      
      // Check if this notification is already being shown as a toast
      const isAlreadyShown = activeToasts.some(toast => 
        toast.id === latestNotification.id || 
        (toast.created_at === latestNotification.created_at && toast.title === latestNotification.title)
      );
      
      if (!isAlreadyShown) {
        const toastId = latestNotification.id || `toast-${Date.now()}`;
        setActiveToasts(prev => [...prev, { ...latestNotification, toastId }]);
      }
    }
  }, [notifications]);

  const removeToast = (toastId) => {
    setActiveToasts(prev => prev.filter(toast => toast.toastId !== toastId));
  };

  const handleLogout = () => {
    logout();
    setCurrentView('dashboard');
    setSelectedProject(null);
    setProjects([]);
    setTasks([]);
    setIdeas([]);
    setDashboardStats(null);
  };

  // Load initial data when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      setAppLoading(true);
      Promise.all([
        fetchProjects(),
        fetchDashboardStats(),
        fetchTasks(),
        fetchIdeas()
      ]).finally(() => {
        setAppLoading(false);
      });
    }
  }, [isAuthenticated]);

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading TaskFlow...</p>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Show app loading screen while fetching data
  if (appLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Loading your projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Components.Navigation 
        currentView={currentView} 
        setCurrentView={setCurrentView}
        projects={projects}
        setSelectedProject={setSelectedProject}
        selectedProject={selectedProject}
        user={user}
        onLogout={handleLogout}
        onShowAdmin={() => setShowAdminPanel(true)}
      />
      
      <main className="main-content">
        {currentView === 'dashboard' && (
          <Components.Dashboard 
            stats={dashboardStats}
            projects={projects}
            tasks={tasks}
            setCurrentView={setCurrentView}
            setSelectedProject={setSelectedProject}
            user={user}
          />
        )}
        
        {currentView === 'tasks' && (
          <Components.TaskView 
            tasks={tasks}
            projects={projects}
            selectedProject={selectedProject}
            refreshData={refreshData}
            user={user}
          />
        )}
        
        {currentView === 'calendar' && (
          <Components.CalendarView 
            tasks={tasks}
            projects={projects}
            refreshData={refreshData}
            user={user}
          />
        )}
        
        {currentView === 'budget' && (
          <Components.BudgetView 
            projects={projects}
            selectedProject={selectedProject}
            onProjectSelect={setSelectedProject}
            refreshData={refreshData}
            user={user}
          />
        )}
        
        {currentView === 'ideas' && (
          <Components.IdeasBoard 
            ideas={ideas}
            projects={projects}
            selectedProject={selectedProject}
            refreshData={refreshData}
            user={user}
          />
        )}
        
        {currentView === 'projects' && (
          <Components.ProjectView 
            projects={projects}
            refreshData={refreshData}
            setSelectedProject={setSelectedProject}
            setCurrentView={setCurrentView}
            user={user}
          />
        )}

        {currentView === 'trusses' && (
          <Components.TrussView 
            refreshData={refreshData}
            user={user}
          />
        )}
      </main>

      {showAdminPanel && (
        <AdminPanel onClose={() => setShowAdminPanel(false)} />
      )}

      {/* Notification Toasts */}
      {activeToasts.map((toast, index) => (
        <div key={toast.toastId} style={{ top: `${20 + index * 80}px` }}>
          <NotificationToast 
            notification={toast}
            onClose={() => removeToast(toast.toastId)}
            duration={5000}
          />
        </div>
      ))}
    </div>
  );
};

// Main App with Auth Provider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;