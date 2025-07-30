from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.models import (
    League, Team, Player,
    Game, PlayerGameStats, Injury, PlayerSalary
)

api_bp = Blueprint("api", __name__)

# Generic save helper for single‐PK models
def _save(obj):
    db.session.add(obj)
    db.session.commit()
    return jsonify(id=obj.id, msg="saved")


# League endpoints
@api_bp.get("/leagues")
def list_leagues():
    return jsonify([
        {"id": l.id, "name": l.name, "level": l.level}
        for l in League.query.all()
    ])

@api_bp.post("/leagues")
@jwt_required()
def create_league():
    d = request.get_json()
    return _save(League(name=d["name"], level=d.get("level")))


# Team endpoints
@api_bp.get("/teams")
def list_teams():
    league_id = request.args.get("league_id", type=int)
    name_filter = request.args.get("name")
    
    # Start with basic Team query
    query = Team.query
    
    # Apply filters
    if league_id:
        query = query.filter(Team.league_id == league_id)
    
    if name_filter:
        query = query.filter(Team.name.ilike(f"%{name_filter}%"))
    
    teams = query.all()
    
    # Build response with league names
    result = []
    for team in teams:
        league = League.query.get(team.league_id)
        result.append({
            "id": team.id,
            "name": team.name,
            "home_city": team.home_city,
            "head_coach": team.head_coach,
            "stadium": team.stadium,
            "league_id": team.league_id,
            "league_name": league.name if league else "Unknown"
        })
    
    return jsonify(result)

@api_bp.post("/teams")
@jwt_required()
def create_team():
    d = request.get_json()
    return _save(Team(
        name=d["name"],
        home_city=d["home_city"],
        league_id=d["league_id"]
    ))


# Player endpoints 
@api_bp.get("/players")
def list_players():
    name_filter = request.args.get("name")
    team_id = request.args.get("team_id", type=int)
    position = request.args.get("position")
    
    # Start with basic Player query
    query = Player.query
    
    # Apply filters
    if name_filter:
        query = query.filter(Player.name.ilike(f"%{name_filter}%"))
    
    if team_id:
        query = query.filter(Player.team_id == team_id)
    
    if position:
        query = query.filter(Player.position.ilike(f"%{position}%"))
    
    players = query.all()
    
    # Build response with team and league names
    result = []
    for player in players:
        team = Team.query.get(player.team_id)
        league = League.query.get(team.league_id) if team else None
        
        result.append({
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "team_id": player.team_id,
            "team_name": team.name if team else "Unknown",
            "league_name": league.name if league else "Unknown",
            "career_passing_yards": player.career_passing_yards,
            "career_passing_completions": player.career_passing_completions,
            "career_passing_attempts": player.career_passing_attempts,
            "career_passing_touchdowns": player.career_passing_touchdowns,
            "career_rushing_yards": player.career_rushing_yards,
            "career_rushing_attempts": player.career_rushing_attempts,
            "career_rushing_touchdowns": player.career_rushing_touchdowns,
            "career_receiving_yards": player.career_receiving_yards,
            "career_receptions": player.career_receptions,
            "career_receiving_touchdowns": player.career_receiving_touchdowns,
            "career_tackles": player.career_tackles,
            "career_sacks": player.career_sacks,
            "career_interceptions": player.career_interceptions,
            "career_passes_defensed": player.career_passes_defensed,
            "career_touchdowns": player.career_touchdowns,
            "career_fumbles": player.career_fumbles,
            "career_fumbles_lost": player.career_fumbles_lost
        })
    
    return jsonify(result)

