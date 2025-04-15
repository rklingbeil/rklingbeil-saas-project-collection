// File: /Users/rick/CaseProject/frontend/src/components/UserDashboard.js
import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';

const UserDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);

  useEffect(() => {
    // This function would fetch the user's subscription status
    // from the backend in a real implementation
    const fetchUserData = async () => {
      try {
        // Mock data for now
        setUserInfo({
          email: "user@example.com",
          name: "Demo User",
          accountCreated: "February 18, 2024"
        });
        
        setSubscription({
          status: "active",
          plan: "Premium",
          renewalDate: "March 18, 2024",
          casesAnalyzed: 5
        });
        
        setLoading(false);
      } catch (err) {
        console.error("Error fetching user data:", err);
        setError("Failed to load user information");
        setLoading(false);
      }
    };

    if (showDashboard) {
      fetchUserData();
    }
  }, [showDashboard]);

  if (!showDashboard) {
    return (
      <div className="dashboard-toggle">
        <button 
          className="dashboard-button" 
          onClick={() => setShowDashboard(true)}
        >
          View Account Dashboard
        </button>
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner message="Loading account information..." />;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  return (
    <div className="user-dashboard">
      <h2>Account Dashboard</h2>
      
      <div className="dashboard-section">
        <h3>User Information</h3>
        {userInfo && (
          <div className="info-grid">
            <div className="info-row">
              <span className="info-label">Email:</span>
              <span className="info-value">{userInfo.email}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Name:</span>
              <span className="info-value">{userInfo.name}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Account Created:</span>
              <span className="info-value">{userInfo.accountCreated}</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="dashboard-section">
        <h3>Subscription Details</h3>
        {subscription && (
          <div className="info-grid">
            <div className="info-row">
              <span className="info-label">Plan:</span>
              <span className="info-value">{subscription.plan}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Status:</span>
              <span className="info-value status-badge status-{subscription.status}">
                {subscription.status.toUpperCase()}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Next Renewal:</span>
              <span className="info-value">{subscription.renewalDate}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Cases Analyzed:</span>
              <span className="info-value">{subscription.casesAnalyzed}</span>
            </div>
          </div>
        )}
      </div>
      
      <button 
        className="dashboard-button secondary" 
        onClick={() => setShowDashboard(false)}
      >
        Hide Dashboard
      </button>
    </div>
  );
};

export default UserDashboard;
