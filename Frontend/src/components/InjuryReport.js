import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './InjuryReport.css';

function InjuryReport() {
  const [injuries, setInjuries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    team_id: '',
    active_only: false,
    severity: ''
  });

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchInjuries = async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams();
      if (filters.team_id) params.append('team_id', filters.team_id);
      if (filters.active_only) params.append('active_only', 'true');
      if (filters.severity) params.append('severity', filters.severity);

      const response = await axios.get(
        `${apiUrl}/analytics/injury-report?${params.toString()}`,
        { headers: getAuthHeaders() }
      );

      // Sort by severity (highest to lowest severity)
      const severityOrder = { 'Critical': 5, 'Severe': 4, 'Moderate': 3, 'Minor': 2, 'Mild': 1 };
      const sortedInjuries = response.data.sort((a, b) => {
        const severityA = severityOrder[a.severity] || 0;
        const severityB = severityOrder[b.severity] || 0;
        return severityB - severityA; // Descending order
      });

      setInjuries(sortedInjuries);
    } catch (err) {
      console.error('Error fetching injuries:', err);
      setError('Failed to fetch injury data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInjuries();
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const getSeverityBadgeClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'severity-critical';
      case 'severe': return 'severity-severe';
      case 'moderate': return 'severity-moderate';
      case 'minor': return 'severity-minor';
      case 'mild': return 'severity-mild';
      default: return 'severity-unknown';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return <div className="injury-loading">Loading injury data...</div>;
  }

  if (error) {
    return <div className="injury-error">{error}</div>;
  }

  return (
    <div className="injury-report-container">
      <h2>🏥 Injury Report</h2>
      <p className="injury-subtitle">Sorted by severity (highest to lowest)</p>
      
      {/* Filters */}
      <div className="injury-filters">
        <div className="filter-group">
          <label>
            <input
              type="checkbox"
              name="active_only"
              checked={filters.active_only}
              onChange={handleFilterChange}
            />
            Active injuries only
          </label>
        </div>
        
        <div className="filter-group">
          <label>
            Severity:
            <select
              name="severity"
              value={filters.severity}
              onChange={handleFilterChange}
            >
              <option value="">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="Severe">Severe</option>
              <option value="Moderate">Moderate</option>
              <option value="Minor">Minor</option>
              <option value="Mild">Mild</option>
            </select>
          </label>
        </div>
      </div>

      {/* Injury Statistics */}
      <div className="injury-stats">
        <div className="stat-card">
          <h4>Total Injuries</h4>
          <p className="stat-number">{injuries.length}</p>
        </div>
        <div className="stat-card">
          <h4>Active Injuries</h4>
          <p className="stat-number">{injuries.filter(injury => injury.is_active).length}</p>
        </div>
        <div className="stat-card">
          <h4>Critical/Severe</h4>
          <p className="stat-number">
            {injuries.filter(injury => 
              injury.severity === 'Critical' || injury.severity === 'Severe'
            ).length}
          </p>
        </div>
      </div>

      {/* Injury Table */}
      <div className="injury-table-container">
        <table className="injury-table">
          <thead>
            <tr>
              <th>Player</th>
              <th>Position</th>
              <th>Team</th>
              <th>Severity</th>
              <th>Description</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Duration (days)</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {injuries.length === 0 ? (
              <tr>
                <td colSpan="9" className="no-data">No injury data available</td>
              </tr>
            ) : (
              injuries.map(injury => (
                <tr key={injury.injury_id} className={injury.is_active ? 'active-injury' : 'recovered-injury'}>
                  <td className="player-name">{injury.player_name}</td>
                  <td>{injury.position}</td>
                  <td>{injury.team_name}</td>
                  <td>
                    <span className={`severity-badge ${getSeverityBadgeClass(injury.severity)}`}>
                      {injury.severity || 'Unknown'}
                    </span>
                  </td>
                  <td className="injury-description">{injury.description}</td>
                  <td>{formatDate(injury.start_date)}</td>
                  <td>{formatDate(injury.end_date)}</td>
                  <td className="duration">{injury.duration_days || 'Ongoing'}</td>
                  <td>
                    <span className={`status-badge ${injury.is_active ? 'status-active' : 'status-recovered'}`}>
                      {injury.is_active ? 'Active' : 'Recovered'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="refresh-section">
        <button onClick={fetchInjuries} className="refresh-btn">
          Refresh Injury Data
        </button>
      </div>
    </div>
  );
}

export default InjuryReport;