@api_bp.get("/players/<int:player_id>/stats")
def get_player_stats(player_id):
    """Get detailed stats for a specific player"""
    # Get player info
    player = Player.query.get_or_404(player_id)
    team = Team.query.get(player.team_id)
    
    # Get game stats for this player
    game_stats = PlayerGameStats.query.filter_by(player_id=player_id).all()
    
    # Get game details for each stat
    game_logs = []
    total_passing = total_rushing = total_receiving = total_touchdowns = 0
    
    for stat in game_stats:
        game = Game.query.get(stat.game_id)
        if game:
            # Determine opponent team
            opponent_team_id = game.away_team_id if game.home_team_id == player.team_id else game.home_team_id
            opponent_team = Team.query.get(opponent_team_id)
            
            game_logs.append({
                "game_id": stat.game_id,
                "season_year": game.season_year,
                "week": game.week,
                "game_date": game.game_date.isoformat() if game.game_date else None,
                "opponent": opponent_team.name if opponent_team else "Unknown",
                "home_score": game.home_score,
                "away_score": game.away_score,
                "passing_yards": stat.passing_yards,
                "passing_completions": stat.passing_completions,
                "passing_attempts": stat.passing_attempts,
                "passing_touchdowns": stat.passing_touchdowns,
                "rushing_yards": stat.rushing_yards,
                "rushing_attempts": stat.rushing_attempts,
                "rushing_touchdowns": stat.rushing_touchdowns,
                "receiving_yards": stat.receiving_yards,
                "receptions": stat.receptions,
                "receiving_targets": stat.receiving_targets,
                "receiving_touchdowns": stat.receiving_touchdowns,
                "touchdowns": stat.touchdowns,
                "tackles": stat.tackles,
                "sacks": stat.sacks,
                "interceptions": stat.interceptions,
                "passes_defensed": stat.passes_defensed,
                "fumbles": stat.fumbles,
                "fumbles_lost": stat.fumbles_lost,
                "field_goals_made": stat.field_goals_made,
                "field_goals_attempted": stat.field_goals_attempted,
                "extra_points_made": stat.extra_points_made,
                "extra_points_attempted": stat.extra_points_attempted
            })
            
            # Accumulate totals
            total_passing += stat.passing_yards
            total_rushing += stat.rushing_yards
            total_receiving += stat.receiving_yards
            total_touchdowns += stat.touchdowns
    
    # Calculate averages
    total_games = len(game_stats)
    avg_passing = total_passing / total_games if total_games > 0 else 0
    avg_rushing = total_rushing / total_games if total_games > 0 else 0
    avg_receiving = total_receiving / total_games if total_games > 0 else 0
    
    # Sort game logs by date (most recent first)
    game_logs.sort(key=lambda x: x['game_date'] or '', reverse=True)
    
    return jsonify({
        "player": {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "team_name": team.name if team else "Unknown",
            "career_passing_yards": player.career_passing_yards,
            "career_passing_completions": player.career_passing_completions,
            "career_passing_attempts": player.career_passing_attempts,
            "career_passing_touchdowns": player.career_passing_touchdowns,
            "career_rushing_yards": player.career_rushing_yards,
            "career_rushing_attempts": player.career_rushing_attempts,
            "career_rushing_touchdowns": player.career_rushing_touchdowns,
            "career_receiving_yards": player.career_receiving_yards,
            "career_receptions": player.career_receptions,
            "career_receiving_touchdowns": player.career_receiving_touchdowns,
            "career_tackles": player.career_tackles,
            "career_sacks": player.career_sacks,
            "career_interceptions": player.career_interceptions,
            "career_passes_defensed": player.career_passes_defensed,
            "career_touchdowns": player.career_touchdowns,
            "career_fumbles": player.career_fumbles,
            "career_fumbles_lost": player.career_fumbles_lost
        },
        "season_stats": {
            "games_played": total_games,
            "total_passing_yards": total_passing,
            "total_rushing_yards": total_rushing,
            "total_receiving_yards": total_receiving,
            "total_touchdowns": total_touchdowns,
            "avg_passing_yards": round(avg_passing, 1),
            "avg_rushing_yards": round(avg_rushing, 1),
            "avg_receiving_yards": round(avg_receiving, 1)
        },
        "game_logs": game_logs
    })

@api_bp.post("/players")
@jwt_required()
def create_player():
    d = request.get_json()
    return _save(Player(
        name=d["name"],
        position=d["position"],
        team_id=d["team_id"]
    ))


