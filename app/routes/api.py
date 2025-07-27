from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.team import Team, Player
from app.models.match import Match, PlayerPerformance
from app.models.auction import Auction, AuctionLot, AuctionBid
from app.routes.auth import token_required

api_bp = Blueprint('api', __name__)

# Team Routes
@api_bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'short_name': team.short_name,
        'logo_url': team.logo_url,
        'home_ground': team.home_ground,
        'total_matches': team.total_matches,
        'wins': team.wins,
        'losses': team.losses,
        'win_percentage': team.win_percentage
    } for team in teams])

@api_bp.route('/teams/<int:team_id>', methods=['GET'])
def get_team(team_id):
    team = Team.get_by_id(team_id)
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    
    players = [{
        'id': player.id,
        'name': player.name,
        'role': player.role,
        'nationality': player.nationality,
        'batting_style': player.batting_style,
        'bowling_style': player.bowling_style,
        'batting_average': player.batting_average,
        'bowling_average': player.bowling_average
    } for player in team.players]
    
    return jsonify({
        'id': team.id,
        'name': team.name,
        'short_name': team.short_name,
        'logo_url': team.logo_url,
        'home_ground': team.home_ground,
        'total_matches': team.total_matches,
        'wins': team.wins,
        'losses': team.losses,
        'win_percentage': team.win_percentage,
        'players': players
    })

# Player Routes
@api_bp.route('/players', methods=['GET'])
def get_players():
    role = request.args.get('role')
    nationality = request.args.get('nationality')
    
    query = Player.query
    if role:
        query = query.filter_by(role=role)
    if nationality:
        query = query.filter_by(nationality=nationality)
    
    players = query.all()
    return jsonify([{
        'id': player.id,
        'name': player.name,
        'team': player.team.name if player.team else None,
        'role': player.role,
        'nationality': player.nationality,
        'batting_style': player.batting_style,
        'bowling_style': player.bowling_style,
        'batting_average': player.batting_average,
        'bowling_average': player.bowling_average
    } for player in players])

@api_bp.route('/players/<int:player_id>', methods=['GET'])
def get_player(player_id):
    player = Player.get_by_id(player_id)
    if not player:
        return jsonify({'message': 'Player not found'}), 404
    
    return jsonify({
        'id': player.id,
        'name': player.name,
        'team': player.team.name if player.team else None,
        'role': player.role,
        'nationality': player.nationality,
        'batting_style': player.batting_style,
        'bowling_style': player.bowling_style,
        'batting_average': player.batting_average,
        'bowling_average': player.bowling_average,
        'strike_rate': player.strike_rate,
        'economy_rate': player.economy_rate,
        'matches_played': player.matches_played,
        'runs_scored': player.runs_scored,
        'wickets_taken': player.wickets_taken,
        'catches': player.catches,
        'stumpings': player.stumpings
    })

@api_bp.route('/players/search', methods=['GET'])
def search_players():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    players = Player.query.filter(Player.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{
        'id': player.id,
        'name': player.name,
        'team': player.team.name if player.team else None,
        'role': player.role
    } for player in players])

# Match Routes
@api_bp.route('/matches', methods=['GET'])
def get_matches():
    season = request.args.get('season')
    team_id = request.args.get('team_id')
    
    query = Match.query
    if season:
        query = query.filter_by(season=season)
    if team_id:
        query = query.filter((Match.team1_id == team_id) | (Match.team2_id == team_id))
    
    matches = query.order_by(Match.match_date.desc()).all()
    return jsonify([{
        'id': match.id,
        'match_date': match.match_date.isoformat(),
        'venue': match.venue,
        'team1': {
            'id': match.team1.id,
            'name': match.team1.name,
            'score': match.team1_score,
            'overs': match.team1_overs,
            'wickets': match.team1_wickets
        },
        'team2': {
            'id': match.team2.id,
            'name': match.team2.name,
            'score': match.team2_score,
            'overs': match.team2_overs,
            'wickets': match.team2_wickets
        },
        'result': match.result,
        'season': match.season,
        'match_type': match.match_type
    } for match in matches])

