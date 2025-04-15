// Registration.js
import React, { useState } from 'react';
import axios from 'axios';

const Registration = () => {
  // State variables for username, password, and messages
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  // Function to handle form submission
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      // Send a POST request to the registration endpoint
      const response = await axios.post('http://127.0.0.1:8000/users/register', {
        username: username,
        password: password,
      });
      setMessage('Registration successful! User ID: ' + response.data.user_id);
    } catch (error) {
      setMessage('Registration failed: ' + (error.response?.data.detail || 'Unknown error'));
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <div style={{ marginBottom: '10px' }}>
          <label>Username: </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Password: </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit">Register</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Registration;