# Game endpoints
@api_bp.get("/games")
def list_games():
    team_name = request.args.get("team")
    week = request.args.get("week")

    # Start with basic Game query
    query = Game.query

    if team_name:
        # Filter by team name using subquery approach
        query = query.join(Team, (Game.home_team_id == Team.id) | (Game.away_team_id == Team.id)).filter(Team.name.ilike(f"%{team_name}%"))
    if week:
        query = query.filter_by(week=week)

    games = query.all()

    # Build response with team names included
    games_data = []
    for g in games:
        # Get team names by querying the Team table
        home_team = Team.query.get(g.home_team_id)
        away_team = Team.query.get(g.away_team_id)
        
        games_data.append({
            "id": g.id,
            "league_id": g.league_id,
            "season_year": g.season_year,
            "week": g.week,
            "home_team_id": g.home_team_id,
            "away_team_id": g.away_team_id,
            "home_team_name": home_team.name if home_team else "Unknown",
            "away_team_name": away_team.name if away_team else "Unknown",
            "venue": g.venue,
            "game_date": g.game_date.isoformat() if g.game_date else None,
            "home_score": g.home_score,
            "away_score": g.away_score,
            "attendance": g.attendance,
        })

    return jsonify(games_data)

@api_bp.post("/games")
@jwt_required()
def create_game():
    d = request.get_json()
    g = Game(
        league_id    = d["league_id"],
        season_year  = d["season_year"],
        week         = d["week"],
        home_team_id = d["home_team_id"],
        away_team_id = d["away_team_id"],
        venue        = d.get("venue"),
        game_date    = d.get("game_date"),
        home_score   = d.get("home_score"),
        away_score   = d.get("away_score"),
        attendance   = d.get("attendance"),
    )
    return _save(g)


# PlayerGameStats endpoints
@api_bp.get("/stats")
def list_stats():
    player_name = request.args.get("player_name")
    team_id = request.args.get("team_id")
    season_year = request.args.get("season_year", type=int)
    
    # Start with basic PlayerGameStats query
    stats = PlayerGameStats.query.all()
    
    # Build response with player and game details
    result = []
    for stat in stats:
        player = Player.query.get(stat.player_id)
        if not player:
            continue
            
        # Apply player name filter
        if player_name and not player.name.lower().find(player_name.lower()) >= 0:
            continue
            
        # Apply team filter
        if team_id and str(player.team_id) != str(team_id):
            continue
        
        game = Game.query.get(stat.game_id)
        if not game:
            continue
            
        # Apply season filter
        if season_year and game.season_year != season_year:
            continue
        
        team = Team.query.get(player.team_id)
        
        result.append({
            "player_id": stat.player_id,
            "game_id": stat.game_id,
            "player_name": player.name,
            "player_position": player.position,
            "team_name": team.name if team else "Unknown",
            "season_year": game.season_year,
            "week": game.week,
            "game_date": game.game_date.isoformat() if game.game_date else None,
            "passing_yards": stat.passing_yards,
            "rushing_yards": stat.rushing_yards,
            "receiving_yards": stat.receiving_yards,
            "tackles": stat.tackles,
            "sacks": stat.sacks,
            "interceptions": stat.interceptions,
            "touchdowns": stat.touchdowns,
            "field_goals_made": stat.field_goals_made,
            "extra_points_made": stat.extra_points_made,
        })
    
    # Sort by most recent games first
    result.sort(key=lambda x: x['game_date'] or '', reverse=True)
    
    return jsonify(result)