@api_bp.route('/matches/<int:match_id>', methods=['GET'])
def get_match(match_id):
    match = Match.get_by_id(match_id)
    if not match:
        return jsonify({'message': 'Match not found'}), 404
    
    performances = [{
        'player': {
            'id': perf.player.id,
            'name': perf.player.name,
            'team': perf.player.team.name if perf.player.team else None
        },
        'runs_scored': perf.runs_scored,
        'balls_faced': perf.balls_faced,
        'fours': perf.fours,
        'sixes': perf.sixes,
        'wickets_taken': perf.wickets_taken,
        'overs_bowled': perf.overs_bowled,
        'runs_conceded': perf.runs_conceded,
        'catches': perf.catches,
        'stumpings': perf.stumpings
    } for perf in match.performances]
    
    return jsonify({
        'id': match.id,
        'match_date': match.match_date.isoformat(),
        'venue': match.venue,
        'team1': {
            'id': match.team1.id,
            'name': match.team1.name,
            'score': match.team1_score,
            'overs': match.team1_overs,
            'wickets': match.team1_wickets
        },
        'team2': {
            'id': match.team2.id,
            'name': match.team2.name,
            'score': match.team2_score,
            'overs': match.team2_overs,
            'wickets': match.team2_wickets
        },
        'result': match.result,
        'season': match.season,
        'match_type': match.match_type,
        'performances': performances
    })

# Auction Routes
@api_bp.route('/auctions', methods=['GET'])
@token_required
def get_auctions(current_user):
    season = request.args.get('season')
    status = request.args.get('status')
    
    query = Auction.query
    if season:
        query = query.filter_by(season=season)
    if status:
        query = query.filter_by(status=status)
    
    auctions = query.order_by(Auction.auction_date.desc()).all()
    return jsonify([{
        'id': auction.id,
        'season': auction.season,
        'auction_date': auction.auction_date.isoformat(),
        'venue': auction.venue,
        'status': auction.status,
        'total_value': auction.total_value
    } for auction in auctions])

@api_bp.route('/auctions/<int:auction_id>/lots', methods=['GET'])
@token_required
def get_auction_lots(current_user, auction_id):
    auction = Auction.get_by_id(auction_id)
    if not auction:
        return jsonify({'message': 'Auction not found'}), 404
    
    lots = AuctionLot.query.filter_by(auction_id=auction_id).all()
    return jsonify([{
        'id': lot.id,
        'player': {
            'id': lot.player.id,
            'name': lot.player.name,
            'role': lot.player.role,
            'nationality': lot.player.nationality
        },
        'base_price': lot.base_price,
        'sold_price': lot.sold_price,
        'status': lot.status,
        'sold_to_team': lot.sold_to_team.name if lot.sold_to_team else None,
        'current_highest_bid': lot.current_highest_bid,
        'current_highest_bidder': lot.current_highest_bidder.name if lot.current_highest_bidder else None
    } for lot in lots])



@api_bp.route('/auctions/<int:auction_id>/bid', methods=['POST'])
@token_required
def place_bid(current_user, auction_id):
    if not current_user.is_team_owner():
        return jsonify({'message': 'Only team owners can place bids'}), 403
    
    team = Team.get_by_owner(current_user.id)
    if not team:
        return jsonify({'message': 'You do not own a team'}), 403
    
    auction = Auction.get_by_id(auction_id)
    if not auction:
        return jsonify({'message': 'Auction not found'}), 404
    
    if auction.status != 'ongoing':
        return jsonify({'message': 'Auction is not active'}), 400
    
    data = request.get_json()
    lot_id = data.get('lot_id')
    bid_amount = data.get('bid_amount')
    
    if not lot_id or not bid_amount:
        return jsonify({'message': 'Missing lot_id or bid_amount'}), 400
    
    lot = AuctionLot.get_by_id(lot_id)
    if not lot:
        return jsonify({'message': 'Lot not found'}), 404
    
    if lot.auction_id != auction_id:
        return jsonify({'message': 'Lot does not belong to this auction'}), 400
    
    if lot.status != 'unsold':
        return jsonify({'message': 'Lot is already sold'}), 400
    
    if bid_amount <= lot.current_highest_bid:
        return jsonify({'message': 'Bid must be higher than current highest bid'}), 400
    
    bid = AuctionBid(
        lot_id=lot_id,
        team_id=team.id,
        bid_amount=bid_amount
    )
    
    db.session.add(bid)
    db.session.commit()
    
    return jsonify({
        'message': 'Bid placed successfully',
        'bid': {
            'id': bid.id,
            'lot_id': bid.lot_id,
            'team_id': bid.team_id,
            'bid_amount': bid.bid_amount,
            'created_at': bid.created_at.isoformat()
        }
    })

