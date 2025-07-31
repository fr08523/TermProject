"""
Sample NFL Data Populator
Creates sample NFL data for testing and demonstration
"""

from app import create_app, db
from app.models.models import NFLPlayer, NFLPlayerSeasonStats, NFLPlayerCareerStats, NFLTeam
from datetime import datetime, date

def populate_sample_nfl_data():
    """Populate the database with sample NFL data"""
    
    app = create_app()
    with app.app_context():
        # Create sample NFL teams
        teams_data = [
            {"name": "Kansas City Chiefs", "abbreviation": "KAN", "city": "Kansas City", "conference": "AFC", "division": "West"},
            {"name": "Buffalo Bills", "abbreviation": "BUF", "city": "Buffalo", "conference": "AFC", "division": "East"},
            {"name": "San Francisco 49ers", "abbreviation": "SFO", "city": "San Francisco", "conference": "NFC", "division": "West"},
            {"name": "Philadelphia Eagles", "abbreviation": "PHI", "city": "Philadelphia", "conference": "NFC", "division": "East"},
            {"name": "Dallas Cowboys", "abbreviation": "DAL", "city": "Dallas", "conference": "NFC", "division": "East"},
        ]
        
        for team_data in teams_data:
            existing = NFLTeam.query.filter_by(abbreviation=team_data["abbreviation"]).first()
            if not existing:
                team = NFLTeam(**team_data)
                db.session.add(team)
        
        # Create sample NFL players
        players_data = [
            {
                "pfr_id": "MahoPa00",
                "name": "Patrick Mahomes",
                "position": "QB",
                "current_team": "KAN",
                "height_inches": 75,
                "weight_lbs": 230,
                "college": "Texas Tech",
                "active": True
            },
            {
                "pfr_id": "AlleJo02", 
                "name": "Josh Allen",
                "position": "QB",
                "current_team": "BUF",
                "height_inches": 77,
                "weight_lbs": 237,
                "college": "Wyoming",
                "active": True
            },
            {
                "pfr_id": "PurdBr00",
                "name": "Brock Purdy",
                "position": "QB", 
                "current_team": "SFO",
                "height_inches": 73,
                "weight_lbs": 220,
                "college": "Iowa State",
                "active": True
            },
            {
                "pfr_id": "HurtJa05",
                "name": "Jalen Hurts",
                "position": "QB",
                "current_team": "PHI", 
                "height_inches": 73,
                "weight_lbs": 223,
                "college": "Oklahoma",
                "active": True
            },
            {
                "pfr_id": "PrescDa01",
                "name": "Dak Prescott",
                "position": "QB",
                "current_team": "DAL",
                "height_inches": 74,
                "weight_lbs": 238,
                "college": "Mississippi State",
                "active": True
            }
        ]
        
        for player_data in players_data:
            existing = NFLPlayer.query.filter_by(pfr_id=player_data["pfr_id"]).first()
            if not existing:
                player = NFLPlayer(**player_data)
                db.session.add(player)
        
        db.session.commit()
        
        # Create sample season stats for Patrick Mahomes
        mahomes = NFLPlayer.query.filter_by(pfr_id="MahoPa00").first()
        if mahomes:
            season_stats_data = [
                {
                    "player_id": mahomes.id,
                    "season_year": 2021,
                    "team": "KAN",
                    "position": "QB",
                    "age": 26,
                    "games_played": 17,
                    "games_started": 17,
                    "pass_completions": 461,
                    "pass_attempts": 700,
                    "pass_yards": 4839,
                    "pass_touchdowns": 37,
                    "interceptions": 13,
                    "qb_rating": 98.5,
                    "rush_attempts": 62,
                    "rush_yards": 381,
                    "rush_touchdowns": 2
                },
                {
                    "player_id": mahomes.id,
                    "season_year": 2022,
                    "team": "KAN", 
                    "position": "QB",
                    "age": 27,
                    "games_played": 17,
                    "games_started": 17,
                    "pass_completions": 435,
                    "pass_attempts": 651,
                    "pass_yards": 5250,
                    "pass_touchdowns": 41,
                    "interceptions": 12,
                    "qb_rating": 105.2,
                    "rush_attempts": 61,
                    "rush_yards": 358,
                    "rush_touchdowns": 4
                },
                {
                    "player_id": mahomes.id,
                    "season_year": 2023,
                    "team": "KAN",
                    "position": "QB", 
                    "age": 28,
                    "games_played": 17,
                    "games_started": 17,
                    "pass_completions": 401,
                    "pass_attempts": 597,
                    "pass_yards": 4183,
                    "pass_touchdowns": 27,
                    "interceptions": 14,
                    "qb_rating": 92.6,
                    "rush_attempts": 76,
                    "rush_yards": 389,
                    "rush_touchdowns": 1
                }
            ]
            
            for stat_data in season_stats_data:
                existing = NFLPlayerSeasonStats.query.filter_by(
                    player_id=stat_data["player_id"],
                    season_year=stat_data["season_year"]
                ).first()
                if not existing:
                    stat = NFLPlayerSeasonStats(**stat_data)
                    db.session.add(stat)
        
        # Create sample season stats for Josh Allen
        allen = NFLPlayer.query.filter_by(pfr_id="AlleJo02").first()
        if allen:
            season_stats_data = [
                {
                    "player_id": allen.id,
                    "season_year": 2021,
                    "team": "BUF",
                    "position": "QB",
                    "age": 25,
                    "games_played": 17,
                    "games_started": 17,
                    "pass_completions": 409,
                    "pass_attempts": 646,
                    "pass_yards": 4407,
                    "pass_touchdowns": 36,
                    "interceptions": 15,
                    "qb_rating": 92.2,
                    "rush_attempts": 122,
                    "rush_yards": 763,
                    "rush_touchdowns": 6
                },
                {
                    "player_id": allen.id,
                    "season_year": 2022,
                    "team": "BUF",
                    "position": "QB", 
                    "age": 26,
                    "games_played": 17,
                    "games_started": 17,
                    "pass_completions": 359,
                    "pass_attempts": 559,
                    "pass_yards": 4283,
                    "pass_touchdowns": 35,
                    "interceptions": 14,
                    "qb_rating": 96.0,
                    "rush_attempts": 95,
                    "rush_yards": 524,
                    "rush_touchdowns": 7
                },
                {
                    "player_id": allen.id,
                    "season_year": 2023,
                    "team": "BUF",
                    "position": "QB",
                    "age": 27, 
                    "games_played": 17,
                    "games_started": 17,
                    "pass_completions": 423,
                    "pass_attempts": 661,
                    "pass_yards": 4306,
                    "pass_touchdowns": 29,
                    "interceptions": 18,
                    "qb_rating": 87.6,
                    "rush_attempts": 95,
                    "rush_yards": 430,
                    "rush_touchdowns": 8
                }
            ]
            
            for stat_data in season_stats_data:
                existing = NFLPlayerSeasonStats.query.filter_by(
                    player_id=stat_data["player_id"],
                    season_year=stat_data["season_year"]
                ).first()
                if not existing:
                    stat = NFLPlayerSeasonStats(**stat_data)
                    db.session.add(stat)
                    
        db.session.commit()
        
        # Update career stats
        from services.nfl_data_service import NFLDataService
        nfl_service = NFLDataService()
        nfl_service._update_career_stats(mahomes.id)
        nfl_service._update_career_stats(allen.id)
        
        print("Sample NFL data populated successfully!")
        
        # Print summary
        total_teams = NFLTeam.query.count()
        total_players = NFLPlayer.query.count()
        total_stats = NFLPlayerSeasonStats.query.count()
        
        print(f"Created {total_teams} teams, {total_players} players, {total_stats} season records")

if __name__ == "__main__":
    populate_sample_nfl_data()