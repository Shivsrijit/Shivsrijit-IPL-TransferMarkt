from app.extensions import db
from app.models.base import BaseModel, TimestampMixin
from datetime import datetime

class Match(BaseModel, TimestampMixin):
    __tablename__ = 'matches'
    
    match_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team1_score = db.Column(db.Integer)
    team2_score = db.Column(db.Integer)
    team1_overs = db.Column(db.Float)
    team2_overs = db.Column(db.Float)
    team1_wickets = db.Column(db.Integer)
    team2_wickets = db.Column(db.Integer)
    result = db.Column(db.String(100))
    season = db.Column(db.String(10), nullable=False)
    match_type = db.Column(db.String(20), default='league')  # league, playoff, final
    
    # Relationships
    team1 = db.relationship('Team', foreign_keys=[team1_id], backref='home_matches')
    team2 = db.relationship('Team', foreign_keys=[team2_id], backref='away_matches')
    performances = db.relationship('PlayerPerformance', backref='match', lazy=True)
    
    @property
    def winner(self):
        if self.result and 'won' in self.result.lower():
            team_name = self.result.split(' won')[0].strip()
            if team_name == self.team1.name:
                return self.team1
            elif team_name == self.team2.name:
                return self.team2
        return None
    
    @property
    def is_completed(self):
        return self.result is not None
    
    @classmethod
    def get_by_season(cls, season):
        return cls.query.filter_by(season=season).order_by(cls.match_date.desc()).all()
    
    @classmethod
    def get_by_team(cls, team_id, season=None):
        query = cls.query.filter(
            (cls.team1_id == team_id) | (cls.team2_id == team_id)
        )
        if season:
            query = query.filter_by(season=season)
        return query.order_by(cls.match_date.desc()).all()

class PlayerPerformance(BaseModel):
    __tablename__ = 'player_performances'
    
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    # Batting Statistics
    runs_scored = db.Column(db.Integer, default=0)
    balls_faced = db.Column(db.Integer, default=0)
    fours = db.Column(db.Integer, default=0)
    sixes = db.Column(db.Integer, default=0)
    strike_rate = db.Column(db.Float, default=0.0)
    
    # Bowling Statistics
    overs_bowled = db.Column(db.Float, default=0.0)
    runs_conceded = db.Column(db.Integer, default=0)
    wickets_taken = db.Column(db.Integer, default=0)
    economy_rate = db.Column(db.Float, default=0.0)
    
    # Fielding Statistics
    catches = db.Column(db.Integer, default=0)
    stumpings = db.Column(db.Integer, default=0)
    run_outs = db.Column(db.Integer, default=0)
    
    def calculate_strike_rate(self):
        if self.balls_faced == 0:
            return 0
        return (self.runs_scored / self.balls_faced) * 100
    
    def calculate_economy_rate(self):
        if self.overs_bowled == 0:
            return 0
        return self.runs_conceded / self.overs_bowled
    
    @classmethod
    def get_player_performances(cls, player_id, season=None):
        query = cls.query.filter_by(player_id=player_id)
        if season:
            query = query.join(Match).filter(Match.season == season)
        return query.order_by(Match.match_date.desc()).all()
    
    @classmethod
    def get_match_performances(cls, match_id):
        return cls.query.filter_by(match_id=match_id).all() 