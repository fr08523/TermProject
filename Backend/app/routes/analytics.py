from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import text, func, and_, or_, case
from app import db
from app.models.models import (
    League, Team, Player, Game, PlayerGameStats, Injury, PlayerSalary
)

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.get("/team-performance")
@jwt_required()
def team_performance():
    """
    Demonstrate complex SQL queries for team performance analytics.
    Shows SQL injection prevention by using SQLAlchemy ORM and parameterized queries.
    """
    season_year = request.args.get('season_year', type=int)
    league_id = request.args.get('league_id', type=int)
    
    # Simpler query that works with SQLite
    teams = Team.query.join(League).all()
    
    result = []
    for team in teams:
        # Apply league filter
        if league_id and team.league_id != league_id:
            continue
            
        # Get games for this team
        home_games = Game.query.filter_by(home_team_id=team.id)
        away_games = Game.query.filter_by(away_team_id=team.id)
        
        # Apply season filter
        if season_year:
            home_games = home_games.filter_by(season_year=season_year)
            away_games = away_games.filter_by(season_year=season_year)
        
        home_games = home_games.all()
        away_games = away_games.all()
        
        # Calculate stats
        total_games = len(home_games) + len(away_games)
        
        home_wins = sum(1 for g in home_games if g.home_score and g.away_score and g.home_score > g.away_score)
        away_wins = sum(1 for g in away_games if g.home_score and g.away_score and g.away_score > g.home_score)
        total_wins = home_wins + away_wins
        
        home_points = sum(g.home_score or 0 for g in home_games)
        away_points = sum(g.away_score or 0 for g in away_games)
        avg_points = (home_points + away_points) / max(total_games, 1)
        
        total_attendance = sum(g.attendance or 0 for g in home_games + away_games)
        avg_attendance = total_attendance / max(total_games, 1)
        
        result.append({
            'team_id': team.id,
            'team_name': team.name,
            'home_city': team.home_city,
            'league_name': team.league.name,
            'games_played': total_games,
            'wins': total_wins,
            'losses': total_games - total_wins,
            'win_percentage': round((total_wins / max(total_games, 1)) * 100, 1),
            'avg_points_scored': round(avg_points, 1),
            'avg_attendance': round(avg_attendance, 0)
        })
    
    return jsonify(result)

@analytics_bp.get("/player-stats")
@jwt_required()
def player_statistics():
    """
    Complex query demonstrating JOIN operations and aggregations
    with proper SQL injection prevention.
    """
    team_id = request.args.get('team_id', type=int)
    position = request.args.get('position', type=str)
    min_games = request.args.get('min_games', type=int, default=1)
    
    # Complex query with multiple JOINs and aggregations
    query = db.session.query(
        Player.id,
        Player.name,
        Player.position,
        Team.name.label('team_name'),
        func.count(PlayerGameStats.game_id).label('games_played'),
        func.sum(PlayerGameStats.passing_yards).label('total_passing_yards'),
        func.sum(PlayerGameStats.rushing_yards).label('total_rushing_yards'),
        func.sum(PlayerGameStats.receiving_yards).label('total_receiving_yards'),
        func.sum(PlayerGameStats.touchdowns).label('total_touchdowns'),
        func.avg(PlayerGameStats.passing_yards).label('avg_passing_yards'),
        func.count(Injury.id).label('injury_count')
    ).join(Team).left_outer_join(
        PlayerGameStats, PlayerGameStats.player_id == Player.id
    ).left_outer_join(
        Injury, Injury.player_id == Player.id
    )
    
    # Apply filters safely
    if team_id:
        query = query.filter(Player.team_id == team_id)
    if position:
        # Safe parameter binding prevents SQL injection
        query = query.filter(Player.position.like(f'%{position}%'))
    
    query = query.group_by(
        Player.id, Player.name, Player.position, Team.name
    ).having(
        func.count(PlayerGameStats.game_id) >= min_games
    ).order_by(
        func.sum(PlayerGameStats.touchdowns).desc()
    )
    
    results = query.all()
    
    return jsonify([
        {
            'player_id': row.id,
            'player_name': row.name,
            'position': row.position,
            'team_name': row.team_name,
            'games_played': row.games_played,
            'total_passing_yards': int(row.total_passing_yards or 0),
            'total_rushing_yards': int(row.total_rushing_yards or 0),
            'total_receiving_yards': int(row.total_receiving_yards or 0),
            'total_touchdowns': int(row.total_touchdowns or 0),
            'avg_passing_yards': round(float(row.avg_passing_yards or 0), 1),
            'injury_count': row.injury_count
        }
        for row in results
    ])

