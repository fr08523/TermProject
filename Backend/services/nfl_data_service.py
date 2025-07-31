"""
NFL Data Management Service
Handles database operations for NFL data
"""

from app import db
from app.models.models import NFLPlayer, NFLPlayerSeasonStats, NFLPlayerCareerStats, NFLTeam
from services.nfl_data_scraper import NFLDataScraper
from typing import List, Dict, Optional
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class NFLDataService:
    """Service for managing NFL data operations"""
    
    def __init__(self):
        self.scraper = NFLDataScraper()
        
    def sync_nfl_teams(self) -> int:
        """Sync NFL teams data from Pro Football Reference"""
        teams_data = self.scraper.get_nfl_teams()
        count = 0
        
        for team_data in teams_data:
            existing_team = NFLTeam.query.filter_by(abbreviation=team_data['abbreviation']).first()
            
            if not existing_team:
                team = NFLTeam(
                    name=team_data['name'],
                    abbreviation=team_data['abbreviation'],
                    city=team_data.get('city', ''),
                )
                db.session.add(team)
                count += 1
                
        try:
            db.session.commit()
            logger.info(f"Successfully synced {count} NFL teams")
            return count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing NFL teams: {e}")
            return 0
            
    def sync_nfl_players(self, limit: int = 50) -> int:
        """Sync NFL players data from Pro Football Reference"""
        players_data = self.scraper.get_active_players_list()
        count = 0
        
        for player_data in players_data[:limit]:  # Limit for initial sync
            if not player_data.get('pfr_id'):
                continue
                
            existing_player = NFLPlayer.query.filter_by(pfr_id=player_data['pfr_id']).first()
            
            if not existing_player:
                # Parse height (e.g., "6-2" -> 74 inches)
                height_inches = self._parse_height(player_data.get('height', ''))
                
                player = NFLPlayer(
                    pfr_id=player_data['pfr_id'],
                    name=player_data['name'],
                    position=player_data.get('position', ''),
                    current_team=player_data.get('current_team', ''),
                    height_inches=height_inches,
                    weight_lbs=player_data.get('weight'),
                    college=player_data.get('college', ''),
                    active=True
                )
                db.session.add(player)
                count += 1
                
        try:
            db.session.commit()
            logger.info(f"Successfully synced {count} NFL players")
            return count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing NFL players: {e}")
            return 0
            
    def sync_player_stats(self, pfr_id: str) -> int:
        """Sync statistics for a specific player"""
        player = NFLPlayer.query.filter_by(pfr_id=pfr_id).first()
        if not player:
            logger.error(f"Player with PFR ID {pfr_id} not found")
            return 0
            
        stats_data = self.scraper.get_player_season_stats(pfr_id)
        count = 0
        
        for stat_data in stats_data:
            existing_stat = NFLPlayerSeasonStats.query.filter_by(
                player_id=player.id,
                season_year=stat_data['season_year']
            ).first()
            
            if not existing_stat:
                stat = NFLPlayerSeasonStats(
                    player_id=player.id,
                    season_year=stat_data['season_year'],
                    team=stat_data.get('team', ''),
                    position=stat_data.get('position', ''),
                    age=stat_data.get('age'),
                    games_played=stat_data.get('games_played', 0),
                    games_started=stat_data.get('games_started', 0),
                    pass_completions=stat_data.get('pass_completions', 0),
                    pass_attempts=stat_data.get('pass_attempts', 0),
                    pass_yards=stat_data.get('pass_yards', 0),
                    pass_touchdowns=stat_data.get('pass_touchdowns', 0),
                    interceptions=stat_data.get('interceptions', 0),
                    qb_rating=stat_data.get('qb_rating', 0.0),
                    rush_attempts=stat_data.get('rush_attempts', 0),
                    rush_yards=stat_data.get('rush_yards', 0),
                    rush_touchdowns=stat_data.get('rush_touchdowns', 0),
                    receptions=stat_data.get('receptions', 0),
                    receiving_yards=stat_data.get('receiving_yards', 0),
                    receiving_touchdowns=stat_data.get('receiving_touchdowns', 0),
                    tackles_total=stat_data.get('tackles_total', 0),
                    tackles_solo=stat_data.get('tackles_solo', 0),
                    tackles_assists=stat_data.get('tackles_assists', 0),
                    sacks=stat_data.get('sacks', 0.0),
                    def_interceptions=stat_data.get('def_interceptions', 0),
                    forced_fumbles=stat_data.get('forced_fumbles', 0),
                    fumble_recoveries=stat_data.get('fumble_recoveries', 0),
                )
                db.session.add(stat)
                count += 1
                
        try:
            db.session.commit()
            # Update career stats
            self._update_career_stats(player.id)
            logger.info(f"Successfully synced {count} season stats for {pfr_id}")
            return count
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing player stats for {pfr_id}: {e}")
            return 0
            
    def _update_career_stats(self, player_id: int) -> None:
        """Update career statistics for a player"""
        season_stats = NFLPlayerSeasonStats.query.filter_by(player_id=player_id).all()
        
        if not season_stats:
            return
            
        # Calculate career totals
        total_seasons = len(season_stats)
        total_games = sum(stat.games_played for stat in season_stats)
        career_pass_yards = sum(stat.pass_yards for stat in season_stats)
        career_pass_tds = sum(stat.pass_touchdowns for stat in season_stats)
        career_rush_yards = sum(stat.rush_yards for stat in season_stats)
        career_rush_tds = sum(stat.rush_touchdowns for stat in season_stats)
        career_rec_yards = sum(stat.receiving_yards for stat in season_stats)
        career_rec_tds = sum(stat.receiving_touchdowns for stat in season_stats)
        career_tackles = sum(stat.tackles_total for stat in season_stats)
        career_sacks = sum(stat.sacks for stat in season_stats)
        career_interceptions = sum(stat.def_interceptions for stat in season_stats)
        
        # Calculate averages
        avg_yards_per_game = (career_pass_yards + career_rush_yards + career_rec_yards) / total_games if total_games > 0 else 0
        avg_tds_per_season = (career_pass_tds + career_rush_tds + career_rec_tds) / total_seasons if total_seasons > 0 else 0
        
        # Update or create career stats
        career_stats = NFLPlayerCareerStats.query.filter_by(player_id=player_id).first()
        
        if career_stats:
            career_stats.total_seasons = total_seasons
            career_stats.total_games = total_games
            career_stats.career_pass_yards = career_pass_yards
            career_stats.career_pass_tds = career_pass_tds
            career_stats.career_rush_yards = career_rush_yards
            career_stats.career_rush_tds = career_rush_tds
            career_stats.career_rec_yards = career_rec_yards
            career_stats.career_rec_tds = career_rec_tds
            career_stats.career_tackles = career_tackles
            career_stats.career_sacks = career_sacks
            career_stats.career_interceptions = career_interceptions
            career_stats.avg_yards_per_game = avg_yards_per_game
            career_stats.avg_touchdowns_per_season = avg_tds_per_season
            career_stats.updated_at = datetime.utcnow()
        else:
            career_stats = NFLPlayerCareerStats(
                player_id=player_id,
                total_seasons=total_seasons,
                total_games=total_games,
                career_pass_yards=career_pass_yards,
                career_pass_tds=career_pass_tds,
                career_rush_yards=career_rush_yards,
                career_rush_tds=career_rush_tds,
                career_rec_yards=career_rec_yards,
                career_rec_tds=career_rec_tds,
                career_tackles=career_tackles,
                career_sacks=career_sacks,
                career_interceptions=career_interceptions,
                avg_yards_per_game=avg_yards_per_game,
                avg_touchdowns_per_season=avg_tds_per_season
            )
            db.session.add(career_stats)
            
        db.session.commit()
        
    def _parse_height(self, height_str: str) -> Optional[int]:
        """Parse height string (e.g., '6-2') to inches"""
        if not height_str or '-' not in height_str:
            return None
            
        try:
            feet, inches = height_str.split('-')
            return int(feet) * 12 + int(inches)
        except (ValueError, IndexError):
            return None
            
    def get_player_predictions(self, pfr_id: str) -> Dict:
        """Generate simple predictions for a player's next season performance"""
        player = NFLPlayer.query.filter_by(pfr_id=pfr_id).first()
        if not player:
            return {}
            
        # Get last 3 seasons of stats for trend analysis
        recent_stats = NFLPlayerSeasonStats.query.filter_by(player_id=player.id)\
                                                .order_by(NFLPlayerSeasonStats.season_year.desc())\
                                                .limit(3).all()
                                                
        if len(recent_stats) < 2:
            return {"error": "Insufficient data for prediction"}
            
        # Simple trend-based prediction
        predictions = {}
        
        if recent_stats[0].pass_yards > 0:
            # Quarterback predictions
            recent_yards = [stat.pass_yards for stat in recent_stats]
            recent_tds = [stat.pass_touchdowns for stat in recent_stats]
            
            # Simple linear trend
            yard_trend = (recent_yards[0] - recent_yards[-1]) / len(recent_yards)
            td_trend = (recent_tds[0] - recent_tds[-1]) / len(recent_tds)
            
            predictions.update({
                'predicted_pass_yards': max(0, recent_yards[0] + yard_trend),
                'predicted_pass_tds': max(0, recent_tds[0] + td_trend),
                'confidence': 'low',
                'based_on_seasons': len(recent_stats)
            })
            
        elif recent_stats[0].rush_yards > 0:
            # Running back predictions
            recent_yards = [stat.rush_yards for stat in recent_stats]
            recent_tds = [stat.rush_touchdowns for stat in recent_stats]
            
            yard_trend = (recent_yards[0] - recent_yards[-1]) / len(recent_yards)
            td_trend = (recent_tds[0] - recent_tds[-1]) / len(recent_tds)
            
            predictions.update({
                'predicted_rush_yards': max(0, recent_yards[0] + yard_trend),
                'predicted_rush_tds': max(0, recent_tds[0] + td_trend),
                'confidence': 'low',
                'based_on_seasons': len(recent_stats)
            })
            
        elif recent_stats[0].receiving_yards > 0:
            # Receiver predictions
            recent_yards = [stat.receiving_yards for stat in recent_stats]
            recent_tds = [stat.receiving_touchdowns for stat in recent_stats]
            
            yard_trend = (recent_yards[0] - recent_yards[-1]) / len(recent_yards)
            td_trend = (recent_tds[0] - recent_tds[-1]) / len(recent_tds)
            
            predictions.update({
                'predicted_receiving_yards': max(0, recent_yards[0] + yard_trend),
                'predicted_receiving_tds': max(0, recent_tds[0] + td_trend),
                'confidence': 'low',
                'based_on_seasons': len(recent_stats)
            })
            
        return predictions
        
    def search_players(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for NFL players by name"""
        players = NFLPlayer.query.filter(
            NFLPlayer.name.ilike(f"%{query}%")
        ).limit(limit).all()
        
        return [
            {
                'id': player.id,
                'pfr_id': player.pfr_id,
                'name': player.name,
                'position': player.position,
                'current_team': player.current_team,
                'active': player.active
            }
            for player in players
        ]
        
    def get_player_detail(self, pfr_id: str) -> Optional[Dict]:
        """Get detailed information for a player"""
        player = NFLPlayer.query.filter_by(pfr_id=pfr_id).first()
        if not player:
            return None
            
        # Get season stats
        season_stats = NFLPlayerSeasonStats.query.filter_by(player_id=player.id)\
                                                 .order_by(NFLPlayerSeasonStats.season_year.desc())\
                                                 .all()
                                                 
        # Get career stats
        career_stats = NFLPlayerCareerStats.query.filter_by(player_id=player.id).first()
        
        return {
            'player': {
                'id': player.id,
                'pfr_id': player.pfr_id,
                'name': player.name,
                'position': player.position,
                'current_team': player.current_team,
                'height_inches': player.height_inches,
                'weight_lbs': player.weight_lbs,
                'college': player.college,
                'active': player.active
            },
            'season_stats': [
                {
                    'season_year': stat.season_year,
                    'team': stat.team,
                    'games_played': stat.games_played,
                    'games_started': stat.games_started,
                    'pass_yards': stat.pass_yards,
                    'pass_touchdowns': stat.pass_touchdowns,
                    'rush_yards': stat.rush_yards,
                    'rush_touchdowns': stat.rush_touchdowns,
                    'receiving_yards': stat.receiving_yards,
                    'receiving_touchdowns': stat.receiving_touchdowns,
                    'tackles_total': stat.tackles_total,
                    'sacks': stat.sacks,
                    'def_interceptions': stat.def_interceptions
                }
                for stat in season_stats
            ],
            'career_stats': {
                'total_seasons': career_stats.total_seasons if career_stats else 0,
                'total_games': career_stats.total_games if career_stats else 0,
                'career_pass_yards': career_stats.career_pass_yards if career_stats else 0,
                'career_rush_yards': career_stats.career_rush_yards if career_stats else 0,
                'career_rec_yards': career_stats.career_rec_yards if career_stats else 0,
                'avg_yards_per_game': career_stats.avg_yards_per_game if career_stats else 0
            } if career_stats else {}
        }