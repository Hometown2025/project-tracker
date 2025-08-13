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
          <h2 className="modal-title">Admin Panel</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="admin-content">
          <div className="admin-section">
            <div className="admin-section-header">
              <h3>Users</h3>
              <button 
                className="btn-primary btn-sm"
                onClick={() => setShowCreateUser(true)}
              >
                Add User
              </button>
            </div>
            
            <div className="users-table">
              <div className="table-header">
                <div>Username</div>
                <div>Role</div>
                <div>Assigned Projects</div>
                <div>Actions</div>
              </div>
              
              {users.map(u => (
                <div key={u.id} className="table-row">
                  <div className="user-info">
                    <span className="username">{u.username}</span>
                    {u.email && <span className="user-email">{u.email}</span>}
                  </div>
                  <div>
                    <span className={`role-badge role-${u.role}`}>
                      {u.role}
                    </span>
                  </div>
                  <div>
                    <span className="project-count">
                      {u.assigned_projects?.length || 0} projects
                    </span>
                  </div>
                  <div>
                    <button 
                      className="btn-secondary btn-sm"
                      onClick={() => setSelectedUser(u)}
                    >
                      Assign Projects
                    </button>
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
                <div className="stat-label">Admins</div>
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