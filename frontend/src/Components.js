import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = ({ currentView, setCurrentView, projects, setSelectedProject, selectedProject }) => {
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">
          <svg className="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          TaskFlow
        </h2>
      </div>
      
      <div className="nav-section">
        <h3 className="nav-section-title">Views</h3>
        <div className="nav-items">
          <button 
            className={`nav-item ${currentView === 'dashboard' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('dashboard')}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
            </svg>
            Dashboard
          </button>
          
          <button 
            className={`nav-item ${currentView === 'tasks' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('tasks')}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M9 5l7 7-7 7" />
            </svg>
            Tasks
          </button>
          
          <button 
            className={`nav-item ${currentView === 'calendar' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('calendar')}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Calendar
          </button>
          
          <button 
            className={`nav-item ${currentView === 'ideas' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('ideas')}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Ideas
          </button>
          
          <button 
            className={`nav-item ${currentView === 'projects' ? 'nav-item-active' : 'nav-item-inactive'}`}
            onClick={() => setCurrentView('projects')}
          >
            <svg className="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M19 11H5m14-4H5m14 8H5m14 4H5" />
            </svg>
            Projects
          </button>
        </div>
      </div>

      {projects.length > 0 && (
        <div className="nav-section">
          <h3 className="nav-section-title">Projects</h3>
          <div className="nav-items">
            <button 
              className={`nav-item ${!selectedProject ? 'nav-item-active' : 'nav-item-inactive'}`}
              onClick={() => setSelectedProject(null)}
            >
              All Projects
            </button>
            {projects.slice(0, 5).map(project => (
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
      )}
    </nav>
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

  return (
    <div className="task-view">
      <div className="view-header">
        <div>
          <h1 className="page-title">
            {selectedProject ? `${selectedProject.name} Tasks` : 'All Tasks'}
          </h1>
          <p className="page-subtitle">{filteredTasks.length} tasks found</p>
        </div>
        <button 
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Task
        </button>
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
                  <button 
                    className="btn-icon task-edit"
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditingTask(task);
                      setShowEditModal(true);
                    }}
                    title="Edit task"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
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
              
              <div className="task-card-footer">
                {project && (
                  <div className="task-project">
                    <div 
                      className="project-color-small" 
                      style={{ backgroundColor: project.color }}
                    ></div>
                    <span className="project-name-small">{project.name}</span>
                  </div>
                )}
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
const CalendarView = ({ tasks, projects, refreshData }) => {
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
                        className={`calendar-event ${event.event_type} priority-${event.priority}`}
                        style={{ borderColor: project?.color || '#8B5CF6' }}
                        title={`${event.title} (${event.event_label})`}
                      >
                        {event.title.length > 25 ? `${event.title.substring(0, 25)}...` : event.title}
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

  const filteredIdeas = ideas.filter(idea => 
    !selectedProject || idea.project_id === selectedProject.id
  );

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
          <h1 className="page-title">Projects</h1>
          <p className="page-subtitle">Manage your project portfolio</p>
        </div>
        <button 
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Project
        </button>
      </div>

      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card-large">
            <div className="project-card-header">
              <div className="project-color-large" style={{ backgroundColor: project.color }}></div>
              <div className="project-actions">
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
              </span>
            </div>
            
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
    </div>
  );
};

// Edit Task Modal
const EditTaskModal = ({ task, projects, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: task.title || '',
    description: task.description || '',
    priority: task.priority || 'medium',
    due_date: task.due_date || '',
    order_date: task.order_date || '',
    delivery_date: task.delivery_date || '',
    project_id: task.project_id || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Only send fields that have values or have been changed
      const updateData = {};
      Object.keys(formData).forEach(key => {
        if (formData[key] !== '' && formData[key] !== null) {
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
          <h2 className="modal-title">Edit Task</h2>
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
            <button 
              type="button" 
              className="btn-danger" 
              onClick={handleDelete}
            >
              Delete Task
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

// Create Task Modal
const CreateTaskModal = ({ projects, selectedProject, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    order_date: '',
    delivery_date: '',
    project_id: selectedProject?.id || ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/tasks`, formData);
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
          <h2 className="modal-title">Create New Task</h2>
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

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Task
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

// Create Project Modal
const CreateProjectModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#8B5CF6'
  });

  const colors = [
    '#8B5CF6', '#EF4444', '#F59E0B', '#10B981', '#3B82F6', 
    '#8B5A2B', '#EC4899', '#6366F1', '#84CC16', '#F97316'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/projects`, formData);
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
          <h2 className="modal-title">Create New Project</h2>
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

// Export all components
export default {
  Navigation,
  Dashboard,
  TaskView,
  CalendarView,
  IdeasBoard,
  ProjectView,
  CreateTaskModal,
  EditTaskModal,
  CreateIdeaModal,
  CreateProjectModal
};