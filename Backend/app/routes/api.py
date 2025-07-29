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
    return jsonify([
        {"id": t.id, "name": t.name, "league_id": t.league_id}
        for t in Team.query.all()
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
    return jsonify([
        {"id": p.id, "name": p.name, "team_id": p.team_id}
        for p in Player.query.all()
    ])

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
    return jsonify([
        {
            "id": g.id,
            "league_id": g.league_id,
            "season_year": g.season_year,
            "week": g.week,
            "home_team_id": g.home_team_id,
            "away_team_id": g.away_team_id,
            "venue": g.venue,
            "game_date": g.game_date.isoformat(),
            "home_score": g.home_score,
            "away_score": g.away_score,
            "attendance": g.attendance,
        }
        for g in Game.query.all()
    ])

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
    return jsonify([
        {
            "player_id": s.player_id,
            "game_id": s.game_id,
            "passing_yards": s.passing_yards,
            "rushing_yards": s.rushing_yards,
            "receiving_yards": s.receiving_yards,
            "tackles": s.tackles,
            "sacks": s.sacks,
            "interceptions": s.interceptions,
            "touchdowns": s.touchdowns,
            "field_goals_made": s.field_goals_made,
            "extra_points_made": s.extra_points_made,
        }
        for s in PlayerGameStats.query.all()
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