@analytics_bp.post("/bulk-game-stats")
@jwt_required()
def create_bulk_game_stats():
    """
    Demonstrate database transactions for bulk operations.
    Shows proper transaction handling and rollback on errors.
    """
    data = request.get_json()
    game_id = data.get('game_id')
    player_stats = data.get('player_stats', [])
    
    if not game_id or not player_stats:
        return jsonify({'error': 'game_id and player_stats are required'}), 400
    
    try:
        # Start transaction (SQLAlchemy handles this automatically)
        with db.session.begin():
            # Verify game exists
            game = Game.query.get(game_id)
            if not game:
                return jsonify({'error': 'Game not found'}), 404
            
            created_stats = []
            
            for stat_data in player_stats:
                # Validate player exists and belongs to one of the teams in the game
                player = Player.query.get(stat_data.get('player_id'))
                if not player:
                    raise ValueError(f"Player {stat_data.get('player_id')} not found")
                
                if player.team_id not in [game.home_team_id, game.away_team_id]:
                    raise ValueError(f"Player {player.name} does not belong to teams in this game")
                
                # Check if stats already exist for this player/game combination
                existing_stats = PlayerGameStats.query.filter_by(
                    player_id=player.id,
                    game_id=game_id
                ).first()
                
                if existing_stats:
                    # Update existing stats
                    for key, value in stat_data.items():
                        if key != 'player_id' and hasattr(existing_stats, key):
                            setattr(existing_stats, key, value)
                    created_stats.append(existing_stats)
                else:
                    # Create new stats
                    stats = PlayerGameStats(
                        player_id=player.id,
                        game_id=game_id,
                        passing_yards=stat_data.get('passing_yards', 0),
                        rushing_yards=stat_data.get('rushing_yards', 0),
                        receiving_yards=stat_data.get('receiving_yards', 0),
                        tackles=stat_data.get('tackles', 0),
                        sacks=stat_data.get('sacks', 0),
                        interceptions=stat_data.get('interceptions', 0),
                        touchdowns=stat_data.get('touchdowns', 0),
                        field_goals_made=stat_data.get('field_goals_made', 0),
                        extra_points_made=stat_data.get('extra_points_made', 0)
                    )
                    db.session.add(stats)
                    created_stats.append(stats)
            
            # Update player career stats (demonstrates complex transaction)
            for stats in created_stats:
                player = Player.query.get(stats.player_id)
                player.career_passing_yards += stats.passing_yards
                player.career_rushing_yards += stats.rushing_yards
                player.career_receiving_yards += stats.receiving_yards
                player.career_tackles += stats.tackles
                player.career_sacks += stats.sacks
                player.career_interceptions += stats.interceptions
                player.career_touchdowns += stats.touchdowns
            
            # Commit happens automatically with the 'with' block
            
        return jsonify({
            'message': f'Successfully created/updated {len(created_stats)} player stats',
            'game_id': game_id,
            'stats_count': len(created_stats)
        }), 201
        
    except ValueError as e:
        # Transaction is automatically rolled back
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Transaction is automatically rolled back
        db.session.rollback()
        return jsonify({'error': 'Failed to create game stats'}), 500

@analytics_bp.get("/injury-report")
@jwt_required()
def injury_report():
    """
    Demonstrate advanced filtering and date calculations.
    Shows how to safely handle user input in date queries.
    """
    team_id = request.args.get('team_id', type=int)
    active_only = request.args.get('active_only', default='false').lower() == 'true'
    severity = request.args.get('severity', type=str)
    
    # Simplified query that works reliably
    query = db.session.query(Injury).join(Player).join(Team)
    
    # Apply filters with proper SQL injection prevention
    if team_id:
        query = query.filter(Player.team_id == team_id)
    
    if active_only:
        query = query.filter(Injury.end_date.is_(None))
    
    if severity:
        query = query.filter(Injury.severity.like(f'%{severity}%'))
    
    query = query.order_by(Injury.start_date.desc())
    
    results = query.all()
    
    injury_data = []
    for injury in results:
        # Calculate duration manually
        duration_days = None
        if injury.start_date:
            if injury.end_date:
                duration_days = (injury.end_date - injury.start_date).days
            else:
                from datetime import date
                duration_days = (date.today() - injury.start_date).days
        
        injury_data.append({
            'injury_id': injury.id,
            'player_name': injury.player.name,
            'position': injury.player.position,
            'team_name': injury.player.current_team.name,
            'description': injury.description,
            'severity': injury.severity,
            'start_date': injury.start_date.isoformat() if injury.start_date else None,
            'end_date': injury.end_date.isoformat() if injury.end_date else None,
            'duration_days': duration_days,
            'is_active': injury.end_date is None
        })
    
    return jsonify(injury_data)

