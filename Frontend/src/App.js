import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from "react-router-dom";
import Home from "./components/Home";
import Login from "./components/Login";
import DataManagement from "./components/DataManagement";
import Analytics from "./components/Analytics";
import PlayerStats from "./components/PlayerStats";
import InjuryReport from "./components/InjuryReport";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    localStorage.getItem('token') !== null
  );

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  return (
    <Router>
      <div>
        <header style={{ backgroundColor: '#007bff', color: 'white', padding: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1200px', margin: '0 auto' }}>
            <h1>Sports Management System</h1>
            {isAuthenticated && (
              <nav style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <Link to="/home" style={{ color: 'white', textDecoration: 'none' }}>Dashboard</Link>
                <Link to="/player-stats" style={{ color: 'white', textDecoration: 'none' }}>Player Stats</Link>
                <Link to="/injuries" style={{ color: 'white', textDecoration: 'none' }}>Injury Report</Link>
                <Link to="/manage" style={{ color: 'white', textDecoration: 'none' }}>Data Management</Link>
                <Link to="/analytics" style={{ color: 'white', textDecoration: 'none' }}>Analytics</Link>
                <button 
                  onClick={handleLogout}
                  style={{ 
                    background: '#dc3545', 
                    color: 'white', 
                    border: 'none', 
                    padding: '0.5rem 1rem', 
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Logout
                </button>
              </nav>
            )}
          </div>
        </header>
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route
            path="/home"
            element={isAuthenticated ? <Home /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/injuries"
            element={isAuthenticated ? <InjuryReport /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/player-stats"
            element={isAuthenticated ? <PlayerStats /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/manage"
            element={isAuthenticated ? <DataManagement /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/analytics"
            element={isAuthenticated ? <Analytics /> : <Navigate to="/login" replace />}
          />
          <Route path="*" element={<Navigate to={isAuthenticated ? "/home" : "/login"} replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;