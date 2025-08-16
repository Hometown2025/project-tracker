import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = ({ onClose }) => {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [deactivatedUsers, setDeactivatedUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserDetails, setShowUserDetails] = useState(null);
  const [activeTab, setActiveTab] = useState('active'); // 'active' or 'deactivated'

  useEffect(() => {
    fetchUsers();
    fetchDeactivatedUsers();
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

  const fetchDeactivatedUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users/deactivated`);
      setDeactivatedUsers(response.data);
    } catch (error) {
      console.error('Error fetching deactivated users:', error);
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

  const deactivateUser = async (userId, username, targetUserRole) => {
    if (userId === user.id) {
      alert('Cannot delete your own account');
      return;
    }
    
    // Different options for Super Admin vs Store Admin
    if (user?.role === 'super_admin') {
      // Super Admin gets choice of deactivate or permanent delete
      const action = window.confirm(
        `What would you like to do with user "${username}"?\n\n` +
        `Click OK for PERMANENT DELETION (cannot be undone)\n` +
        `Click Cancel for DEACTIVATION (can be reactivated later)`
      );
      
      if (action !== null) { // User didn't press X to close
        const permanent = action; // OK = true (permanent), Cancel = false (deactivate)
        const actionText = permanent ? 'permanently delete' : 'deactivate';
        const confirmText = permanent ? 
          `⚠️ PERMANENT DELETION CONFIRMATION ⚠️\n\nAre you absolutely sure you want to PERMANENTLY DELETE user "${username}"?\n\nThis action:\n• Cannot be undone\n• Will remove all user data\n• Will unassign them from all projects\n\nType "DELETE" to confirm:` :
          `Are you sure you want to deactivate user "${username}"? They will be logged out and unable to login until reactivated.`;
        
        let confirmed = false;
        if (permanent) {
          const userInput = prompt(confirmText);
          confirmed = userInput === 'DELETE';
          if (!confirmed && userInput !== null) {
            alert('Deletion cancelled. You must type "DELETE" exactly to confirm permanent deletion.');
            return;
          }
        } else {
          confirmed = window.confirm(confirmText);
        }
        
        if (confirmed) {
          try {
            const url = permanent ? 
              `${API}/admin/users/${userId}?permanent=true` : 
              `${API}/admin/users/${userId}`;
              
            await axios.delete(url);
            setUsers(users.filter(u => u.id !== userId));
            fetchDeactivatedUsers(); // Refresh deactivated list
            
            const successMessage = permanent ? 
              `User "${username}" permanently deleted successfully` : 
              `User "${username}" deactivated successfully`;
            alert(successMessage);
          } catch (error) {
            console.error('Error managing user:', error);
            const errorMessage = error.response?.data?.detail || 'Failed to manage user';
            alert(errorMessage);
          }
        }
      }
    } else {
      // Store Admin gets only deactivate option (and only for customers)
      if (targetUserRole === 'admin' || targetUserRole === 'super_admin') {
        alert('You cannot deactivate other administrators. Only super admin can manage administrators.');
        return;
      }
      
      if (window.confirm(`Are you sure you want to deactivate customer "${username}"? They will be logged out and unable to login until reactivated by an administrator.`)) {
        try {
          await axios.delete(`${API}/admin/users/${userId}`);
          setUsers(users.filter(u => u.id !== userId));
          fetchDeactivatedUsers(); // Refresh deactivated list
          alert(`Customer "${username}" deactivated successfully`);
        } catch (error) {
          console.error('Error deactivating user:', error);
          const errorMessage = error.response?.data?.detail || 'Failed to deactivate user';
          alert(errorMessage);
        }
      }
    }
  };

  const handleReactivateUser = async (userId) => {
    if (window.confirm('Are you sure you want to reactivate this user?')) {
      try {
        await axios.post(`${API}/admin/users/${userId}/reactivate`);
        fetchUsers(); // Refresh active users
        fetchDeactivatedUsers(); // Refresh deactivated users
        alert('User reactivated successfully');
      } catch (error) {
        console.error('Error reactivating user:', error);
        if (error.response?.status === 409) {
          alert('Cannot reactivate: Username is already taken by an active user. Please rename the active user first or choose a different username.');
        } else {
          alert('Failed to reactivate user');
        }
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
          {/* Tab Navigation */}
          <div className="admin-tabs">
            <button 
              className={`tab-button ${activeTab === 'active' ? 'active' : ''}`}
              onClick={() => setActiveTab('active')}
            >
              Active Users ({users.length})
            </button>
            <button 
              className={`tab-button ${activeTab === 'deactivated' ? 'active' : ''}`}
              onClick={() => setActiveTab('deactivated')}
            >
              Deactivated Users ({deactivatedUsers.length})
            </button>
          </div>

          <div className="admin-section">
            <div className="admin-section-header">
              <h3>{activeTab === 'active' ? 'Active Users' : 'Deactivated Users'}</h3>
              {(user?.role === 'admin' || user?.role === 'super_admin') && activeTab === 'active' && (
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
              )}
            </div>
            
            <div className="users-table">
              <div className="table-header">
                <div>User Info</div>
                <div>Role</div>
                <div>Access</div>
                <div>Actions</div>
              </div>
              
              {(activeTab === 'active' ? users : deactivatedUsers).map(u => (
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
                      {u.role === 'super_admin' ? 'Super Administrator' : 
                       u.role === 'admin' ? 'Store Administrator' : 'User'}
                    </span>
                  </div>
                  <div>
                    {u.role === 'super_admin' ? (
                      <span className="access-badge super-admin-access">Global Access</span>
                    ) : u.role === 'admin' ? (
                      <span className="access-badge full-access">Store Access</span>
                    ) : (
                      <span className="access-badge limited-access">
                        {u.assigned_projects?.length || 0} project{u.assigned_projects?.length !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                  <div className="action-buttons">
                    {activeTab === 'active' ? (
                      // Actions for active users
                      <>
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
                            onClick={() => deactivateUser(u.id, u.username, u.role)}
                            title={user?.role === 'super_admin' ? 'Delete/Deactivate User' : 'Deactivate User'}
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        )}
                      </>
                    ) : (
                      // Actions for deactivated users
                      <>
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
                        {(user?.role === 'admin' || user?.role === 'super_admin') && (
                          <button 
                            className="btn-primary btn-sm"
                            onClick={() => handleReactivateUser(u.id)}
                            title="Reactivate User"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                          </button>
                        )}
                        {user?.role === 'super_admin' && (
                          <button 
                            className="btn-danger btn-sm"
                            onClick={() => deactivateUser(u.id, u.username, u.role)}
                            title="Permanently Delete User"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        )}
                      </>
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
                <div className="stat-number">{users.filter(u => u.role === 'admin' || u.role === 'super_admin').length}</div>
                <div className="stat-label">Administrators</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{users.filter(u => u.role === 'customer').length}</div>
                <div className="stat-label">Customers</div>
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
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    role: 'customer',
    store_id: user?.store_id || ''  // Default to current user's store
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generatePassword = () => {
    const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789';
    let password = '';
    for (let i = 0; i < 8; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setFormData({...formData, password: password});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/admin/users`, formData);
      onSuccess();
      alert(`User "${formData.username}" created successfully!\n\nCredentials:\nStore ID: ${formData.store_id}\nUsername: ${formData.username}\nPassword: ${formData.password}\n\nPlease provide these credentials to the user.`);
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

          <div className="form-note">
            <p>Create login credentials for a new user. You can assign projects to regular users after creation.</p>
          </div>
          
          <div className="form-group">
            <label className="form-label">Username <span className="required">*</span></label>
            <input 
              type="text"
              className="form-input"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              placeholder="Enter username (e.g., john.doe)"
              required
              disabled={loading}
            />
            <small className="form-hint">This will be used to log in to the system</small>
          </div>

          <div className="form-group">
            <label className="form-label">Password <span className="required">*</span></label>
            <div className="password-input-group">
              <input 
                type="text"
                className="form-input"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                placeholder="Enter password or generate one"
                required
                disabled={loading}
              />
              <button 
                type="button" 
                className="btn-generate"
                onClick={generatePassword}
                disabled={loading}
                title="Generate secure password"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
            <small className="form-hint">You will provide this password to the user</small>
          </div>

          <div className="form-group">
            <label className="form-label">Email (Optional)</label>
            <input 
              type="email"
              className="form-input"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="user@company.com"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Store ID <span className="required">*</span></label>
            <input 
              type="text"
              className="form-input"
              value={formData.store_id}
              onChange={(e) => setFormData({...formData, store_id: e.target.value})}
              placeholder="Enter store ID (e.g., STORE_001)"
              required
              disabled={loading || user?.role !== 'super_admin'}  // Only super admin can change store ID
            />
            <small className="form-hint">
              {user?.role === 'super_admin' 
                ? 'Specify which lumber yard/store this user belongs to' 
                : 'Users will be created for your store only'}
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">Role <span className="required">*</span></label>
            <select 
              className="form-select"
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              disabled={loading}
            >
              <option value="customer">Customer - View assigned projects only</option>
              {(user?.role === 'admin' || user?.role === 'super_admin') && (
                <option value="admin">Store Administrator - Manage this store</option>
              )}
              {user?.role === 'super_admin' && (
                <option value="super_admin">Super Administrator - Manage all stores</option>
              )}
            </select>
            {user?.role === 'customer' && (
              <small className="form-hint">Only customers can be created. Contact your administrator to create store administrators.</small>
            )}
            {user?.role === 'admin' && (
              <small className="form-hint">You can create customers and store administrators for your store.</small>
            )}
            {user?.role === 'super_admin' && (
              <small className="form-hint">You can create customers and administrators for any store, including super administrators.</small>
            )}
          </div>

          <div className="role-explanation">
            {formData.role === 'customer' ? (
              <div className="role-note user-role-note">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <div>
                  <strong>Customer</strong>
                  <p>Can view projects and quotes assigned by administrators. Can see budgets and communicate with lumber yard staff.</p>
                </div>
              </div>
            ) : formData.role === 'admin' ? (
              <div className="role-note admin-role-note">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <div>
                  <strong>Store Administrator</strong>
                  <p>Can manage their store only: create, edit, and delete projects and tasks. Can create regular users and other store administrators for their store.</p>
                </div>
              </div>
            ) : (
              <div className="role-note super-admin-role-note">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M5 3l14 9-14 9V3z" />
                </svg>
                <div>
                  <strong>Super Administrator</strong>
                  <p>Full system access: manage all stores, create store administrators, assign users across lumber yards.</p>
                </div>
              </div>
            )}
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating User...' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const UserDetailsModal = ({ user, projects, onClose }) => {
  const userProjects = projects.filter(p => user.assigned_projects?.includes(p.id));

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">User Details: {user.username}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-form">
          <div className="user-details-content">
            <div className="detail-section">
              <h3>Account Information</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Username:</label>
                  <span>{user.username}</span>
                </div>
                {user.email && (
                  <div className="detail-item">
                    <label>Email:</label>
                    <span>{user.email}</span>
                  </div>
                )}
                <div className="detail-item">
                  <label>Role:</label>
                  <span className={`role-badge role-${user.role}`}>
                    {user.role === 'super_admin' ? 'Super Administrator' : 
                     user.role === 'admin' ? 'Store Administrator' : 'Regular User'}
                  </span>
                </div>
                <div className="detail-item">
                  <label>Account Created:</label>
                  <span>{new Date(user.created_date).toLocaleDateString()}</span>
                </div>
                {user.last_login && (
                  <div className="detail-item">
                    <label>Last Login:</label>
                    <span>{new Date(user.last_login).toLocaleDateString()}</span>
                  </div>
                )}
                <div className="detail-item">
                  <label>Status:</label>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            </div>

            {user.role === 'user' && (
              <div className="detail-section">
                <h3>Project Access ({userProjects.length} projects)</h3>
                {userProjects.length > 0 ? (
                  <div className="assigned-projects">
                    {userProjects.map(project => (
                      <div key={project.id} className="assigned-project">
                        <div 
                          className="project-color-small" 
                          style={{ backgroundColor: project.color }}
                        ></div>
                        <div className="project-info">
                          <div className="project-name">{project.name}</div>
                          <div className="project-description">{project.description || 'No description'}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-projects">
                    <p>This user has not been assigned any projects yet.</p>
                  </div>
                )}
              </div>
            )}

            {(user.role === 'admin' || user.role === 'super_admin') && (
              <div className="detail-section">
                <h3>{user.role === 'super_admin' ? 'Super Administrator Access' : 'Store Administrator Access'}</h3>
                <div className="admin-access-note">
                  <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>
                    {user.role === 'super_admin' 
                      ? 'Has full administrative access to all stores and can create store administrators.'
                      : 'Has full administrative access to their assigned store and can create regular users.'}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
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