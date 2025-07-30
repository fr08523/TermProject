import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Analytics.css';

function Analytics() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchAnalytics = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Fetch multiple datasets to demonstrate complex queries
      const [leaguesRes, teamsRes, playersRes, gamesRes] = await Promise.all([
        axios.get(`${apiUrl}/api/leagues`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/teams`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/players`, { headers: getAuthHeaders() }),
        axios.get(`${apiUrl}/api/games`, { headers: getAuthHeaders() })
      ]);

      // Process data to create analytics
      const leagues = leaguesRes.data;
      const teams = teamsRes.data;
      const players = playersRes.data;
      const games = gamesRes.data;

      // Calculate team statistics
      const teamStats = teams.map(team => {
        const homeGames = games.filter(game => game.home_team_id === team.id);
        const awayGames = games.filter(game => game.away_team_id === team.id);
        const allGames = [...homeGames, ...awayGames];
        
        const wins = homeGames.filter(game => game.home_score > game.away_score).length +
                    awayGames.filter(game => game.away_score > game.home_score).length;
        
        const totalGames = allGames.length;
        const winPercentage = totalGames > 0 ? ((wins / totalGames) * 100).toFixed(1) : 0;
        
        const totalHomeScore = homeGames.reduce((sum, game) => sum + (game.home_score || 0), 0);
        const totalAwayScore = awayGames.reduce((sum, game) => sum + (game.away_score || 0), 0);
        const avgPointsScored = totalGames > 0 ? ((totalHomeScore + totalAwayScore) / totalGames).toFixed(1) : 0;

        return {
          ...team,
          gamesPlayed: totalGames,
          wins: wins,
          losses: totalGames - wins,
          winPercentage: winPercentage,
          avgPointsScored: avgPointsScored
        };
      });

      // Calculate league statistics
      const leagueStats = leagues.map(league => {
        const leagueTeams = teams.filter(team => team.league_id === league.id);
        const leaguePlayers = players.filter(player => 
          leagueTeams.some(team => team.id === player.team_id)
        );
        const leagueGames = games.filter(game => game.league_id === league.id);
        
        const totalAttendance = leagueGames.reduce((sum, game) => sum + (game.attendance || 0), 0);
        const avgAttendance = leagueGames.length > 0 ? (totalAttendance / leagueGames.length).toFixed(0) : 0;

        return {
          ...league,
          teamCount: leagueTeams.length,
          playerCount: leaguePlayers.length,
          gameCount: leagueGames.length,
          totalAttendance: totalAttendance,
          avgAttendance: avgAttendance
        };
      });

      setAnalyticsData({
        teamStats: teamStats,
        leagueStats: leagueStats,
        totalGames: games.length,
        totalPlayers: players.length,
        totalTeams: teams.length
      });
      
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError('Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

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
        </div>
      </div>

      {/* League Statistics */}
      <div className="league-section">
        <h3>League Statistics</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>League</th>
                <th>Level</th>
                <th>Teams</th>
                <th>Players</th>
                <th>Games</th>
                <th>Avg Attendance</th>
              </tr>
            </thead>
            <tbody>
              {analyticsData.leagueStats.map(league => (
                <tr key={league.id}>
                  <td>{league.name}</td>
                  <td>{league.level}</td>
                  <td>{league.teamCount}</td>
                  <td>{league.playerCount}</td>
                  <td>{league.gameCount}</td>
                  <td>{league.avgAttendance ? Number(league.avgAttendance).toLocaleString() : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Team Performance */}
      <div className="team-section">
        <h3>Team Performance</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Team</th>
                <th>Home City</th>
                <th>Games</th>
                <th>Wins</th>
                <th>Losses</th>
                <th>Win %</th>
                <th>Avg Points</th>
              </tr>
            </thead>
            <tbody>
              {analyticsData.teamStats
                .sort((a, b) => parseFloat(b.winPercentage) - parseFloat(a.winPercentage))
                .map(team => (
                <tr key={team.id}>
                  <td>{team.name}</td>
                  <td>{team.home_city}</td>
                  <td>{team.gamesPlayed}</td>
                  <td>{team.wins}</td>
                  <td>{team.losses}</td>
                  <td>{team.winPercentage}%</td>
                  <td>{team.avgPointsScored}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="refresh-section">
        <button onClick={fetchAnalytics} className="refresh-btn">
          Refresh Analytics
        </button>
      </div>
    </div>
  );
}

export default Analytics;