"""
Feedback model for storing user feedback and ratings
"""

from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import JSON
from . import db


class Feedback(db.Model):
    """
    Model for storing user feedback about the service
    """
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)
    
    # Rating and feedback
    rating = db.Column(db.Integer, nullable=False)  # 1-5 scale
    feedback_text = db.Column(db.Text, nullable=True)
    feedback_category = db.Column(db.String(50), nullable=True)  # helpful, accurate, fast, etc.
    
    # User context
    user_agent = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    language = db.Column(db.String(10), nullable=False, default='en')
    
    # Metadata
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    processed = db.Column(db.Boolean, default=False)  # For admin review
    admin_notes = db.Column(db.Text, nullable=True)
    
    # Additional context data
    context = db.Column(JSON, nullable=True)
    
    def __repr__(self):
        return f'<Feedback {self.id}: Rating {self.rating}>'
    
    def to_dict(self):
        """Convert feedback to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'conversation_id': self.conversation_id,
            'rating': self.rating,
            'feedback_text': self.feedback_text,
            'feedback_category': self.feedback_category,
            'language': self.language,
            'timestamp': self.timestamp.isoformat(),
            'processed': self.processed,
            'admin_notes': self.admin_notes,
            'context': self.context
        }
    
    @classmethod
    def get_average_rating(cls, days=30):
        """Get average rating for the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = db.session.query(db.func.avg(cls.rating))\
                          .filter(cls.timestamp >= cutoff_date)\
                          .scalar()
        return float(result) if result else 0.0
    
    @classmethod
    def get_rating_distribution(cls, days=30):
        """Get rating distribution for the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        results = db.session.query(cls.rating, db.func.count(cls.id))\
                           .filter(cls.timestamp >= cutoff_date)\
                           .group_by(cls.rating)\
                           .all()
        return {rating: count for rating, count in results}
    
    @classmethod
    def get_recent_feedback(cls, limit=50):
        """Get recent feedback entries"""
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_unprocessed_feedback(cls):
        """Get feedback that hasn't been reviewed by admin"""
        return cls.query.filter_by(processed=False)\
                       .order_by(cls.timestamp.desc())\
                       .all()
    
    @classmethod
    def get_negative_feedback(cls, threshold=3, days=30):
        """Get feedback with rating below threshold"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(cls.rating < threshold)\
                       .filter(cls.timestamp >= cutoff_date)\
                       .order_by(cls.timestamp.desc())\
                       .all()
    
    def mark_processed(self, admin_notes=None):
        """Mark feedback as processed"""
        self.processed = True
        if admin_notes:
            self.admin_notes = admin_notes
        db.session.commit()
