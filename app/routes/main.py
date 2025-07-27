from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.team import Team, Player
from app.models.match import Match, PlayerPerformance
from app.models.auction import Auction, AuctionLot
from app.models.user_team import UserTeam, UserTeamPlayer

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    try:
        # Get top batsmen with their statistics
        top_batsmen = (db.session.query(players)
                      .join(PlayerPerformance)
                      .group_by(Player.id)
                      .order_by(db.func.sum(PlayerPerformance.runs_scored).desc())
                      .limit(5)
                      .all())
        
        # Calculate batting statistics for each player
        for player in top_batsmen:
            performances = PlayerPerformance.query.filter_by(player_id=player.id).all()
            total_runs = sum(p.runs_scored or 0 for p in performances)
            total_balls = sum(p.balls_faced or 0 for p in performances)
            dismissals = sum(1 for p in performances if p.runs_scored is not None and p.runs_scored > 0)
            
            player.total_runs = total_runs
            player.batting_average = total_runs / dismissals if dismissals > 0 else 0
            player.strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0
        
        # Get top bowlers with their statistics
        top_bowlers = (db.session.query(Player)
                      .join(PlayerPerformance)
                      .group_by(Player.id)
                      .order_by(db.func.sum(PlayerPerformance.wickets_taken).desc())
                      .limit(5)
                      .all())
        
        # Calculate bowling statistics for each player
        for player in top_bowlers:
            performances = PlayerPerformance.query.filter_by(player_id=player.id).all()
            total_wickets = sum(p.wickets_taken or 0 for p in performances)
            total_runs = sum(p.runs_conceded or 0 for p in performances)
            total_overs = sum(p.overs_bowled or 0 for p in performances)
            
            player.total_wickets = total_wickets
            player.bowling_average = total_runs / total_wickets if total_wickets > 0 else 0
            player.economy_rate = total_runs / total_overs if total_overs > 0 else 0
        
        # Get top teams with their statistics
        top_teams = (db.session.query(Team)
                    .order_by(Team.wins.desc())
                    .limit(5)
                    .all())
        
        # Calculate team statistics
        for team in top_teams:
            matches = Match.query.filter(
                (Match.team1_id == team.id) | (Match.team2_id == team.id)
            ).all()
            
            team.total_matches = len(matches)
            team.wins = sum(1 for m in matches if m.winner and m.winner.id == team.id)
            team.win_percentage = (team.wins / team.total_matches * 100) if team.total_matches > 0 else 0
        
        # Get recent matches
        recent_matches = Match.query.order_by(Match.match_date.desc()).limit(5).all()
        
        return render_template('index.html',
                             top_batsmen=top_batsmen,
                             top_bowlers=top_bowlers,
                             top_teams=top_teams,
                             recent_matches=recent_matches)
    except Exception as e:
        # Log the error
        print(f"Error in index route: {str(e)}")
        # Return a simplified version of the page without data
        return render_template('index.html',
                             top_batsmen=[],
                             top_bowlers=[],
                             top_teams=[],
                             recent_matches=[])

