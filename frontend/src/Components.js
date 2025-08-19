import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NotificationPanel from './components/NotificationPanel';
import MessageCenter from './components/MessageCenter';
import NotificationToast from './components/NotificationToast';
import FileManager from './components/FileManager';
import SubtaskManager from './components/SubtaskManager';
import BudgetView from './components/BudgetView';
import { useAuth } from './AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Tags Input Component
const TagsInput = ({ tags, onChange, placeholder }) => {
  const [inputValue, setInputValue] = useState('');

  const handleInputKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const newTag = inputValue.trim();
      if (newTag && !tags.includes(newTag)) {
        onChange([...tags, newTag]);
      }
      setInputValue('');
    } else if (e.key === 'Backspace' && inputValue === '' && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const removeTag = (tagToRemove) => {
    onChange(tags.filter(tag => tag !== tagToRemove));
  };

  return (
    <div className="tags-input-container">
      <div className="tags-display">
        {tags.map((tag, index) => (
          <span key={index} className="tag">
            {tag}
            <button
              type="button"
              className="tag-remove"
              onClick={() => removeTag(tag)}
            >
              ×
            </button>
          </span>
        ))}
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleInputKeyDown}
          placeholder={tags.length === 0 ? placeholder : ''}
          className="tags-input"
        />
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = ({ currentView, setCurrentView, projects, setSelectedProject, selectedProject, user, onLogout, onShowAdmin, sidebarCollapsed, onToggleSidebar }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showMessages, setShowMessages] = useState(false);
  
  return (
    <>
      <nav className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <StoreLogo storeId={user?.store_id} className="sidebar-logo" />
            {!sidebarCollapsed && (
              <h2 className="sidebar-title">
                <svg className="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                House Builder
              </h2>
            )}
          </div>
          
          {/* Sidebar Toggle Button - Only show in header when expanded */}
          {!sidebarCollapsed && (
            <button 
              className="sidebar-toggle"
              onClick={onToggleSidebar}
              title="Collapse Sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M11 19l-7-7 7-7M3 12h18" />
              </svg>
            </button>
          )}
        </div>

        {/* Toggle Button Below Logo - Only show when collapsed */}
        {sidebarCollapsed && (
          <div className="collapsed-toggle-container">
            <button 
              className="sidebar-toggle collapsed-toggle"
              onClick={onToggleSidebar}
              title="Expand Sidebar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* Admin Panel Section - Now directly under the logo */}
        {(user?.role === 'admin' || user?.role === 'super_admin') && (
          <div className="admin-section">
            {!sidebarCollapsed && <h3 className="nav-section-title">Administration</h3>}
            <div className="nav-items">
              <button 
                className="nav-item nav-item-inactive admin-panel-button"
                onClick={onShowAdmin}
                title={sidebarCollapsed ? 'Admin Panel' : ''}
              >
                <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {!sidebarCollapsed && 'Admin Panel'}
              </button>
            </div>
          </div>
        )}

        {/* User Info Section - Now simplified */}
        <div className="user-info-section">
          <div className="user-avatar">
            <div className="avatar-circle">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            {!sidebarCollapsed && (
              <div className="user-details">
                <div className="username">{user?.username}</div>
                <div className={`user-role role-${user?.role}`}>
                  {(user?.role === 'admin' || user?.role === 'super_admin') ? 
                    (user?.role === 'super_admin' ? 'Super Admin' : 'Administrator') : 'Customer'}
                </div>
              </div>
            )}
          </div>
          
          {!sidebarCollapsed && (
            <div className="user-actions">
              <button className="user-action-btn logout-btn" onClick={onLogout} title="Logout">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          )}
        </div>
      
      <div className="nav-section">
        <h3 className="nav-section-title">Views</h3>
        <div className="nav-items">
          <button 
            className={`nav-item ${currentView === 'dashboard' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('dashboard')}
            title={sidebarCollapsed ? 'Dashboard' : ''}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
            </svg>
            {!sidebarCollapsed && 'Dashboard'}
          </button>
          
          <button 
            className={`nav-item ${currentView === 'projects' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('projects')}
            title={sidebarCollapsed ? 'House Projects' : ''}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            {!sidebarCollapsed && (
              <>
                House Projects
                <span className="nav-badge">{user?.role === 'user' ? 'Assigned Only' : ''}</span>
              </>
            )}
          </button>

          <button 
            className={`nav-item ${currentView === 'tasks' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('tasks')}
            title={sidebarCollapsed ? 'House Rooms' : ''}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
            </svg>
            {!sidebarCollapsed && (
              <>
                House Rooms
                <span className="nav-badge">{user?.role === 'user' ? 'View Only' : ''}</span>
              </>
            )}
          </button>
          
          <button 
            className={`nav-item ${currentView === 'budget' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('budget')}
            title={sidebarCollapsed ? 'Budget' : ''}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            {!sidebarCollapsed && 'Budget'}
          </button>
          
          <button 
            className={`nav-item ${currentView === 'calendar' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('calendar')}
            title={sidebarCollapsed ? 'Calendar' : ''}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {!sidebarCollapsed && 'Calendar'}
          </button>
          
          <button 
            className={`nav-item ${currentView === 'ideas' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('ideas')}
            title={sidebarCollapsed ? 'Ideas' : ''}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            {!sidebarCollapsed && 'Ideas'}
          </button>

          {/* Trusses tab - Admin only */}
          {(user?.role === 'admin' || user?.role === 'super_admin') && (
            <button 
              className={`nav-item ${currentView === 'trusses' ? 'nav-item-active' : 'nav-item-inactive'}`}
              onClick={() => setCurrentView('trusses')}
              title={sidebarCollapsed ? 'Trusses (Admin Only)' : ''}
            >
              <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              {!sidebarCollapsed && (
                <>
                  Trusses
                  <span className="nav-badge">Admin Only</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {projects.length > 0 && !sidebarCollapsed && (
        <div className="nav-section">
          <h3 className="nav-section-title">Your Projects</h3>
          <div className="nav-items">
            <button 
              className={`nav-item ${!selectedProject ? 'nav-item-active' : 'nav-item-inactive'}`}
              onClick={() => setSelectedProject(null)}
            >
              All Projects ({projects.length})
            </button>
            <div className="project-list-scrollable">
              {projects.map(project => (
                <button 
                  key={project.id}
                  className={`nav-item ${selectedProject?.id === project.id ? 'nav-item-active' : 'nav-item-inactive'}`}
                  onClick={() => setSelectedProject(project)}
                >
                  <div 
                    className="project-color-dot" 
                    style={{ backgroundColor: project.color }}
                  ></div>
                  {project.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </nav>

    {/* Notification Panel */}
    <NotificationPanel 
      isOpen={showNotifications}
      onClose={() => setShowNotifications(false)}
    />

    {/* Message Center */}
    <MessageCenter 
      isOpen={showMessages}
      onClose={() => setShowMessages(false)}
    />
  </>
);
};

// Notification Button Component
const NotificationButton = ({ onClick }) => {
  const { notifications } = useAuth();
  
  return (
    <button 
      className="user-action-btn" 
      onClick={onClick} 
      title="Notifications"
    >
      <div className="relative">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {notifications.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
            {notifications.length > 9 ? '9+' : notifications.length}
          </span>
        )}
      </div>
    </button>
  );
};

// Messages Button Component
const MessagesButton = ({ onClick }) => {
  const { unreadMessages } = useAuth();
  
  return (
    <button 
      className="user-action-btn" 
      onClick={onClick} 
      title="Messages"
    >
      <div className="relative">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        {unreadMessages > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
            {unreadMessages > 9 ? '9+' : unreadMessages}
          </span>
        )}
      </div>
    </button>
  );
};

// Dashboard Component
const Dashboard = ({ stats, projects, tasks, setCurrentView, setSelectedProject }) => {
  const recentTasks = tasks.slice(0, 5);
  const urgentTasks = tasks.filter(task => task.priority === 'high' && !task.completed).slice(0, 3);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Your productivity overview</p>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stats-card stats-card-total">
            <div className="stats-content">
              <div className="stats-number">{stats.total_projects}</div>
              <div className="stats-label">Total Projects</div>
            </div>
            <div className="stats-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M19 11H5m14-4H5m14 8H5m14 4H5" />
              </svg>
            </div>
          </div>

          <div className="stats-card stats-card-completed">
            <div className="stats-content">
              <div className="stats-number">{stats.completed_tasks}</div>
              <div className="stats-label">Tasks Completed</div>
            </div>
            <div className="stats-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          <div className="stats-card stats-card-overdue">
            <div className="stats-content">
              <div className="stats-number">{stats.overdue_tasks}</div>
              <div className="stats-label">Overdue Tasks</div>
            </div>
            <div className="stats-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          <div className="stats-card stats-card-ideas">
            <div className="stats-content">
              <div className="stats-number">{stats.ideas_count}</div>
              <div className="stats-label">Ideas Saved</div>
            </div>
            <div className="stats-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-content">
        <div className="dashboard-section">
          <div className="section-header">
            <h2 className="section-title">Recent Projects</h2>
            <button 
              className="btn-secondary"
              onClick={() => setCurrentView('projects')}
            >
              View All
            </button>
          </div>
          <div className="projects-grid">
            {projects.slice(0, 4).map(project => (
              <div key={project.id} className="project-card" onClick={() => {
                setSelectedProject(project);
                setCurrentView('tasks');
              }}>
                <div className="project-header">
                  <div className="project-color" style={{ backgroundColor: project.color }}></div>
                  <h3 className="project-name">{project.name}</h3>
                </div>
                <p className="project-description">{project.description || 'No description'}</p>
                <div className="project-stats">
                  <span className="project-stat">
                    {project.completed_tasks}/{project.task_count} tasks completed
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {urgentTasks.length > 0 && (
          <div className="dashboard-section">
            <div className="section-header">
              <h2 className="section-title">Urgent Tasks</h2>
              <button 
                className="btn-secondary"
                onClick={() => setCurrentView('tasks')}
              >
                View All
              </button>
            </div>
            <div className="task-list">
              {urgentTasks.map(task => (
                <div key={task.id} className="task-item">
                  <div className="task-priority priority-high"></div>
                  <div className="task-content">
                    <h4 className="task-title">{task.title}</h4>
                    <p className="task-due">Due: {task.due_date || 'No date'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Task View Component
const TaskView = ({ tasks, projects, selectedProject, refreshData }) => {
  const { user } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  const filteredTasks = tasks.filter(task => {
    if (selectedProject && task.project_id !== selectedProject.id) return false;
    if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
    if (filterStatus !== 'all' && task.status !== filterStatus) return false;
    return true;
  });

  const handleTaskToggle = async (task) => {
    try {
      await axios.put(`${API}/tasks/${task.id}`, {
        completed: !task.completed
      });
      refreshData();
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const generateStandardSubtasks = async (taskId, taskTitle) => {
    try {
      const response = await axios.post(`${API}/tasks/${taskId}/generate-subtasks`);
      const data = response.data;
      
      alert(`✅ ${data.message}\n\nRoom Type: ${data.room_type.charAt(0).toUpperCase() + data.room_type.slice(1)}\nSubtasks Created: ${data.total_created}\n\n${data.created_subtasks.map(st => '• ' + st.title).join('\n')}`);
      
      refreshData(); // Refresh to show new subtasks
    } catch (error) {
      console.error('Error generating subtasks:', error);
      if (error.response?.status === 400) {
        alert(`❌ ${error.response.data.detail}\n\nTip: Make sure the room name includes a recognizable room type like "Kitchen", "Bathroom", "Bedroom", etc.`);
      } else if (error.response?.data?.detail) {
        alert(`❌ ${error.response.data.detail}`);
      } else {
        alert('❌ Failed to generate standard subtasks. Please try again.');
      }
    }
  };

  return (
    <div className="task-view">
      <div className="view-header">
        <div>
          <h1 className="page-title">
            {selectedProject ? `${selectedProject.name} Tasks` : 'House Rooms'}
          </h1>
          <p className="page-subtitle">{filteredTasks.length} house rooms found across all projects</p>
        </div>
        {(user?.role === 'admin' || user?.role === 'super_admin') && (
          <button 
            className="btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add House Room
          </button>
        )}
      </div>

      <div className="filters">
        <select 
          className="filter-select"
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
        >
          <option value="all">All Priorities</option>
          <option value="high">High Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="low">Low Priority</option>
        </select>

        <select 
          className="filter-select"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="all">All Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div className="task-grid">
        {filteredTasks.map(task => {
          const project = projects.find(p => p.id === task.project_id);
          return (
            <div key={task.id} className={`task-card ${task.completed ? 'task-completed' : ''}`}>
              <div className="task-card-header">
                <div className="task-card-priority">
                  <div className={`priority-dot priority-${task.priority}`}></div>
                  <span className="priority-text">{task.priority}</span>
                </div>
                <div className="task-actions">
                  {(user?.role === 'admin' || user?.role === 'super_admin') && (
                    <button 
                      className="btn-icon task-edit"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingTask(task);
                        setShowEditModal(true);
                      }}
                      title="Edit room"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}
                  <button 
                    className={`checkbox ${task.completed ? 'checked' : ''}`}
                    onClick={() => handleTaskToggle(task)}
                  >
                    {task.completed && (
                      <svg className="check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              
              <h3 className="task-card-title">{task.title}</h3>
              {task.description && <p className="task-card-description">{task.description}</p>}
              
              {/* Generate Standard Subtasks Button (only for main rooms with no subtasks) */}
              {task.subtask_level === 0 && task.subtask_count === 0 && user && (user.role === 'admin' || user.role === 'super_admin') && (
                <div className="generate-subtasks-section">
                  <button 
                    className="btn-primary btn-sm generate-subtasks-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      generateStandardSubtasks(task.id, task.title);
                    }}
                    title="Auto-generate standard subtasks based on room type"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                            d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Generate Standard Subtasks
                  </button>
                  <small className="generate-subtasks-hint">
                    Create standard subtasks for this room type automatically
                  </small>
                </div>
              )}

              {/* Subtask Manager */}
              {task.subtask_level === 0 && (
                <SubtaskManager 
                  parentTask={task}
                  onSubtaskUpdate={refreshData}
                />
              )}

              {/* Room Budget Summary (for main rooms only) */}
              {task.subtask_level === 0 && (task.total_actual > 0 || task.subtask_actual_total > 0) && (
                <div className="room-budget-summary">
                  <h4 className="budget-summary-title">Room Budget & Costs</h4>
                  <div className="cost-grid">
                    <div className="cost-column">
                      <div className="budget-item">
                        <span className="budget-label">Room Budget:</span>
                        <span className="budget-amount">
                          ${(task.actual_cost || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                        </span>
                      </div>
                      <div className="budget-item">
                        <span className="budget-label">Subtasks Cost:</span>
                        <span className="budget-amount">
                          ${(task.subtask_actual_total || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                        </span>
                      </div>
                    </div>
                    <div className="cost-column">
                      <div className="budget-item total">
                        <span className="budget-label">Total Cost:</span>
                        <span className="budget-amount">
                          ${(task.total_actual || 0).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* File Manager for Tasks */}
              <FileManager 
                taskId={task.id}
                title={`Files (${task.file_count || 0})`}
              />
              
              <div className="task-card-footer">
                <div className="task-project-section">
                  {project ? (
                    <div className="task-project">
                      <div 
                        className="project-color-small" 
                        style={{ backgroundColor: project.color }}
                      ></div>
                      <span className="project-name-small">{project.name}</span>
                    </div>
                  ) : (
                    <div className="task-project unassigned">
                      <div className="project-color-small unassigned-color"></div>
                      <span className="project-name-small">Unassigned</span>
                    </div>
                  )}
                </div>
                <div className="task-dates">
                  {task.due_date && (
                    <span className="task-date task-due">
                      📋 Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                  {task.order_date && (
                    <span className="task-date task-order">
                      📦 Order: {new Date(task.order_date).toLocaleDateString()}
                    </span>
                  )}
                  {task.delivery_date && (
                    <span className="task-date task-delivery">
                      🚚 Delivery: {new Date(task.delivery_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {showCreateModal && (
        <CreateTaskModal 
          projects={projects}
          selectedProject={selectedProject}
          onClose={() => setShowCreateModal(false)}
          onSuccess={refreshData}
        />
      )}

      {showEditModal && editingTask && (
        <EditTaskModal 
          task={editingTask}
          projects={projects}
          onClose={() => {
            setShowEditModal(false);
            setEditingTask(null);
          }}
          onSuccess={refreshData}
        />
      )}
    </div>
  );
};

// Calendar View Component
const CalendarView = ({ tasks, projects, refreshData, setCurrentView, setSelectedProject }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarEvents, setCalendarEvents] = useState([]);

  useEffect(() => {
    fetchCalendarEvents();
  }, [tasks]);

  const fetchCalendarEvents = async () => {
    try {
      const response = await axios.get(`${API}/calendar`);
      setCalendarEvents(response.data);
    } catch (error) {
      console.error('Error fetching calendar events:', error);
    }
  };

  const handleEventClick = (event) => {
    if (event.project_id) {
      const project = projects.find(p => p.id === event.project_id);
      if (project) {
        setSelectedProject(project);
        setCurrentView('tasks');
      }
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Previous month's days
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const prevDate = new Date(year, month, -i);
      days.push({ date: prevDate, isCurrentMonth: false });
    }
    
    // Current month's days
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      days.push({ date: date, isCurrentMonth: true });
    }
    
    return days;
  };

  // Group events by date
  const eventsByDate = calendarEvents.reduce((acc, event) => {
    const dateKey = new Date(event.date).toDateString();
    if (!acc[dateKey]) acc[dateKey] = [];
    acc[dateKey].push(event);
    return acc;
  }, {});

  const days = getDaysInMonth(currentDate);

  return (
    <div className="calendar-view">
      <div className="view-header">
        <h1 className="page-title">Calendar</h1>
        <div className="calendar-nav">
          <button 
            className="btn-secondary"
            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
          >
            Previous
          </button>
          <h2 className="calendar-month">
            {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </h2>
          <button 
            className="btn-secondary"
            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
          >
            Next
          </button>
        </div>
      </div>

      {/* Calendar Legend */}
      <div className="calendar-legend">
        <div className="legend-item">
          <div className="legend-color due-date-color"></div>
          <span>📋 Due Date</span>
        </div>
        <div className="legend-item">
          <div className="legend-color order-date-color"></div>
          <span>📦 Order Date</span>
        </div>
        <div className="legend-item">
          <div className="legend-color delivery-date-color"></div>
          <span>🚚 Delivery Date</span>
        </div>
      </div>

      <div className="calendar-grid">
        <div className="calendar-header">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="calendar-day-header">{day}</div>
          ))}
        </div>
        
        <div className="calendar-days">
          {days.map(({ date, isCurrentMonth }, index) => {
            const dateKey = date.toDateString();
            const dayEvents = eventsByDate[dateKey] || [];
            const isToday = date.toDateString() === new Date().toDateString();
            
            return (
              <div 
                key={index} 
                className={`calendar-day ${!isCurrentMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}`}
              >
                <div className="calendar-day-number">{date.getDate()}</div>
                <div className="calendar-day-tasks">
                  {dayEvents.slice(0, 3).map(event => {
                    const project = projects.find(p => p.id === event.project_id);
                    return (
                      <div 
                        key={event.id} 
                        className={`calendar-event ${event.event_type} priority-${event.priority} ${project ? 'clickable' : ''}`}
                        style={{ borderColor: project?.color || '#8B5CF6' }}
                        title={`${event.title} (${event.event_label})\nProject: ${project?.name || 'No Project'}\nClick to view project`}
                        onClick={() => handleEventClick(event)}
                      >
                        <div className="calendar-event-content">
                          <div className="calendar-event-title">
                            {event.title.length > 20 ? `${event.title.substring(0, 20)}...` : event.title}
                          </div>
                          {project && (
                            <div className="calendar-event-project">
                              <div 
                                className="calendar-project-indicator"
                                style={{ backgroundColor: project.color }}
                              ></div>
                              <span className="calendar-project-name">
                                {project.name.length > 15 ? `${project.name.substring(0, 15)}...` : project.name}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                  {dayEvents.length > 3 && (
                    <div className="calendar-event-more">+{dayEvents.length - 3} more</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Ideas Board Component
const IdeasBoard = ({ ideas, projects, selectedProject, refreshData }) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingIdea, setEditingIdea] = useState(null);
  const { canEdit, canDelete } = useAuth();

  const filteredIdeas = ideas.filter(idea => 
    !selectedProject || idea.project_id === selectedProject.id
  );

  const handleDeleteIdea = async (ideaId, ideaTitle) => {
    if (window.confirm(`Are you sure you want to delete the idea "${ideaTitle}"?`)) {
      try {
        await axios.delete(`${API}/ideas/${ideaId}`);
        refreshData();
      } catch (error) {
        console.error('Error deleting idea:', error);
        alert('Failed to delete idea');
      }
    }
  };

  const handleEditIdea = (idea) => {
    setEditingIdea(idea);
  };

  const handleUpdateIdea = async (ideaData) => {
    try {
      await axios.put(`${API}/ideas/${editingIdea.id}`, ideaData);
      setEditingIdea(null);
      refreshData();
    } catch (error) {
      console.error('Error updating idea:', error);
      alert('Failed to update idea');
    }
  };

  return (
    <div className="ideas-board">
      <div className="view-header">
        <div>
          <h1 className="page-title">
            {selectedProject ? `${selectedProject.name} Ideas` : 'All Ideas'}
          </h1>
          <p className="page-subtitle">Visual inspiration board</p>
        </div>
        <button 
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Idea
        </button>
      </div>

      <div className="ideas-grid">
        {filteredIdeas.map(idea => {
          const project = projects.find(p => p.id === idea.project_id);
          return (
            <div key={idea.id} className="idea-card">
              {/* Edit/Delete Actions */}
              {(canEdit() || canDelete()) && (
                <div className="idea-actions">
                  {canEdit() && (
                    <button
                      onClick={() => handleEditIdea(idea)}
                      className="idea-action-btn edit"
                      title="Edit Idea"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}
                  {canDelete() && (
                    <button
                      onClick={() => handleDeleteIdea(idea.id, idea.title)}
                      className="idea-action-btn delete"
                      title="Delete Idea"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              )}

              {idea.image_data && (
                <div className="idea-image">
                  <img src={`data:image/jpeg;base64,${idea.image_data}`} alt={idea.title} />
                </div>
              )}
              
              <div className="idea-content">
                <h3 className="idea-title">{idea.title}</h3>
                {idea.description && <p className="idea-description">{idea.description}</p>}
                
                {idea.tags.length > 0 && (
                  <div className="idea-tags">
                    {idea.tags.map((tag, index) => (
                      <span key={index} className="idea-tag">{tag}</span>
                    ))}
                  </div>
                )}

                <div className="idea-footer">
                  {project && (
                    <div className="idea-project">
                      <div 
                        className="project-color-small" 
                        style={{ backgroundColor: project.color }}
                      ></div>
                      <span className="project-name-small">{project.name}</span>
                    </div>
                  )}
                  
                  {idea.pinterest_url && (
                    <a 
                      href={idea.pinterest_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="pinterest-link"
                    >
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.477 2 2 6.477 2 12c0 4.237 2.636 7.855 6.356 9.312-.088-.791-.167-2.005.035-2.868.181-.78 1.172-4.97 1.172-4.97s-.299-.6-.299-1.486c0-1.39.806-2.428 1.81-2.428.853 0 1.264.64 1.264 1.408 0 .858-.546 2.14-.828 3.33-.236.995.5 1.807 1.48 1.807 1.778 0 3.144-1.874 3.144-4.58 0-2.393-1.72-4.068-4.176-4.068-2.845 0-4.515 2.135-4.515 4.34 0 .859.331 1.781.745 2.281a.3.3 0 01.069.288l-.278 1.133c-.044.183-.145.223-.334.134-1.249-.581-2.03-2.407-2.03-3.874 0-3.154 2.292-6.052 6.608-6.052 3.469 0 6.165 2.473 6.165 5.776 0 3.447-2.173 6.22-5.19 6.22-1.013 0-1.965-.525-2.291-1.148l-.623 2.378c-.226.869-.835 1.958-1.244 2.621.937.29 1.931.446 2.962.446 5.523 0 10-4.477 10-10S17.523 2 12 2z"/>
                      </svg>
                      Pinterest
                    </a>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {showCreateModal && (
        <CreateIdeaModal 
          projects={projects}
          selectedProject={selectedProject}
          onClose={() => setShowCreateModal(false)}
          onSuccess={refreshData}
        />
      )}

      {editingIdea && (
        <EditIdeaModal 
          idea={editingIdea}
          projects={projects}
          onClose={() => setEditingIdea(null)}
          onSuccess={handleUpdateIdea}
        />
      )}
    </div>
  );
};

// Project View Component
const ProjectView = ({ projects, refreshData, setSelectedProject, setCurrentView }) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);

  return (
    <div className="project-view">
      <div className="view-header">
        <div>
          <h1 className="page-title">House Building Projects</h1>
          <p className="page-subtitle">Manage your house building projects</p>
        </div>
        <button 
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New House Project
        </button>
      </div>

      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card-large">
            <div className="project-card-header">
              <div className="project-color-large" style={{ backgroundColor: project.color }}></div>
              <div className="project-actions">
                <button 
                  className="btn-icon project-edit"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingProject(project);
                    setShowEditModal(true);
                  }}
                  title="Edit project"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button className="btn-icon">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                  </svg>
                </button>
              </div>
            </div>
            
            <h3 className="project-card-title">{project.name}</h3>
            <p className="project-card-description">{project.description || 'No description provided'}</p>
            
            <div className="project-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${project.task_count > 0 ? (project.completed_tasks / project.task_count) * 100 : 0}%`,
                    backgroundColor: project.color 
                  }}
                ></div>
              </div>
              <span className="progress-text">
                {project.completed_tasks}/{project.task_count} tasks completed
                {project.file_count > 0 && ` • ${project.file_count} files`}
              </span>
            </div>

            {/* Budget Summary */}
            {(project.project_total_budget > 0 || project.rooms_actual_spent > 0) && (
              <div className="project-budget-summary">
                <div className="budget-row">
                  <span className="budget-label">Total Budget:</span>
                  <span className="budget-value total">
                    ${project.project_total_budget?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}
                  </span>
                </div>
                <div className="budget-row">
                  <span className="budget-label">Allocated:</span>
                  <span className="budget-value allocated">
                    ${project.rooms_allocated_estimated?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}
                  </span>
                </div>
                <div className="budget-row">
                  <span className="budget-label">Spent:</span>
                  <span className="budget-value spent">
                    ${project.rooms_actual_spent?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}
                  </span>
                </div>
                {project.remaining_budget !== 0 && (
                  <div className="budget-row">
                    <span className="budget-label">Remaining:</span>
                    <span className={`budget-value remaining ${project.remaining_budget >= 0 ? 'positive' : 'negative'}`}>
                      ${project.remaining_budget?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '0.00'}
                    </span>
                  </div>
                )}
              </div>
            )}
            
            {/* File Manager for Projects */}
            <FileManager 
              projectId={project.id}
              title={`Files (${project.file_count || 0})`}
            />
            
            <div className="project-card-footer">
              <span className="project-date">
                Created {new Date(project.created_date).toLocaleDateString()}
              </span>
              <button 
                className="btn-secondary-small"
                onClick={() => {
                  setSelectedProject(project);
                  setCurrentView('tasks');
                }}
              >
                View Tasks
              </button>
            </div>
          </div>
        ))}
      </div>

      {showCreateModal && (
        <CreateProjectModal 
          onClose={() => setShowCreateModal(false)}
          onSuccess={refreshData}
        />
      )}

      {showEditModal && editingProject && (
        <EditProjectModal 
          project={editingProject}
          onClose={() => {
            setShowEditModal(false);
            setEditingProject(null);
          }}
          onSuccess={refreshData}
        />
      )}
    </div>
  );
};

// Edit Task Modal
const EditTaskModal = ({ task, projects, onClose, onSuccess }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    title: task.title || '',
    description: task.description || '',
    priority: task.priority || 'medium',
    due_date: task.due_date || '',
    order_date: task.order_date || '',
    delivery_date: task.delivery_date || '',
    actual_cost: task.actual_cost || '',
    project_id: task.project_id || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Only send fields that have values or have been changed
      const updateData = {};
      Object.keys(formData).forEach(key => {
        if (key === 'actual_cost') {
          // Handle cost field - allow 0 as valid value
          if (formData[key] !== '' && formData[key] !== null && formData[key] !== undefined) {
            updateData[key] = parseFloat(formData[key]) || null;
          }
        } else if (formData[key] !== '' && formData[key] !== null) {
          updateData[key] = formData[key];
        }
      });

      await axios.put(`${API}/tasks/${task.id}`, updateData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await axios.delete(`${API}/tasks/${task.id}`);
        onSuccess();
        onClose();
      } catch (error) {
        console.error('Error deleting task:', error);
      }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Edit Room</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Title</label>
            <input 
              type="text"
              className="form-input"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              className="form-textarea"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Priority</label>
              <select 
                className="form-select"
                value={formData.priority}
                onChange={(e) => setFormData({...formData, priority: e.target.value})}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Due Date</label>
              <input 
                type="date"
                className="form-input"
                value={formData.due_date}
                onChange={(e) => setFormData({...formData, due_date: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Order Date</label>
              <input 
                type="date"
                className="form-input"
                value={formData.order_date}
                onChange={(e) => setFormData({...formData, order_date: e.target.value})}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Delivery Date</label>
              <input 
                type="date"
                className="form-input"
                value={formData.delivery_date}
                onChange={(e) => setFormData({...formData, delivery_date: e.target.value})}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Project</label>
            <select 
              className="form-select"
              value={formData.project_id}
              onChange={(e) => setFormData({...formData, project_id: e.target.value})}
              required
            >
              <option value="">Select a project</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Budget</label>
              <input 
                type="number"
                className="form-input"
                value={formData.actual_cost}
                onChange={(e) => setFormData({...formData, actual_cost: e.target.value})}
                placeholder="Budget allocated for this room"
                min="0"
                step="0.01"
              />
            </div>
          </div>

          <div className="task-status-section">
            <div className="form-group">
              <label className="form-label">Status</label>
              <div className="task-status-display">
                <span className={`status-badge status-${task.status}`}>
                  {task.status?.replace('_', ' ').toUpperCase()}
                </span>
                {task.completed && (
                  <span className="completion-badge">
                    ✅ Completed {task.completed_date ? new Date(task.completed_date).toLocaleDateString() : ''}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="modal-actions">
            {(user?.role === 'admin' || user?.role === 'super_admin') && (
              <button 
                type="button" 
                className="btn-danger" 
                onClick={handleDelete}
              >
                Delete Task
              </button>
            )}
            <div className="modal-actions-right">
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Save Changes
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Room Modal
const CreateTaskModal = ({ projects, selectedProject, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    order_date: '',
    delivery_date: '',
    project_id: selectedProject?.id || '',
    actual_cost: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Only send non-empty fields to backend
      const submitData = {};
      Object.keys(formData).forEach(key => {
        if (key === 'actual_cost') {
          // Handle cost field - allow 0 as valid value
          if (formData[key] !== '' && formData[key] !== null && formData[key] !== undefined) {
            submitData[key] = parseFloat(formData[key]) || null;
          }
        } else if (formData[key] && formData[key].toString().trim() !== '') {
          submitData[key] = formData[key];
        }
      });
      
      // Title is always required
      if (!submitData.title) {
        alert('Task title is required');
        return;
      }

      await axios.post(`${API}/tasks`, submitData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Add House Room</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Title <span className="required">*</span></label>
            <input 
              type="text"
              className="form-input"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
              placeholder="Room name (e.g., Master Bedroom, Kitchen, Living Room)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description <span className="optional">(optional)</span></label>
            <textarea 
              className="form-textarea"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
              placeholder="Room specifications, materials needed, special requirements (optional)"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Priority</label>
              <select 
                className="form-select"
                value={formData.priority}
                onChange={(e) => setFormData({...formData, priority: e.target.value})}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Due Date <span className="optional">(optional)</span></label>
              <input 
                type="date"
                className="form-input"
                value={formData.due_date}
                onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                placeholder="Set due date later if needed"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Order Date <span className="optional">(optional)</span></label>
              <input 
                type="date"
                className="form-input"
                value={formData.order_date}
                onChange={(e) => setFormData({...formData, order_date: e.target.value})}
                placeholder="Set order date later if needed"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Delivery Date <span className="optional">(optional)</span></label>
              <input 
                type="date"
                className="form-input"
                value={formData.delivery_date}
                onChange={(e) => setFormData({...formData, delivery_date: e.target.value})}
                placeholder="Set delivery date later if needed"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">House Project (required)</label>
            <select 
              className="form-select"
              value={formData.project_id}
              onChange={(e) => setFormData({...formData, project_id: e.target.value})}
            >
              <option value="">Select which house project this room belongs to</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
            <small className="form-hint">You can assign this task to a project later</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Budget <span className="optional">(optional)</span></label>
              <input 
                type="number"
                className="form-input"
                value={formData.actual_cost}
                onChange={(e) => setFormData({...formData, actual_cost: e.target.value})}
                placeholder="Budget allocated for this room"
                min="0"
                step="0.01"
              />
            </div>
          </div>

          <div className="quick-create-note">
            <p className="note-text">
              💡 <strong>Quick Create:</strong> Just add a title to create the task quickly. 
              You can fill in the details later by editing the task.
            </p>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Room
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Idea Modal
const CreateIdeaModal = ({ projects, selectedProject, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    pinterest_url: '',
    tags: '',
    project_id: selectedProject?.id || ''
  });
  const [imageFile, setImageFile] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      let imageData = null;
      
      if (imageFile) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          imageData = e.target.result.split(',')[1]; // Remove data:image/jpeg;base64,
          
          const submitData = {
            ...formData,
            tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
            image_data: imageData
          };
          
          await axios.post(`${API}/ideas`, submitData);
          onSuccess();
          onClose();
        };
        reader.readAsDataURL(imageFile);
      } else {
        const submitData = {
          ...formData,
          tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        };
        
        await axios.post(`${API}/ideas`, submitData);
        onSuccess();
        onClose();
      }
    } catch (error) {
      console.error('Error creating idea:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Add New Idea</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Title</label>
            <input 
              type="text"
              className="form-input"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              className="form-textarea"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Image</label>
            <input 
              type="file"
              className="form-input"
              accept="image/*"
              onChange={handleImageChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Pinterest URL</label>
            <input 
              type="url"
              className="form-input"
              value={formData.pinterest_url}
              onChange={(e) => setFormData({...formData, pinterest_url: e.target.value})}
              placeholder="https://pinterest.com/pin/..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Tags (comma-separated)</label>
            <input 
              type="text"
              className="form-input"
              value={formData.tags}
              onChange={(e) => setFormData({...formData, tags: e.target.value})}
              placeholder="inspiration, design, ui, ux"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Project</label>
            <select 
              className="form-select"
              value={formData.project_id}
              onChange={(e) => setFormData({...formData, project_id: e.target.value})}
              required
            >
              <option value="">Select a project</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Add Idea
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Change History Modal Component
const ChangeHistoryModal = ({ project, onClose }) => {
  const [changeLogs, setChangeLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChangeLogs();
  }, [project.id]);

  const fetchChangeLogs = async () => {
    try {
      const response = await axios.get(`${API}/projects/${project.id}/change-logs`);
      setChangeLogs(response.data);
    } catch (error) {
      console.error('Error fetching change logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatChangeType = (changeType) => {
    const types = {
      'created': 'Created',
      'updated': 'Updated', 
      'deleted': 'Deleted',
      'completed': 'Completed',
      'status_changed': 'Status Changed'
    };
    return types[changeType] || changeType;
  };

  const formatEntityType = (entityType) => {
    const types = {
      'project': 'Project',
      'task': 'Room/Task',
      'subtask': 'Subtask'
    };
    return types[entityType] || entityType;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal change-history-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">
            Change History - {project.name}
          </h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading change history...</p>
            </div>
          ) : changeLogs.length === 0 ? (
            <div className="empty-state">
              <p>No changes recorded for this project yet.</p>
            </div>
          ) : (
            <div className="change-logs-list">
              {changeLogs.map((log) => (
                <div key={log.id} className="change-log-item">
                  <div className="change-log-header">
                    <div className="change-log-info">
                      <span className={`change-type ${log.change_type}`}>
                        {formatChangeType(log.change_type)}
                      </span>
                      <span className="entity-type">
                        {formatEntityType(log.entity_type)}
                      </span>
                      <span className="entity-title">
                        {log.entity_title}
                      </span>
                    </div>
                    <div className="change-log-meta">
                      <span className="user-info">
                        {log.username} ({log.user_role})
                      </span>
                      <span className="change-date">
                        {new Date(log.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="change-description">
                    {log.changes_description}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
const EditProjectModal = ({ project, onClose, onSuccess }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: project.name || '',
    description: project.description || '',
    color: project.color || '#8B5CF6',
    square_footage: project.square_footage || '',
    tags: project.tags || []
  });
  const [showChangeHistory, setShowChangeHistory] = useState(false);

  const colors = [
    '#8B5CF6', '#EF4444', '#F59E0B', '#10B981', '#3B82F6', 
    '#8B5A2B', '#EC4899', '#6366F1', '#84CC16', '#F97316'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Only send fields that have values
      const updateData = {};
      Object.keys(formData).forEach(key => {
        if (key === 'square_footage') {
          // Handle square footage field - allow 0 as valid value
          if (formData[key] !== '' && formData[key] !== null && formData[key] !== undefined) {
            updateData[key] = parseInt(formData[key]) || null;
          }
        } else if (formData[key] && formData[key].toString().trim() !== '') {
          updateData[key] = formData[key];
        }
      });

      await axios.put(`${API}/projects/${project.id}`, updateData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error updating project:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this project? This will also delete all associated tasks and ideas.')) {
      try {
        await axios.delete(`${API}/projects/${project.id}`);
        alert('Project deleted successfully!');
        onSuccess();
        onClose();
      } catch (error) {
        console.error('Error deleting project:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
        alert(`Failed to delete project: ${errorMessage}`);
      }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Edit Project</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Project Name</label>
            <input 
              type="text"
              className="form-input"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              className="form-textarea"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Color</label>
            <div className="color-picker">
              {colors.map(color => (
                <button
                  key={color}
                  type="button"
                  className={`color-option ${formData.color === color ? 'selected' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => setFormData({...formData, color})}
                />
              ))}
            </div>
          </div>

          <div className="project-status-section">
            <div className="form-group">
              <label className="form-label">Project Statistics</label>
              <div className="project-stats-display">
                <div className="stat-item">
                  <span className="stat-label">Total Tasks:</span>
                  <span className="stat-value">{project.task_count || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Completed Tasks:</span>
                  <span className="stat-value">{project.completed_tasks || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Progress:</span>
                  <span className="stat-value">
                    {project.task_count > 0 
                      ? `${Math.round((project.completed_tasks / project.task_count) * 100)}%`
                      : '0%'
                    }
                  </span>
                </div>
                {project.square_footage && (
                  <div className="stat-item">
                    <span className="stat-label">Square Footage:</span>
                    <span className="stat-value">{project.square_footage.toLocaleString()} sq ft</span>
                  </div>
                )}
                <div className="stat-item">
                  <span className="stat-label">Created:</span>
                  <span className="stat-value">
                    {new Date(project.created_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="modal-actions">
            {user && (user.role === 'admin' || user.role === 'super_admin') && (
              <button 
                type="button" 
                className="btn-danger" 
                onClick={handleDelete}
              >
                Delete Project
              </button>
            )}
            <button 
              type="button" 
              className="btn-secondary" 
              onClick={() => setShowChangeHistory(true)}
            >
              View Changes
            </button>
            <div className="modal-actions-right">
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Save Changes
              </button>
            </div>
          </div>
        </form>

        {showChangeHistory && (
          <ChangeHistoryModal 
            project={project}
            onClose={() => setShowChangeHistory(false)}
          />
        )}
      </div>
    </div>
  );
};

// Create Project Modal
const CreateProjectModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#8B5CF6',
    square_footage: '',
    tags: []
  });

  const colors = [
    '#8B5CF6', '#EF4444', '#F59E0B', '#10B981', '#3B82F6', 
    '#8B5A2B', '#EC4899', '#6366F1', '#84CC16', '#F97316'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Prepare data for submission, handle square footage field properly
      const submitData = { ...formData };
      if (submitData.square_footage !== '' && submitData.square_footage !== null) {
        submitData.square_footage = parseInt(submitData.square_footage) || null;
      } else {
        submitData.square_footage = null;
      }

      await axios.post(`${API}/projects`, submitData);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">New House Building Project</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Project Name</label>
            <input 
              type="text"
              placeholder="Enter house project name (e.g., '123 Main Street House')"
              className="form-input"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              placeholder="Project details: client info, lot specifications, house type, etc. (optional)"
              className="form-textarea"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Total Square Footage <span className="optional">(optional)</span></label>
            <input 
              type="number"
              placeholder="Enter total square footage (e.g., 2400)"
              className="form-input"
              value={formData.square_footage}
              onChange={(e) => setFormData({...formData, square_footage: e.target.value})}
              min="0"
              step="1"
            />
            <small className="form-hint">Total living space square footage of the house</small>
          </div>

          <div className="form-group">
            <label className="form-label">Tags <span className="optional">(optional)</span></label>
            <TagsInput 
              tags={formData.tags || []}
              onChange={(tags) => setFormData({...formData, tags})}
              placeholder="Add tags for organization (e.g., luxury, historic, custom)"
            />
            <small className="form-hint">Add tags to organize and categorize projects</small>
          </div>

          <div className="form-group">
            <label className="form-label">Color</label>
            <div className="color-picker">
              {colors.map(color => (
                <button
                  key={color}
                  type="button"
                  className={`color-option ${formData.color === color ? 'selected' : ''}`}
                  style={{ backgroundColor: color }}
                  onClick={() => setFormData({...formData, color})}
                />
              ))}
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Edit Idea Modal
const EditIdeaModal = ({ idea, projects, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: idea?.title || '',
    description: idea?.description || '',
    pinterest_url: idea?.pinterest_url || '',
    tags: idea?.tags?.join(', ') || '',
    project_id: idea?.project_id || ''
  });
  const [imageFile, setImageFile] = useState(null);
  const [currentImageData, setCurrentImageData] = useState(idea?.image_data || null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      // Preview the new image
      const reader = new FileReader();
      reader.onload = (e) => {
        setCurrentImageData(e.target.result.split(',')[1]);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setCurrentImageData(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      let imageData = currentImageData;
      
      if (imageFile) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          imageData = e.target.result.split(',')[1]; // Remove data:image/jpeg;base64,
          
          const submitData = {
            ...formData,
            tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
            image_data: imageData
          };
          
          await onSuccess(submitData);
        };
        reader.readAsDataURL(imageFile);
      } else {
        const submitData = {
          ...formData,
          tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          image_data: imageData
        };
        
        await onSuccess(submitData);
      }
    } catch (error) {
      console.error('Error updating idea:', error);
      alert('Failed to update idea');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Edit Idea</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Title</label>
            <input 
              type="text"
              className="form-input"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea 
              className="form-textarea"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Image</label>
            {currentImageData && (
              <div className="current-image-preview">
                <img 
                  src={`data:image/jpeg;base64,${currentImageData}`} 
                  alt="Current idea" 
                  style={{ maxWidth: '200px', maxHeight: '150px', objectFit: 'cover', marginBottom: '10px' }}
                />
                <button 
                  type="button" 
                  className="btn-secondary remove-image"
                  onClick={removeImage}
                  style={{ display: 'block', marginBottom: '10px' }}
                >
                  Remove Image
                </button>
              </div>
            )}
            <input 
              type="file"
              className="form-input"
              accept="image/*"
              onChange={handleImageChange}
            />
            {!currentImageData && <p className="form-help">Choose a new image to upload</p>}
            {currentImageData && <p className="form-help">Choose a file to replace the current image</p>}
          </div>

          <div className="form-group">
            <label className="form-label">Pinterest URL</label>
            <input 
              type="url"
              className="form-input"
              value={formData.pinterest_url}
              onChange={(e) => setFormData({...formData, pinterest_url: e.target.value})}
              placeholder="https://pinterest.com/pin/..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Tags (comma-separated)</label>
            <input 
              type="text"
              className="form-input"
              value={formData.tags}
              onChange={(e) => setFormData({...formData, tags: e.target.value})}
              placeholder="inspiration, design, ui, ux"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Project</label>
            <select 
              className="form-select"
              value={formData.project_id}
              onChange={(e) => setFormData({...formData, project_id: e.target.value})}
              required
            >
              <option value="">Select a project</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>{project.name}</option>
              ))}
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Update Idea
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Store Logo Component
const StoreLogo = ({ storeId, className = "store-logo" }) => {
  const [logoUrl, setLogoUrl] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (storeId) {
      fetchStoreLogo();
    }
  }, [storeId]);

  const fetchStoreLogo = async () => {
    try {
      const response = await axios.get(`${API}/stores/${storeId}/logo`);
      setLogoUrl(response.data.logo_url);
    } catch (error) {
      console.error('Error fetching store logo:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className={`${className} loading`}>Loading...</div>;
  }

  if (!logoUrl) {
    return (
      <div className={`${className} default`}>
        <span className="store-name">{storeId}</span>
      </div>
    );
  }

  return (
    <div className={className}>
      <img 
        src={logoUrl} 
        alt={`${storeId} logo`}
        onError={(e) => {
          e.target.style.display = 'none';
          e.target.nextSibling.style.display = 'inline';
        }}
      />
      <span className="fallback-text" style={{display: 'none'}}>{storeId}</span>
    </div>
  );
};

// Truss View Component
const TrussView = ({ refreshData, user }) => {
  const [trusses, setTrusses] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTruss, setEditingTruss] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDesigner, setFilterDesigner] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState('project_name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [showArchived, setShowArchived] = useState(false);
  const [showShipmentModal, setShowShipmentModal] = useState(false);
  const [shipmentTruss, setShipmentTruss] = useState(null);

  const fetchTrusses = async () => {
    try {
      const endpoint = showArchived ? `${API}/trusses/archived` : `${API}/trusses`;
      const response = await axios.get(endpoint);
      setTrusses(response.data);
    } catch (error) {
      console.error('Error fetching trusses:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrusses();
  }, [showArchived]);

  // Get unique designers for filter
  const uniqueDesigners = [...new Set(trusses.map(t => t.designer).filter(Boolean))];

  // Filter and sort trusses
  const filteredAndSortedTrusses = trusses
    .filter(truss => {
      const matchesStatus = filterStatus === 'all' || truss.project_status === filterStatus;
      const matchesDesigner = filterDesigner === 'all' || truss.designer === filterDesigner;
      const matchesSearch = !searchTerm || 
        truss.project_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (truss.project_number && truss.project_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (truss.salesman && truss.salesman.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesStatus && matchesDesigner && matchesSearch;
    })
    .sort((a, b) => {
      // Define status priority order (lower number = higher priority)
      const statusPriority = {
        'on_hold': 1,              // Hold - highest priority
        'in_the_shop': 2,          // In The Shop
        'ready_for_shop': 3,       // Ready for Shop
        'optimizing': 4,           // Optimizing
        'awaiting_final_measurements': 5, // Awaiting Final Measurements
        'completed': 6,            // Completed
        'delivered': 7             // Delivered - lowest priority
      };

      // First, sort by status priority
      const aPriority = statusPriority[a.project_status] || 999;
      const bPriority = statusPriority[b.project_status] || 999;
      
      if (aPriority !== bPriority) {
        return aPriority - bPriority; // Lower priority number comes first
      }

      // If statuses are the same, sort by estimated delivery date
      const aDate = a.estimated_delivery ? new Date(a.estimated_delivery) : new Date('9999-12-31');
      const bDate = b.estimated_delivery ? new Date(b.estimated_delivery) : new Date('9999-12-31');
      
      if (aDate.getTime() !== bDate.getTime()) {
        return aDate - bDate; // Earlier dates first
      }

      // If both status and date are the same, fall back to manual sorting
      if (sortColumn && a[sortColumn] !== undefined && b[sortColumn] !== undefined) {
        let aVal = a[sortColumn] || '';
        let bVal = b[sortColumn] || '';
        
        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase();
          bVal = bVal.toLowerCase();
        }
        
        if (sortDirection === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      }

      // Finally, sort by project name as tie-breaker
      return (a.project_name || '').localeCompare(b.project_name || '');
    });

  // Calculate lumber totals from filtered results
  const lumberTotals = filteredAndSortedTrusses.reduce((totals, truss) => {
    return {
      lumber_2x4_bd_ft: totals.lumber_2x4_bd_ft + (parseFloat(truss.lumber_2x4_bd_ft) || 0),
      lumber_2x6_bd_ft: totals.lumber_2x6_bd_ft + (parseFloat(truss.lumber_2x6_bd_ft) || 0),
      lumber_2x8_12ft: totals.lumber_2x8_12ft + (parseInt(truss.lumber_2x8_12ft) || 0),
      lumber_2x8_16ft: totals.lumber_2x8_16ft + (parseInt(truss.lumber_2x8_16ft) || 0),
      lumber_2x8_18ft: totals.lumber_2x8_18ft + (parseInt(truss.lumber_2x8_18ft) || 0),
      lumber_2x8_20ft: totals.lumber_2x8_20ft + (parseInt(truss.lumber_2x8_20ft) || 0),
      estimated_production_days: totals.estimated_production_days + (parseFloat(truss.estimated_production_days) || 0)
    };
  }, {
    lumber_2x4_bd_ft: 0,
    lumber_2x6_bd_ft: 0,
    lumber_2x8_12ft: 0,
    lumber_2x8_16ft: 0,
    lumber_2x8_18ft: 0,
    lumber_2x8_20ft: 0,
    estimated_production_days: 0
  });

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const handleDelete = async (trussId, projectName) => {
    if (window.confirm(`Are you sure you want to delete the truss "${projectName}"?`)) {
      try {
        await axios.delete(`${API}/trusses/${trussId}`);
        fetchTrusses();
      } catch (error) {
        console.error('Error deleting truss:', error);
        alert('Failed to delete truss');
      }
    }
  };

  const handleArchive = async (trussId, projectName) => {
    if (window.confirm(`Are you sure you want to archive the truss "${projectName}"? Archived projects can still be viewed but won't appear in the main list.`)) {
      try {
        await axios.post(`${API}/trusses/${trussId}/archive`);
        fetchTrusses();
        alert('Truss project archived successfully');
      } catch (error) {
        console.error('Error archiving truss:', error);
        alert('Failed to archive truss project');
      }
    }
  };

  const handleUnarchive = async (trussId, projectName) => {
    if (window.confirm(`Are you sure you want to unarchive the truss "${projectName}"?`)) {
      try {
        await axios.post(`${API}/trusses/${trussId}/unarchive`);
        fetchTrusses();
        alert('Truss project unarchived successfully');
      } catch (error) {
        console.error('Error unarchiving truss:', error);
        alert('Failed to unarchive truss project');
      }
    }
  };

  const handleScheduleShipment = (truss) => {
    setShipmentTruss(truss);
    setShowShipmentModal(true);
  };

  const submitShipment = async (shipmentDate) => {
    try {
      await axios.post(`${API}/trusses/${shipmentTruss.id}/schedule-shipment`, {
        shipment_date: new Date(shipmentDate + 'T00:00:00').toISOString()
      });
      fetchTrusses();
      setShowShipmentModal(false);
      setShipmentTruss(null);
      alert('Shipment scheduled successfully and added to calendar');
    } catch (error) {
      console.error('Error scheduling shipment:', error);
      alert('Failed to schedule shipment');
    }
  };

  const getSortIcon = (column) => {
    if (sortColumn !== column) return '↕️';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const getStatusColor = (status) => {
    const colors = {
      'ready_for_shop': '#eab308',        // Changed to yellow
      'in_the_shop': '#8b5cf6',
      'optimizing': '#06b6d4',
      'awaiting_final_measurements': '#1e40af',  // Changed to dark blue
      'completed': '#10b981',
      'delivered': '#22c55e',
      'on_hold': '#ef4444'
    };
    return colors[status] || '#6b7280';
  };

  const formatStatus = (status) => {
    return status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  };

  if (loading) {
    return (
      <div className="truss-view">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading trusses...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="truss-view">
      <div className="view-header">
        <div>
          <h1 className="page-title">
            Truss Tracker {showArchived && '(Archived)'}
          </h1>
          <p className="page-subtitle">Manage truss projects and production</p>
        </div>
        <div className="header-actions">
          <button 
            className={`btn-secondary ${showArchived ? 'btn-active' : ''}`}
            onClick={() => setShowArchived(!showArchived)}
          >
            {showArchived ? 'Show Active' : 'Show Archived'}
          </button>
          {!showArchived && (
            <button 
              className="btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Quick Add Project
            </button>
          )}
        </div>
      </div>

      {/* Filters and Search */}
      <div className="truss-filters">
        <div className="filters-row">
          <input
            type="text"
            placeholder="Search projects, numbers, or salesman..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select 
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="ready_for_shop">Ready for Shop</option>
            <option value="in_the_shop">In the Shop</option>
            <option value="optimizing">Optimizing</option>
            <option value="awaiting_final_measurements">Awaiting Final Measurements</option>
            <option value="completed">Completed</option>
            <option value="delivered">Delivered</option>
            <option value="on_hold">On Hold</option>
          </select>
          <select 
            className="filter-select"
            value={filterDesigner}
            onChange={(e) => setFilterDesigner(e.target.value)}
          >
            <option value="all">All Designers</option>
            {uniqueDesigners.map(designer => (
              <option key={designer} value={designer}>{designer}</option>
            ))}
          </select>
        </div>
        <div className="results-count">
          <span>Showing {filteredAndSortedTrusses.length} of {trusses.length} truss projects</span>
          <span className="production-total">
            • Total Production Days: {filteredAndSortedTrusses.reduce((total, truss) => {
              return total + (parseFloat(truss.estimated_production_days) || 0);
            }, 0).toFixed(1)}
          </span>
        </div>
      </div>

      {/* Truss Table */}
      <div className="truss-table-container">
        <table className="truss-table">
          {/* Totals Row */}
          <thead>
            <tr className="totals-row">
              <th className="totals-cell">TOTALS</th>
              <th className="totals-cell"></th>
              <th className="totals-cell"></th>
              <th className="totals-cell"></th>
              <th className="totals-cell"></th>
              <th className="totals-cell"></th>
              <th className="totals-cell"></th>
              <th className="totals-cell lumber-total">
                {lumberTotals.lumber_2x4_bd_ft.toFixed(1)}
              </th>
              <th className="totals-cell lumber-total">
                {lumberTotals.lumber_2x6_bd_ft.toFixed(1)}
              </th>
              <th className="totals-cell lumber-total">
                {lumberTotals.lumber_2x8_12ft}
              </th>
              <th className="totals-cell lumber-total">
                {lumberTotals.lumber_2x8_16ft}
              </th>
              <th className="totals-cell lumber-total">
                {lumberTotals.lumber_2x8_18ft}
              </th>
              <th className="totals-cell lumber-total">
                {lumberTotals.lumber_2x8_20ft}
              </th>
              <th className="totals-cell lumber-total">
                {lumberTotals.estimated_production_days.toFixed(1)}
              </th>
              <th className="totals-cell"></th>
              <th className="totals-cell"></th>
            </tr>
            {/* Column Headers */}
            <tr>
              <th onClick={() => handleSort('project_name')} className="sortable">
                Project Name {getSortIcon('project_name')}
              </th>
              <th onClick={() => handleSort('project_number')} className="sortable">
                Project # {getSortIcon('project_number')}
              </th>
              <th onClick={() => handleSort('designer')} className="sortable">
                Designer {getSortIcon('designer')}
              </th>
              <th onClick={() => handleSort('salesman')} className="sortable">
                Salesman {getSortIcon('salesman')}
              </th>
              <th onClick={() => handleSort('project_status')} className="sortable">
                Status {getSortIcon('project_status')}
              </th>
              <th onClick={() => handleSort('date_ordered')} className="sortable compact-header">
                Date Ordered {getSortIcon('date_ordered')}
              </th>
              <th onClick={() => handleSort('estimated_delivery')} className="sortable compact-header">
                Est. Delivery {getSortIcon('estimated_delivery')}
              </th>
              <th onClick={() => handleSort('lumber_2x4_bd_ft')} className="sortable compact-header">
                2x4 BD FT {getSortIcon('lumber_2x4_bd_ft')}
              </th>
              <th onClick={() => handleSort('lumber_2x6_bd_ft')} className="sortable compact-header">
                2x6 BD FT {getSortIcon('lumber_2x6_bd_ft')}
              </th>
              <th onClick={() => handleSort('lumber_2x8_12ft')} className="sortable compact-header">
                2x8 12' {getSortIcon('lumber_2x8_12ft')}
              </th>
              <th onClick={() => handleSort('lumber_2x8_16ft')} className="sortable compact-header">
                2x8 16' {getSortIcon('lumber_2x8_16ft')}
              </th>
              <th onClick={() => handleSort('lumber_2x8_18ft')} className="sortable compact-header">
                2x8 18' {getSortIcon('lumber_2x8_18ft')}
              </th>
              <th onClick={() => handleSort('lumber_2x8_20ft')} className="sortable compact-header">
                2x8 20' {getSortIcon('lumber_2x8_20ft')}
              </th>
              <th onClick={() => handleSort('estimated_production_days')} className="sortable compact-header">
                Est. Days {getSortIcon('estimated_production_days')}
              </th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedTrusses.map(truss => (
              <tr key={truss.id}>
                <td className="project-name-cell">
                  <div className="project-name">{truss.project_name}</div>
                </td>
                <td>{truss.project_number || '-'}</td>
                <td>{truss.designer || '-'}</td>
                <td>{truss.salesman || '-'}</td>
                <td>
                  <span 
                    className="status-badge" 
                    style={{ backgroundColor: getStatusColor(truss.project_status) }}
                  >
                    {formatStatus(truss.project_status)}
                  </span>
                </td>
                <td className="date-cell">{truss.date_ordered ? new Date(truss.date_ordered).toLocaleDateString() : '-'}</td>
                <td className="date-cell">{truss.estimated_delivery ? new Date(truss.estimated_delivery).toLocaleDateString() : '-'}</td>
                <td className="number-cell">{truss.lumber_2x4_bd_ft || '-'}</td>
                <td className="number-cell">{truss.lumber_2x6_bd_ft || '-'}</td>
                <td className="number-cell">{truss.lumber_2x8_12ft || '-'}</td>
                <td className="number-cell">{truss.lumber_2x8_16ft || '-'}</td>
                <td className="number-cell">{truss.lumber_2x8_18ft || '-'}</td>
                <td className="number-cell">{truss.lumber_2x8_20ft || '-'}</td>
                <td className="number-cell">{truss.estimated_production_days || '-'}</td>
                <td className="notes-cell">
                  {truss.notes && (
                    <div className="table-notes" title={truss.notes}>
                      {truss.notes.length > 30 ? `${truss.notes.substring(0, 30)}...` : truss.notes}
                    </div>
                  )}
                </td>
                <td>
                  <div className="action-buttons">
                    {!showArchived && (
                      <>
                        <button 
                          className="btn-icon edit"
                          onClick={() => {
                            setEditingTruss(truss);
                            setShowEditModal(true);
                          }}
                          title="Edit truss"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        
                        {(truss.project_status === 'completed' || truss.project_status === 'delivered') && (
                          <button 
                            className="btn-icon shipment"
                            onClick={() => handleScheduleShipment(truss)}
                            title="Schedule Shipment"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M8 7V3a1 1 0 011-1h6a1 1 0 011 1v4h3a1 1 0 011 1v9a1 1 0 01-1 1H5a1 1 0 01-1-1V8a1 1 0 011-1h3z" />
                            </svg>
                          </button>
                        )}
                        
                        {truss.project_status === 'delivered' && (
                          <button 
                            className="btn-icon archive"
                            onClick={() => handleArchive(truss.id, truss.project_name)}
                            title="Archive Project"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M5 8l6 6M5 8l6-6m2-2L12 5l3-3m-7 14l6-6m-6 6l6 6" />
                            </svg>
                          </button>
                        )}
                        
                        <button 
                          className="btn-icon delete"
                          onClick={() => handleDelete(truss.id, truss.project_name)}
                          title="Delete truss"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </>
                    )}
                    
                    {showArchived && (
                      <button 
                        className="btn-icon unarchive"
                        onClick={() => handleUnarchive(truss.id, truss.project_name)}
                        title="Unarchive Project"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredAndSortedTrusses.length === 0 && !loading && (
        <div className="empty-state">
          <p>No truss projects found matching your criteria.</p>
          <button 
            className="btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Quick Add First Project
          </button>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateTrussModal 
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            fetchTrusses();
            setShowCreateModal(false);
          }}
        />
      )}

      {/* Edit Modal */}
      {showEditModal && editingTruss && (
        <EditTrussModal 
          truss={editingTruss}
          onClose={() => {
            setShowEditModal(false);
            setEditingTruss(null);
          }}
          onSuccess={() => {
            fetchTrusses();
            setShowEditModal(false);
            setEditingTruss(null);
          }}
        />
      )}

      {/* Shipment Scheduling Modal */}
      {showShipmentModal && shipmentTruss && (
        <ShipmentModal 
          truss={shipmentTruss}
          onClose={() => {
            setShowShipmentModal(false);
            setShipmentTruss(null);
          }}
          onSubmit={submitShipment}
        />
      )}
    </div>
  );
};

// Shipment Modal Component
const ShipmentModal = ({ truss, onClose, onSubmit }) => {
  const [shipmentDate, setShipmentDate] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!shipmentDate) {
      alert('Please select a shipment date');
      return;
    }
    onSubmit(shipmentDate);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal shipment-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Schedule Shipment</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label className="form-label">Project</label>
            <div className="project-info">
              <strong>{truss.project_name}</strong>
              {truss.project_number && <span> (#{truss.project_number})</span>}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Current Status</label>
            <div className="status-info">
              <span 
                className="status-badge" 
                style={{ backgroundColor: truss.project_status === 'completed' ? '#10b981' : '#22c55e' }}
              >
                {truss.project_status === 'completed' ? 'Completed' : 'Delivered'}
              </span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Shipment Date <span className="required">*</span></label>
            <input 
              type="date"
              className="form-input"
              value={shipmentDate}
              onChange={(e) => setShipmentDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]} // Today or later
              required
            />
          </div>

          <div className="form-note">
            <p><strong>Note:</strong> This shipment will be added to the calendar and visible to all team members.</p>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Schedule Shipment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Truss Modal
const CreateTrussModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    project_name: '',
    project_number: '',
    designer: '',
    salesman: '',
    project_status: 'ready_for_shop',
    date_ordered: '',
    estimated_delivery: '',
    lumber_2x4_bd_ft: '',
    lumber_2x6_bd_ft: '',
    lumber_2x8_12ft: '',
    lumber_2x8_16ft: '',
    lumber_2x8_18ft: '',
    lumber_2x8_20ft: '',
    estimated_production_days: '',
    notes: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {};
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '') {
          if (key.includes('lumber_') || key === 'estimated_production_days') {
            submitData[key] = parseFloat(formData[key]) || null;
          } else if (key === 'date_ordered' || key === 'estimated_delivery') {
            // Convert date string to ISO datetime string for backend
            submitData[key] = new Date(formData[key] + 'T00:00:00').toISOString();
          } else {
            submitData[key] = formData[key];
          }
        }
      });

      await axios.post(`${API}/trusses`, submitData);
      onSuccess();
    } catch (error) {
      console.error('Error creating truss:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to create truss project: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal truss-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Quick Add Truss Project</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="form-note">
          <p><strong>Quick Start:</strong> Only project name is required. You can add all other details (lumber specs, dates, etc.) later by editing the project.</p>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Project Name <span className="required">*</span></label>
              <input 
                type="text"
                className="form-input"
                value={formData.project_name}
                onChange={(e) => setFormData({...formData, project_name: e.target.value})}
                required
                placeholder="Enter project name..."
              />
            </div>
            <div className="form-group">
              <label className="form-label">Project Number <span className="optional">(optional)</span></label>
              <input 
                type="text"
                className="form-input"
                value={formData.project_number}
                onChange={(e) => setFormData({...formData, project_number: e.target.value})}
                placeholder="e.g., TRP-2024-001"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Designer <span className="optional">(optional)</span></label>
              <select 
                className="form-select"
                value={formData.designer}
                onChange={(e) => setFormData({...formData, designer: e.target.value})}
              >
                <option value="">Select Designer</option>
                <option value="Dan">Dan</option>
                <option value="Dave">Dave</option>
                <option value="Brandon">Brandon</option>
                <option value="McKenzie">McKenzie</option>
                <option value="Clayton">Clayton</option>
                <option value="Nick">Nick</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Salesman <span className="optional">(optional)</span></label>
              <input 
                type="text"
                className="form-input"
                value={formData.salesman}
                onChange={(e) => setFormData({...formData, salesman: e.target.value})}
                placeholder="Salesman name"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Initial Status</label>
              <select 
                className="form-select"
                value={formData.project_status}
                onChange={(e) => setFormData({...formData, project_status: e.target.value})}
              >
                <option value="ready_for_shop">Ready for Shop</option>
                <option value="in_the_shop">In the Shop</option>
                <option value="optimizing">Optimizing</option>
                <option value="awaiting_final_measurements">Awaiting Final Measurements</option>
                <option value="completed">Completed</option>
                <option value="delivered">Delivered</option>
                <option value="on_hold">On Hold</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Notes <span className="optional">(optional)</span></label>
              <textarea 
                className="form-textarea"
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                rows={2}
                placeholder="Any initial notes..."
              />
            </div>
          </div>

          <div className="optional-fields-note">
            <p><em>💡 Tip: Dates and lumber specifications can be added later when you have more details.</em></p>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Edit Truss Modal
const EditTrussModal = ({ truss, onClose, onSuccess }) => {
  // Helper function to format date for HTML input
  const formatDateForInput = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return '';
    return date.toISOString().split('T')[0]; // Returns YYYY-MM-DD format
  };

  const [formData, setFormData] = useState({
    project_name: truss.project_name || '',
    project_number: truss.project_number || '',
    designer: truss.designer || '',
    salesman: truss.salesman || '',
    project_status: truss.project_status || 'ready_for_shop',
    date_ordered: formatDateForInput(truss.date_ordered),
    estimated_delivery: formatDateForInput(truss.estimated_delivery),
    lumber_2x4_bd_ft: truss.lumber_2x4_bd_ft || '',
    lumber_2x6_bd_ft: truss.lumber_2x6_bd_ft || '',
    lumber_2x8_12ft: truss.lumber_2x8_12ft || '',
    lumber_2x8_16ft: truss.lumber_2x8_16ft || '',
    lumber_2x8_18ft: truss.lumber_2x8_18ft || '',
    lumber_2x8_20ft: truss.lumber_2x8_20ft || '',
    estimated_production_days: truss.estimated_production_days || '',
    notes: truss.notes || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {};
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '') {
          if (key.includes('lumber_') || key === 'estimated_production_days') {
            submitData[key] = parseFloat(formData[key]) || null;
          } else if (key === 'date_ordered' || key === 'estimated_delivery') {
            // Convert date string to ISO datetime string for backend
            if (formData[key]) {
              submitData[key] = new Date(formData[key] + 'T00:00:00').toISOString();
            } else {
              submitData[key] = null;
            }
          } else {
            submitData[key] = formData[key];
          }
        } else {
          submitData[key] = null;
        }
      });

      await axios.put(`${API}/trusses/${truss.id}`, submitData);
      onSuccess();
    } catch (error) {
      console.error('Error updating truss:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to update truss project: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete the truss "${truss.project_name}"?`)) {
      try {
        await axios.delete(`${API}/trusses/${truss.id}`);
        onSuccess();
        onClose();
      } catch (error) {
        console.error('Error deleting truss:', error);
        alert('Failed to delete truss project');
      }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal truss-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Edit Truss Project</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Project Name <span className="required">*</span></label>
              <input 
                type="text"
                className="form-input"
                value={formData.project_name}
                onChange={(e) => setFormData({...formData, project_name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Project Number <span className="optional">(optional)</span></label>
              <input 
                type="text"
                className="form-input"
                value={formData.project_number}
                onChange={(e) => setFormData({...formData, project_number: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Designer <span className="optional">(optional)</span></label>
              <select 
                className="form-select"
                value={formData.designer}
                onChange={(e) => setFormData({...formData, designer: e.target.value})}
              >
                <option value="">Select Designer</option>
                <option value="Dan">Dan</option>
                <option value="Dave">Dave</option>
                <option value="Brandon">Brandon</option>
                <option value="McKenzie">McKenzie</option>
                <option value="Clayton">Clayton</option>
                <option value="Nick">Nick</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Salesman <span className="optional">(optional)</span></label>
              <input 
                type="text"
                className="form-input"
                value={formData.salesman}
                onChange={(e) => setFormData({...formData, salesman: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Project Status</label>
              <select 
                className="form-select"
                value={formData.project_status}
                onChange={(e) => setFormData({...formData, project_status: e.target.value})}
              >
                <option value="ready_for_shop">Ready for Shop</option>
                <option value="in_the_shop">In the Shop</option>
                <option value="optimizing">Optimizing</option>
                <option value="awaiting_final_measurements">Awaiting Final Measurements</option>
                <option value="completed">Completed</option>
                <option value="delivered">Delivered</option>
                <option value="on_hold">On Hold</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Estimated Production Days <span className="optional">(optional)</span></label>
              <input 
                type="number"
                className="form-input"
                step="0.25"
                value={formData.estimated_production_days}
                onChange={(e) => setFormData({...formData, estimated_production_days: e.target.value})}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Date Ordered <span className="optional">(optional)</span></label>
              <input 
                type="date"
                className="form-input"
                value={formData.date_ordered}
                onChange={(e) => setFormData({...formData, date_ordered: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Estimated Delivery <span className="optional">(optional)</span></label>
              <input 
                type="date"
                className="form-input"
                value={formData.estimated_delivery}
                onChange={(e) => setFormData({...formData, estimated_delivery: e.target.value})}
              />
            </div>
          </div>

          <div className="form-section">
            <h4 className="form-section-title">Lumber Requirements <span className="optional">(all optional)</span></h4>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">2x4 Board Feet</label>
                <input 
                  type="number"
                  className="form-input"
                  step="0.01"
                  value={formData.lumber_2x4_bd_ft}
                  onChange={(e) => setFormData({...formData, lumber_2x4_bd_ft: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label className="form-label">2x6 Board Feet</label>
                <input 
                  type="number"
                  className="form-input"
                  step="0.01"
                  value={formData.lumber_2x6_bd_ft}
                  onChange={(e) => setFormData({...formData, lumber_2x6_bd_ft: e.target.value})}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">2x8 12' Count</label>
                <input 
                  type="number"
                  className="form-input"
                  value={formData.lumber_2x8_12ft}
                  onChange={(e) => setFormData({...formData, lumber_2x8_12ft: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label className="form-label">2x8 16' Count</label>
                <input 
                  type="number"
                  className="form-input"
                  value={formData.lumber_2x8_16ft}
                  onChange={(e) => setFormData({...formData, lumber_2x8_16ft: e.target.value})}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">2x8 18' Count</label>
                <input 
                  type="number"
                  className="form-input"
                  value={formData.lumber_2x8_18ft}
                  onChange={(e) => setFormData({...formData, lumber_2x8_18ft: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label className="form-label">2x8 20' Count</label>
                <input 
                  type="number"
                  className="form-input"
                  value={formData.lumber_2x8_20ft}
                  onChange={(e) => setFormData({...formData, lumber_2x8_20ft: e.target.value})}
                />
              </div>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Notes <span className="optional">(optional)</span></label>
            <textarea 
              className="form-textarea"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              rows={3}
            />
          </div>

          <div className="modal-actions">
            <button 
              type="button" 
              className="btn-danger" 
              onClick={handleDelete}
            >
              Delete Project
            </button>
            <div className="modal-actions-right">
              <button type="button" className="btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Save Changes
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// Export all components
export default {
  Navigation,
  Dashboard,
  TaskView,
  CalendarView,
  IdeasBoard,
  ProjectView,
  BudgetView,
  TrussView,
  CreateTaskModal,
  EditTaskModal,
  CreateIdeaModal,
  EditIdeaModal,
  CreateProjectModal,
  EditProjectModal,
  ChangeHistoryModal,
  CreateTrussModal,
  EditTrussModal,
  ShipmentModal,
  StoreLogo
};

export { Dashboard, TaskView, ProjectView, CreateTaskModal, EditTaskModal, EditProjectModal, CreateProjectModal, CreateIdeaModal, EditIdeaModal, IdeasBoard as IdeasView, BudgetView, TrussView, CreateTrussModal, EditTrussModal, ShipmentModal, StoreLogo, ChangeHistoryModal };