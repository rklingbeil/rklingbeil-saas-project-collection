// File: /Users/rick/CaseProject/frontend/src/components/case/CaseHistory.js

import React, { useState, useEffect } from 'react';
import { useApi } from '../../services/api';
import '../../App.css';

const CaseHistory = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedCase, setExpandedCase] = useState(null);
  const api = useApi();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch case history from the API
        const data = await api.request('/cases/history');
        setHistory(data);
      } catch (err) {
        console.error('Error fetching case history:', err);
        setError(`Failed to load case history: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchHistory();
  }, [api]);

  const toggleCaseDetails = (id) => {
    if (expandedCase === id) {
      setExpandedCase(null);
    } else {
      setExpandedCase(id);
    }
  };

  // Format date string to a more readable format
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  // Extract a brief summary from case facts (first 100 characters)
  const getCaseSummary = (facts) => {
    if (!facts) return 'No case details available';
    return facts.length > 100 ? `${facts.substring(0, 100)}...` : facts;
  };

  if (loading) {
    return <div className="case-history-loading">Loading case history...</div>;
  }

  if (error) {
    return <div className="case-history-error">{error}</div>;
  }

  if (history.length === 0) {
    return (
      <div className="case-history-empty">
        <h2>Case History</h2>
        <p>You haven't analyzed any cases yet.</p>
      </div>
    );
  }

  return (
    <div className="case-history">
      <h2>Case History</h2>
      <div className="case-list">
        {history.map((item) => (
          <div key={item.id} className="case-history-item">
            <div className="case-header" onClick={() => toggleCaseDetails(item.id)}>
              <div className="case-date">{formatDate(item.created_at)}</div>
              <div className="case-summary">{getCaseSummary(item.subject_case.facts)}</div>
              <div className="case-expand-icon">
                {expandedCase === item.id ? '▼' : '▶'}
              </div>
            </div>
            
            {expandedCase === item.id && (
              <div className="case-details">
                <div className="case-section">
                  <h3>Case Details</h3>
                  <p><strong>Court:</strong> {item.subject_case.court || 'N/A'}</p>
                  <p><strong>Date:</strong> {item.subject_case.date || 'N/A'}</p>
                  <p><strong>Claim Type:</strong> {item.subject_case.claim_type || 'N/A'}</p>
                  <p><strong>Injury Type:</strong> {item.subject_case.injury_type || 'N/A'}</p>
                  <p><strong>Facts:</strong> {item.subject_case.facts}</p>
                  <p><strong>Injuries:</strong> {item.subject_case.injuries}</p>
                  <p><strong>Economic Damages:</strong> {item.subject_case.economic_damages}</p>
                </div>
                
                <div className="case-section">
                  <h3>Prediction</h3>
                  <div className="prediction-text">
                    {item.prediction.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CaseHistory;
