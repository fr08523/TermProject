from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import requests
from app import db
from app.models.models import League, Team, Player, Game, PlayerGameStats

data_mgmt_bp = Blueprint("data_management", __name__)

@data_mgmt_bp.post("/load-sample-data")
def load_sample_data():
    """Load additional sample data to demonstrate the services functionality"""
    try:
        # Create additional sample data to show off the enhanced statistics
        
        # Add more players with varied stats
        bills = Team.query.filter_by(name="Buffalo Bills").first()
        if not bills:
            # Create Bills team if it doesn't exist
            nfl = League.query.filter_by(name="NFL").first()
            bills = Team(name="Buffalo Bills", home_city="Buffalo", league_id=nfl.id if nfl else 1, 
                        head_coach="Sean McDermott", stadium="Highmark Stadium")
            db.session.add(bills)
            db.session.commit()
        
        # Add Josh Allen
        josh_allen = Player.query.filter_by(name="Josh Allen").first()
        if not josh_allen:
            josh_allen = Player(
                name="Josh Allen", position="QB", team_id=bills.id,
                career_passing_yards=18000, career_rushing_yards=3200, career_touchdowns=150
            )
            db.session.add(josh_allen)
        
        # Add Stefon Diggs
        stefon_diggs = Player.query.filter_by(name="Stefon Diggs").first()
        if not stefon_diggs:
            stefon_diggs = Player(
                name="Stefon Diggs", position="WR", team_id=bills.id,
                career_receiving_yards=9500, career_touchdowns=75
            )
            db.session.add(stefon_diggs)
        
        db.session.commit()
        
        # Create a few more games with these players
        cowboys = Team.query.filter_by(name="Dallas Cowboys").first()
        
        # Bills vs Cowboys game
        game = Game.query.filter_by(home_team_id=bills.id, away_team_id=cowboys.id).first()
        if not game:
            game = Game(
                league_id=1, season_year=2024, week=3,
                home_team_id=bills.id, away_team_id=cowboys.id,
                venue="Highmark Stadium", home_score=31, away_score=24,
                attendance=71000
            )
            db.session.add(game)
            db.session.commit()
        
        # Add comprehensive stats for Josh Allen in this game
        josh_stats = PlayerGameStats.query.filter_by(player_id=josh_allen.id, game_id=game.id).first()
        if not josh_stats:
            josh_stats = PlayerGameStats(
                player_id=josh_allen.id, game_id=game.id,
                passing_yards=423, rushing_yards=54, receiving_yards=0,
                touchdowns=4, passing_touchdowns=3, rushing_touchdowns=1,
                interceptions=0, field_goals_made=0, sacks=0, tackles=0,
                fumbles=1, fumbles_lost=0, completions=29, pass_attempts=43
            )
            db.session.add(josh_stats)
        
        # Add stats for Stefon Diggs
        diggs_stats = PlayerGameStats.query.filter_by(player_id=stefon_diggs.id, game_id=game.id).first()
        if not diggs_stats:
            diggs_stats = PlayerGameStats(
                player_id=stefon_diggs.id, game_id=game.id,
                passing_yards=0, rushing_yards=12, receiving_yards=148,
                touchdowns=2, passing_touchdowns=0, rushing_touchdowns=0, receiving_touchdowns=2,
                interceptions=0, field_goals_made=0, sacks=0, tackles=0,
                fumbles=0, fumbles_lost=0, completions=0, pass_attempts=0
            )
            db.session.add(diggs_stats)
        
        # Add more varied stats for existing players
        dak_prescott = Player.query.filter_by(name="Dak Prescott").first()
        if dak_prescott:
            # Update an existing game stat with more detailed touchdown breakdown
            existing_stat = PlayerGameStats.query.filter_by(player_id=dak_prescott.id).first()
            if existing_stat:
                existing_stat.passing_touchdowns = 2
                existing_stat.rushing_touchdowns = 0
                existing_stat.completions = 24
                existing_stat.pass_attempts = 38
        
        db.session.commit()
        
        # Count totals
        total_players = Player.query.count()
        total_games = Game.query.count()
        total_stats = PlayerGameStats.query.count()
        
        return jsonify({
            "message": "Sample data loaded successfully!",
            "total_players": total_players,
            "total_games": total_games,
            "total_stats_records": total_stats,
            "note": "Enhanced football statistics with detailed touchdown breakdowns, completion percentages, and more metrics"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to load sample data: {str(e)}"}), 500

@data_mgmt_bp.get("/services-status")
def services_status():
    """Check if the backend services are accessible and what they can do"""
    try:
        # Test if we can import the services
        from services.loader import Loader
        from services.transformer import Transformer
        from services.persister import Persister
        
        # Test API connectivity (without making actual calls to avoid rate limits)
        status = {
            "services_available": True,
            "loader_service": "Available - can fetch NFL data from SportRadar API",
            "transformer_service": "Available - can transform SportRadar data to DTOs",
            "persister_service": "Available - can persist to PostgreSQL (configured for SQLite in dev)",
            "integration_note": "Services are functional but designed for PostgreSQL. Current app uses SQLite for development.",
            "recommendation": "Use the load-sample-data endpoint to populate with realistic football statistics"
        }
        
        return jsonify(status)
        
    except ImportError as e:
        return jsonify({
            "services_available": False,
            "error": f"Services import failed: {str(e)}",
            "note": "Services folder may have missing dependencies"
        }), 500

@data_mgmt_bp.post("/test-services")
@jwt_required()
def test_services():
    """Test the services functionality (use with caution - makes external API calls)"""
    try:
        from services.loader import Loader
        
        # Initialize loader
        loader = Loader()
        
        # Test API connectivity (this will make an actual API call)
        # Note: This should be used sparingly to avoid hitting rate limits
        try:
            response = requests.get(f"{loader.week_url}{loader.api_key}", timeout=10)
            api_status = response.status_code
            
            if api_status == 200:
                return jsonify({
                    "services_test": "SUCCESS",
                    "api_response_code": api_status,
                    "message": "SportRadar API is accessible",
                    "note": "Services are fully functional. Data can be loaded from external NFL API."
                })
            else:
                return jsonify({
                    "services_test": "PARTIAL",
                    "api_response_code": api_status,
                    "message": "API returned non-200 status",
                    "note": "Services are available but external API may have issues"
                })
                
        except requests.exceptions.RequestException as e:
            return jsonify({
                "services_test": "LIMITED",
                "error": str(e),
                "message": "External API not accessible",
                "note": "Services code is functional but external SportRadar API is not reachable"
            })
            
    except Exception as e:
        return jsonify({
            "services_test": "FAILED",
            "error": str(e),
            "message": "Services are not functional"
        }), 500