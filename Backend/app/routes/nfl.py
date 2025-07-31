"""
NFL Data API Routes
Provides endpoints for NFL player data and statistics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from services.nfl_data_service import NFLDataService
import logging

logger = logging.getLogger(__name__)

nfl_bp = Blueprint("nfl", __name__)
nfl_service = NFLDataService()

@nfl_bp.route("/teams/sync", methods=["POST"])
@jwt_required()
def sync_nfl_teams():
    """Sync NFL teams from Pro Football Reference"""
    try:
        count = nfl_service.sync_nfl_teams()
        return jsonify({
            "success": True,
            "message": f"Successfully synced {count} NFL teams",
            "teams_synced": count
        })
    except Exception as e:
        logger.error(f"Error syncing NFL teams: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to sync NFL teams"
        }), 500

@nfl_bp.route("/players/sync", methods=["POST"])
@jwt_required()
def sync_nfl_players():
    """Sync NFL players from Pro Football Reference"""
    try:
        limit = request.json.get('limit', 50) if request.json else 50
        count = nfl_service.sync_nfl_players(limit=limit)
        return jsonify({
            "success": True,
            "message": f"Successfully synced {count} NFL players",
            "players_synced": count
        })
    except Exception as e:
        logger.error(f"Error syncing NFL players: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to sync NFL players"
        }), 500

@nfl_bp.route("/players/<pfr_id>/sync", methods=["POST"])
@jwt_required()
def sync_player_stats(pfr_id):
    """Sync statistics for a specific player"""
    try:
        count = nfl_service.sync_player_stats(pfr_id)
        return jsonify({
            "success": True,
            "message": f"Successfully synced {count} season stats for player {pfr_id}",
            "stats_synced": count
        })
    except Exception as e:
        logger.error(f"Error syncing player stats for {pfr_id}: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to sync stats for player {pfr_id}"
        }), 500

@nfl_bp.route("/players/search", methods=["GET"])
def search_players():
    """Search for NFL players by name"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Query parameter 'q' is required"
        }), 400
    
    try:
        players = nfl_service.search_players(query, limit)
        return jsonify({
            "success": True,
            "players": players,
            "count": len(players)
        })
    except Exception as e:
        logger.error(f"Error searching players: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to search players"
        }), 500

@nfl_bp.route("/players/<pfr_id>", methods=["GET"])
def get_player_detail(pfr_id):
    """Get detailed information for a specific player"""
    try:
        player_data = nfl_service.get_player_detail(pfr_id)
        
        if not player_data:
            return jsonify({
                "success": False,
                "error": f"Player with ID {pfr_id} not found"
            }), 404
            
        return jsonify({
            "success": True,
            "data": player_data
        })
    except Exception as e:
        logger.error(f"Error getting player detail for {pfr_id}: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to get player details for {pfr_id}"
        }), 500

@nfl_bp.route("/players/<pfr_id>/predictions", methods=["GET"])
def get_player_predictions(pfr_id):
    """Get performance predictions for a player"""
    try:
        predictions = nfl_service.get_player_predictions(pfr_id)
        
        if not predictions:
            return jsonify({
                "success": False,
                "error": f"Unable to generate predictions for player {pfr_id}"
            }), 404
            
        return jsonify({
            "success": True,
            "predictions": predictions,
            "disclaimer": "Predictions are based on simple trend analysis and should not be used for gambling or professional decisions."
        })
    except Exception as e:
        logger.error(f"Error generating predictions for {pfr_id}: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to generate predictions for player {pfr_id}"
        }), 500

@nfl_bp.route("/stats/summary", methods=["GET"])
def get_stats_summary():
    """Get summary statistics about the NFL data"""
    try:
        from app.models.models import NFLPlayer, NFLPlayerSeasonStats, NFLTeam
        
        total_players = NFLPlayer.query.count()
        active_players = NFLPlayer.query.filter_by(active=True).count()
        total_teams = NFLTeam.query.count()
        total_season_records = NFLPlayerSeasonStats.query.count()
        
        # Get some top performers
        top_passers = db.session.query(NFLPlayerSeasonStats)\
                                .join(NFLPlayer)\
                                .filter(NFLPlayerSeasonStats.pass_yards > 3000)\
                                .order_by(NFLPlayerSeasonStats.pass_yards.desc())\
                                .limit(5).all()
                                
        return jsonify({
            "success": True,
            "summary": {
                "total_players": total_players,
                "active_players": active_players,
                "total_teams": total_teams,
                "total_season_records": total_season_records,
                "top_passers": [
                    {
                        "player_name": stat.nfl_player.name,
                        "season_year": stat.season_year,
                        "pass_yards": stat.pass_yards,
                        "team": stat.team
                    }
                    for stat in top_passers
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats summary: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to get statistics summary"
        }), 500

@nfl_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for NFL data service"""
    return jsonify({
        "success": True,
        "service": "NFL Data API",
        "status": "healthy",
        "endpoints": [
            "POST /nfl/teams/sync - Sync NFL teams",
            "POST /nfl/players/sync - Sync NFL players", 
            "POST /nfl/players/<pfr_id>/sync - Sync player stats",
            "GET /nfl/players/search?q=<query> - Search players",
            "GET /nfl/players/<pfr_id> - Get player details",
            "GET /nfl/players/<pfr_id>/predictions - Get predictions",
            "GET /nfl/stats/summary - Get data summary"
        ]
    })