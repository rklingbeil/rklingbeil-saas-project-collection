// File: /Users/rick/CaseProject/frontend/src/components/auth/LogoutButton.js
import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const LogoutButton = () => {
  const { logout, isLoading } = useAuth0();

  return (
    <button 
      onClick={() => logout({ returnTo: window.location.origin })}
      className="logout-button"
      disabled={isLoading}
    >
      Log Out
    </button>
  );
};

export default LogoutButton;
