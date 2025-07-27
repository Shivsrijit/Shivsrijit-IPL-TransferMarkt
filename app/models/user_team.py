from app.extensions import db
from datetime import datetime

class UserTeam(db.Model):
    __tablename__ = 'user_teams'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('teams', lazy=True))
    
    # Relationship with players through association table
    players = db.relationship('Player', secondary='user_team_players', backref=db.backref('user_teams', lazy=True))

class UserTeamPlayer(db.Model):
    __tablename__ = 'user_team_players'
    
    id = db.Column(db.Integer, primary_key=True)
    user_team_id = db.Column(db.Integer, db.ForeignKey('user_teams.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_team = db.relationship('UserTeam', backref=db.backref('team_players', lazy=True))
    player = db.relationship('Player', backref=db.backref('team_players', lazy=True))
    
    # Unique constraint to prevent duplicate players in a team
    __table_args__ = (
        db.UniqueConstraint('user_team_id', 'player_id', name='unique_team_player'),
    ) 