@analytics_bp.get("/top-performers")
def top_performers():
    """
    Advanced analytics query for top performing players.
    Demonstrates complex aggregations and rankings.
    """
    # Get top passing leaders
    passing_leaders = db.session.query(
        Player.name,
        Player.position,
        Team.name.label('team_name'),
        func.sum(PlayerGameStats.passing_yards).label('total_passing'),
        func.count(PlayerGameStats.game_id).label('games_played'),
        func.avg(PlayerGameStats.passing_yards).label('avg_passing')
    ).join(Team, Player.team_id == Team.id)\
     .join(PlayerGameStats, Player.id == PlayerGameStats.player_id)\
     .filter(PlayerGameStats.passing_yards > 0)\
     .group_by(Player.id, Player.name, Player.position, Team.name)\
     .order_by(func.sum(PlayerGameStats.passing_yards).desc())\
     .limit(5).all()
    
    # Get top rushing leaders
    rushing_leaders = db.session.query(
        Player.name,
        Player.position,
        Team.name.label('team_name'),
        func.sum(PlayerGameStats.rushing_yards).label('total_rushing'),
        func.count(PlayerGameStats.game_id).label('games_played'),
        func.avg(PlayerGameStats.rushing_yards).label('avg_rushing')
    ).join(Team, Player.team_id == Team.id)\
     .join(PlayerGameStats, Player.id == PlayerGameStats.player_id)\
     .filter(PlayerGameStats.rushing_yards > 0)\
     .group_by(Player.id, Player.name, Player.position, Team.name)\
     .order_by(func.sum(PlayerGameStats.rushing_yards).desc())\
     .limit(5).all()
    
    return jsonify({
        "passing_leaders": [
            {
                "name": row.name,
                "position": row.position,
                "team": row.team_name,
                "total_yards": int(row.total_passing),
                "games_played": row.games_played,
                "avg_per_game": round(float(row.avg_passing), 1)
            }
            for row in passing_leaders
        ],
        "rushing_leaders": [
            {
                "name": row.name,
                "position": row.position,
                "team": row.team_name,
                "total_yards": int(row.total_rushing),
                "games_played": row.games_played,
                "avg_per_game": round(float(row.avg_rushing), 1)
            }
            for row in rushing_leaders
        ]
    })

@analytics_bp.get("/team-comparison")
def team_comparison():
    """
    Complex team comparison analytics with multiple metrics.
    Shows advanced database query capabilities.
    """
    teams = Team.query.all()
    comparison_data = []
    
    for team in teams:
        # Get offensive stats
        offensive_stats = db.session.query(
            func.avg(PlayerGameStats.passing_yards).label('avg_passing'),
            func.avg(PlayerGameStats.rushing_yards).label('avg_rushing'),
            func.avg(PlayerGameStats.touchdowns).label('avg_touchdowns'),
            func.count(PlayerGameStats.game_id).label('total_player_games')
        ).join(Player, PlayerGameStats.player_id == Player.id)\
         .filter(Player.team_id == team.id).first()
        
        # Get team record
        home_games = Game.query.filter_by(home_team_id=team.id).all()
        away_games = Game.query.filter_by(away_team_id=team.id).all()
        
        wins = (len([g for g in home_games if g.home_score and g.away_score and g.home_score > g.away_score]) +
                len([g for g in away_games if g.home_score and g.away_score and g.away_score > g.home_score]))
        
        total_games = len(home_games) + len(away_games)
        
        comparison_data.append({
            "team_name": team.name,
            "home_city": team.home_city,
            "total_games": total_games,
            "wins": wins,
            "losses": total_games - wins,
            "win_percentage": round((wins / max(total_games, 1)) * 100, 1),
            "avg_passing_per_game": round(float(offensive_stats.avg_passing or 0), 1),
            "avg_rushing_per_game": round(float(offensive_stats.avg_rushing or 0), 1),
            "avg_touchdowns_per_game": round(float(offensive_stats.avg_touchdowns or 0), 1),
            "total_player_games": offensive_stats.total_player_games or 0
        })
    
    # Sort by win percentage
    comparison_data.sort(key=lambda x: x['win_percentage'], reverse=True)
    
    return jsonify(comparison_data)