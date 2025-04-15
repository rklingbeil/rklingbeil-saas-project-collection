// File: /Users/rick/CaseProject/frontend/src/components/auth/LoginButton.js
import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const LoginButton = () => {
  const { loginWithRedirect, isLoading } = useAuth0();

  return (
    <button 
      onClick={() => loginWithRedirect()}
      className="auth-button"
      disabled={isLoading}
    >
      {isLoading ? "Connecting..." : "Log In"}
    </button>
  );
};

export default LoginButton;
