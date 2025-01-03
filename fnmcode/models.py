import uuid
from sqlalchemy import func

from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    # email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000), unique=True)
    is_active = db.Column(db.Boolean, default=False)


# FNMSessions model
class FNMSessions(db.Model):
    __tablename__ = 'fnmsessions'
    
    # Primary key with UUID
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  
    
    # Fields
    name = db.Column(db.String(1000), nullable=False, unique=True)  
    inputs = db.Column(db.Text, nullable=True)  # Text with no character limit
    instructions = db.Column(db.Text, nullable=True)  # Text with no character limit
    tags = db.Column(db.Text, nullable=True)  # Text with no character limit, nullable if no tags
    
    # Foreign key reference to User model
    user_id = db.Column(db.String(36), db.ForeignKey(User.id), nullable=False)  
    
    # Created at field with UTC timestamp
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    
    
    def __repr__(self):
        return f'<FNMSession {self.name}>'