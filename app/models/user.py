from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager
from app.models.base import BaseModel, TimestampMixin

class User(BaseModel, UserMixin, TimestampMixin):
    __tablename__ = 'users'
    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # user, team_owner, admin
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    team = db.relationship('Team', backref='owner', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_team_owner(self):
        return self.role == 'team_owner'
    
    def is_admin(self):
        return self.role == 'admin'
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id)) 