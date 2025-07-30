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
  
  // Filter states
  const [teamFilter, setTeamFilter] = useState({ league_id: '', name: '' });
  const [playerFilter, setPlayerFilter] = useState({ team_id: '', name: '', position: '' });

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
        fetchTeamsWithFilter(),
        fetchPlayersWithFilter()
      ]);
      
      setLeagues(leaguesRes.data);
    } catch (err) {
      setError('Failed to fetch data');
    }
  };

  const fetchTeamsWithFilter = async () => {
    try {
      const params = new URLSearchParams();
      if (teamFilter.league_id) params.append('league_id', teamFilter.league_id);
      if (teamFilter.name) params.append('name', teamFilter.name);
      
      const response = await axios.get(`${apiUrl}/api/teams?${params.toString()}`, { headers: getAuthHeaders() });
      setTeams(response.data);
      return response;
    } catch (err) {
      setError('Failed to fetch teams');
      return { data: [] };
    }
  };

  const fetchPlayersWithFilter = async () => {
    try {
      const params = new URLSearchParams();
      if (playerFilter.team_id) params.append('team_id', playerFilter.team_id);
      if (playerFilter.name) params.append('name', playerFilter.name);
      if (playerFilter.position) params.append('position', playerFilter.position);
      
      const response = await axios.get(`${apiUrl}/api/players?${params.toString()}`, { headers: getAuthHeaders() });
      setPlayers(response.data);
      return response;
    } catch (err) {
      setError('Failed to fetch players');
      return { data: [] };
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
          <div className="filter-section">
            <h3>Filter Teams</h3>
            <div className="filter-form">
              <select
                value={teamFilter.league_id}
                onChange={(e) => setTeamFilter({...teamFilter, league_id: e.target.value})}
              >
                <option value="">All Leagues</option>
                {leagues.map(league => (
                  <option key={league.id} value={league.id}>{league.name}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Filter by team name"
                value={teamFilter.name}
                onChange={(e) => setTeamFilter({...teamFilter, name: e.target.value})}
              />
              <button onClick={fetchTeamsWithFilter}>Apply Filters</button>
              <button onClick={() => {setTeamFilter({league_id: '', name: ''}); fetchTeamsWithFilter();}}>Clear</button>
            </div>
          </div>
          
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
            <h3>Teams ({teams.length} found)</h3>
            <div className="teams-grid">
              {teams.map(team => (
                <div key={team.id} className="team-card">
                  <h4>{team.name}</h4>
                  <p><strong>City:</strong> {team.home_city}</p>
                  <p><strong>League:</strong> {team.league_name}</p>
                  {team.head_coach && <p><strong>Coach:</strong> {team.head_coach}</p>}
                  {team.stadium && <p><strong>Stadium:</strong> {team.stadium}</p>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'players' && (
        <div className="tab-content">
          <div className="filter-section">
            <h3>Filter Players</h3>
            <div className="filter-form">
              <select
                value={playerFilter.team_id}
                onChange={(e) => setPlayerFilter({...playerFilter, team_id: e.target.value})}
              >
                <option value="">All Teams</option>
                {teams.map(team => (
                  <option key={team.id} value={team.id}>{team.name}</option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Filter by player name"
                value={playerFilter.name}
                onChange={(e) => setPlayerFilter({...playerFilter, name: e.target.value})}
              />
              <input
                type="text"
                placeholder="Filter by position"
                value={playerFilter.position}
                onChange={(e) => setPlayerFilter({...playerFilter, position: e.target.value})}
              />
              <button onClick={fetchPlayersWithFilter}>Apply Filters</button>
              <button onClick={() => {setPlayerFilter({team_id: '', name: '', position: ''}); fetchPlayersWithFilter();}}>Clear</button>
            </div>
          </div>
          
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
            <h3>Players ({players.length} found)</h3>
            <div className="players-grid">
              {players.map(player => (
                <div key={player.id} className="player-card">
                  <h4>{player.name}</h4>
                  <p><strong>Position:</strong> {player.position}</p>
                  <p><strong>Team:</strong> {player.team_name}</p>
                  <p><strong>League:</strong> {player.league_name}</p>
                  <div className="career-stats-summary">
                    {(player.career_passing_yards > 0 || player.career_rushing_yards > 0 || 
                      player.career_receiving_yards > 0 || player.career_touchdowns > 0) && (
                      <div>
                        <strong>Career Stats:</strong>
                        {player.career_passing_yards > 0 && <span>Pass: {player.career_passing_yards.toLocaleString()}</span>}
                        {player.career_rushing_yards > 0 && <span>Rush: {player.career_rushing_yards.toLocaleString()}</span>}
                        {player.career_receiving_yards > 0 && <span>Rec: {player.career_receiving_yards.toLocaleString()}</span>}
                        {player.career_touchdowns > 0 && <span>TDs: {player.career_touchdowns}</span>}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DataManagement;