// Logout.js
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Remove the token from local storage
    localStorage.removeItem('token');
    // Optionally, you could also clear other user-related data here
    // Redirect the user to the home or login page
    navigate('/login');
  }, [navigate]);

  return (
    <div style={{ padding: '20px' }}>
      <h2>You have been logged out.</h2>
    </div>
  );
};

export default Logout;

