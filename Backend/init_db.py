#!/usr/bin/env python3
"""Initialize the database with tables and sample data."""

from app import create_app, db
from app.models.models import User, League, Team, Player, Game, PlayerGameStats, Injury, PlayerSalary
from datetime import datetime, date

def init_database():
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        # Create a test user
        user = User(username="admin")
        user.set_password("password123")
        db.session.add(user)
        
        # Create leagues
        nfl = League(name="NFL", level="Professional")
        college = League(name="NCAA", level="College")
        db.session.add_all([nfl, college])
        db.session.commit()  # Commit to get IDs
        
        # Create teams
        cowboys = Team(name="Dallas Cowboys", home_city="Dallas", league_id=nfl.id, head_coach="Mike McCarthy", stadium="AT&T Stadium")
        giants = Team(name="New York Giants", home_city="New York", league_id=nfl.id, head_coach="Brian Daboll", stadium="MetLife Stadium")
        alabama = Team(name="Alabama Crimson Tide", home_city="Tuscaloosa", league_id=college.id, head_coach="Kalen DeBoer", stadium="Bryant-Denny Stadium")
        db.session.add_all([cowboys, giants, alabama])
        db.session.commit()
        
        # Create players
        dak_prescott = Player(
            name="Dak Prescott", position="QB", team_id=cowboys.id,
            career_passing_yards=29000, career_rushing_yards=1800, career_touchdowns=220
        )
        ezekiel_elliott = Player(
            name="Ezekiel Elliott", position="RB", team_id=cowboys.id,
            career_rushing_yards=8900, career_touchdowns=89
        )
        ceedee_lamb = Player(
            name="CeeDee Lamb", position="WR", team_id=cowboys.id,
            career_receiving_yards=5400, career_touchdowns=35
        )
        daniel_jones = Player(
            name="Daniel Jones", position="QB", team_id=giants.id,
            career_passing_yards=12000, career_rushing_yards=2100, career_touchdowns=70
        )
        saquon_barkley = Player(
            name="Saquon Barkley", position="RB", team_id=giants.id,
            career_rushing_yards=6500, career_touchdowns=52
        )
        
        db.session.add_all([dak_prescott, ezekiel_elliott, ceedee_lamb, daniel_jones, saquon_barkley])
        db.session.commit()
        
        # Create games
        game1 = Game(
            league_id=nfl.id, season_year=2024, week=1,
            home_team_id=cowboys.id, away_team_id=giants.id,
            venue="AT&T Stadium", game_date=datetime(2024, 9, 8, 20, 0),
            home_score=28, away_score=14, attendance=80000
        )
        game2 = Game(
            league_id=nfl.id, season_year=2024, week=2,
            home_team_id=giants.id, away_team_id=cowboys.id,
            venue="MetLife Stadium", game_date=datetime(2024, 9, 15, 13, 0),
            home_score=21, away_score=35, attendance=75000
        )
        
        db.session.add_all([game1, game2])
        db.session.commit()
        
        # Create player game stats
        dak_stats_game1 = PlayerGameStats(
            player_id=dak_prescott.id, game_id=game1.id,
            passing_yards=342, touchdowns=3, interceptions=0
        )
        dak_stats_game2 = PlayerGameStats(
            player_id=dak_prescott.id, game_id=game2.id,
            passing_yards=298, touchdowns=2, interceptions=1
        )
        ezekiel_stats_game1 = PlayerGameStats(
            player_id=ezekiel_elliott.id, game_id=game1.id,
            rushing_yards=125, touchdowns=2
        )
        ceedee_stats_game1 = PlayerGameStats(
            player_id=ceedee_lamb.id, game_id=game1.id,
            receiving_yards=156, touchdowns=1
        )
        daniel_stats_game1 = PlayerGameStats(
            player_id=daniel_jones.id, game_id=game1.id,
            passing_yards=189, touchdowns=1, interceptions=2
        )
        daniel_stats_game2 = PlayerGameStats(
            player_id=daniel_jones.id, game_id=game2.id,
            passing_yards=245, touchdowns=2, interceptions=0
        )
        
        db.session.add_all([
            dak_stats_game1, dak_stats_game2, ezekiel_stats_game1, 
            ceedee_stats_game1, daniel_stats_game1, daniel_stats_game2
        ])
        
        # Create sample salaries
        dak_salary = PlayerSalary(
            player_id=dak_prescott.id, season_year=2024,
            base_salary=40000000, bonuses=5000000, cap_hit=55000000, total_comp=45000000
        )
        daniel_salary = PlayerSalary(
            player_id=daniel_jones.id, season_year=2024,
            base_salary=32000000, bonuses=3000000, cap_hit=47000000, total_comp=35000000
        )
        
        db.session.add_all([dak_salary, daniel_salary])
        
        # Create sample injury
        injury = Injury(
            player_id=saquon_barkley.id,
            start_date=date(2024, 8, 15),
            end_date=date(2024, 9, 1),
            description="Ankle sprain during training camp",
            severity="Minor"
        )
        
        db.session.add(injury)
        db.session.commit()
        
        print("Database initialized successfully with sample data!")
        print(f"Created {User.query.count()} users")
        print(f"Created {League.query.count()} leagues")
        print(f"Created {Team.query.count()} teams")
        print(f"Created {Player.query.count()} players")
        print(f"Created {Game.query.count()} games")
        print(f"Created {PlayerGameStats.query.count()} player game stats")
        print(f"Created {PlayerSalary.query.count()} salary records")
        print(f"Created {Injury.query.count()} injury records")

if __name__ == "__main__":
    init_database()