// File: /Users/rick/CaseProject/frontend/src/Checkout.js

import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useApi } from './services/api';
import './App.css';

const StripeCheckout = () => {
  const { isAuthenticated } = useAuth0();
  const api = useApi();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [processingPayment, setProcessingPayment] = useState(false);

  // Fetch subscription plans and user's current subscription
  useEffect(() => {
    if (isAuthenticated) {
      const fetchData = async () => {
        try {
          setLoading(true);
          
          // Fetch subscription plans
          const plansData = await api.request('/subscriptions/plans');
          setPlans(plansData.plans);
          
          // Fetch user's current subscription
          const subscriptionData = await api.request('/subscriptions/my-subscription');
          setSubscription(subscriptionData);
        } catch (error) {
          console.error('Error fetching data:', error);
          setError(error.message);
        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    }
  }, [isAuthenticated, api]);

  // Handle subscription creation
  const handleSubscribe = async (planId) => {
    if (!isAuthenticated) {
      setError('Please log in to subscribe');
      return;
    }
    
    try {
      setProcessingPayment(true);
      
      // Create customer if needed and then subscription
      const data = await api.request('/subscriptions/create-subscription', {
        method: 'POST',
        body: JSON.stringify({ plan_id: planId })
      });
      
      if (data.client_secret) {
        // If we have a client secret, redirect to Stripe checkout
        window.location.href = `https://checkout.stripe.com/pay/${data.client_secret}`;
      } else {
        // Otherwise, the subscription was already created or updated
        // Refresh the subscription data
        const refreshData = await api.request('/subscriptions/my-subscription');
        setSubscription(refreshData);
      }
    } catch (error) {
      console.error('Error creating subscription:', error);
      setError(error.message);
    } finally {
      setProcessingPayment(false);
    }
  };

  // Handle subscription cancellation
  const handleCancelSubscription = async () => {
    if (!isAuthenticated || !subscription.has_subscription) {
      return;
    }
    
    if (!window.confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your billing period.')) {
      return;
    }
    
    try {
      setLoading(true);
      
      await api.request('/subscriptions/cancel-subscription', {
        method: 'POST'
      });
      
      // Refresh subscription data
      const refreshData = await api.request('/subscriptions/my-subscription');
      setSubscription(refreshData);
      
      alert('Your subscription has been canceled. You will have access until the end of your current billing period.');
    } catch (error) {
      console.error('Error canceling subscription:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle opening Stripe customer portal
  const handleManageSubscription = async () => {
    if (!isAuthenticated || !subscription.has_subscription) {
      return;
    }
    
    try {
      setLoading(true);
      
      const data = await api.request('/subscriptions/customer-portal', {
        method: 'POST',
        body: JSON.stringify({ return_url: window.location.href })
      });
      
      window.location.href = data.url;
    } catch (error) {
      console.error('Error opening customer portal:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Render loading state
  if (loading) {
    return <div className="checkout-loading">Loading subscription information...</div>;
  }

  // Render error state
  if (error) {
    return <div className="checkout-error">Error: {error}</div>;
  }

  // Render current subscription
  if (subscription && subscription.has_subscription) {
    const { plan_name, status, monthly_quota, remaining_quota } = subscription.details;
    
    return (
      <div className="subscription-info">
        <h2>Your Subscription</h2>
        <div className="subscription-details">
          <p><strong>Plan:</strong> {plan_name}</p>
          <p><strong>Status:</strong> {status}</p>
          <p><strong>Monthly Quota:</strong> {monthly_quota} case analyses</p>
          <p><strong>Remaining Quota:</strong> {remaining_quota} case analyses</p>
        </div>
        <div className="subscription-actions">
          <button onClick={handleManageSubscription} className="manage-button">
            Manage Subscription
          </button>
          <button onClick={handleCancelSubscription} className="cancel-button">
            Cancel Subscription
          </button>
        </div>
      </div>
    );
  }

  // Render subscription plans
  return (
    <div className="subscription-plans">
      <h2>Choose a Subscription Plan</h2>
      <div className="plans-container">
        {plans.map((plan) => (
          <div key={plan.id} className="plan-card">
            <h3>{plan.name}</h3>
            <p className="plan-quota">{plan.monthly_quota} case analyses per month</p>
            <p className="plan-price">
              {plan.id === 'basic' ? '$29' : plan.id === 'professional' ? '$99' : '$299'} 
              <span className="plan-price-period">/month</span>
            </p>
            <button 
              onClick={() => handleSubscribe(plan.id)} 
              className="subscribe-button"
              disabled={processingPayment}
            >
              {processingPayment ? 'Processing...' : 'Subscribe'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StripeCheckout;
