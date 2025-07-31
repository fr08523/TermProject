import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './NFLData.css';

const NFLData = () => {
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerDetail, setPlayerDetail] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState(null);

  const API_BASE = 'http://127.0.0.1:5000';

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE}/nfl/stats/summary`);
      if (response.data.success) {
        setSummary(response.data.summary);
      }
    } catch (err) {
      console.error('Error loading summary:', err);
    }
  };

  const searchPlayers = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a player name to search');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE}/nfl/players/search?q=${encodeURIComponent(searchQuery)}`);
      if (response.data.success) {
        setPlayers(response.data.players);
        if (response.data.players.length === 0) {
          setError('No players found matching your search');
        }
      } else {
        setError(response.data.error || 'Failed to search players');
      }
    } catch (err) {
      setError('Error searching players. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadPlayerDetail = async (pfrId) => {
    setLoading(true);
    setError('');
    
    try {
      const [detailResponse, predictionResponse] = await Promise.all([
        axios.get(`${API_BASE}/nfl/players/${pfrId}`),
        axios.get(`${API_BASE}/nfl/players/${pfrId}/predictions`)
      ]);

      if (detailResponse.data.success) {
        setPlayerDetail(detailResponse.data.data);
      }

      if (predictionResponse.data.success) {
        setPredictions(predictionResponse.data.predictions);
      }
    } catch (err) {
      setError('Error loading player details');
      console.error('Detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayerSelect = (player) => {
    setSelectedPlayer(player);
    setPlayerDetail(null);
    setPredictions(null);
    loadPlayerDetail(player.pfr_id);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchPlayers();
    }
  };

  return (
    <div className="nfl-data-container">
      <h1>NFL Player Statistics & Predictions</h1>
      <p className="description">
        Search for NFL players to view their historical statistics and get performance predictions for the upcoming season.
        Data is sourced from Pro Football Reference.
      </p>

      {/* Summary Stats */}
      {summary && (
        <div className="summary-section">
          <h2>Database Summary</h2>
          <div className="summary-grid">
            <div className="summary-card">
              <h3>Total Players</h3>
              <p className="summary-number">{summary.total_players}</p>
            </div>
            <div className="summary-card">
              <h3>Active Players</h3>
              <p className="summary-number">{summary.active_players}</p>
            </div>
            <div className="summary-card">
              <h3>Teams</h3>
              <p className="summary-number">{summary.total_teams}</p>
            </div>
            <div className="summary-card">
              <h3>Season Records</h3>
              <p className="summary-number">{summary.total_season_records}</p>
            </div>
          </div>

          {summary.top_passers && summary.top_passers.length > 0 && (
            <div className="top-passers">
              <h3>Top Passing Performances</h3>
              <div className="top-passers-list">
                {summary.top_passers.map((passer, index) => (
                  <div key={index} className="top-passer-item">
                    <span className="player-name">{passer.player_name}</span>
                    <span className="season-year">({passer.season_year})</span>
                    <span className="yards">{passer.pass_yards.toLocaleString()} yards</span>
                    <span className="team">{passer.team}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Search Section */}
      <div className="search-section">
        <h2>Search Players</h2>
        <div className="search-controls">
          <input
            type="text"
            placeholder="Enter player name (e.g., Mahomes, Allen)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            className="search-input"
          />
          <button onClick={searchPlayers} disabled={loading} className="search-button">
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        
        {error && <div className="error-message">{error}</div>}
      </div>

      {/* Search Results */}
      {players.length > 0 && (
        <div className="search-results">
          <h3>Search Results</h3>
          <div className="players-grid">
            {players.map((player) => (
              <div 
                key={player.id} 
                className={`player-card ${selectedPlayer?.id === player.id ? 'selected' : ''}`}
                onClick={() => handlePlayerSelect(player)}
              >
                <h4>{player.name}</h4>
                <p className="position">{player.position}</p>
                <p className="team">{player.current_team}</p>
                <span className="status">{player.active ? 'Active' : 'Inactive'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Player Details */}
      {selectedPlayer && playerDetail && (
        <div className="player-details">
          <h2>{playerDetail.player.name}</h2>
          
          <div className="player-info">
            <div className="player-basic-info">
              <h3>Player Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="label">Position:</span>
                  <span className="value">{playerDetail.player.position}</span>
                </div>
                <div className="info-item">
                  <span className="label">Team:</span>
                  <span className="value">{playerDetail.player.current_team}</span>
                </div>
                <div className="info-item">
                  <span className="label">Height:</span>
                  <span className="value">
                    {playerDetail.player.height_inches ? 
                      `${Math.floor(playerDetail.player.height_inches / 12)}'${playerDetail.player.height_inches % 12}"` : 
                      'N/A'}
                  </span>
                </div>
                <div className="info-item">
                  <span className="label">Weight:</span>
                  <span className="value">{playerDetail.player.weight_lbs || 'N/A'} lbs</span>
                </div>
                <div className="info-item">
                  <span className="label">College:</span>
                  <span className="value">{playerDetail.player.college || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Career Stats */}
            {playerDetail.career_stats && Object.keys(playerDetail.career_stats).length > 0 && (
              <div className="career-stats">
                <h3>Career Statistics</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">Total Seasons:</span>
                    <span className="stat-value">{playerDetail.career_stats.total_seasons}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Total Games:</span>
                    <span className="stat-value">{playerDetail.career_stats.total_games}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Career Passing Yards:</span>
                    <span className="stat-value">{playerDetail.career_stats.career_pass_yards?.toLocaleString() || 0}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Career Rushing Yards:</span>
                    <span className="stat-value">{playerDetail.career_stats.career_rush_yards?.toLocaleString() || 0}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Avg Yards/Game:</span>
                    <span className="stat-value">{playerDetail.career_stats.avg_yards_per_game?.toFixed(1) || 0}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Season by Season Stats */}
          {playerDetail.season_stats && playerDetail.season_stats.length > 0 && (
            <div className="season-stats">
              <h3>Season-by-Season Statistics</h3>
              <div className="stats-table-container">
                <table className="stats-table">
                  <thead>
                    <tr>
                      <th>Season</th>
                      <th>Team</th>
                      <th>GP</th>
                      <th>GS</th>
                      <th>Pass Yds</th>
                      <th>Pass TDs</th>
                      <th>Rush Yds</th>
                      <th>Rush TDs</th>
                      <th>Rec Yds</th>
                      <th>Rec TDs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {playerDetail.season_stats.map((season, index) => (
                      <tr key={index}>
                        <td>{season.season_year}</td>
                        <td>{season.team}</td>
                        <td>{season.games_played}</td>
                        <td>{season.games_started}</td>
                        <td>{season.pass_yards?.toLocaleString() || 0}</td>
                        <td>{season.pass_touchdowns || 0}</td>
                        <td>{season.rush_yards?.toLocaleString() || 0}</td>
                        <td>{season.rush_touchdowns || 0}</td>
                        <td>{season.receiving_yards?.toLocaleString() || 0}</td>
                        <td>{season.receiving_touchdowns || 0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Predictions */}
          {predictions && (
            <div className="predictions">
              <h3>2024 Season Predictions</h3>
              <div className="predictions-disclaimer">
                <strong>Disclaimer:</strong> {predictions.disclaimer || 'Predictions are estimates based on historical data and should not be used for gambling.'}
              </div>
              <div className="predictions-content">
                <div className="prediction-stats">
                  {predictions.predicted_pass_yards && (
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Passing Yards:</span>
                      <span className="prediction-value">{Math.round(predictions.predicted_pass_yards).toLocaleString()}</span>
                    </div>
                  )}
                  {predictions.predicted_pass_tds && (
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Passing TDs:</span>
                      <span className="prediction-value">{Math.round(predictions.predicted_pass_tds)}</span>
                    </div>
                  )}
                  {predictions.predicted_rush_yards && (
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Rushing Yards:</span>
                      <span className="prediction-value">{Math.round(predictions.predicted_rush_yards).toLocaleString()}</span>
                    </div>
                  )}
                  {predictions.predicted_rush_tds && (
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Rushing TDs:</span>
                      <span className="prediction-value">{Math.round(predictions.predicted_rush_tds)}</span>
                    </div>
                  )}
                  {predictions.predicted_receiving_yards && (
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Receiving Yards:</span>
                      <span className="prediction-value">{Math.round(predictions.predicted_receiving_yards).toLocaleString()}</span>
                    </div>
                  )}
                  {predictions.predicted_receiving_tds && (
                    <div className="prediction-item">
                      <span className="prediction-label">Predicted Receiving TDs:</span>
                      <span className="prediction-value">{Math.round(predictions.predicted_receiving_tds)}</span>
                    </div>
                  )}
                  <div className="prediction-item">
                    <span className="prediction-label">Confidence Level:</span>
                    <span className="prediction-value">{predictions.confidence || 'Low'}</span>
                  </div>
                  <div className="prediction-item">
                    <span className="prediction-label">Based on Seasons:</span>
                    <span className="prediction-value">{predictions.based_on_seasons}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NFLData;