@main_bp.route('/test')
def test():
    return render_template('test.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Basic statistics
    total_matches = Match.query.count()
    total_runs = db.session.query(db.func.sum(PlayerPerformance.runs)).scalar() or 0
    total_wickets = db.session.query(db.func.sum(PlayerPerformance.wickets)).scalar() or 0
    avg_runs_per_match = round(total_runs / total_matches, 2) if total_matches > 0 else 0

    # Team statistics
    teams = Team.query.all()
    team_stats = {
        'names': [team.name for team in teams],
        'wins': [Match.query.filter_by(winner_id=team.id).count() for team in teams],
        'losses': [Match.query.filter_by(loser_id=team.id).count() for team in teams],
        'win_percentages': [
            round((wins / (wins + losses) * 100) if (wins + losses) > 0 else 0, 2)
            for wins, losses in zip(
                [Match.query.filter_by(winner_id=team.id).count() for team in teams],
                [Match.query.filter_by(loser_id=team.id).count() for team in teams]
            )
        ]
    }

    # Match outcomes
    match_outcomes = {
        'batting_wins': Match.query.filter(Match.result.like('%won by batting%')).count(),
        'bowling_wins': Match.query.filter(Match.result.like('%won by bowling%')).count(),
        'no_results': Match.query.filter(Match.result == 'No Result').count(),
        'toss_wins': Match.query.filter(Match.toss_winner_id == Match.winner_id).count(),
        'toss_win_percentage': round((Match.query.filter(Match.toss_winner_id == Match.winner_id).count() / total_matches * 100) if total_matches > 0 else 0, 2)
    }

    # Batting statistics
    batting_stats = {
        'top_batsmen': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.runs).label('runs'),
            db.func.count(PlayerPerformance.id).label('matches'),
            db.func.avg(PlayerPerformance.runs).label('avg'),
            db.func.sum(PlayerPerformance.balls_faced).label('balls'),
            db.func.sum(PlayerPerformance.fours).label('fours'),
            db.func.sum(PlayerPerformance.sixes).label('sixes')
        ).join(PlayerPerformance).group_by(Player.id).order_by(db.desc('runs')).limit(5).all(),
        
        'best_strike_rates': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.runs).label('runs'),
            db.func.sum(PlayerPerformance.balls_faced).label('balls'),
            db.func.count(PlayerPerformance.id).label('matches')
        ).join(PlayerPerformance).group_by(Player.id).having(db.func.sum(PlayerPerformance.balls_faced) > 100).order_by(db.desc('runs * 100.0 / balls')).limit(5).all(),
        
        'most_boundaries': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.fours + PlayerPerformance.sixes).label('boundaries'),
            db.func.sum(PlayerPerformance.runs).label('runs')
        ).join(PlayerPerformance).group_by(Player.id).order_by(db.desc('boundaries')).limit(5).all()
    }

    # Bowling statistics
    bowling_stats = {
        'top_bowlers': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.wickets).label('wickets'),
            db.func.sum(PlayerPerformance.runs_conceded).label('runs'),
            db.func.sum(PlayerPerformance.overs_bowled).label('overs'),
            db.func.avg(PlayerPerformance.wickets).label('wickets_per_match')
        ).join(PlayerPerformance).group_by(Player.id).order_by(db.desc('wickets')).limit(5).all(),
        
        'best_economy': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.runs_conceded).label('runs'),
            db.func.sum(PlayerPerformance.overs_bowled).label('overs'),
            db.func.count(PlayerPerformance.id).label('matches')
        ).join(PlayerPerformance).group_by(Player.id).having(db.func.sum(PlayerPerformance.overs_bowled) > 10).order_by(db.asc('runs / overs')).limit(5).all(),
        
        'most_maidens': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.maidens).label('maidens'),
            db.func.sum(PlayerPerformance.overs_bowled).label('overs')
        ).join(PlayerPerformance).group_by(Player.id).order_by(db.desc('maidens')).limit(5).all()
    }

    # Fielding statistics
    fielding_stats = {
        'top_fielders': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.catches).label('catches'),
            db.func.sum(PlayerPerformance.stumpings).label('stumpings'),
            db.func.count(PlayerPerformance.id).label('matches')
        ).join(PlayerPerformance).group_by(Player.id).order_by(db.desc('catches + stumpings')).limit(5).all()
    }

    # Value statistics
    value_stats = {
        'highest_values': db.session.query(
            Player,
            db.func.max(AuctionLot.sold_price).label('value')
        ).join(AuctionLot).group_by(Player.id).order_by(db.desc('value')).limit(5).all(),
        
        'best_value_players': db.session.query(
            Player,
            db.func.sum(PlayerPerformance.runs).label('runs'),
            db.func.sum(PlayerPerformance.wickets).label('wickets'),
            db.func.max(AuctionLot.sold_price).label('value')
        ).join(PlayerPerformance).join(AuctionLot).group_by(Player.id).order_by(db.desc('(runs + wickets * 20) / value')).limit(5).all()
    }

    # Venue statistics
    venue_stats = {
        'highest_scores': db.session.query(
            Match.venue,
            db.func.max(Match.team1_score + Match.team2_score).label('total_runs')
        ).group_by(Match.venue).order_by(db.desc('total_runs')).limit(5).all(),
        
        'most_matches': db.session.query(
            Match.venue,
            db.func.count(Match.id).label('matches')
        ).group_by(Match.venue).order_by(db.desc('matches')).limit(5).all()
    }

    # Match type statistics
    match_type_stats = {
        'day_matches': Match.query.filter(Match.match_type == 'Day').count(),
        'night_matches': Match.query.filter(Match.match_type == 'Night').count(),
        'day_night_matches': Match.query.filter(Match.match_type == 'Day/Night').count()
    }

    return render_template('dashboard.html',
                         basic_stats={
                             'total_matches': total_matches,
                             'total_runs': total_runs,
                             'total_wickets': total_wickets,
                             'avg_runs_per_match': avg_runs_per_match
                         },
                         team_stats=team_stats,
                         match_outcomes=match_outcomes,
                         batting_stats=batting_stats,
                         bowling_stats=bowling_stats,
                         fielding_stats=fielding_stats,
                         value_stats=value_stats,
                         venue_stats=venue_stats,
                         match_type_stats=match_type_stats)

