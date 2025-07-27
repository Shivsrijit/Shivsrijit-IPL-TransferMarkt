from app.extensions import db
from app.models.base import BaseModel, TimestampMixin
from datetime import datetime

class Auction(BaseModel, TimestampMixin):
    __tablename__ = 'auctions'
    
    season = db.Column(db.String(10), nullable=False)
    auction_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100))
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed
    
    # Relationships
    lots = db.relationship('AuctionLot', backref='auction', lazy=True)
    
    @property
    def total_value(self):
        return sum(lot.sold_price or 0 for lot in self.lots if lot.status == 'sold')
    
    @property
    def unsold_lots(self):
        return [lot for lot in self.lots if lot.status == 'unsold']
    
    @classmethod
    def get_by_season(cls, season):
        return cls.query.filter_by(season=season).first()
    
    @classmethod
    def get_active(cls):
        return cls.query.filter_by(status='ongoing').first()

class AuctionLot(BaseModel, TimestampMixin):
    __tablename__ = 'auction_lots'
    
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    sold_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='unsold')  # unsold, sold
    sold_to_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    
    # Relationships
    player = db.relationship('Player', backref='auction_lots')
    sold_to_team = db.relationship('Team', backref='purchased_lots')
    bids = db.relationship('AuctionBid', backref='lot', lazy=True, order_by='AuctionBid.bid_amount.desc()')
    
    @property
    def current_highest_bid(self):
        return max([bid.bid_amount for bid in self.bids]) if self.bids else self.base_price
    
    @property
    def current_highest_bidder(self):
        return self.bids[0].team if self.bids else None

class AuctionBid(BaseModel, TimestampMixin):
    __tablename__ = 'auction_bids'
    
    lot_id = db.Column(db.Integer, db.ForeignKey('auction_lots.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
    
    # Relationships
    team = db.relationship('Team', backref='auction_bids')
    
    @classmethod
    def get_team_bids(cls, team_id, auction_id):
        return cls.query.join(AuctionLot).filter(
            cls.team_id == team_id,
            AuctionLot.auction_id == auction_id
        ).order_by(cls.bid_amount.desc()).all() 