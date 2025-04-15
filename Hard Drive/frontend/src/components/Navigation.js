// File: /Users/rick/CaseProject/frontend/src/components/Navigation.js

import React from 'react';
import '../App.css';

const Navigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'analyze', label: 'Case Analysis' },
    { id: 'history', label: 'History' },
    { id: 'subscription', label: 'Subscription' },
  ];

  return (
    <div className="navigation">
      <ul className="nav-tabs">
        {tabs.map((tab) => (
          <li 
            key={tab.id} 
            className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Navigation;