@api_bp.route('/dashboard-data')
def get_dashboard_data():
    year = request.args.get('year', 'all')
    
    # Base queries
    matches_query = Match.query
    players_query = Player.query
    
    # Filter by year if specified
    if year != 'all':
        matches_query = matches_query.filter(Match.season == year)
        players_query = players_query.join(PlayerPerformance).join(Match).filter(Match.season == year)
    
    # Basic Statistics
    total_matches = matches_query.count()
    total_runs = db.session.query(db.func.sum(PlayerPerformance.runs_scored)).scalar() or 0
    total_wickets = db.session.query(db.func.sum(PlayerPerformance.wickets_taken)).scalar() or 0
    avg_runs_per_match = round(total_runs / total_matches if total_matches > 0 else 0, 2)
    
    # Team Statistics
    teams = Team.query.all()
    team_names = [team.name for team in teams]
    team_wins = [team.wins for team in teams]
    team_losses = [team.losses for team in teams]
    
    # Match Outcomes
    match_outcomes = [
        matches_query.filter(Match.result.like('%won by batting%')).count(),
        matches_query.filter(Match.result.like('%won by bowling%')).count(),
        matches_query.filter(Match.result == 'No Result').count()
    ]
    
    # Batting Statistics
    top_batsmen = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.runs_scored).label('total_runs'),
        db.func.count(PlayerPerformance.id).label('matches_played'),
        db.func.avg(PlayerPerformance.runs_scored).label('batting_avg'),
        db.func.sum(PlayerPerformance.balls_faced).label('total_balls'),
        db.func.sum(PlayerPerformance.fours).label('total_fours'),
        db.func.sum(PlayerPerformance.sixes).label('total_sixes')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .order_by(db.desc('total_runs'))
    .limit(5)
    .all())
    
    top_batsmen_data = [{
        'name': player.name,
        'runs': runs,
        'matches': matches,
        'average': round(float(avg), 2),
        'strike_rate': round((runs / balls * 100) if balls > 0 else 0, 2),
        'fours': fours,
        'sixes': sixes
    } for player, runs, matches, avg, balls, fours, sixes in top_batsmen]
    
    # Bowling Statistics
    top_bowlers = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.wickets_taken).label('total_wickets'),
        db.func.sum(PlayerPerformance.runs_conceded).label('total_runs'),
        db.func.sum(PlayerPerformance.overs_bowled).label('total_overs'),
        db.func.avg(PlayerPerformance.wickets_taken).label('wickets_per_match')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .order_by(db.desc('total_wickets'))
    .limit(5)
    .all())
    
    top_bowlers_data = [{
        'name': player.name,
        'wickets': wickets,
        'runs': runs,
        'overs': overs,
        'average': round((runs / wickets) if wickets > 0 else 0, 2),
        'economy': round((runs / overs) if overs > 0 else 0, 2),
        'wickets_per_match': round(float(wpm), 2)
    } for player, wickets, runs, overs, wpm in top_bowlers]
    
    # Fielding Statistics
    top_fielders = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.catches).label('total_catches'),
        db.func.sum(PlayerPerformance.stumpings).label('total_stumpings')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .order_by(db.desc('total_catches'))
    .limit(5)
    .all())
    
    top_fielders_data = [{
        'name': player.name,
        'catches': catches,
        'stumpings': stumpings,
        'total_dismissals': catches + stumpings
    } for player, catches, stumpings in top_fielders]
    
    # Match Statistics
    highest_totals = (db.session.query(
        Match,
        db.func.greatest(Match.team1_score, Match.team2_score).label('highest_score')
    )
    .order_by(db.desc('highest_score'))
    .limit(5)
    .all())
    
    highest_totals_data = [{
        'team1': match.team1.name,
        'team2': match.team2.name,
        'score': score,
        'date': match.match_date.strftime('%d %b %Y')
    } for match, score in highest_totals]
    
    # Player Value Statistics
    top_values = (db.session.query(
        Player,
        db.func.max(AuctionLot.sold_price).label('max_value')
    )
    .join(AuctionLot)
    .group_by(Player.id)
    .order_by(db.desc('max_value'))
    .limit(5)
    .all())
    
    top_values_data = [{
        'name': player.name,
        'value': value
    } for player, value in top_values]
    
    # Additional Insights
    # 1. Best Strike Rates
    best_strike_rates = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.runs_scored).label('runs'),
        db.func.sum(PlayerPerformance.balls_faced).label('balls'),
        db.func.count(PlayerPerformance.id).label('matches')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .having(db.func.sum(PlayerPerformance.balls_faced) > 100)
    .order_by(db.desc(db.func.sum(PlayerPerformance.runs_scored) * 100 / db.func.sum(PlayerPerformance.balls_faced)))
    .limit(5)
    .all())
    
    best_strike_rates_data = [{
        'name': player.name,
        'strike_rate': round((runs / balls * 100) if balls > 0 else 0, 2),
        'runs': runs,
        'matches': matches
    } for player, runs, balls, matches in best_strike_rates]
    
    # 2. Best Economy Rates
    best_economy_rates = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.runs_conceded).label('runs'),
        db.func.sum(PlayerPerformance.overs_bowled).label('overs'),
        db.func.count(PlayerPerformance.id).label('matches')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .having(db.func.sum(PlayerPerformance.overs_bowled) > 20)
    .order_by(db.func.sum(PlayerPerformance.runs_conceded) / db.func.sum(PlayerPerformance.overs_bowled))
    .limit(5)
    .all())
    
    best_economy_rates_data = [{
        'name': player.name,
        'economy': round((runs / overs) if overs > 0 else 0, 2),
        'matches': matches
    } for player, runs, overs, matches in best_economy_rates]
    
    # 3. Most Consistent Batsmen (Lowest Standard Deviation)
    consistent_batsmen = (db.session.query(
        Player,
        db.func.avg(PlayerPerformance.runs_scored).label('avg_runs'),
        db.func.stddev(PlayerPerformance.runs_scored).label('std_dev'),
        db.func.count(PlayerPerformance.id).label('matches')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .having(db.func.count(PlayerPerformance.id) > 5)
    .order_by(db.func.stddev(PlayerPerformance.runs_scored))
    .limit(5)
    .all())
    
    consistent_batsmen_data = [{
        'name': player.name,
        'average': round(float(avg), 2),
        'std_dev': round(float(std_dev), 2),
        'matches': matches
    } for player, avg, std_dev, matches in consistent_batsmen]
    
    # 4. Most Valuable Players (Performance per Match)
    mvp_candidates = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.runs_scored).label('runs'),
        db.func.sum(PlayerPerformance.wickets_taken).label('wickets'),
        db.func.count(PlayerPerformance.id).label('matches')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .having(db.func.count(PlayerPerformance.id) > 5)
    .order_by(db.desc((db.func.sum(PlayerPerformance.runs_scored) + db.func.sum(PlayerPerformance.wickets_taken) * 25) / db.func.count(PlayerPerformance.id)))
    .limit(5)
    .all())
    
    mvp_candidates_data = [{
        'name': player.name,
        'runs': runs,
        'wickets': wickets,
        'matches': matches,
        'impact_per_match': round((runs + wickets * 25) / matches, 2)
    } for player, runs, wickets, matches in mvp_candidates]
    
    # 5. Best All-rounders
    all_rounders = (db.session.query(
        Player,
        db.func.sum(PlayerPerformance.runs_scored).label('runs'),
        db.func.sum(PlayerPerformance.wickets_taken).label('wickets'),
        db.func.count(PlayerPerformance.id).label('matches')
    )
    .join(PlayerPerformance)
    .group_by(Player.id)
    .having(db.func.sum(PlayerPerformance.runs_scored) > 500)
    .having(db.func.sum(PlayerPerformance.wickets_taken) > 10)
    .order_by(db.desc(db.func.sum(PlayerPerformance.runs_scored) + db.func.sum(PlayerPerformance.wickets_taken) * 25))
    .limit(5)
    .all())
    
    all_rounders_data = [{
        'name': player.name,
        'runs': runs,
        'wickets': wickets,
        'matches': matches,
        'all_round_score': runs + wickets * 25
    } for player, runs, wickets, matches in all_rounders]
    
    return jsonify({
        'basic_stats': {
            'total_matches': total_matches,
            'total_runs': total_runs,
            'total_wickets': total_wickets,
            'avg_runs_per_match': avg_runs_per_match
        },
        'team_stats': {
            'names': team_names,
            'wins': team_wins,
            'losses': team_losses
        },
        'match_outcomes': match_outcomes,
        'batting_stats': {
            'top_batsmen': top_batsmen_data,
            'highest_totals': highest_totals_data,
            'best_strike_rates': best_strike_rates_data,
            'consistent_batsmen': consistent_batsmen_data
        },
        'bowling_stats': {
            'top_bowlers': top_bowlers_data,
            'best_economy_rates': best_economy_rates_data
        },
        'fielding_stats': {
            'top_fielders': top_fielders_data
        },
        'value_stats': {
            'top_values': top_values_data,
            'mvp_candidates': mvp_candidates_data,
            'all_rounders': all_rounders_data
        }
    })

