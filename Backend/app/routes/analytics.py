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
    
    # Complex query with date calculations
    query = db.session.query(
        Injury.id,
        Player.name.label('player_name'),
        Player.position,
        Team.name.label('team_name'),
        Injury.description,
        Injury.severity,
        Injury.start_date,
        Injury.end_date,
        case(
            (Injury.end_date.is_(None), func.current_date() - Injury.start_date),
            else_=Injury.end_date - Injury.start_date
        ).label('duration_days')
    ).join(Player).join(Team)
    
    # Apply filters with proper SQL injection prevention
    if team_id:
        query = query.filter(Player.team_id == team_id)
    
    if active_only:
        query = query.filter(Injury.end_date.is_(None))
    
    if severity:
        query = query.filter(Injury.severity.like(f'%{severity}%'))
    
    query = query.order_by(Injury.start_date.desc())
    
    results = query.all()
    
    return jsonify([
        {
            'injury_id': row.id,
            'player_name': row.player_name,
            'position': row.position,
            'team_name': row.team_name,
            'description': row.description,
            'severity': row.severity,
            'start_date': row.start_date.isoformat() if row.start_date else None,
            'end_date': row.end_date.isoformat() if row.end_date else None,
            'duration_days': row.duration_days.days if row.duration_days else None,
            'is_active': row.end_date is None
        }
        for row in results
    ])

@analytics_bp.get("/sql-injection-demo")
@jwt_required()
def sql_injection_demo():
    """
    Demonstrates SQL injection prevention techniques.
    Shows both vulnerable and safe approaches for educational purposes.
    """
    team_name = request.args.get('team_name', '')
    
    # SAFE: Using SQLAlchemy ORM (parameterized queries)
    safe_results = Team.query.filter(Team.name.like(f'%{team_name}%')).all()
    
    # SAFE: Using text() with bound parameters (SQLite compatible)
    safe_sql_results = db.session.execute(
        text("SELECT * FROM team WHERE name LIKE :team_name"),
        {'team_name': f'%{team_name}%'}
    ).fetchall()
    
    return jsonify({
        'message': 'SQL Injection Prevention Demonstration',
        'user_input': team_name,
        'safe_orm_results': [{'id': t.id, 'name': t.name} for t in safe_results],
        'safe_sql_count': len(safe_sql_results),
        'explanation': {
            'orm_protection': 'SQLAlchemy ORM automatically escapes parameters',
            'bound_parameters': 'Using text() with bound parameters prevents injection',
            'never_do': 'Never concatenate user input directly into SQL strings',
            'example_attack': "'; DROP TABLE team; --",
            'why_safe': 'Parameters are escaped/quoted automatically by SQLAlchemy'
        }
    })