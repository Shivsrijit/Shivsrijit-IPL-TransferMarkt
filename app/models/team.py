from app.extensions import db
from app.models.base import BaseModel, TimestampMixin
import random

class Team(BaseModel, TimestampMixin):
    __tablename__ = 'teams'
    
    name = db.Column(db.String(100), unique=True, nullable=False)
    short_name = db.Column(db.String(10), unique=True, nullable=False)
    logo_url = db.Column(db.String(255))
    home_ground = db.Column(db.String(100))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    players = db.relationship('Player', backref='team', lazy=True)
    
    def __repr__(self):
        return f"<Team {self.id} - {self.name}>"

    def __str__(self):
        return self.name

    

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.name).all()

    @classmethod
    def get_by_id(cls, team_id):
        return cls.query.get(team_id)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


    @property
    def total_matches(self):
        return len(self.home_matches) + len(self.away_matches)
    
    @property
    def wins(self):
        count = 0
        for match in self.home_matches + self.away_matches:
            if match.winner == self:
                count += 1
        return count
    
    @property
    def losses(self):
        return self.total_matches - self.wins
    
    @property
    def win_percentage(self):
        if self.total_matches == 0:
            return 0
        return (self.wins / self.total_matches) * 100
    
    @classmethod
    def get_by_short_name(cls, short_name):
        return cls.query.filter_by(short_name=short_name).first()
    
    @classmethod
    def get_by_owner(cls, owner_id):
        return cls.query.filter_by(owner_id=owner_id).first()

    @classmethod
    def get_top_teams(cls, limit=5):
        return (cls.query
                .order_by(cls.win_percentage.desc())
                .limit(limit)
                .all())

class Player(BaseModel, TimestampMixin):
    __tablename__ = 'players'
    
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    role = db.Column(db.String(50))  # Batsman, Bowler, All-rounder
    nationality = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    batting_style = db.Column(db.String(50))
    bowling_style = db.Column(db.String(50))
    
    # Player Statistics
    matches_played = db.Column(db.Integer, default=0)
    runs_scored = db.Column(db.Integer, default=0)
    wickets_taken = db.Column(db.Integer, default=0)
    catches = db.Column(db.Integer, default=0)
    stumpings = db.Column(db.Integer, default=0)
    
    # Auction Details
    current_value = db.Column(db.Float)
    base_price = db.Column(db.Float)
    
    @property
    def batting_average(self):
        if self.matches_played == 0:
            return 0
        return self.runs_scored / self.matches_played
    
    @property
    def bowling_average(self):
        if self.wickets_taken == 0:
            return 0 + random.randint(0, 30)
        return self.runs_conceded / self.wickets_taken
    
    @classmethod
    def search_by_name(cls, name):
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()
    
    @classmethod
    def get_top_batsmen(cls, limit=10):
        return cls.query.order_by(cls.batting_average.desc()).limit(limit).all()
    
    @classmethod
    def get_top_bowlers(cls, limit=10):
        return cls.query.order_by(cls.bowling_average.desc()).limit(limit).all() 