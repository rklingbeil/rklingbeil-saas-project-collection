// File: /Users/rick/CaseProject/frontend/src/App.js

import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, BorderStyle } from 'docx';
import { saveAs } from 'file-saver';
import './App.css';

function App() {
  const { isAuthenticated, user, loginWithRedirect, logout, getAccessTokenSilently } = useAuth0();
  const [activeTab, setActiveTab] = useState('cases');
  const [formData, setFormData] = useState({
    court: '',
    date: '',
    plaintiff_medical_expert: '',
    defense_medical_expert: '',
    plaintiff_expert: '',
    defense_expert: '',
    judge_arbitrator_mediator: '',
    insurance_company: '',
    claim_type: '',
    injury_type: '',
    facts: '',
    injuries: '',
    economic_damages: ''
  });
  const [prediction, setPrediction] = useState(null);
  const [similarCases, setSimilarCases] = useState([]);
  const [showSimilarCases, setShowSimilarCases] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [caseHistory, setCaseHistory] = useState([]);
  const [expandedCase, setExpandedCase] = useState(null);
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);

  useEffect(() => {
    if (isAuthenticated) {
      // Load case history when authenticated
      fetchCaseHistory();
      // Load subscription info when authenticated
      fetchSubscriptionInfo();
      // Load subscription plans when authenticated
      fetchSubscriptionPlans();
    }
  }, [isAuthenticated]);

  const fetchCaseHistory = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('http://127.0.0.1:8000/cases/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error(`Error fetching case history: ${response.status}`);
      }
      const data = await response.json();
      setCaseHistory(data);
    } catch (error) {
      console.error('Error fetching case history:', error);
      setError('Error loading case history. Please try again later.');
    }
  };

  const fetchSubscriptionInfo = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('http://127.0.0.1:8000/subscriptions/my-subscription', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        // Don't throw error for 404 - just means no subscription yet
        if (response.status !== 404) {
          throw new Error(`Error fetching subscription: ${response.status}`);
        }
        setSubscriptionInfo({ has_subscription: false });
        return;
      }
      const data = await response.json();
      setSubscriptionInfo(data);
    } catch (error) {
      console.error('Error fetching subscription info:', error);
      setError('Error loading subscription information. Please try again later.');
    }
  };

  const fetchSubscriptionPlans = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('http://127.0.0.1:8000/subscriptions/plans', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error(`Error fetching subscription plans: ${response.status}`);
      }
      const data = await response.json();
      // Ensure data is an array
      setSubscriptionPlans(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
      setError('Error loading subscription plans. Please try again later.');
      // Set to empty array on error
      setSubscriptionPlans([]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleAnalyzeCase = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.facts || !formData.injuries || !formData.economic_damages) {
      setError('Please fill in all required fields.');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAccessTokenSilently();
      
      const response = await fetch('http://127.0.0.1:8000/cases/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          subject_case: formData
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      setPrediction(data.prediction);
      setSimilarCases(data.similar_cases || []);
      
      // Refresh case history
      fetchCaseHistory();
      
    } catch (error) {
      console.error('Error analyzing case:', error);
      setError(`Error analyzing case data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const createPredictionDocument = async () => {
    if (!prediction) return;
    
    // Create a new document
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [
              new TextRun({
                text: "Case Settlement Value Analysis",
                bold: true,
                size: 32
              })
            ],
            alignment: AlignmentType.CENTER
          }),
          
          new Paragraph({
            children: [new TextRun("")],
            spacing: { before: 200, after: 200 }
          }),
          
          new Paragraph({
            children: [
              new TextRun({
                text: "Case Facts:",
                bold: true,
                size: 28
              })
            ]
          }),
          
          new Paragraph({
            children: [
              new TextRun(formData.facts || "No facts provided")
            ],
            spacing: { after: 200 }
          }),
          
          new Paragraph({
            children: [
              new TextRun({
                text: "Injuries:",
                bold: true,
                size: 28
              })
            ]
          }),
          
          new Paragraph({
            children: [
              new TextRun(formData.injuries || "No injuries provided")
            ],
            spacing: { after: 200 }
          }),
          
          new Paragraph({
            children: [
              new TextRun({
                text: "Economic Damages:",
                bold: true,
                size: 28
              })
            ]
          }),
          
          new Paragraph({
            children: [
              new TextRun(formData.economic_damages || "No economic damages provided")
            ],
            spacing: { after: 400 }
          }),
          
          new Paragraph({
            children: [
              new TextRun({
                text: "Analysis and Prediction:",
                bold: true,
                size: 28
              })
            ]
          }),
          
          new Paragraph({
            children: [
              new TextRun(prediction || "No prediction available")
            ],
            spacing: { after: 200 }
          }),
          
          new Paragraph({
            children: [
              new TextRun({
                text: `Generated on: ${new Date().toLocaleDateString()}`
              })
            ],
            spacing: { before: 400 }
          })
        ]
      }]
    });
    
    // Generate the document as a blob
    Packer.toBlob(doc).then(blob => {
      // Save the document
      saveAs(blob, "case-analysis.docx");
    });
  };
  
  const createSimilarCasesDocument = async () => {
    if (!similarCases || similarCases.length === 0) return;
    
    // Create a new document
    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            heading: HeadingLevel.HEADING_1,
            children: [
              new TextRun({
                text: "Similar Cases Analysis",
                bold: true,
                size: 32
              })
            ],
            alignment: AlignmentType.CENTER
          }),
          
          ...similarCases.flatMap((caseItem, index) => [
            new Paragraph({
              heading: HeadingLevel.HEADING_2,
              children: [
                new TextRun({
                  text: `Case ${index + 1}`,
                  bold: true,
                  size: 28
                })
              ],
              spacing: { before: 400 }
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Court: ",
                  bold: true
                }),
                new TextRun(caseItem.court || "Not specified")
              ]
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Date: ",
                  bold: true
                }),
                new TextRun(caseItem.date || "Not specified")
              ]
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Claim Type: ",
                  bold: true
                }),
                new TextRun(caseItem.claim_type || "Not specified")
              ]
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Facts: ",
                  bold: true
                }),
                new TextRun(caseItem.facts || "Not specified")
              ]
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Injuries: ",
                  bold: true
                }),
                new TextRun(caseItem.injuries || "Not specified")
              ]
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Economic Damages: ",
                  bold: true
                }),
                new TextRun(caseItem.economic_damages || "Not specified")
              ]
            }),
            
            new Paragraph({
              children: [
                new TextRun({
                  text: "Result: ",
                  bold: true
                }),
                new TextRun(caseItem.result || "Not specified")
              ],
              spacing: { after: 200 }
            })
          ])
        ]
      }]
    });
    
    // Generate the document as a blob
    Packer.toBlob(doc).then(blob => {
      // Save the document
      saveAs(blob, "similar-cases.docx");
    });
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const toggleSimilarCases = () => {
    setShowSimilarCases(!showSimilarCases);
  };

  const handleExpandCase = (index) => {
    setExpandedCase(expandedCase === index ? null : index);
  };

  const handleCreateSubscription = async (planId) => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('http://127.0.0.1:8000/subscriptions/create-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan_id: planId
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Redirect to Stripe checkout
      window.location.href = data.checkout_url;
      
    } catch (error) {
      console.error('Error creating subscription:', error);
      setError(`Error creating subscription: ${error.message}`);
    }
  };

  const renderCaseForm = () => (
    <div className="case-form-container">
      <h2>Case Settlement Value Analysis</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleAnalyzeCase} className="case-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="court">Court:</label>
            <input 
              type="text" 
              id="court" 
              name="court" 
              value={formData.court} 
              onChange={handleInputChange} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="date">Date:</label>
            <input 
              type="date" 
              id="date" 
              name="date" 
              value={formData.date} 
              onChange={handleInputChange} 
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="plaintiff_medical_expert">Plaintiff Medical Expert:</label>
            <input 
              type="text" 
              id="plaintiff_medical_expert" 
              name="plaintiff_medical_expert" 
              value={formData.plaintiff_medical_expert} 
              onChange={handleInputChange} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="defense_medical_expert">Defense Medical Expert:</label>
            <input 
              type="text" 
              id="defense_medical_expert" 
              name="defense_medical_expert" 
              value={formData.defense_medical_expert} 
              onChange={handleInputChange} 
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="plaintiff_expert">Plaintiff Expert:</label>
            <input 
              type="text" 
              id="plaintiff_expert" 
              name="plaintiff_expert" 
              value={formData.plaintiff_expert} 
              onChange={handleInputChange} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="defense_expert">Defense Expert:</label>
            <input 
              type="text" 
              id="defense_expert" 
              name="defense_expert" 
              value={formData.defense_expert} 
              onChange={handleInputChange} 
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="judge_arbitrator_mediator">Judge/Arbitrator/Mediator:</label>
            <input 
              type="text" 
              id="judge_arbitrator_mediator" 
              name="judge_arbitrator_mediator" 
              value={formData.judge_arbitrator_mediator} 
              onChange={handleInputChange} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="insurance_company">Insurance Company:</label>
            <input 
              type="text" 
              id="insurance_company" 
              name="insurance_company" 
              value={formData.insurance_company} 
              onChange={handleInputChange} 
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="claim_type">Claim Type:</label>
            <input 
              type="text" 
              id="claim_type" 
              name="claim_type" 
              value={formData.claim_type} 
              onChange={handleInputChange} 
            />
          </div>
          <div className="form-group">
            <label htmlFor="injury_type">General type of Injury or Damage:</label>
            <input 
              type="text" 
              id="injury_type" 
              name="injury_type" 
              value={formData.injury_type} 
              onChange={handleInputChange} 
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="facts">Facts *:</label>
          <textarea 
            id="facts" 
            name="facts" 
            value={formData.facts} 
            onChange={handleInputChange} 
            required
          ></textarea>
        </div>
        
        <div className="form-group">
          <label htmlFor="injuries">Details - Injuries or Damages *:</label>
          <textarea 
            id="injuries" 
            name="injuries" 
            value={formData.injuries} 
            onChange={handleInputChange} 
            required
          ></textarea>
        </div>
        
        <div className="form-group">
          <label htmlFor="economic_damages">Economic Damages *:</label>
          <input 
            type="text" 
            id="economic_damages" 
            name="economic_damages" 
            value={formData.economic_damages} 
            onChange={handleInputChange} 
            required
          />
        </div>
        
        <div className="form-note">* Indicates required data.</div>
        
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze Case'}
        </button>
      </form>
      
      {prediction && (
        <div className="prediction-container">
          <h3>Analysis Result:</h3>
          <div className="prediction-text">
            {prediction.split('\n').map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
          <button type="button" onClick={createPredictionDocument} className="download-button">
            Download Results as Word
          </button>
          
          <button type="button" onClick={toggleSimilarCases} className="similar-cases-button">
            {showSimilarCases ? 'Hide Similar Cases' : 'View Similar Cases'}
          </button>
          
          {showSimilarCases && similarCases.length > 0 && (
            <div className="similar-cases-container">
              <h3>Similar Cases:</h3>
              {similarCases.map((caseItem, index) => (
                <div key={index} className="similar-case">
                  <h4>Case {index + 1}</h4>
                  <div className="case-details">
                    <p><strong>Court:</strong> {caseItem.court || 'Not specified'}</p>
                    <p><strong>Date:</strong> {caseItem.date || 'Not specified'}</p>
                    <p><strong>Claim Type:</strong> {caseItem.claim_type || 'Not specified'}</p>
                    <p><strong>Facts:</strong> {caseItem.facts || 'Not specified'}</p>
                    <p><strong>Injuries:</strong> {caseItem.injuries || 'Not specified'}</p>
                    <p><strong>Economic Damages:</strong> {caseItem.economic_damages || 'Not specified'}</p>
                    <p><strong>Result:</strong> {caseItem.result || 'Not specified'}</p>
                  </div>
                </div>
              ))}
              <button type="button" onClick={createSimilarCasesDocument} className="download-button">
                Download as Word Document
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderCaseHistory = () => (
    <div className="case-history-container">
      <h2>Case History</h2>
      {caseHistory.length === 0 ? (
        <p>No case analyses found. Analyze a case to see it in your history.</p>
      ) : (
        <div className="case-history-list">
          {caseHistory.map((caseItem, index) => (
            <div key={index} className="case-history-item">
              <div 
                className="case-history-header" 
                onClick={() => handleExpandCase(index)}
              >
                <h3>
                  {caseItem.subject_case.court 
                    ? `${caseItem.subject_case.court} - ` 
                    : ''
                  }
                  {caseItem.subject_case.claim_type 
                    ? `${caseItem.subject_case.claim_type} - ` 
                    : ''
                  }
                  {new Date(caseItem.created_at).toLocaleDateString()}
                </h3>
                <span className={`expand-icon ${expandedCase === index ? 'expanded' : ''}`}>
                  ▼
                </span>
              </div>
              
              {expandedCase === index && (
                <div className="case-history-details">
                  <div className="case-facts">
                    <h4>Case Details:</h4>
                    <p><strong>Facts:</strong> {caseItem.subject_case.facts}</p>
                    <p><strong>Injuries:</strong> {caseItem.subject_case.injuries}</p>
                    <p><strong>Economic Damages:</strong> {caseItem.subject_case.economic_damages}</p>
                  </div>
                  
                  <div className="case-prediction">
                    <h4>Analysis:</h4>
                    {caseItem.prediction.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderSubscription = () => (
    <div className="subscription-container">
      <h2>Subscription Management</h2>
      
      {subscriptionInfo && subscriptionInfo.has_subscription ? (
        <div className="current-subscription">
          <h3>Current Subscription</h3>
          <div className="subscription-details">
            <p><strong>Plan:</strong> {subscriptionInfo.details.plan_name}</p>
            <p><strong>Status:</strong> {subscriptionInfo.details.status}</p>
            <p><strong>Monthly Quota:</strong> {subscriptionInfo.details.monthly_quota} analyses</p>
            <p><strong>Remaining Quota:</strong> {subscriptionInfo.details.remaining_quota} analyses</p>
            <p><strong>Current Period Ends:</strong> {new Date(subscriptionInfo.details.current_period_end).toLocaleDateString()}</p>
          </div>
        </div>
      ) : (
        <div className="no-subscription">
          <p>You do not have an active subscription. Please choose a plan below.</p>
        </div>
      )}
      
      <div className="subscription-plans">
        <h3>Available Plans</h3>
        {!Array.isArray(subscriptionPlans) || subscriptionPlans.length === 0 ? (
          <p>Loading available plans...</p>
        ) : (
          <div className="plans-container">
            {subscriptionPlans.map((plan, index) => (
              <div key={index} className="plan-card">
                <h4>{plan.name}</h4>
                <p className="plan-price">${plan.price_per_month}/month</p>
                <div className="plan-features">
                  <p>{plan.monthly_quota} case analyses per month</p>
                  <p>{plan.description}</p>
                </div>
                <button 
                  onClick={() => handleCreateSubscription(plan.id)}
                  className="subscribe-button"
                >
                  {subscriptionInfo && subscriptionInfo.has_subscription ? 'Change to This Plan' : 'Subscribe'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Case Settlement Value Analysis</h1>
        {isAuthenticated ? (
          <div className="user-info">
            <p>{user.email}</p>
            <button onClick={() => logout({ returnTo: window.location.origin })}>
              Log Out
            </button>
          </div>
        ) : (
          <button onClick={() => loginWithRedirect()}>Log In</button>
        )}
      </header>
      
      {isAuthenticated ? (
        <div className="main-content">
          <nav className="tab-navigation">
            <ul>
              <li 
                className={activeTab === 'cases' ? 'active' : ''}
                onClick={() => handleTabChange('cases')}
              >
                Case Analysis
              </li>
              <li 
                className={activeTab === 'history' ? 'active' : ''}
                onClick={() => handleTabChange('history')}
              >
                History
              </li>
              <li 
                className={activeTab === 'subscription' ? 'active' : ''}
                onClick={() => handleTabChange('subscription')}
              >
                Subscription
              </li>
            </ul>
          </nav>
          
          <div className="tab-content">
            {activeTab === 'cases' && renderCaseForm()}
            {activeTab === 'history' && renderCaseHistory()}
            {activeTab === 'subscription' && renderSubscription()}
          </div>
        </div>
      ) : (
        <div className="login-prompt">
          <p>Please log in to use the Case Settlement Value Analysis tool.</p>
        </div>
      )}
    </div>
  );
}

export default App;