@api_bp.post("/stats")
@jwt_required()
def create_stats():
    d = request.get_json()
    s = PlayerGameStats(
        player_id         = d["player_id"],
        game_id           = d["game_id"],
        # Passing stats
        passing_yards     = d.get("passing_yards", 0),
        passing_completions = d.get("passing_completions", 0),
        passing_attempts  = d.get("passing_attempts", 0),
        passing_touchdowns = d.get("passing_touchdowns", 0),
        # Rushing stats
        rushing_yards     = d.get("rushing_yards", 0),
        rushing_attempts  = d.get("rushing_attempts", 0),
        rushing_touchdowns = d.get("rushing_touchdowns", 0),
        # Receiving stats
        receiving_yards   = d.get("receiving_yards", 0),
        receptions        = d.get("receptions", 0),
        receiving_targets = d.get("receiving_targets", 0),
        receiving_touchdowns = d.get("receiving_touchdowns", 0),
        # Defensive stats
        tackles           = d.get("tackles", 0),
        sacks             = d.get("sacks", 0),
        interceptions     = d.get("interceptions", 0),
        passes_defensed   = d.get("passes_defensed", 0),
        # General stats
        touchdowns        = d.get("touchdowns", 0),
        fumbles           = d.get("fumbles", 0),
        fumbles_lost      = d.get("fumbles_lost", 0),
        # Kicking stats
        field_goals_made  = d.get("field_goals_made", 0),
        field_goals_attempted = d.get("field_goals_attempted", 0),
        extra_points_made = d.get("extra_points_made", 0),
        extra_points_attempted = d.get("extra_points_attempted", 0)
    )
    db.session.add(s)
    
    # Update player career stats
    player = Player.query.get(s.player_id)
    if player:
        player.career_passing_yards += s.passing_yards
        player.career_passing_completions += s.passing_completions
        player.career_passing_attempts += s.passing_attempts
        player.career_passing_touchdowns += s.passing_touchdowns
        player.career_rushing_yards += s.rushing_yards
        player.career_rushing_attempts += s.rushing_attempts
        player.career_rushing_touchdowns += s.rushing_touchdowns
        player.career_receiving_yards += s.receiving_yards
        player.career_receptions += s.receptions
        player.career_receiving_touchdowns += s.receiving_touchdowns
        player.career_tackles += s.tackles
        player.career_sacks += s.sacks
        player.career_interceptions += s.interceptions
        player.career_passes_defensed += s.passes_defensed
        player.career_touchdowns += s.touchdowns
        player.career_fumbles += s.fumbles
        player.career_fumbles_lost += s.fumbles_lost
    
    db.session.commit()
    # composite PK → return both keys
    return jsonify(
        player_id=s.player_id,
        game_id=s.game_id,
        msg="saved"
    )


# Injury endpoints
@api_bp.get("/injuries")
def list_injuries():
    return jsonify([
        {
            "id": i.id,
            "player_id": i.player_id,
            "start_date": i.start_date.isoformat() if i.start_date else None,
            "end_date": i.end_date.isoformat()   if i.end_date   else None,
            "description": i.description,
            "severity": i.severity,
        }
        for i in Injury.query.all()
    ])

@api_bp.post("/injuries")
@jwt_required()
def create_injury():
    d = request.get_json()
    i = Injury(
        player_id   = d["player_id"],
        start_date  = d.get("start_date"),
        end_date    = d.get("end_date"),
        description = d.get("description"),
        severity    = d.get("severity"),
    )
    return _save(i)


# PlayerSalary endpoints
@api_bp.get("/salaries")
def list_salaries():
    return jsonify([
        {
            "player_id": s.player_id,
            "season_year": s.season_year,
            "base_salary": float(s.base_salary),
            "bonuses": float(s.bonuses),
            "cap_hit": float(s.cap_hit),
            "total_compensation": float(s.total_comp),
        }
        for s in PlayerSalary.query.all()
    ])

@api_bp.post("/salaries")
@jwt_required()
def create_salary():
    d = request.get_json()
    s = PlayerSalary(
        player_id      = d["player_id"],
        season_year    = d["season_year"],
        base_salary    = d.get("base_salary"),
        bonuses        = d.get("bonuses"),
        cap_hit        = d.get("cap_hit"),
        total_comp     = d.get("total_compensation"),
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(
        player_id=s.player_id,
        season_year=s.season_year,
        msg="saved"
    )
