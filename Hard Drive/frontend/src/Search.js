// Search.js
import React, { useState } from 'react';
import axios from 'axios';

const Search = () => {
  // State variables for the query, session ID, and search results
  const [query, setQuery] = useState('');
  const [sessionId, setSessionId] = useState('session-1'); // For now, using a fixed session ID
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  // Function to handle search form submission
  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      // Send a POST request to the /cases/search endpoint
      const response = await axios.post(
        'http://127.0.0.1:8000/cases/search',
        { query: query, session_id: sessionId },
        {
          headers: {
            'Content-Type': 'application/json',
            // Include the token from login (dummy token for now)
            'Authorization': 'Bearer dummy-token-123'
          },
        }
      );
      // Save the returned search results
      setResults(response.data);
      setError('');
    } catch (err) {
      setError('Search failed: ' + (err.response?.data.detail || 'Unknown error'));
      setResults(null);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Search Cases</h2>
      <form onSubmit={handleSearch}>
        <div style={{ marginBottom: '10px' }}>
          <label>Query: </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your legal case query"
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Session ID: </label>
          <input
            type="text"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
          />
        </div>
        <button type="submit">Search</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {results && (
        <div style={{ marginTop: '20px' }}>
          <h3>Search Results:</h3>
          <div>
            <h4>Similar Cases:</h4>
            <ul>
              {results.similar_cases.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4>Predictions:</h4>
            <p>Settlement Value: {results.predictions.settlement_value}</p>
            <p>Verdict Outcome: {results.predictions.verdict_outcome}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;

