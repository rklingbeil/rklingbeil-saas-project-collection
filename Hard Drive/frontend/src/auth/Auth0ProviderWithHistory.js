// File: /Users/rick/CaseProject/frontend/src/auth/Auth0ProviderWithHistory.js
import React from 'react';
import { Auth0Provider } from '@auth0/auth0-react';

const Auth0ProviderWithHistory = ({ children }) => {
  const domain = 'dev-wmydj4rlx48n5trz.us.auth0.com';
  const clientId = 'WvY1U2l9FY3xbHtnWLLSEyAWBeXi1Y6h';
  const audience = 'https://my-saas-app.local/api';

  const onRedirectCallback = (appState) => {
    window.history.replaceState(
      {},
      document.title,
      appState?.returnTo || window.location.pathname
    );
  };

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      redirectUri={window.location.origin}
      onRedirectCallback={onRedirectCallback}
      audience={audience}
      scope="openid profile email offline_access"  // Added offline_access for refresh tokens
      useRefreshTokens={true}  // Enable refresh tokens
      cacheLocation="localstorage"  // Store tokens in localStorage
    >
      {children}
    </Auth0Provider>
  );
};

export default Auth0ProviderWithHistory;