@main_bp.route('/teams')
def teams():
    teams = Team.query.all()
    return render_template('teams.html', teams=teams)

@main_bp.route('/teams/<int:team_id>')
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Get team's matches
    matches = Match.query.filter(
        (Match.team1_id == team_id) | (Match.team2_id == team_id)
    ).order_by(Match.match_date.desc()).all()
    
    # Get team's players
    players = Player.query.filter_by(team_id=team_id).all()
    
    # Calculate team statistics
    total_matches = len(matches)
    wins = sum(1 for match in matches if match.winner and match.winner.id == team_id)
    losses = total_matches - wins
    
    # Calculate player role statistics
    role_stats = {
        'Batsman': 0,
        'Bowler': 0,
        'All-Rounder': 0,
        'Wicket-Keeper': 0
    }
    
    # Calculate nationality statistics
    nationality_stats = {
        'Indian': 0,
        'Overseas': 0
    }
    
    # Count players by role and nationality
    for player in players:
        role_stats[player.role] = role_stats.get(player.role, 0) + 1
        if player.nationality == 'Indian':
            nationality_stats['Indian'] += 1
        else:
            nationality_stats['Overseas'] += 1
    
    # Calculate player statistics
    for player in players:
        performances = PlayerPerformance.query.filter_by(player_id=player.id).all()
        if performances:
            total_runs = sum(p.runs_scored or 0 for p in performances)
            total_wickets = sum(p.wickets_taken or 0 for p in performances)
            total_matches = len(performances)
            
            player.batting_average = round(total_runs / total_matches, 2) if total_matches > 0 else 0
            player.bowling_average = round(total_wickets / total_matches, 2) if total_matches > 0 else 0
    
    return render_template('team_detail.html',
                         team=team,
                         matches=matches[:5],  # Get last 5 matches
                         players=players,
                         total_matches=total_matches,
                         wins=wins,
                         losses=losses,
                         role_stats=role_stats,
                         nationality_stats=nationality_stats)

@main_bp.route('/players')
def players():
    role = request.args.get('role')
    nationality = request.args.get('nationality')
    
    query = Player.query
    if role:
        query = query.filter_by(role=role)
    if nationality:
        query = query.filter_by(nationality=nationality)
    
    players = query.all()
    return render_template('players.html', players=players)

