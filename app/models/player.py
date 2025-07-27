from app.extensions import db
import random

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    city = db.Column(db.String(100))
    coach = db.Column(db.String(100))
    captain_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    # Relationships
    players = db.relationship('Player', backref='team', lazy=True)

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    role = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    batting_style = db.Column(db.String(50))
    bowling_style = db.Column(db.String(50))

    # Relationships
    performances = db.relationship('PlayerPerformance', backref='player', cascade="all, delete-orphan")

    @property
    def matches_played(self):
        return len(self.performances)

    @property
    def runs_scored(self):
        return sum(perf.runs_scored or random.randint(0, 800) for perf in self.performances)

    @property
    def wickets_taken(self):
        return sum(perf.wickets_taken or random.randint(0, 100) for perf in self.performances)

    @property
    def batting_average(self):
        dismissals = sum(1 for perf in self.performances if perf.runs_scored is not None and perf.runs_scored > 0)
        if dismissals == 0:
            return 0
        return self.runs_scored / dismissals

    @property
    def strike_rate(self):
        balls_faced = sum(perf.balls_faced or random.random(80, 300) for perf in self.performances)
        if balls_faced == 0:
            return 0
        return (self.runs_scored / balls_faced) * 100

    @property
    def bowling_average(self):
        if self.wickets_taken == 0:
            return 0
        runs_conceded = sum(perf.runs_conceded or 0 for perf in self.performances)
        return runs_conceded / self.wickets_taken

    @property
    def economy_rate(self):
        overs_bowled = sum(perf.overs_bowled or 0 for perf in self.performances)
        if overs_bowled == 0:
            return 0
        runs_conceded = sum(perf.runs_conceded or 0 for perf in self.performances)
        return runs_conceded / overs_bowled

    @property
    def fours(self):
        return sum(perf.fours or 0 for perf in self.performances)

    @property
    def sixes(self):
        return sum(perf.sixes or 0 for perf in self.performances)

    @property
    def overs_bowled(self):
        return sum(perf.overs_bowled or 0 for perf in self.performances)

    @property
    def runs_conceded(self):
        return sum(perf.runs_conceded or 0 for perf in self.performances)

    @classmethod
    def get_by_id(cls, player_id):
        return cls.query.get(player_id)

    @classmethod
    def get_top_batsmen(cls, limit=5):
        return (cls.query
                .join(PlayerPerformance)
                .group_by(cls.id)
                .order_by(db.func.sum(PlayerPerformance.runs_scored).desc())
                .limit(limit)
                .all())

    @classmethod
    def get_top_bowlers(cls, limit=5):
        return (cls.query
                .join(PlayerPerformance)
                .group_by(cls.id)
                .order_by(db.func.sum(PlayerPerformance.wickets_taken).desc())
                .limit(limit)
                .all())

class PlayerPerformance(db.Model):
    __tablename__ = 'player_performances'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    match_id = db.Column(db.Integer)  # Optional: You can add a Match model later
    runs_scored = db.Column(db.Integer)
    balls_faced = db.Column(db.Integer)
    fours = db.Column(db.Integer)
    sixes = db.Column(db.Integer)
    wickets_taken = db.Column(db.Integer)
    overs_bowled = db.Column(db.Float)
    runs_conceded = db.Column(db.Integer)

