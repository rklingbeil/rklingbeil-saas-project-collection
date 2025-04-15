// File: /Users/rick/CaseProject/frontend/src/services/api.js

import { useAuth0 } from '@auth0/auth0-react';

export const useApi = () => {
  const { getAccessTokenSilently } = useAuth0();
  
  // Base API URL
  const API_URL = 'http://127.0.0.1:8000';
  
  // Generic API request function with authentication
  const apiRequest = async (endpoint, options = {}) => {
    try {
      const token = await getAccessTokenSilently({
        audience: "https://my-saas-app.local/api",
      });
      
      // Merge default headers with passed options
      const mergedOptions = {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      };
      
      const response = await fetch(`${API_URL}${endpoint}`, mergedOptions);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  };
  
  // Specific API methods
  return {
    // Case analysis
    analyzeCase: (caseData) => 
      apiRequest('/cases/search', {
        method: 'POST',
        body: JSON.stringify(caseData),
      }),
    
    // User profile
    getUserProfile: () => 
      apiRequest('/auth/users/profile'),
    
    // Generic request method for other endpoints
    request: apiRequest,
  };
};
