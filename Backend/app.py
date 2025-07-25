from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text

app = Flask(__name__)
CORS(app)

@app.route('/api/sports', methods=['GET'])
def get_team_data():
    # Get team name and week from query parameters
    team_name = request.args.get('team', '') 
    week = request.args.get('week')
    # If no team name is provided, return an error
    if not team_name:
        return jsonify({"error": "Team name is required"}), 400
    
    engine = create_engine('postgresql://postgres:@localhost:5432/sms')  # Change connection string
    with engine.connect() as conn:
    # Get the current week
        current_week_template = 'SELECT week_num from week order by week_num desc limit 1'
        current_week_result = conn.execute(text(current_week_template))
        current_week_row = current_week_result.fetchone()
        if current_week_row:
            current_week = current_week_row[0]
        is_venue = False
        if team_name:
    # Making sure the week is a valid input
            if week is not None and int(week) > 0 and int(week) <= int(current_week):
                if int(week) == int(current_week):
                    week_query = '''
                        SELECT week_id 
                        FROM week 
                        WHERE CAST(week_num AS INTEGER) = :current_week
                    '''
                    week_result = conn.execute(text(week_query), {'current_week': current_week})
                    week_row = week_result.fetchone()
                    if week_row:
                        week_id = week_row[0]
                        print(week_id)
                    is_venue = True
                    venue_id_query = '''
                        SELECT venue_id 
                        FROM game 
                        WHERE (home_team_name = :team_name OR away_team_name = :team_name) 
                        AND week_id = :week_id
                    '''
                    venue_id_result = conn.execute(text(venue_id_query), {'team_name': team_name, 'week_id': week_id})
                    venue_id_row = venue_id_result.fetchone()
                    if venue_id_row:
                        venue_id = venue_id_row[0]
                    
                    venue_query = '''
                        SELECT * 
                        FROM venue 
                        WHERE venue_id = :venue_id
                    '''
                    
                    game_query = '''
                        SELECT home_team_name, home_points, away_team_name, away_points 
                        FROM game 
                        WHERE (home_team_name = :team_name OR away_team_name = :team_name) 
                        AND week_id = :week_id
                    '''
                    game_result = conn.execute(text(game_query), {'team_name': team_name, 'week_id': week_id})

                else:
                    game_query = '''
                        SELECT * 
                        FROM game 
                        WHERE (home_team_name = :team_name OR away_team_name = :team_name) 
                        AND (home_team_games_played = :week OR away_team_games_played = :week)
                    '''
                    game_result = conn.execute(text(game_query), {'team_name': team_name, 'week': week})
            else:
                game_query = '''
                            SELECT * 
                            FROM game 
                            WHERE (home_team_name = :team_name OR away_team_name = :team_name) 
                            
                        '''
                game_result = conn.execute(text(game_query), {'team_name': team_name})
                    # Now, execute the venue_query after retrieving the venue_id
    
        if is_venue:
            venue_result = conn.execute(text(venue_query), {'venue_id': venue_id})
            venue = [dict(row) for row in venue_result.mappings()]
            data = [dict(row) for row in game_result.mappings()]
            print(data,venue)
            return jsonify({"venue": venue, "game_data": data})
        
        else :
            data = [dict(row) for row in game_result.mappings()]
            print(data)
        return jsonify({"game_data": data})


if __name__ == '__main__':
    app.run(debug=True, port=5000)