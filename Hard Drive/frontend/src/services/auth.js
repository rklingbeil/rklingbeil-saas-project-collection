// File: /Users/rick/CaseProject/frontend/src/services/auth.js

import { useAuth0 } from '@auth0/auth0-react';

// Custom hook to get token
export const useAuthToken = () => {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  
  // Function to get the token
  const getToken = async () => {
    if (!isAuthenticated) {
      return null;
    }
    
    try {
      return await getAccessTokenSilently({
        audience: "https://my-saas-app.local/api",
      });
    } catch (error) {
      console.error("Error getting access token:", error);
      return null;
    }
  };
  
  return { getToken };
};

// Legacy methods for compatibility (you can remove these later)
export const getToken = () => {
  return localStorage.getItem('access_token');
};

export const setToken = (token) => {
  localStorage.setItem('access_token', token);
};

export const removeToken = () => {
  localStorage.removeItem('access_token');
};

// This function will be deprecated
export const getClientCredentialsToken = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/auth/client-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get token: ${response.status}`);
    }
    
    const data = await response.json();
    return data.access_token;
  } catch (error) {
    console.error('Error getting client credentials token:', error);
    throw error;
  }
};
