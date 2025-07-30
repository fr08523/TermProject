import React, { useState } from 'react';
import axios from 'axios';
import './PlayerStats.css';

function PlayerStats() {
  const [playerName, setPlayerName] = useState('');
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerStats, setPlayerStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchPerformed, setSearchPerformed] = useState(false);
  
  // Sorting state for game logs table
  const [sortField, setSortField] = useState('game_date');
  const [sortDirection, setSortDirection] = useState('desc');

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';



  const searchPlayers = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSearchPerformed(true);
    
    try {
      const response = await axios.get(
        `${apiUrl}/api/players?name=${encodeURIComponent(playerName)}`
      );
      
      setPlayers(response.data);
      setSelectedPlayer(null);
      setPlayerStats(null);
      
      if (response.data.length === 0) {
        setError('No players found matching your search');
      }
    } catch (err) {
      console.error('Error searching players:', err);
      setError('Failed to search for players. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const selectPlayer = async (player) => {
    setSelectedPlayer(player);
    setLoading(true);
    setError('');
    
    try {
      const playerStatsRes = await axios.get(`${apiUrl}/api/players/${player.id}/stats`);
      
      setPlayerStats(playerStatsRes.data);
    } catch (err) {
      console.error('Error fetching player stats:', err);
      setError('Failed to fetch player statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setPlayerName('');
    setPlayers([]);
    setSelectedPlayer(null);
    setPlayerStats(null);
    setSearchPerformed(false);
    setError('');
    // Reset sorting
    setSortField('game_date');
    setSortDirection('desc');
  };

  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to descending for most stats, ascending for dates
      setSortField(field);
      setSortDirection(field === 'game_date' || field === 'week' ? 'asc' : 'desc');
    }
  };

  const sortGameLogs = (gameLogs) => {
    if (!gameLogs || !Array.isArray(gameLogs)) return [];
    
    return [...gameLogs].sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      // Handle different data types
      if (sortField === 'game_date') {
        aValue = new Date(aValue || '1900-01-01');
        bValue = new Date(bValue || '1900-01-01');
      } else if (sortField === 'opponent') {
        aValue = (aValue || '').toLowerCase();
        bValue = (bValue || '').toLowerCase();
      } else {
        // Numeric fields
        aValue = aValue || 0;
        bValue = bValue || 0;
      }
      
      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  };

  const getSortIcon = (field) => {
    if (sortField !== field) return ' ↕️';
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };

  return (
    <div className="player-stats-container">
      <div className="search-header">
        <h2>Player Statistics Search</h2>
        <p>Search for individual player statistics and performance data</p>
      </div>

      <form className="search-form" onSubmit={searchPlayers}>
        <div className="search-input-group">
          <input
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Enter player name (e.g., Dak Prescott)"
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Searching...' : 'Search Players'}
          </button>
          {searchPerformed && (
            <button type="button" onClick={clearSearch} className="clear-btn">
              Clear Search
            </button>
          )}
        </div>
      </form>

      {error && <div className="error-message">{error}</div>}

      {searchPerformed && players.length > 0 && !selectedPlayer && (
        <div className="players-list">
          <h3>Search Results ({players.length} player{players.length !== 1 ? 's' : ''} found)</h3>
          <div className="players-grid">
            {players.map(player => (
              <div key={player.id} className="player-card" onClick={() => selectPlayer(player)}>
                <h4>{player.name}</h4>
                <p><strong>Position:</strong> {player.position}</p>
                <p><strong>Team:</strong> {player.team_name}</p>
                <p><strong>League:</strong> {player.league_name}</p>
                <div className="career-stats">
                  <p><strong>Career Stats:</strong></p>
                  <div className="stats-row">
                    {player.career_passing_yards > 0 && <span>Passing: {player.career_passing_yards.toLocaleString()} yds</span>}
                    {player.career_rushing_yards > 0 && <span>Rushing: {player.career_rushing_yards.toLocaleString()} yds</span>}
                    {player.career_receiving_yards > 0 && <span>Receiving: {player.career_receiving_yards.toLocaleString()} yds</span>}
                    {player.career_touchdowns > 0 && <span>TDs: {player.career_touchdowns}</span>}
                  </div>
                </div>
                <div className="click-hint">Click to view detailed stats</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && selectedPlayer && (
        <div className="loading-message">Loading player statistics...</div>
      )}

      {playerStats && selectedPlayer && (
        <div className="player-details">
          <div className="player-header">
            <button onClick={() => setSelectedPlayer(null)} className="back-btn">
              ← Back to Search Results
            </button>
            <h3>{playerStats.player.name} - Detailed Statistics</h3>
            <div className="player-info">
              <span><strong>Position:</strong> {playerStats.player.position}</span>
              <span><strong>Team:</strong> {playerStats.player.team_name}</span>
            </div>
          </div>

          <div className="stats-sections">
            <div className="career-section">
              <h4>Career Statistics</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Passing Yards</span>
                  <span className="stat-value">{playerStats.player.career_passing_yards?.toLocaleString() || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Completion %</span>
                  <span className="stat-value">
                    {playerStats.player.career_passing_attempts > 0 
                      ? ((playerStats.player.career_passing_completions / playerStats.player.career_passing_attempts) * 100).toFixed(1) + '%'
                      : '0.0%'}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Passing TDs</span>
                  <span className="stat-value">{playerStats.player.career_passing_touchdowns || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Rushing Yards</span>
                  <span className="stat-value">{playerStats.player.career_rushing_yards?.toLocaleString() || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Yards per Rush</span>
                  <span className="stat-value">
                    {playerStats.player.career_rushing_attempts > 0 
                      ? (playerStats.player.career_rushing_yards / playerStats.player.career_rushing_attempts).toFixed(1)
                      : '0.0'}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Rushing TDs</span>
                  <span className="stat-value">{playerStats.player.career_rushing_touchdowns || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Receiving Yards</span>
                  <span className="stat-value">{playerStats.player.career_receiving_yards?.toLocaleString() || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Receptions</span>
                  <span className="stat-value">{playerStats.player.career_receptions || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Receiving TDs</span>
                  <span className="stat-value">{playerStats.player.career_receiving_touchdowns || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Touchdowns</span>
                  <span className="stat-value">{playerStats.player.career_touchdowns || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Tackles</span>
                  <span className="stat-value">{playerStats.player.career_tackles || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Sacks</span>
                  <span className="stat-value">{playerStats.player.career_sacks || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Interceptions</span>
                  <span className="stat-value">{playerStats.player.career_interceptions || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Fumbles</span>
                  <span className="stat-value">{playerStats.player.career_fumbles || 0}</span>
                </div>
              </div>
            </div>

            <div className="season-section">
              <h4>Current Season Statistics</h4>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-label">Games Played</span>
                  <span className="stat-value">{playerStats.season_stats.games_played}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Passing Yards</span>
                  <span className="stat-value">{playerStats.season_stats.total_passing_yards.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Rushing Yards</span>
                  <span className="stat-value">{playerStats.season_stats.total_rushing_yards.toLocaleString()}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Touchdowns</span>
                  <span className="stat-value">{playerStats.season_stats.total_touchdowns}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Passing/Game</span>
                  <span className="stat-value">{playerStats.season_stats.avg_passing_yards}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Rushing/Game</span>
                  <span className="stat-value">{playerStats.season_stats.avg_rushing_yards}</span>
                </div>
              </div>
            </div>
          </div>

          {playerStats.game_logs && playerStats.game_logs.length > 0 && (
            <div className="game-logs-section">
              <h4>Game-by-Game Performance</h4>
              <div className="game-logs-table">
                <table>
                  <thead>
                    <tr>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('game_date')}
                        title="Click to sort by date"
                      >
                        Date{getSortIcon('game_date')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('week')}
                        title="Click to sort by week"
                      >
                        Week{getSortIcon('week')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('opponent')}
                        title="Click to sort by opponent"
                      >
                        Opponent{getSortIcon('opponent')}
                      </th>
                      <th>Score</th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('passing_yards')}
                        title="Click to sort by passing yards"
                      >
                        Pass Yds{getSortIcon('passing_yards')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('passing_completions')}
                        title="Click to sort by completions"
                      >
                        Comp{getSortIcon('passing_completions')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('passing_attempts')}
                        title="Click to sort by attempts"
                      >
                        Att{getSortIcon('passing_attempts')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('rushing_yards')}
                        title="Click to sort by rushing yards"
                      >
                        Rush Yds{getSortIcon('rushing_yards')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('receiving_yards')}
                        title="Click to sort by receiving yards"
                      >
                        Rec Yds{getSortIcon('receiving_yards')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('receptions')}
                        title="Click to sort by receptions"
                      >
                        Rec{getSortIcon('receptions')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('touchdowns')}
                        title="Click to sort by total touchdowns"
                      >
                        Total TDs{getSortIcon('touchdowns')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('fumbles')}
                        title="Click to sort by fumbles"
                      >
                        Fum{getSortIcon('fumbles')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('interceptions')}
                        title="Click to sort by interceptions"
                      >
                        INT{getSortIcon('interceptions')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('tackles')}
                        title="Click to sort by tackles"
                      >
                        Tackles{getSortIcon('tackles')}
                      </th>
                      <th 
                        className="sortable-header" 
                        onClick={() => handleSort('sacks')}
                        title="Click to sort by sacks"
                      >
                        Sacks{getSortIcon('sacks')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortGameLogs(playerStats.game_logs).map((game, index) => (
                      <tr key={`${game.game_id}-${index}`}>
                        <td>{game.game_date ? new Date(game.game_date).toLocaleDateString() : 'N/A'}</td>
                        <td>{game.week}</td>
                        <td>{game.opponent}</td>
                        <td>{game.home_score}-{game.away_score}</td>
                        <td className="stat-cell">{game.passing_yards}</td>
                        <td className="stat-cell">{game.passing_completions || 0}</td>
                        <td className="stat-cell">{game.passing_attempts || 0}</td>
                        <td className="stat-cell">{game.rushing_yards}</td>
                        <td className="stat-cell">{game.receiving_yards}</td>
                        <td className="stat-cell">{game.receptions || 0}</td>
                        <td className="stat-cell highlight">{game.touchdowns}</td>
                        <td className="stat-cell">{game.fumbles || 0}</td>
                        <td className="stat-cell">{game.interceptions}</td>
                        <td className="stat-cell">{game.tackles}</td>
                        <td className="stat-cell">{game.sacks}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PlayerStats;