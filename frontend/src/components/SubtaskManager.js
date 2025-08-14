import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../AuthContext';
import FileManager from './FileManager';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SubtaskManager = ({ parentTask, onSubtaskUpdate }) => {
  const [subtasks, setSubtasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newSubtask, setNewSubtask] = useState({ title: '', description: '', order_date: '', delivery_date: '' });
  const [editingSubtask, setEditingSubtask] = useState(null);
  const [expandedSubtasks, setExpandedSubtasks] = useState(new Set());
  const { canCreate, canEdit } = useAuth();

  useEffect(() => {
    if (isExpanded) {
      fetchSubtasks();
    }
  }, [isExpanded, parentTask.id]);

  const fetchSubtasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tasks/${parentTask.id}/subtasks`);
      setSubtasks(response.data);
    } catch (error) {
      console.error('Error fetching subtasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const createSubtask = async () => {
    if (!newSubtask.title.trim()) return;

    try {
      const subtaskData = {
        ...newSubtask,
        parent_task_id: parentTask.id,
        project_id: parentTask.project_id,
        priority: parentTask.priority
      };

      await axios.post(`${API}/tasks`, subtaskData);
      
      setNewSubtask({ title: '', description: '', order_date: '', delivery_date: '' });
      setShowCreateForm(false);
      await fetchSubtasks();
      
      if (onSubtaskUpdate) onSubtaskUpdate();
    } catch (error) {
      console.error('Error creating subtask:', error);
      alert('Failed to create subtask');
    }
  };

  const updateSubtask = async (subtaskId, updates) => {
    try {
      await axios.put(`${API}/tasks/${subtaskId}`, updates);
      await fetchSubtasks();
      if (onSubtaskUpdate) onSubtaskUpdate();
    } catch (error) {
      console.error('Error updating subtask:', error);
      alert('Failed to update subtask');
    }
  };

  const toggleSubtaskCompletion = async (subtask) => {
    await updateSubtask(subtask.id, { completed: !subtask.completed });
  };

  const toggleSubtaskExpansion = (subtaskId) => {
    const newExpanded = new Set(expandedSubtasks);
    if (newExpanded.has(subtaskId)) {
      newExpanded.delete(subtaskId);
    } else {
      newExpanded.add(subtaskId);
    }
    setExpandedSubtasks(newExpanded);
  };

  const getSubtaskColor = (parentTask) => {
    // Use parent task/room color for subtask identification
    const colors = [
      '#8B5CF6', // Purple (default)
      '#3B82F6', // Blue
      '#10B981', // Green
      '#F59E0B', // Yellow
      '#EF4444', // Red
      '#8B5A2B', // Brown
      '#EC4899', // Pink
      '#6366F1', // Indigo
      '#84CC16', // Lime
      '#F97316'  // Orange
    ];
    
    // Generate consistent color based on parent task ID
    if (parentTask && parentTask.id) {
      const hash = parentTask.id.split('').reduce((a, b) => {
        a = ((a << 5) - a) + b.charCodeAt(0);
        return a & a;
      }, 0);
      return colors[Math.abs(hash) % colors.length];
    }
    
    return colors[0]; // Default purple
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  const getSubtaskProgress = (subtask) => {
    if (subtask.subtask_count === 0) return null;
    const percentage = (subtask.completed_subtasks / subtask.subtask_count) * 100;
    return { percentage, completed: subtask.completed_subtasks, total: subtask.subtask_count };
  };

  const totalSubtasks = parentTask.subtask_count || 0;
  const completedSubtasks = parentTask.completed_subtasks || 0;
  const progressPercentage = totalSubtasks > 0 ? (completedSubtasks / totalSubtasks) * 100 : 0;
  const taskColor = getSubtaskColor(parentTask);

  return (
    <div className="subtask-manager">
      {/* Subtask Summary & Toggle */}
      <div 
        className="subtask-header"
        onClick={() => setIsExpanded(!isExpanded)}
        style={{ borderLeft: `4px solid ${taskColor}` }}
      >
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: taskColor }}
            ></div>
            <svg 
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="font-medium text-gray-700">
              Subtasks ({completedSubtasks}/{totalSubtasks})
            </span>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              Room: {parentTask.title}
            </span>
          </div>
          
          {totalSubtasks > 0 && (
            <div className="flex items-center gap-2">
              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 transition-all duration-300"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-500">{Math.round(progressPercentage)}%</span>
            </div>
          )}
        </div>
      </div>

      {/* Expanded Subtask Content */}
      {isExpanded && (
        <div 
          className="subtask-content"
          style={{ borderLeft: `3px solid ${taskColor}` }}
        >
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
            </div>
          ) : (
            <>
              {/* Create New Subtask */}
              {canCreate() && (
                <div className="create-subtask-section">
                  {!showCreateForm ? (
                    <button
                      onClick={() => setShowCreateForm(true)}
                      className="btn-secondary-small"
                    >
                      + Add Subtask
                    </button>
                  ) : (
                    <div className="create-subtask-form">
                      <input
                        type="text"
                        placeholder="Subtask title"
                        value={newSubtask.title}
                        onChange={(e) => setNewSubtask({ ...newSubtask, title: e.target.value })}
                        className="form-input mb-2"
                      />
                      <textarea
                        placeholder="Description (optional)"
                        value={newSubtask.description}
                        onChange={(e) => setNewSubtask({ ...newSubtask, description: e.target.value })}
                        className="form-input mb-2"
                        rows="2"
                      />
                      <div className="grid grid-cols-2 gap-2 mb-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Order Date (optional)
                          </label>
                          <input
                            type="date"
                            value={newSubtask.order_date}
                            onChange={(e) => setNewSubtask({ ...newSubtask, order_date: e.target.value })}
                            className="form-input"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Delivery Date (optional)
                          </label>
                          <input
                            type="date"
                            value={newSubtask.delivery_date}
                            onChange={(e) => setNewSubtask({ ...newSubtask, delivery_date: e.target.value })}
                            className="form-input"
                          />
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={createSubtask} className="btn-primary-small">Create</button>
                        <button 
                          onClick={() => {
                            setShowCreateForm(false);
                            setNewSubtask({ title: '', description: '', order_date: '', delivery_date: '' });
                          }}
                          className="btn-secondary-small"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Subtask List */}
              <div className="subtasks-list">
                {subtasks.map((subtask) => (
                  <div key={subtask.id} className="subtask-item">
                    <div className="subtask-main">
                      <div className="flex items-start gap-3">
                        {/* Completion Checkbox */}
                        <button
                          onClick={() => toggleSubtaskCompletion(subtask)}
                          className={`subtask-checkbox ${subtask.completed ? 'completed' : ''}`}
                          disabled={!canEdit()}
                        >
                          {subtask.completed && (
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </button>

                        {/* Subtask Content */}
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className={`subtask-title ${subtask.completed ? 'completed' : ''}`}>
                              {subtask.title}
                            </h4>
                            
                            {/* Subtask Actions */}
                            <div className="flex items-center gap-1">
                              {subtask.subtask_count > 0 && (
                                <button
                                  onClick={() => toggleSubtaskExpansion(subtask.id)}
                                  className="btn-icon-small"
                                  title="Toggle sub-subtasks"
                                >
                                  <svg 
                                    className={`w-3 h-3 transition-transform ${expandedSubtasks.has(subtask.id) ? 'rotate-90' : ''}`} 
                                    fill="none" 
                                    stroke="currentColor" 
                                    viewBox="0 0 24 24"
                                  >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                  </svg>
                                </button>
                              )}
                              
                              {canEdit() && (
                                <button
                                  onClick={() => setEditingSubtask(subtask)}
                                  className="btn-icon-small"
                                  title="Edit subtask"
                                >
                                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                  </svg>
                                </button>
                              )}
                            </div>
                          </div>

                          {/* Subtask Description */}
                          {subtask.description && (
                            <p className="subtask-description">{subtask.description}</p>
                          )}

                          {/* Subtask Dates */}
                          <div className="subtask-dates">
                            {subtask.order_date && (
                              <span className="subtask-date order">
                                📦 Order: {formatDate(subtask.order_date)}
                              </span>
                            )}
                            {subtask.delivery_date && (
                              <span className="subtask-date delivery">
                                🚚 Delivery: {formatDate(subtask.delivery_date)}
                              </span>
                            )}
                          </div>

                          {/* Sub-subtask Progress */}
                          {subtask.subtask_count > 0 && (
                            <div className="sub-subtask-progress">
                              <span className="text-xs text-gray-500">
                                Sub-subtasks: {subtask.completed_subtasks}/{subtask.subtask_count}
                              </span>
                              <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-blue-500 transition-all duration-300"
                                  style={{ width: `${getSubtaskProgress(subtask)?.percentage || 0}%` }}
                                ></div>
                              </div>
                            </div>
                          )}

                          {/* File Manager for Subtask */}
                          {subtask.file_count > 0 && (
                            <FileManager 
                              taskId={subtask.id}
                              title={`Files (${subtask.file_count})`}
                            />
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Sub-subtasks (Nested) */}
                    {expandedSubtasks.has(subtask.id) && subtask.subtask_level === 1 && (
                      <div className="sub-subtasks">
                        <SubtaskManager 
                          parentTask={subtask}
                          onSubtaskUpdate={fetchSubtasks}
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Edit Subtask Modal */}
      {editingSubtask && (
        <div className="modal-overlay" onClick={() => setEditingSubtask(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Subtask</h3>
              <button onClick={() => setEditingSubtask(null)} className="btn-icon">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <input
                type="text"
                value={editingSubtask.title}
                onChange={(e) => setEditingSubtask({ ...editingSubtask, title: e.target.value })}
                className="form-input mb-3"
                placeholder="Subtask title"
              />
              <textarea
                value={editingSubtask.description || ''}
                onChange={(e) => setEditingSubtask({ ...editingSubtask, description: e.target.value })}
                className="form-input mb-3"
                rows="3"
                placeholder="Description"
              />
              <div className="grid grid-cols-2 gap-3 mb-3">
                <input
                  type="date"
                  value={editingSubtask.order_date || ''}
                  onChange={(e) => setEditingSubtask({ ...editingSubtask, order_date: e.target.value })}
                  className="form-input"
                />
                <input
                  type="date"
                  value={editingSubtask.delivery_date || ''}
                  onChange={(e) => setEditingSubtask({ ...editingSubtask, delivery_date: e.target.value })}
                  className="form-input"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                onClick={async () => {
                  await updateSubtask(editingSubtask.id, {
                    title: editingSubtask.title,
                    description: editingSubtask.description,
                    order_date: editingSubtask.order_date || null,
                    delivery_date: editingSubtask.delivery_date || null
                  });
                  setEditingSubtask(null);
                }}
                className="btn-primary"
              >
                Save Changes
              </button>
              <button onClick={() => setEditingSubtask(null)} className="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubtaskManager;