// Login.js
import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for redirection

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate(); // Hook to navigate between routes

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Send a POST request to the login endpoint
      const response = await axios.post('http://127.0.0.1:8000/auth/login', {
        username: username,
        password: password,
      });
      // Save the token in local storage
      localStorage.setItem('token', response.data.token);
      setMessage('Login successful!');
      // Redirect to the Home page or Dashboard after login
      navigate('/');
    } catch (error) {
      setMessage('Login failed: ' + (error.response?.data.detail || 'Unknown error'));
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
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
        <button type="submit">Login</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Login;

