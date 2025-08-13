import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = ({ onClose }) => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserDetails, setShowUserDetails] = useState(null);

  useEffect(() => {
    fetchUsers();
    fetchProjects();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
    setLoading(false);
  };

  const assignProjects = async (userId, projectIds) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/assign-projects`, {
        user_id: userId,
        project_ids: projectIds
      });
      
      // Update local state
      setUsers(users.map(u => 
        u.id === userId 
          ? { ...u, assigned_projects: projectIds }
          : u
      ));
      
      setSelectedUser(null);
      alert('Projects assigned successfully!');
    } catch (error) {
      console.error('Error assigning projects:', error);
      alert('Failed to assign projects');
    }
  };

  const deactivateUser = async (userId, username) => {
    if (userId === user.id) {
      alert('Cannot deactivate your own account');
      return;
    }
    
    if (window.confirm(`Are you sure you want to deactivate user "${username}"?`)) {
      try {
        await axios.delete(`${API}/admin/users/${userId}`);
        setUsers(users.filter(u => u.id !== userId));
        alert('User deactivated successfully');
      } catch (error) {
        console.error('Error deactivating user:', error);
        alert('Failed to deactivate user');
      }
    }
  };

  if (loading) {
    return (
      <div className="modal-overlay">
        <div className="modal">
          <div className="loading-spinner">Loading admin panel...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal admin-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">User Management</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="admin-content">
          <div className="admin-section">
            <div className="admin-section-header">
              <h3>System Users</h3>
              <button 
                className="btn-primary btn-sm"
                onClick={() => setShowCreateUser(true)}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add User
              </button>
            </div>
            
            <div className="users-table">
              <div className="table-header">
                <div>User Info</div>
                <div>Role</div>
                <div>Access</div>
                <div>Actions</div>
              </div>
              
              {users.map(u => (
                <div key={u.id} className="table-row">
                  <div className="user-info">
                    <div className="username-large">{u.username}</div>
                    {u.email && <div className="user-email">{u.email}</div>}
                    <div className="user-meta">
                      Created: {new Date(u.created_date).toLocaleDateString()}
                      {u.last_login && (
                        <span> • Last login: {new Date(u.last_login).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <span className={`role-badge role-${u.role}`}>
                      {u.role === 'admin' ? 'Administrator' : 'User'}
                    </span>
                  </div>
                  <div>
                    {u.role === 'admin' ? (
                      <span className="access-badge full-access">Full Access</span>
                    ) : (
                      <span className="access-badge limited-access">
                        {u.assigned_projects?.length || 0} project{u.assigned_projects?.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                  <div className="action-buttons">
                    <button 
                      className="btn-secondary btn-sm"
                      onClick={() => setShowUserDetails(u)}
                      title="View Details"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    {u.role !== 'admin' && (
                      <button 
                        className="btn-secondary btn-sm"
                        onClick={() => setSelectedUser(u)}
                        title="Assign Projects"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                      </button>
                    )}
                    {u.id !== user.id && (
                      <button 
                        className="btn-danger btn-sm"
                        onClick={() => deactivateUser(u.id, u.username)}
                        title="Deactivate User"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="admin-section">
            <h3>System Overview</h3>
            <div className="system-stats">
              <div className="stat-card">
                <div className="stat-number">{users.length}</div>
                <div className="stat-label">Total Users</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{projects.length}</div>
                <div className="stat-label">Total Projects</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{users.filter(u => u.role === 'admin').length}</div>
                <div className="stat-label">Administrators</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{users.filter(u => u.role === 'user').length}</div>
                <div className="stat-label">Regular Users</div>
              </div>
            </div>
          </div>
        </div>

        {showCreateUser && (
          <CreateUserModal 
            onClose={() => setShowCreateUser(false)}
            onSuccess={() => {
              setShowCreateUser(false);
              fetchUsers();
            }}
          />
        )}

        {selectedUser && (
          <AssignProjectsModal 
            user={selectedUser}
            projects={projects}
            onClose={() => setSelectedUser(null)}
            onAssign={assignProjects}
          />
        )}

        {showUserDetails && (
          <UserDetailsModal 
            user={showUserDetails}
            projects={projects}
            onClose={() => setShowUserDetails(null)}
          />
        )}
      </div>
    </div>
  );
};

const CreateUserModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    role: 'user'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/admin/users`, formData);
      onSuccess();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create user');
    }
    
    setLoading(false);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create New User</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="modal-form">
          {error && (
            <div className="error-message">{error}</div>
          )}
          
          <div className="form-group">
            <label className="form-label">Username</label>
            <input 
              type="text"
              className="form-input"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password"
              className="form-input"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email (Optional)</label>
            <input 
              type="email"
              className="form-input"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Role</label>
            <select 
              className="form-select"
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              disabled={loading}
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const AssignProjectsModal = ({ user, projects, onClose, onAssign }) => {
  const [selectedProjects, setSelectedProjects] = useState(user.assigned_projects || []);

  const toggleProject = (projectId) => {
    setSelectedProjects(prev => 
      prev.includes(projectId) 
        ? prev.filter(id => id !== projectId)
        : [...prev, projectId]
    );
  };

  const handleAssign = () => {
    onAssign(user.id, selectedProjects);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Assign Projects to {user.username}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-form">
          <div className="project-selection">
            <p className="selection-note">
              Select projects that {user.username} can view:
            </p>
            
            <div className="project-list">
              {projects.map(project => (
                <div key={project.id} className="project-option">
                  <label className="checkbox-label">
                    <input 
                      type="checkbox"
                      checked={selectedProjects.includes(project.id)}
                      onChange={() => toggleProject(project.id)}
                    />
                    <div className="project-option-content">
                      <div className="project-option-header">
                        <div 
                          className="project-color-small" 
                          style={{ backgroundColor: project.color }}
                        ></div>
                        <span className="project-name">{project.name}</span>
                      </div>
                      {project.description && (
                        <p className="project-description">{project.description}</p>
                      )}
                    </div>
                  </label>
                </div>
              ))}
            </div>
            
            <div className="selection-summary">
              {selectedProjects.length} of {projects.length} projects selected
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="button" className="btn-primary" onClick={handleAssign}>
              Assign Projects
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;