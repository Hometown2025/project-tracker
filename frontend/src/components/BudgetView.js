import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Color palette for rooms (matching the existing project colors)
const ROOM_COLORS = [
  '#8B5CF6', '#EF4444', '#F59E0B', '#10B981', '#3B82F6', 
  '#8B5A2B', '#EC4899', '#6366F1', '#84CC16', '#F97316'
];

// PieChart Component
const PieChart = ({ data, title }) => {
  if (!data || !Array.isArray(data) || data.length === 0) return null;

  const total = data.reduce((sum, item) => sum + (item?.value || 0), 0);
  if (total === 0) return null;

  let currentAngle = 0;
  const radius = 80;
  const centerX = 100;
  const centerY = 100;

  const slices = data.map((item, index) => {
    const percentage = (item.value / total) * 100;
    const angle = (item.value / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;
    
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;
    
    const x1 = centerX + radius * Math.cos(startAngleRad);
    const y1 = centerY + radius * Math.sin(startAngleRad);
    const x2 = centerX + radius * Math.cos(endAngleRad);
    const y2 = centerY + radius * Math.sin(endAngleRad);
    
    const largeArcFlag = angle > 180 ? 1 : 0;
    
    const pathData = [
      `M ${centerX} ${centerY}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z'
    ].join(' ');
    
    currentAngle += angle;
    
    return {
      ...item,
      pathData,
      percentage: percentage.toFixed(1),
      color: ROOM_COLORS[index % ROOM_COLORS.length]
    };
  });

  return (
    <div className="pie-chart-container">
      <h4 className="chart-title">{title}</h4>
      <div className="pie-chart-wrapper">
        <svg width="200" height="200" viewBox="0 0 200 200">
          {slices.map((slice, index) => (
            <g key={index}>
              <path
                d={slice.pathData}
                fill={slice.color}
                stroke="#fff"
                strokeWidth="2"
              />
              <title>{`${slice.label}: $${slice.value.toLocaleString()} (${slice.percentage}%)`}</title>
            </g>
          ))}
        </svg>
        <div className="pie-legend">
          {slices.map((slice, index) => (
            <div key={index} className="legend-item">
              <div 
                className="legend-color" 
                style={{ backgroundColor: slice.color }}
              ></div>
              <span className="legend-text">
                {slice.label} ({slice.percentage}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// BarChart Component
const BarChart = ({ data, title }) => {
  if (!data || data.length === 0) return null;

  const maxValue = Math.max(...data.map(item => Math.max(item.estimated || 0, item.actual || 0)));
  if (maxValue === 0) return null;

  return (
    <div className="bar-chart-container">
      <h4 className="chart-title">{title}</h4>
      <div className="bar-chart-wrapper">
        {data.map((item, index) => (
          <div key={index} className="bar-group">
            <div className="bar-label">{item.label}</div>
            <div className="bars">
              <div className="bar-pair">
                <div className="bar estimated-bar">
                  <div 
                    className="bar-fill"
                    style={{ 
                      height: `${((item.estimated || 0) / maxValue) * 100}%`,
                      backgroundColor: ROOM_COLORS[index % ROOM_COLORS.length],
                      opacity: 0.7
                    }}
                  ></div>
                  <div className="bar-value">
                    ${(item.estimated || 0).toLocaleString()}
                  </div>
                </div>
                <div className="bar actual-bar">
                  <div 
                    className="bar-fill"
                    style={{ 
                      height: `${((item.actual || 0) / maxValue) * 100}%`,
                      backgroundColor: ROOM_COLORS[index % ROOM_COLORS.length]
                    }}
                  ></div>
                  <div className="bar-value">
                    ${(item.actual || 0).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        <div className="bar-legend">
          <div className="legend-item">
            <div className="legend-color estimated"></div>
            <span>Estimated</span>
          </div>
          <div className="legend-item">
            <div className="legend-color actual"></div>
            <span>Actual</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const BudgetView = ({ projects, selectedProject, onProjectSelect }) => {
  const { user } = useAuth();
  const [budgetData, setBudgetData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (selectedProject) {
      fetchBudgetData();
    }
  }, [selectedProject]);

  const fetchBudgetData = async () => {
    if (!selectedProject) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API}/projects/${selectedProject.id}/budget-summary`);
      setBudgetData(response.data);
    } catch (error) {
      console.error('Error fetching budget data:', error);
      setError('Failed to load budget information');
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const prepareChartData = () => {
    if (!budgetData || !budgetData.room_breakdown || !Array.isArray(budgetData.room_breakdown)) {
      return { pieData: [], barData: [] };
    }

    const pieData = budgetData.room_breakdown
      .filter(room => room && room.room_total_estimated > 0)
      .map(room => ({
        label: room.room_name || 'Unnamed Room',
        value: room.room_total_estimated || 0
      }));

    const barData = budgetData.room_breakdown
      .filter(room => room && (room.room_total_estimated > 0 || room.room_total_actual > 0))
      .map(room => ({
        label: room.room_name || 'Unnamed Room',
        estimated: room.room_total_estimated || 0,
        actual: room.room_total_actual || 0
      }));

    return { pieData, barData };
  };

  if (!selectedProject) {
    return (
      <div className="budget-view">
        <div className="budget-header">
          <h2>Budget Overview</h2>
          <div className="project-selector">
            <label>Select a project to view budget details:</label>
            <select 
              onChange={(e) => {
                const project = projects.find(p => p.id === e.target.value);
                onProjectSelect(project);
              }}
              value=""
            >
              <option value="">Choose a project...</option>
              {projects.map(project => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="budget-placeholder">
          <div className="placeholder-icon">💰</div>
          <h3>No Project Selected</h3>
          <p>Choose a project from the dropdown above to view detailed budget information, cost breakdowns, and spending analysis.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="budget-view">
        <div className="budget-header">
          <h2>Budget Overview - {selectedProject.name}</h2>
        </div>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading budget information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="budget-view">
        <div className="budget-header">
          <h2>Budget Overview - {selectedProject.name}</h2>
        </div>
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Budget Information Unavailable</h3>
          <p>{error}</p>
          <button className="btn-primary" onClick={fetchBudgetData}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const { pieData, barData } = prepareChartData();

  return (
    <div className="budget-view">
      <div className="budget-header">
        <h2>Budget Overview - {selectedProject.name}</h2>
        <div className="project-selector">
          <select 
            onChange={(e) => {
              const project = projects.find(p => p.id === e.target.value);
              onProjectSelect(project);
            }}
            value={selectedProject.id}
          >
            {projects.map(project => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {budgetData && (
        <div className="budget-content">
          {/* Project Summary */}
          <div className="project-budget-summary">
            <h3>Project Budget Summary</h3>
            <div className="summary-cards">
              <div className="summary-card project-estimated">
                <div className="card-icon">🏠</div>
                <div className="card-content">
                  <h4>Project Budget</h4>
                  <div className="amount">${(budgetData.project_own_estimated_budget || 0).toLocaleString()}</div>
                </div>
              </div>
              
              <div className="summary-card total-estimated">
                <div className="card-icon">📊</div>
                <div className="card-content">
                  <h4>Total Estimated</h4>
                  <div className="amount">${(budgetData.total_estimated_with_project || 0).toLocaleString()}</div>
                </div>
              </div>
              
              <div className="summary-card actual">
                <div className="card-icon">💵</div>
                <div className="card-content">
                  <h4>Total Spent</h4>
                  <div className="amount">${(budgetData.project_actual_total || 0).toLocaleString()}</div>
                </div>
              </div>
              
              <div className={`summary-card variance ${budgetData.budget_variance >= 0 ? 'over' : 'under'}`}>
                <div className="card-icon">{budgetData.budget_variance >= 0 ? '📈' : '📉'}</div>
                <div className="card-content">
                  <h4>Variance</h4>
                  <div className="amount">
                    {budgetData.budget_variance >= 0 ? '+' : ''}${(budgetData.budget_variance || 0).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          {(pieData.length > 0 || barData.length > 0) && (
            <div className="budget-charts">
              <h3>Room Budget Analysis</h3>
              <div className="charts-container">
                {pieData.length > 0 && (
                  <PieChart 
                    data={pieData} 
                    title="Budget Distribution by Room" 
                  />
                )}
                {barData.length > 0 && (
                  <BarChart 
                    data={barData} 
                    title="Estimated vs Actual by Room" 
                  />
                )}
              </div>
            </div>
          )}

          {/* Room Breakdown */}
          {budgetData.room_breakdown && budgetData.room_breakdown.length > 0 && (
            <div className="room-breakdown">
              <h3>Room-by-Room Breakdown</h3>
              <div className="breakdown-table">
                <div className="table-header">
                  <div className="col room-name">Room</div>
                  <div className="col budget-info">Room Budget</div>
                  <div className="col subtask-info">Subtasks</div>
                  <div className="col total-info">Total</div>
                  <div className="col percentage">% of Project</div>
                  <div className="col variance">Variance</div>
                </div>
                {budgetData.room_breakdown.map((room, index) => {
                  const percentage = budgetData.total_estimated_with_project > 0 
                    ? ((room.room_total_estimated / budgetData.total_estimated_with_project) * 100).toFixed(1)
                    : 0;
                  
                  return (
                    <div key={room.room_id} className="table-row">
                      <div className="col room-name">
                        <div 
                          className="room-color-indicator"
                          style={{ backgroundColor: ROOM_COLORS[index % ROOM_COLORS.length] }}
                        ></div>
                        <span>{room.room_name}</span>
                        <small>{room.subtask_count} subtasks</small>
                      </div>
                      <div className="col budget-info">
                        <div className="budget-amounts">
                          <div className="estimated">${room.room_estimated_budget.toLocaleString()}</div>
                          <div className="actual">${room.room_actual_cost.toLocaleString()}</div>
                        </div>
                      </div>
                      <div className="col subtask-info">
                        <div className="budget-amounts">
                          <div className="estimated">${room.subtask_estimated_total.toLocaleString()}</div>
                          <div className="actual">${room.subtask_actual_total.toLocaleString()}</div>
                        </div>
                      </div>
                      <div className="col total-info">
                        <div className="budget-amounts total">
                          <div className="estimated">${room.room_total_estimated.toLocaleString()}</div>
                          <div className="actual">${room.room_total_actual.toLocaleString()}</div>
                        </div>
                      </div>
                      <div className="col percentage">
                        <div className="percentage-value">{percentage}%</div>
                      </div>
                      <div className={`col variance ${room.room_budget_variance >= 0 ? 'over' : 'under'}`}>
                        <div className="variance-value">
                          {room.room_budget_variance >= 0 ? '+' : ''}${room.room_budget_variance.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BudgetView;