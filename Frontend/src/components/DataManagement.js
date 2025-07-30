import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DataManagement.css';

function DataManagement() {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('leagues');

  // Form states
  const [leagueForm, setLeagueForm] = useState({ name: '', level: '' });
  const [teamForm, setTeamForm] = useState({ name: '', home_city: '', league_id: '' });
  const [playerForm, setPlayerForm] = useState({ name: '', position: '', team_id: '' });

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [leaguesRes, teamsRes, playersRes] = await Promise.all([
        axios.get(`${apiUrl}/api/leagues`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/teams`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/players`, { headers: getAuthHeaders() })
      ]);
      
      setLeagues(leaguesRes.data);
      setTeams(teamsRes.data);
      setPlayers(playersRes.data);
    } catch (err) {
      setError('Failed to fetch data');
    }
  };

  const handleLeagueSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/leagues`, leagueForm, { headers: getAuthHeaders() });
      setLeagueForm({ name: '', level: '' });
      setSuccess('League created successfully!');
      fetchData();
    } catch (err) {
      setError('Failed to create league');
    }
  };

  const handleTeamSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/teams`, teamForm, { headers: getAuthHeaders() });
      setTeamForm({ name: '', home_city: '', league_id: '' });
      setSuccess('Team created successfully!');
      fetchData();
    } catch (err) {
      setError('Failed to create team');
    }
  };

  const handlePlayerSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl}/api/players`, playerForm, { headers: getAuthHeaders() });
      setPlayerForm({ name: '', position: '', team_id: '' });
      setSuccess('Player created successfully!');
      fetchData();
    } catch (err) {
      setError('Failed to create player');
    }
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  return (
    <div className="data-management">
      <h2>Data Management</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      
      <div className="tabs">
        <button 
          className={activeTab === 'leagues' ? 'active' : ''} 
          onClick={() => { setActiveTab('leagues'); clearMessages(); }}
        >
          Leagues
        </button>
        <button 
          className={activeTab === 'teams' ? 'active' : ''} 
          onClick={() => { setActiveTab('teams'); clearMessages(); }}
        >
          Teams
        </button>
        <button 
          className={activeTab === 'players' ? 'active' : ''} 
          onClick={() => { setActiveTab('players'); clearMessages(); }}
        >
          Players
        </button>
      </div>

      {activeTab === 'leagues' && (
        <div className="tab-content">
          <div className="form-section">
            <h3>Create New League</h3>
            <form onSubmit={handleLeagueSubmit}>
              <input
                type="text"
                placeholder="League Name"
                value={leagueForm.name}
                onChange={(e) => setLeagueForm({...leagueForm, name: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Level (e.g., Professional, College)"
                value={leagueForm.level}
                onChange={(e) => setLeagueForm({...leagueForm, level: e.target.value})}
              />
              <button type="submit">Create League</button>
            </form>
          </div>
          
          <div className="list-section">
            <h3>Existing Leagues</h3>
            <ul>
              {leagues.map(league => (
                <li key={league.id}>{league.name} - {league.level}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'teams' && (
        <div className="tab-content">
          <div className="form-section">
            <h3>Create New Team</h3>
            <form onSubmit={handleTeamSubmit}>
              <input
                type="text"
                placeholder="Team Name"
                value={teamForm.name}
                onChange={(e) => setTeamForm({...teamForm, name: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Home City"
                value={teamForm.home_city}
                onChange={(e) => setTeamForm({...teamForm, home_city: e.target.value})}
                required
              />
              <select
                value={teamForm.league_id}
                onChange={(e) => setTeamForm({...teamForm, league_id: e.target.value})}
                required
              >
                <option value="">Select League</option>
                {leagues.map(league => (
                  <option key={league.id} value={league.id}>{league.name}</option>
                ))}
              </select>
              <button type="submit">Create Team</button>
            </form>
          </div>
          
          <div className="list-section">
            <h3>Existing Teams</h3>
            <ul>
              {teams.map(team => (
                <li key={team.id}>
                  {team.name} - League ID: {team.league_id}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'players' && (
        <div className="tab-content">
          <div className="form-section">
            <h3>Create New Player</h3>
            <form onSubmit={handlePlayerSubmit}>
              <input
                type="text"
                placeholder="Player Name"
                value={playerForm.name}
                onChange={(e) => setPlayerForm({...playerForm, name: e.target.value})}
                required
              />
              <input
                type="text"
                placeholder="Position (e.g., QB, RB, WR)"
                value={playerForm.position}
                onChange={(e) => setPlayerForm({...playerForm, position: e.target.value})}
                required
              />
              <select
                value={playerForm.team_id}
                onChange={(e) => setPlayerForm({...playerForm, team_id: e.target.value})}
                required
              >
                <option value="">Select Team</option>
                {teams.map(team => (
                  <option key={team.id} value={team.id}>{team.name}</option>
                ))}
              </select>
              <button type="submit">Create Player</button>
            </form>
          </div>
          
          <div className="list-section">
            <h3>Existing Players</h3>
            <ul>
              {players.map(player => (
                <li key={player.id}>
                  {player.name} ({player.position}) - Team ID: {player.team_id}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataManagement;