import React, { useState } from "react";
import axios from "axios";
import ResultList from "./ResultList";
import "./Home.css";

function Home() {
  const [teamName, setTeamName] = useState("");
  const [week, setWeek] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  // Get JWT token from localStorage
  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResults([]);

    try {
      const params = new URLSearchParams();
      if (teamName) params.append("team", teamName);
      if (week) params.append("week", week);
      
      const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
      const response = await axios.get(
        `${apiUrl}/api/games?${params.toString()}`,
        { headers: getAuthHeaders() }
      );
      
      setResults(response.data);
    } catch (err) {
      console.error("Error:", err.toString());
      if (err.response?.status === 401) {
        setError("Authentication failed. Please log in again.");
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else {
        setError("Failed to fetch data. Please try again.");
      }
    }
  };

  return (
    <div className="home-container">
      <div className="form-header">
        <h2>Search for Team Analytics</h2>
      </div>
      <form className="form-section" onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="teamName">Team Name</label>
          <input
            id="teamName"
            type="text"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            placeholder="Enter team name"
          />
        </div>
        <div className="input-group">
          <label htmlFor="week">Week Number</label>
          <input
            id="week"
            type="number"
            value={week}
            onChange={(e) => setWeek(e.target.value)}
            placeholder="Enter week number (optional)"
            min="1"
          />
        </div>
        <div className="btn-group">
          <button type="submit">Search</button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      <div className="results-section">
        <ResultList results={results} />
      </div>
    </div>
  );
}

export default Home;