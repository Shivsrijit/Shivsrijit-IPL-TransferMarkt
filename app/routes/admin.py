from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.extensions import db
from app.models.user import User
from app.models.team import Team, Player
from app.models.match import Match, PlayerPerformance
from app.models.auction import Auction, AuctionLot, AuctionBid

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_teams = Team.query.count()
    total_players = Player.query.count()
    total_matches = Match.query.count()
    total_auctions = Auction.query.count()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_teams=total_teams,
                          total_players=total_players,
                          total_matches=total_matches,
                          total_auctions=total_auctions)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'role' in data:
        user.role = data['role']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully'})

@admin_bp.route('/teams')
@login_required
@admin_required
def manage_teams():
    teams = Team.query.all()
    return render_template('admin/teams.html', teams=teams)

@admin_bp.route('/teams', methods=['POST'])
@login_required
@admin_required
def create_team():
    data = request.get_json()
    
    if Team.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Team name already exists'}), 400
    
    if Team.query.filter_by(short_name=data['short_name']).first():
        return jsonify({'message': 'Team short name already exists'}), 400
    
    team = Team(
        name=data['name'],
        short_name=data['short_name'],
        owner_id=data.get('owner_id'),
        logo_url=data.get('logo_url'),
        home_ground=data.get('home_ground')
    )
    
    db.session.add(team)
    db.session.commit()
    
    return jsonify({'message': 'Team created successfully', 'team_id': team.id}), 201

@admin_bp.route('/teams/<int:team_id>', methods=['PUT'])
@login_required
@admin_required
def update_team(team_id):
    team = Team.get_by_id(team_id)
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data and data['name'] != team.name:
        if Team.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'Team name already exists'}), 400
        team.name = data['name']
    
    if 'short_name' in data and data['short_name'] != team.short_name:
        if Team.query.filter_by(short_name=data['short_name']).first():
            return jsonify({'message': 'Team short name already exists'}), 400
        team.short_name = data['short_name']
    
    if 'owner_id' in data:
        team.owner_id = data['owner_id']
    
    if 'logo_url' in data:
        team.logo_url = data['logo_url']
    
    if 'home_ground' in data:
        team.home_ground = data['home_ground']
    
    db.session.commit()
    
    return jsonify({'message': 'Team updated successfully'})

@admin_bp.route('/players')
@login_required
@admin_required
def manage_players():
    players = Player.query.all()
    return render_template('admin/players.html', players=players)

@admin_bp.route('/players', methods=['POST'])
@login_required
@admin_required
def create_player():
    data = request.get_json()
    
    player = Player(
        name=data['name'],
        team_id=data.get('team_id'),
        role=data['role'],
        nationality=data['nationality'],
        batting_style=data.get('batting_style'),
        bowling_style=data.get('bowling_style')
    )
    
    db.session.add(player)
    db.session.commit()
    
    return jsonify({'message': 'Player created successfully', 'player_id': player.id}), 201

@admin_bp.route('/players/<int:player_id>', methods=['PUT'])
@login_required
@admin_required
def update_player(player_id):
    player = Player.get_by_id(player_id)
    if not player:
        return jsonify({'message': 'Player not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        player.name = data['name']
    
    if 'team_id' in data:
        player.team_id = data['team_id']
    
    if 'role' in data:
        player.role = data['role']
    
    if 'nationality' in data:
        player.nationality = data['nationality']
    
    if 'batting_style' in data:
        player.batting_style = data['batting_style']
    
    if 'bowling_style' in data:
        player.bowling_style = data['bowling_style']
    
    db.session.commit()
    
    return jsonify({'message': 'Player updated successfully'})

@admin_bp.route('/matches')
@login_required
@admin_required
def manage_matches():
    matches = Match.query.order_by(Match.match_date.desc()).all()
    return render_template('admin/matches.html', matches=matches)

@admin_bp.route('/matches', methods=['POST'])
@login_required
@admin_required
def create_match():
    data = request.get_json()
    
    match = Match(
        match_date=data['match_date'],
        venue=data['venue'],
        team1_id=data['team1_id'],
        team2_id=data['team2_id'],
        season=data['season'],
        match_type=data.get('match_type', 'league')
    )
    
    db.session.add(match)
    db.session.commit()
    
    return jsonify({'message': 'Match created successfully', 'match_id': match.id}), 201

@admin_bp.route('/matches/<int:match_id>/performances', methods=['POST'])
@login_required
@admin_required
def add_match_performance(match_id):
    match = Match.get_by_id(match_id)
    if not match:
        return jsonify({'message': 'Match not found'}), 404
    
    data = request.get_json()
    
    performance = PlayerPerformance(
        match_id=match_id,
        player_id=data['player_id'],
        runs_scored=data.get('runs_scored', 0),
        balls_faced=data.get('balls_faced', 0),
        fours=data.get('fours', 0),
        sixes=data.get('sixes', 0),
        wickets_taken=data.get('wickets_taken', 0),
        overs_bowled=data.get('overs_bowled', 0),
        runs_conceded=data.get('runs_conceded', 0),
        catches=data.get('catches', 0),
        stumpings=data.get('stumpings', 0)
    )
    
    db.session.add(performance)
    db.session.commit()
    
    return jsonify({'message': 'Performance added successfully', 'performance_id': performance.id}), 201

@admin_bp.route('/auctions')
@login_required
@admin_required
def manage_auctions():
    auctions = Auction.query.order_by(Auction.auction_date.desc()).all()
    return render_template('admin/auctions.html', auctions=auctions)

@admin_bp.route('/auctions', methods=['POST'])
@login_required
@admin_required
def create_auction():
    data = request.get_json()
    
    auction = Auction(
        season=data['season'],
        auction_date=data['auction_date'],
        venue=data['venue'],
        status=data.get('status', 'upcoming')
    )
    
    db.session.add(auction)
    db.session.commit()
    
    return jsonify({'message': 'Auction created successfully', 'auction_id': auction.id}), 201

@admin_bp.route('/auctions/<int:auction_id>/lots', methods=['POST'])
@login_required
@admin_required
def add_auction_lot(auction_id):
    auction = Auction.get_by_id(auction_id)
    if not auction:
        return jsonify({'message': 'Auction not found'}), 404
    
    data = request.get_json()
    
    lot = AuctionLot(
        auction_id=auction_id,
        player_id=data['player_id'],
        base_price=data['base_price']
    )
    
    db.session.add(lot)
    db.session.commit()
    
    return jsonify({'message': 'Lot added successfully', 'lot_id': lot.id}), 201

@admin_bp.route('/import-data', methods=['POST'])
@login_required
@admin_required
def import_data():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    # Process the file based on its type
    # This is a placeholder for the actual implementation
    try:
        # Import logic here
        return jsonify({'message': 'Data imported successfully'})
    except Exception as e:
        return jsonify({'message': f'Error importing data: {str(e)}'}), 500

@admin_bp.route('/export-data', methods=['GET'])
@login_required
@admin_required
def export_data():
    data_type = request.args.get('type', 'all')
    format = request.args.get('format', 'json')
    
    # Export logic based on data_type and format
    # This is a placeholder for the actual implementation
    try:
        # Export logic here
        return jsonify({'message': 'Data exported successfully'})
    except Exception as e:
        return jsonify({'message': f'Error exporting data: {str(e)}'}), 500 