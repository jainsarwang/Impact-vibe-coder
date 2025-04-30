import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchRepositories = async () => {
    setLoading(true);
    setError('');
    setRepositories([]);

    try {
      const response = await fetch(`https://api.github.com/users/${username}/repos`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('User not found');
        } else {
          throw new Error('Could not fetch projects');
        }
      }
      const data = await response.json();
      setRepositories(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchRepositories();
  };

  return (
    <div className="app-container">
      <h1 className="app-title">DevDash</h1>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          placeholder="Enter GitHub username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="username-input"
        />
        <button type="submit" className="fetch-button" disabled={loading}>
          {loading ? 'Loading...' : 'Fetch Repositories'}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {loading && !error && <div className="loading-message">Loading...</div>}

      <ul className="repository-list">
        {repositories.map((repo) => (
          <li key={repo.id} className="repository-item">
            <h2 className="repo-name">{repo.name}</h2>
            {repo.description && <p className="repo-description">{repo.description}</p>}
            {repo.language && <p className="repo-language">Language: {repo.language}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;