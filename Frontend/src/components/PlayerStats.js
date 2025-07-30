import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PlayerStats.css';

function PlayerStats() {
  const [playerName, setPlayerName] = useState('');
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerStats, setPlayerStats] = useState(null);
  const [gameStats, setGameStats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchPerformed, setSearchPerformed] = useState(false);

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

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
      setGameStats([]);
      
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
      const [playerStatsRes, gameStatsRes] = await Promise.all([
        axios.get(`${apiUrl}/api/players/${player.id}/stats`),
        axios.get(`${apiUrl}/api/stats?player_name=${encodeURIComponent(player.name)}`)
      ]);
      
      setPlayerStats(playerStatsRes.data);
      setGameStats(gameStatsRes.data);
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
    setGameStats([]);
    setSearchPerformed(false);
    setError('');
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
                  <span className="stat-label">Rushing Yards</span>
                  <span className="stat-value">{playerStats.player.career_rushing_yards?.toLocaleString() || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Receiving Yards</span>
                  <span className="stat-value">{playerStats.player.career_receiving_yards?.toLocaleString() || 0}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Career Touchdowns</span>
                  <span className="stat-value">{playerStats.player.career_touchdowns || 0}</span>
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
                      <th>Date</th>
                      <th>Week</th>
                      <th>Opponent</th>
                      <th>Score</th>
                      <th>Pass Yds</th>
                      <th>Rush Yds</th>
                      <th>Rec Yds</th>
                      <th>TDs</th>
                      <th>INT</th>
                    </tr>
                  </thead>
                  <tbody>
                    {playerStats.game_logs.map((game, index) => (
                      <tr key={`${game.game_id}-${index}`}>
                        <td>{game.game_date ? new Date(game.game_date).toLocaleDateString() : 'N/A'}</td>
                        <td>{game.week}</td>
                        <td>{game.opponent}</td>
                        <td>{game.home_score}-{game.away_score}</td>
                        <td>{game.passing_yards}</td>
                        <td>{game.rushing_yards}</td>
                        <td>{game.receiving_yards}</td>
                        <td>{game.touchdowns}</td>
                        <td>{game.interceptions}</td>
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