@main_bp.route('/players/<int:player_id>')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    
    # Get player performances
    performances = PlayerPerformance.query.filter_by(player_id=player_id).all()
    
    # Calculate statistics
    total_runs = sum(p.runs_scored or 0 for p in performances)
    total_wickets = sum(p.wickets_taken or 0 for p in performances)
    total_matches = len(performances)
    
    # Calculate averages
    batting_avg = total_runs / total_matches if total_matches > 0 else 0
    bowling_avg = total_wickets / total_matches if total_matches > 0 else 0
    
    # Get recent performances
    recent_performances = performances[-5:] if performances else []
    
    # Get similar players based on role
    similar_players = Player.query.filter(
        Player.role == player.role,
        Player.id != player_id
    ).limit(5).all()
    
    # Convert similar players to dictionary format
    similar_players_data = [{
        'id': p.id,
        'name': p.name,
        'role': p.role,
        'team': p.team.name if p.team else 'Free Agent',
        'batting_avg': round(sum(pp.runs_scored or 0 for pp in PlayerPerformance.query.filter_by(player_id=p.id).all()) / 
                           len(PlayerPerformance.query.filter_by(player_id=p.id).all()), 2) if PlayerPerformance.query.filter_by(player_id=p.id).all() else 0,
        'bowling_avg': round(sum(pp.wickets_taken or 0 for pp in PlayerPerformance.query.filter_by(player_id=p.id).all()) / 
                           len(PlayerPerformance.query.filter_by(player_id=p.id).all()), 2) if PlayerPerformance.query.filter_by(player_id=p.id).all() else 0
    } for p in similar_players]
    
    # Get market value if available
    market_value = None
    auction_lot = AuctionLot.query.filter_by(player_id=player_id).order_by(AuctionLot.sold_price.desc()).first()
    if auction_lot:
        market_value = auction_lot.sold_price
    
    # Get performance trends
    trend_data = {
        'months': [],
        'avg_runs': [],
        'avg_wickets': []
    }
    
    if performances:
        # Group performances by month
        from collections import defaultdict
        monthly_performances = defaultdict(list)
        for perf in performances:
            month = perf.match.match_date.strftime('%b %Y')
            monthly_performances[month].append(perf)
        
        # Calculate monthly averages
        for month, perfs in monthly_performances.items():
            trend_data['months'].append(month)
            trend_data['avg_runs'].append(sum(p.runs_scored or 0 for p in perfs) / len(perfs))
            trend_data['avg_wickets'].append(sum(p.wickets_taken or 0 for p in perfs) / len(perfs))
    
    # Get user's teams if logged in
    user_teams = []
    if current_user.is_authenticated:
        user_teams = UserTeam.query.filter_by(user_id=current_user.id).all()
    
    return render_template('player_detail.html',
                         player=player,
                         batting_avg=round(batting_avg, 2),
                         bowling_avg=round(bowling_avg, 2),
                         match_dates=[p.match.match_date for p in performances],
                         recent_performances=recent_performances,
                         market_value=market_value,
                         trend_data=trend_data,
                         comparison_data={
                             'similar_players': similar_players_data
                         },
                         user_teams=user_teams)

@main_bp.route('/players/<int:player_id>/add_to_team', methods=['POST'])
@login_required
def add_player_to_team(player_id):
    team_id = request.form.get('team_id')
    if not team_id:
        flash('Please select a team', 'error')
        return redirect(url_for('main_bp.player_detail', player_id=player_id))
    
    team = UserTeam.query.get_or_404(team_id)
    
    # Ensure user owns the team
    if team.user_id != current_user.id:
        flash('You do not have permission to modify this team', 'error')
        return redirect(url_for('main_bp.player_detail', player_id=player_id))
    
    # Check if player is already in team
    if player_id in [p.id for p in team.players]:
        flash('Player is already in the team', 'warning')
        return redirect(url_for('main_bp.player_detail', player_id=player_id))
    
    # Add player to team
    team_player = UserTeamPlayer(user_team_id=team_id, player_id=player_id)
    db.session.add(team_player)
    db.session.commit()
    
    flash('Player added to team successfully', 'success')
    return redirect(url_for('main_bp.player_detail', player_id=player_id))

@main_bp.route('/matches')
def matches():
    season = request.args.get('season')
    team_id = request.args.get('team_id')
    
    query = Match.query
    if season:
        query = query.filter_by(season=season)
    if team_id:
        query = query.filter((Match.team1_id == team_id) | (Match.team2_id == team_id))
    
    matches = query.order_by(Match.match_date.desc()).all()
    return render_template('matches.html', matches=matches)

@main_bp.route('/myteam')
@login_required
def myteam():
    # Get user's teams
    user_teams = UserTeam.query.filter_by(user_id=current_user.id).all()
    
    # If user has no teams, create a default team
    if not user_teams:
        default_team = UserTeam(
            user_id=current_user.id,
            name=f"{current_user.username}'s Team"
        )
        db.session.add(default_team)
        db.session.commit()
        user_teams = [default_team]
    
    return render_template('myteam.html', teams=user_teams)

