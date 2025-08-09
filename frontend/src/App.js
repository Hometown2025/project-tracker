import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import Components from "./Components";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [ideas, setIdeas] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch data functions
  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
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
    }
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  };

  useEffect(() => {
    fetchProjects();
    fetchDashboardStats();
    fetchTasks();
    fetchIdeas();
  }, []);

  const refreshData = () => {
    fetchProjects();
    fetchDashboardStats();
    fetchTasks();
    fetchIdeas();
  };

  return (
    <div className="App">
      <Components.Navigation 
        currentView={currentView} 
        setCurrentView={setCurrentView}
        projects={projects}
        setSelectedProject={setSelectedProject}
        selectedProject={selectedProject}
      />
      
      <main className="main-content">
        {currentView === 'dashboard' && (
          <Components.Dashboard 
            stats={dashboardStats}
            projects={projects}
            tasks={tasks}
            setCurrentView={setCurrentView}
            setSelectedProject={setSelectedProject}
          />
        )}
        
        {currentView === 'tasks' && (
          <Components.TaskView 
            tasks={tasks}
            projects={projects}
            selectedProject={selectedProject}
            refreshData={refreshData}
          />
        )}
        
        {currentView === 'calendar' && (
          <Components.CalendarView 
            tasks={tasks}
            projects={projects}
            refreshData={refreshData}
          />
        )}
        
        {currentView === 'ideas' && (
          <Components.IdeasBoard 
            ideas={ideas}
            projects={projects}
            selectedProject={selectedProject}
            refreshData={refreshData}
          />
        )}
        
        {currentView === 'projects' && (
          <Components.ProjectView 
            projects={projects}
            refreshData={refreshData}
            setSelectedProject={setSelectedProject}
            setCurrentView={setCurrentView}
          />
        )}
      </main>
    </div>
  );
}

export default App;