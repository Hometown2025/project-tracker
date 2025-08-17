import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const BudgetView = ({ selectedProject }) => {
  const { user } = useAuth();
  const [budgetSummary, setBudgetSummary] = useState(null);
  const [budgetItems, setBudgetItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (selectedProject) {
      fetchBudgetData();
    } else {
      setBudgetSummary(null);
      setBudgetItems([]);
      setLoading(false);
    }
  }, [selectedProject]);

  const fetchBudgetData = async () => {
    if (!selectedProject) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API}/projects/${selectedProject.id}/budget`);
      setBudgetSummary(response.data);
      setBudgetItems(response.data.budget_items || []);
    } catch (error) {
      console.error('Error fetching budget:', error);
      setError('Failed to load budget information');
      setBudgetSummary(null);
      setBudgetItems([]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (typeof amount !== 'number') return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const categoryColors = {
    'Materials': '#4CAF50',
    'Labor': '#2196F3', 
    'Equipment': '#FF9800',
    'Permits': '#9C27B0',
    'Other': '#607D8B'
  };

  if (loading) {
    return (
      <div className="budget-view">
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
        <div className="error-state">
          <svg className="w-8 h-8 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  if (!selectedProject) {
    return (
      <div className="budget-view">
        <div className="empty-state">
          <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Project Selected</h3>
          <p className="text-gray-500">Select a project to view budget information</p>
        </div>
      </div>
    );
  }

  return (
    <div className="budget-view">
      <div className="view-header">
        <div>
          <h1 className="page-title">Project Budget</h1>
          <p className="page-subtitle">{selectedProject.name}</p>
        </div>
      </div>

      {budgetSummary && (
        <>
          {/* Budget Summary Cards */}
          <div className="budget-summary-cards">
            <div className="budget-card">
              <div className="budget-card-header">
                <h3>Total Estimate</h3>
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="budget-amount">{formatCurrency(budgetSummary.total_estimated)}</div>
            </div>

            <div className="budget-card">
              <div className="budget-card-header">
                <h3>Amount Spent</h3>
                <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <div className="budget-amount">{formatCurrency(budgetSummary.total_spent)}</div>
            </div>

            <div className={`budget-card ${budgetSummary.over_budget ? 'over-budget' : ''}`}>
              <div className="budget-card-header">
                <h3>Remaining</h3>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="budget-amount">
                {formatCurrency(budgetSummary.remaining_budget)}
              </div>
              {budgetSummary.over_budget && (
                <div className="over-budget-warning">Over Budget!</div>
              )}
            </div>
          </div>

          {/* Budget Progress Bar */}
          <div className="budget-progress">
            <div className="budget-progress-header">
              <h3>Budget Progress</h3>
              <span className="progress-percentage">
                {budgetSummary.total_estimated > 0 
                  ? Math.round((budgetSummary.total_spent / budgetSummary.total_estimated) * 100)
                  : 0}% Used
              </span>
            </div>
            <div className="progress-bar">
              <div 
                className={`progress-fill ${budgetSummary.over_budget ? 'over-budget' : ''}`}
                style={{
                  width: `${Math.min(
                    budgetSummary.total_estimated > 0 
                      ? (budgetSummary.total_spent / budgetSummary.total_estimated) * 100 
                      : 0, 
                    100
                  )}%`
                }}
              ></div>
            </div>
          </div>

          {/* Budget Items */}
          {budgetItems.length > 0 && (
            <div className="budget-items">
              <h3 className="section-title">Budget Breakdown</h3>
              <div className="budget-items-list">
                {budgetItems.map(item => (
                  <div key={item.id} className="budget-item">
                    <div className="budget-item-header">
                      <div className="budget-item-info">
                        <div 
                          className="category-indicator"
                          style={{ backgroundColor: categoryColors[item.category] || categoryColors['Other'] }}
                        ></div>
                        <div>
                          <h4 className="budget-item-name">{item.item_name}</h4>
                          <p className="budget-item-category">{item.category}</p>
                          {item.description && (
                            <p className="budget-item-description">{item.description}</p>
                          )}
                        </div>
                      </div>
                      <div className="budget-item-amounts">
                        <div className="estimated-cost">
                          <span className="label">Estimated:</span>
                          <span className="amount">{formatCurrency(item.estimated_cost * item.quantity)}</span>
                        </div>
                        {item.actual_cost && (
                          <div className="actual-cost">
                            <span className="label">Actual:</span>
                            <span className="amount">{formatCurrency(item.actual_cost * item.quantity)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="budget-item-details">
                      <span className="quantity">Qty: {item.quantity} {item.unit}</span>
                      <span className="unit-price">
                        {formatCurrency(item.estimated_cost)} per {item.unit}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {budgetItems.length === 0 && (
            <div className="empty-budget-items">
              <svg className="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Budget Items</h3>
              <p className="text-gray-500">
                {user?.role === 'customer' 
                  ? 'Your lumber yard will add budget items for this project soon.'
                  : 'No budget items have been added to this project yet.'}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default BudgetView;