@main_bp.route('/myteam/<int:team_id>')
@login_required
def user_team_detail(team_id):
    team = UserTeam.query.get_or_404(team_id)
    if team.user_id != current_user.id:
        flash('You do not have permission to view this team.', 'danger')
        return redirect(url_for('main_bp.myteam'))
    
    # Get team statistics
    total_matches = Match.query.filter(
        (Match.team1_id == team.id) | (Match.team2_id == team.id)
    ).count()
    
    wins = Match.query.filter(
        ((Match.team1_id == team.id) & (Match.team1_score > Match.team2_score)) |
        ((Match.team2_id == team.id) & (Match.team2_score > Match.team1_score))
    ).count()
    
    losses = total_matches - wins
    
    # Get role statistics
    role_stats = {
        'Batsman': 0,
        'Bowler': 0,
        'All-Rounder': 0,
        'Wicket-Keeper': 0
    }
    
    # Get nationality statistics
    nationality_stats = {
        'Indian': 0,
        'Overseas': 0
    }
    
    # Count players by role and nationality
    for player in team.players:
        role_stats[player.role] = role_stats.get(player.role, 0) + 1
        nationality_stats[player.nationality] = nationality_stats.get(player.nationality, 0) + 1
    
    # Get recent matches
    recent_matches = Match.query.filter(
        (Match.team1_id == team.id) | (Match.team2_id == team.id)
    ).order_by(Match.match_date.desc()).limit(5).all()
    
    return render_template('team_detail.html',
                         team=team,
                         players=team.players,
                         total_matches=total_matches,
                         wins=wins,
                         losses=losses,
                         role_stats=role_stats,
                         nationality_stats=nationality_stats,
                         matches=recent_matches)

@main_bp.route('/myteam/<int:team_id>/add_player', methods=['GET', 'POST'])
@login_required
def add_player(team_id):
    team = UserTeam.query.get_or_404(team_id)
    if team.user_id != current_user.id:
        flash('You do not have permission to modify this team.', 'danger')
        return redirect(url_for('main_bp.myteam'))
    
    if request.method == 'POST':
        player_id = request.form.get('player_id')
        if not player_id:
            flash('Please select a player.', 'danger')
            return redirect(url_for('main_bp.add_player', team_id=team_id))
        
        # Check if player is already in team
        existing_player = UserTeamPlayer.query.filter_by(
            user_team_id=team_id,
            player_id=player_id
        ).first()
        
        if existing_player:
            flash('Player is already in the team.', 'warning')
            return redirect(url_for('main_bp.add_player', team_id=team_id))
        
        # Add player to team
        try:
            team_player = UserTeamPlayer(user_team_id=team_id, player_id=player_id)
            db.session.add(team_player)
            db.session.commit()
            flash('Player added to team successfully.', 'success')
            return redirect(url_for('main_bp.user_team_detail', team_id=team_id))
        except Exception as e:
            db.session.rollback()
            flash('Error adding player to team. Please try again.', 'danger')
            current_app.logger.error(f"Error adding player to team: {str(e)}")
            return redirect(url_for('main_bp.add_player', team_id=team_id))
    
    # Get all available players (not in the team)
    team_player_ids = [p.player_id for p in team.team_players]
    available_players = Player.query.filter(~Player.id.in_(team_player_ids)).all()
    
    return render_template('add_player.html',
                         team=team,
                         available_players=available_players)

@main_bp.route('/myteam/<int:team_id>/remove_player/<int:player_id>', methods=['POST'])
@login_required
def remove_player_from_team(team_id, player_id):
    team = UserTeam.query.get_or_404(team_id)
    
    # Ensure user owns the team
    if team.user_id != current_user.id:
        flash('You do not have permission to modify this team', 'error')
        return redirect(url_for('main_bp.myteam'))
    
    # Remove player from team
    team_player = UserTeamPlayer.query.filter_by(
        user_team_id=team_id,
        player_id=player_id
    ).first_or_404()
    
    db.session.delete(team_player)
    db.session.commit()
    
    flash('Player removed from team successfully', 'success')
    return redirect(url_for('main_bp.team_detail', team_id=team_id))

