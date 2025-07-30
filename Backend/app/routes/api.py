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
    
    # Enhanced query with league information
    query = db.session.query(
        Team,
        League.name.label('league_name')
    ).select_from(Team).join(League, Team.league_id == League.id)
    
    # Apply filters
    if league_id:
        query = query.filter(Team.league_id == league_id)
    
    if name_filter:
        query = query.filter(Team.name.ilike(f"%{name_filter}%"))
    
    results = query.all()
    
    return jsonify([
        {
            "id": result.Team.id,
            "name": result.Team.name,
            "home_city": result.Team.home_city,
            "head_coach": result.Team.head_coach,
            "stadium": result.Team.stadium,
            "league_id": result.Team.league_id,
            "league_name": result.league_name
        }
        for result in results
    ])

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
    
    # Enhanced query with team information
    query = db.session.query(
        Player,
        Team.name.label('team_name'),
        League.name.label('league_name')
    ).select_from(Player).join(Team, Player.team_id == Team.id).join(League, Team.league_id == League.id)
    
    # Apply filters
    if name_filter:
        query = query.filter(Player.name.ilike(f"%{name_filter}%"))
    
    if team_id:
        query = query.filter(Player.team_id == team_id)
    
    if position:
        query = query.filter(Player.position.ilike(f"%{position}%"))
    
    results = query.all()
    
    return jsonify([
        {
            "id": result.Player.id,
            "name": result.Player.name,
            "position": result.Player.position,
            "team_id": result.Player.team_id,
            "team_name": result.team_name,
            "league_name": result.league_name,
            "career_passing_yards": result.Player.career_passing_yards,
            "career_rushing_yards": result.Player.career_rushing_yards,
            "career_receiving_yards": result.Player.career_receiving_yards,
            "career_tackles": result.Player.career_tackles,
            "career_sacks": result.Player.career_sacks,
            "career_interceptions": result.Player.career_interceptions,
            "career_touchdowns": result.Player.career_touchdowns
        }
        for result in results
    ])

@api_bp.get("/players/<int:player_id>/stats")
def get_player_stats(player_id):
    """Get detailed stats for a specific player"""
    # Get player info
    player = Player.query.get_or_404(player_id)
    
    # Get game stats with game details
    stats_query = db.session.query(
        PlayerGameStats,
        Game.season_year,
        Game.week,
        Game.game_date,
        Game.home_score,
        Game.away_score,
        Team.name.label('opponent_team')
    ).join(Game).join(
        Team, 
        case(
            (Game.home_team_id == player.team_id, Game.away_team_id),
            else_=Game.home_team_id
        ) == Team.id
    ).filter(PlayerGameStats.player_id == player_id).order_by(Game.game_date.desc())
    
    stats_results = stats_query.all()
    
    # Calculate totals and averages
    total_games = len(stats_results)
    if total_games > 0:
        total_passing = sum(s.PlayerGameStats.passing_yards for s in stats_results)
        total_rushing = sum(s.PlayerGameStats.rushing_yards for s in stats_results)
        total_receiving = sum(s.PlayerGameStats.receiving_yards for s in stats_results)
        total_touchdowns = sum(s.PlayerGameStats.touchdowns for s in stats_results)
        
        avg_passing = total_passing / total_games
        avg_rushing = total_rushing / total_games
        avg_receiving = total_receiving / total_games
    else:
        total_passing = total_rushing = total_receiving = total_touchdowns = 0
        avg_passing = avg_rushing = avg_receiving = 0
    
    return jsonify({
        "player": {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "team_name": player.current_team.name,
            "career_passing_yards": player.career_passing_yards,
            "career_rushing_yards": player.career_rushing_yards,
            "career_receiving_yards": player.career_receiving_yards,
            "career_touchdowns": player.career_touchdowns
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
        "game_logs": [
            {
                "game_id": result.PlayerGameStats.game_id,
                "season_year": result.season_year,
                "week": result.week,
                "game_date": result.game_date.isoformat() if result.game_date else None,
                "opponent": result.opponent_team,
                "home_score": result.home_score,
                "away_score": result.away_score,
                "passing_yards": result.PlayerGameStats.passing_yards,
                "rushing_yards": result.PlayerGameStats.rushing_yards,
                "receiving_yards": result.PlayerGameStats.receiving_yards,
                "touchdowns": result.PlayerGameStats.touchdowns,
                "tackles": result.PlayerGameStats.tackles,
                "sacks": result.PlayerGameStats.sacks,
                "interceptions": result.PlayerGameStats.interceptions
            }
            for result in stats_results
        ]
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
    
    # Start with a query that joins with Player and Game tables
    query = db.session.query(
        PlayerGameStats,
        Player.name.label('player_name'),
        Player.position.label('player_position'),
        Team.name.label('team_name'),
        Game.season_year,
        Game.week,
        Game.game_date
    ).join(Player).join(Team, Player.team_id == Team.id).join(Game)
    
    # Apply filters
    if player_name:
        # Safe filtering using LIKE with parameter binding
        query = query.filter(Player.name.ilike(f"%{player_name}%"))
    
    if team_id:
        query = query.filter(Player.team_id == team_id)
    
    if season_year:
        query = query.filter(Game.season_year == season_year)
    
    # Order by most recent games first
    query = query.order_by(Game.game_date.desc())
    
    results = query.all()
    
    return jsonify([
        {
            "player_id": result.PlayerGameStats.player_id,
            "game_id": result.PlayerGameStats.game_id,
            "player_name": result.player_name,
            "player_position": result.player_position,
            "team_name": result.team_name,
            "season_year": result.season_year,
            "week": result.week,
            "game_date": result.game_date.isoformat() if result.game_date else None,
            "passing_yards": result.PlayerGameStats.passing_yards,
            "rushing_yards": result.PlayerGameStats.rushing_yards,
            "receiving_yards": result.PlayerGameStats.receiving_yards,
            "tackles": result.PlayerGameStats.tackles,
            "sacks": result.PlayerGameStats.sacks,
            "interceptions": result.PlayerGameStats.interceptions,
            "touchdowns": result.PlayerGameStats.touchdowns,
            "field_goals_made": result.PlayerGameStats.field_goals_made,
            "extra_points_made": result.PlayerGameStats.extra_points_made,
        }
        for result in results
    ])

@api_bp.post("/stats")
@jwt_required()
def create_stats():
    d = request.get_json()
    s = PlayerGameStats(
        player_id         = d["player_id"],
        game_id           = d["game_id"],
        passing_yards     = d.get("passing_yards", 0),
        rushing_yards     = d.get("rushing_yards", 0),
        receiving_yards   = d.get("receiving_yards", 0),
        tackles           = d.get("tackles", 0),
        sacks             = d.get("sacks", 0),
        interceptions     = d.get("interceptions", 0),
        touchdowns        = d.get("touchdowns", 0),
        field_goals_made  = d.get("field_goals_made", 0),
        extra_points_made = d.get("extra_points_made", 0),
    )
    db.session.add(s)
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
