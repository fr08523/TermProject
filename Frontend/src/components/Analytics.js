import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Analytics.css';

function Analytics() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [careerLeaders, setCareerLeaders] = useState(null);
  const [topPerformers, setTopPerformers] = useState(null);
  const [teamPerformance, setTeamPerformance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('passing_yards');
  const [selectedPosition, setSelectedPosition] = useState('');

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchAnalytics = React.useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      // Fetch career leaders with sorting
      const careerLeadersRes = await axios.get(
        `${apiUrl}/analytics/career-leaders?sort_by=${sortBy}&limit=10${selectedPosition ? `&position=${selectedPosition}` : ''}`,
        { headers: getAuthHeaders() }
      );

      // Fetch top performers (season stats)
      const topPerformersRes = await axios.get(
        `${apiUrl}/analytics/top-performers?limit=5`,
        { headers: getAuthHeaders() }
      );

      // Fetch team performance
      const teamPerformanceRes = await axios.get(
        `${apiUrl}/analytics/team-performance`,
        { headers: getAuthHeaders() }
      );

      setCareerLeaders(careerLeadersRes.data);
      setTopPerformers(topPerformersRes.data);
      setTeamPerformance(teamPerformanceRes.data);

      // Also fetch basic analytics for overview
      const [leaguesRes, teamsRes, playersRes, gamesRes] = await Promise.all([
        axios.get(`${apiUrl}/api/leagues`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/teams`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/players`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/games`, { headers: getAuthHeaders() })
      ]);

      setAnalyticsData({
        totalGames: gamesRes.data.length,
        totalPlayers: playersRes.data.length,
        totalTeams: teamsRes.data.length,
        totalLeagues: leaguesRes.data.length
      });
      
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to fetch analytics data. Please ensure you are logged in.');
    } finally {
      setLoading(false);
    }
  }, [apiUrl, sortBy, selectedPosition]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
  };

  const handlePositionFilter = (position) => {
    setSelectedPosition(position);
  };

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  if (error) {
    return <div className="analytics-error">{error}</div>;
  }

  if (!analyticsData) {
    return <div className="analytics-empty">No analytics data available</div>;
  }

  return (
    <div className="analytics-container">
      <h2>Sports Analytics Dashboard</h2>
      
      {/* Overall Statistics */}
      <div className="overview-section">
        <h3>System Overview</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Total Games</h4>
            <p className="stat-number">{analyticsData.totalGames}</p>
          </div>
          <div className="stat-card">
            <h4>Total Teams</h4>
            <p className="stat-number">{analyticsData.totalTeams}</p>
          </div>
          <div className="stat-card">
            <h4>Total Players</h4>
            <p className="stat-number">{analyticsData.totalPlayers}</p>
          </div>
          <div className="stat-card">
            <h4>Total Leagues</h4>
            <p className="stat-number">{analyticsData.totalLeagues}</p>
          </div>
        </div>
      </div>

      {/* Career Leaders Section */}
      <div className="career-leaders-section">
        <h3>Career Leaders</h3>
        <div className="controls">
          <div className="sort-controls">
            <label>Sort by: </label>
            <select value={sortBy} onChange={(e) => handleSortChange(e.target.value)}>
              <option value="passing_yards">Passing Yards</option>
              <option value="passing_touchdowns">Passing TDs</option>
              <option value="rushing_yards">Rushing Yards</option>
              <option value="rushing_touchdowns">Rushing TDs</option>
              <option value="receiving_yards">Receiving Yards</option>
              <option value="receiving_touchdowns">Receiving TDs</option>
              <option value="receptions">Receptions</option>
              <option value="touchdowns">Total Touchdowns</option>
              <option value="tackles">Tackles</option>
              <option value="sacks">Sacks</option>
              <option value="interceptions">Interceptions</option>
              <option value="passes_defensed">Passes Defensed</option>
              <option value="fumbles">Fumbles</option>
            </select>
          </div>
          <div className="position-filter">
            <label>Position: </label>
            <select value={selectedPosition} onChange={(e) => handlePositionFilter(e.target.value)}>
              <option value="">All Positions</option>
              <option value="QB">Quarterback (QB)</option>
              <option value="RB">Running Back (RB)</option>
              <option value="WR">Wide Receiver (WR)</option>
              <option value="TE">Tight End (TE)</option>
              <option value="K">Kicker (K)</option>
              <option value="LB">Linebacker (LB)</option>
              <option value="CB">Cornerback (CB)</option>
              <option value="S">Safety (S)</option>
              <option value="DE">Defensive End (DE)</option>
              <option value="DT">Defensive Tackle (DT)</option>
            </select>
          </div>
        </div>
        {careerLeaders && careerLeaders.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Player</th>
                  <th>Position</th>
                  <th>Team</th>
                  <th>Pass Yds</th>
                  <th>Comp %</th>
                  <th>Pass TDs</th>
                  <th>Rush Yds</th>
                  <th>Rush TDs</th>
                  <th>Rec Yds</th>
                  <th>Rec TDs</th>
                  <th>Total TDs</th>
                  <th>Tackles</th>
                  <th>Sacks</th>
                  <th>INTs</th>
                  <th className="highlight">{sortBy.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</th>
                </tr>
              </thead>
              <tbody>
                {careerLeaders.map((player, index) => (
                  <tr key={player.player_id}>
                    <td>{index + 1}</td>
                    <td>{player.name}</td>
                    <td>{player.position}</td>
                    <td>{player.team}</td>
                    <td>{player.career_passing_yards.toLocaleString()}</td>
                    <td>{player.completion_percentage}%</td>
                    <td>{player.career_passing_touchdowns}</td>
                    <td>{player.career_rushing_yards.toLocaleString()}</td>
                    <td>{player.career_rushing_touchdowns}</td>
                    <td>{player.career_receiving_yards.toLocaleString()}</td>
                    <td>{player.career_receiving_touchdowns}</td>
                    <td>{player.career_touchdowns}</td>
                    <td>{player.career_tackles}</td>
                    <td>{player.career_sacks}</td>
                    <td>{player.career_interceptions}</td>
                    <td className="highlight">{player.sorted_value.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No career leaders data available</p>
        )}
      </div>

      {/* Season Top Performers */}
      {topPerformers && (
        <div className="top-performers-section">
          <h3>Season Top Performers</h3>
          <div className="performers-grid">
            <div className="performer-category">
              <h4>Passing Leaders</h4>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Team</th>
                      <th>Total Yards</th>
                      <th>Games</th>
                      <th>Avg/Game</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topPerformers.passing_leaders.map((player, index) => (
                      <tr key={index}>
                        <td>{player.name} ({player.position})</td>
                        <td>{player.team}</td>
                        <td>{player.total_yards.toLocaleString()}</td>
                        <td>{player.games_played}</td>
                        <td>{player.avg_per_game}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="performer-category">
              <h4>Rushing Leaders</h4>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Team</th>
                      <th>Total Yards</th>
                      <th>Games</th>
                      <th>Avg/Game</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topPerformers.rushing_leaders.map((player, index) => (
                      <tr key={index}>
                        <td>{player.name} ({player.position})</td>
                        <td>{player.team}</td>
                        <td>{player.total_yards.toLocaleString()}</td>
                        <td>{player.games_played}</td>
                        <td>{player.avg_per_game}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="performer-category">
              <h4>Receiving Leaders</h4>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Team</th>
                      <th>Total Yards</th>
                      <th>Games</th>
                      <th>Avg/Game</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topPerformers.receiving_leaders.map((player, index) => (
                      <tr key={index}>
                        <td>{player.name} ({player.position})</td>
                        <td>{player.team}</td>
                        <td>{player.total_yards.toLocaleString()}</td>
                        <td>{player.games_played}</td>
                        <td>{player.avg_per_game}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Team Performance */}
      {teamPerformance && teamPerformance.length > 0 && (
        <div className="team-section">
          <h3>Team Performance</h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Team</th>
                  <th>League</th>
                  <th>Games</th>
                  <th>Wins</th>
                  <th>Losses</th>
                  <th>Win %</th>
                  <th>Avg Points</th>
                  <th>Avg Attendance</th>
                </tr>
              </thead>
              <tbody>
                {teamPerformance
                  .sort((a, b) => b.win_percentage - a.win_percentage)
                  .map(team => (
                  <tr key={team.team_id}>
                    <td>{team.team_name}</td>
                    <td>{team.league_name}</td>
                    <td>{team.games_played}</td>
                    <td>{team.wins}</td>
                    <td>{team.losses}</td>
                    <td>{team.win_percentage}%</td>
                    <td>{team.avg_points_scored}</td>
                    <td>{Number(team.avg_attendance).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="refresh-section">
        <button onClick={fetchAnalytics} className="refresh-btn">
          Refresh Analytics
        </button>
      </div>
    </div>
  );
}

export default Analytics;