@api_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search_results.html', teams=[], players=[], matches=[], query=query)
    
    # Search in teams
    teams = Team.query.filter(
        (Team.name.ilike(f'%{query}%')) |
        (Team.short_name.ilike(f'%{query}%'))
    ).all()
    
    # Search in players
    players = Player.query.filter(
        (Player.name.ilike(f'%{query}%')) |
        (Player.role.ilike(f'%{query}%')) |
        (Player.nationality.ilike(f'%{query}%'))
    ).all()
    
    # Search in matches
    matches = Match.query.filter(
        (Match.venue.ilike(f'%{query}%')) |
        (Match.team1_score.ilike(f'%{query}%')) |
        (Match.team2_score.ilike(f'%{query}%'))
    ).all()
    
    return render_template('search_results.html',
                         teams=teams,
                         players=players,
                         matches=matches,
                         query=query) 


# @api_bp.route('/myteam', methods=['GET'])
# def my_team():
#     season = request.args.get('season')
#     team_id = request.args.get('team_id')
    
#     query = Match.query
#     if season:
#         query = query.filter_by(season=season)
#     if team_id:
#         query = query.filter((Match.team1_id == team_id) | (Match.team2_id == team_id))
    
#     matches = query.order_by(Match.match_date.desc()).all()
#     return jsonify([{
#         'id': match.id,
#         'match_date': match.match_date.isoformat(),
#         'venue': match.venue,
#         'team1': {
#             'id': match.team1.id,
#             'name': match.team1.name,
#             'score': match.team1_score,
#             'overs': match.team1_overs,
#             'wickets': match.team1_wickets
#         },
#         'team2': {
#             'id': match.team2.id,
#             'name': match.team2.name,
#             'score': match.team2_score,
#             'overs': match.team2_overs,
#             'wickets': match.team2_wickets
#         },
#         'result': match.result,
#         'season': match.season,
#         'match_type': match.match_type
#     } for match in matches])