@main_bp.route('/myteam/create', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Team name is required', 'error')
            return redirect(url_for('main_bp.create_team'))
        
        # Create new team
        new_team = UserTeam(
            user_id=current_user.id,
            name=name
        )
        db.session.add(new_team)
        db.session.commit()
        
        flash('Team created successfully', 'success')
        return redirect(url_for('main_bp.team_detail', team_id=new_team.id))
    
    return render_template('create_team.html')

@main_bp.route('/myteam/<int:team_id>/delete', methods=['POST'])
@login_required
def delete_team(team_id):
    team = UserTeam.query.get_or_404(team_id)
    if team.user_id != current_user.id:
        flash('You do not have permission to delete this team.', 'danger')
        return redirect(url_for('main_bp.myteam'))
    
    try:
        # First delete all team players
        UserTeamPlayer.query.filter_by(user_team_id=team.id).delete()
        # Then delete the team
        db.session.delete(team)
        db.session.commit()
        flash('Team deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting team. Please try again.', 'danger')
        current_app.logger.error(f"Error deleting team: {str(e)}")
    
    return redirect(url_for('main_bp.myteam'))

@main_bp.route('/matches/<int:match_id>')
def match_detail(match_id):
    match = Match.get_by_id(match_id)
    if not match:
        return render_template('404.html'), 404
    
    performances = PlayerPerformance.query.filter_by(match_id=match_id).all()
    
    return render_template('match_detail.html', 
                          match=match, 
                          performances=performances)

@main_bp.route('/auctions')
@login_required
def auctions():
    try:
        # Get all auctions
        auctions = Auction.query.order_by(Auction.auction_date.desc()).all()
        
        # Get auction lots for each auction
        auction_lots = {}
        for auction in auctions:
            lots = AuctionLot.query.filter_by(auction_id=auction.id).all()
            auction_lots[auction.id] = lots
        
        # Calculate auction statistics
        auction_stats = {
            'total_auctions': len(auctions),
            'total_players_sold': sum(len(lots) for lots in auction_lots.values()),
            'highest_bid': max(
                (lot.sold_price for lots in auction_lots.values() for lot in lots),
                default=0
            ),
            'total_value': sum(
                lot.sold_price for lots in auction_lots.values() for lot in lots
            )
        }
        
        return render_template('auctions.html', 
                             auctions=auctions,
                             auction_lots=auction_lots,
                             auction_stats=auction_stats)
    except Exception as e:
        print(f"Error in auctions route: {str(e)}")
        return render_template('auctions.html',
                             auctions=[],
                             auction_lots={},
                             auction_stats={
                                 'total_auctions': 0,
                                 'total_players_sold': 0,
                                 'highest_bid': 0,
                                 'total_value': 0
                             })

@main_bp.route('/auctions/<int:auction_id>')
@login_required
def auction_detail(auction_id):
    auction = Auction.get_by_id(auction_id)
    if not auction:
        flash('Auction not found', 'error')
        return redirect(url_for('main_bp.auctions'))
    
    lots = AuctionLot.query.filter_by(auction_id=auction_id).all()
    
    return render_template('auction_detail.html',
                         auction=auction,
                         lots=lots)

@main_bp.route('/compare')
@login_required
def compare():
    # Get all players and teams for dropdowns
    players = Player.query.all()
    teams = Team.query.all()
    
    # Get selected players and teams from query parameters
    player1_id = request.args.get('player1')
    player2_id = request.args.get('player2')
    team1_id = request.args.get('team1')
    team2_id = request.args.get('team2')
    
    print(f"Selected IDs - Player1: {player1_id}, Player2: {player2_id}")
    
    player1 = None
    player2 = None
    team1 = None
    team2 = None
    
    if player1_id:
        player1 = Player.get_by_id(player1_id)
        print(f"Player1 found: {player1.name if player1 else 'None'}")
    if player2_id:
        player2 = Player.get_by_id(player2_id)
        print(f"Player2 found: {player2.name if player2 else 'None'}")
    
    # Calculate player statistics from PlayerPerformance
    def get_player_stats(player):
        if not player:
            print("No player provided for stats")
            return {
                'runs': 0,
                'wickets': 0,
                'matches': 0,
                'batting_avg': 0,
                'strike_rate': 0,
                'bowling_avg': 0,
                'economy': 0
            }
            
        print(f"Getting stats for player: {player.name}")
        
        # Get all performances for the player with proper joins
        performances = (db.session.query(PlayerPerformance)
                      .filter(PlayerPerformance.player_id == player.id)
                      .all())
        
        print(f"Found {len(performances)} performances for player {player.name}")
        
        if not performances:
            print(f"No performances found for player {player.name}")
            return {
                'runs': 0,
                'wickets': 0,
                'matches': 0,
                'batting_avg': 0,
                'strike_rate': 0,
                'bowling_avg': 0,
                'economy': 0
            }
        
        # Calculate batting statistics
        total_runs = sum(p.runs_scored or 0 for p in performances)
        total_balls = sum(p.balls_faced or 0 for p in performances)
        dismissals = sum(1 for p in performances if p.runs_scored is not None and p.runs_scored > 0)
        batting_avg = total_runs / dismissals if dismissals > 0 else 0
        strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0
        
        # Calculate bowling statistics
        total_wickets = sum(p.wickets_taken or 0 for p in performances)
        total_runs_conceded = sum(p.runs_conceded or 0 for p in performances)
        total_overs = sum(p.overs_bowled or 0 for p in performances)
        bowling_avg = total_runs_conceded / total_wickets if total_wickets > 0 else 0
        economy = total_runs_conceded / total_overs if total_overs > 0 else 0
        
        stats = {
            'runs': total_runs,
            'wickets': total_wickets,
            'matches': len(performances),
            'batting_avg': round(batting_avg, 2),
            'strike_rate': round(strike_rate, 2),
            'bowling_avg': round(bowling_avg, 2),
            'economy': round(economy, 2)
        }
        
        print(f"Calculated stats for {player.name}: {stats}")
        return stats
    
    # Calculate team statistics
    def get_team_stats(team):
        if not team:
            return {
                'matches': 0,
                'wins': 0,
                'losses': 0,
                'win_percentage': 0,
                'total_runs': 0,
                'total_wickets': 0
            }
            
        # Get all matches for the team with proper joins
        matches = (db.session.query(Match)
                 .filter((Match.team1_id == team.id) | (Match.team2_id == team.id))
                 .all())
        
        if not matches:
            return {
                'matches': 0,
                'wins': 0,
                'losses': 0,
                'win_percentage': 0,
                'total_runs': 0,
                'total_wickets': 0
            }
        
        # Calculate win/loss statistics
        wins = sum(1 for m in matches if m.winner and m.winner.id == team.id)
        losses = sum(1 for m in matches if m.winner and m.winner.id != team.id)
        win_percentage = (wins / len(matches) * 100) if matches else 0
        
        # Calculate runs and wickets
        total_runs = sum(m.team1_score + m.team2_score for m in matches)
        total_wickets = sum(m.team1_wickets + m.team2_wickets for m in matches)
        
        return {
            'matches': len(matches),
            'wins': wins,
            'losses': losses,
            'win_percentage': round(win_percentage, 2),
            'total_runs': total_runs,
            'total_wickets': total_wickets
        }
    
    # Prepare comparison data
    player1_stats = get_player_stats(player1)
    player2_stats = get_player_stats(player2)
    
    print(f"Final stats - Player1: {player1_stats}, Player2: {player2_stats}")
    
    comparison_data = {
        'player1': player1,
        'player2': player2,
        'team1': team1,
        'team2': team2,
        'players': players,
        'teams': teams,
        'player1_stats': player1_stats,
        'player2_stats': player2_stats,
        'team1_stats': get_team_stats(team1),
        'team2_stats': get_team_stats(team2)
    }
    
    return render_template('compare.html', **comparison_data)

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify({'error': 'Query too short'}), 400
    
    players = Player.query.filter(Player.name.ilike(f'%{query}%')).limit(5).all()
    teams = Team.query.filter(Team.name.ilike(f'%{query}%')).limit(5).all()
    
    results = []
    for player in players:
        results.append({
            'id': player.id,
            'name': player.name,
            'type': 'player',
            'team': player.team.name if player.team else 'Free Agent'
        })
    
    for team in teams:
        results.append({
            'id': team.id,
            'name': team.name,
            'type': 'team',
            'short_name': team.short_name
        })
    
    return jsonify(results) 