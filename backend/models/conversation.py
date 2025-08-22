"""
Conversation model for storing chat interactions
"""

from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import JSON
from . import db


class Conversation(db.Model):
    """
    Model for storing user-assistant conversations
    """
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    assistant_response = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False, default='en')
    context = db.Column(JSON, nullable=True)  # Additional context data
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Metadata fields
    response_time_ms = db.Column(db.Integer, nullable=True)  # Response generation time
    tokens_used = db.Column(db.Integer, nullable=True)  # LLM tokens consumed
    model_used = db.Column(db.String(100), nullable=True)  # Which LLM model was used
    
    # Safety and quality flags
    safety_flagged = db.Column(db.Boolean, default=False)
    quality_score = db.Column(db.Float, nullable=True)  # Quality assessment score
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.session_id}>'
    
    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_message': self.user_message,
            'assistant_response': self.assistant_response,
            'language': self.language,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'response_time_ms': self.response_time_ms,
            'tokens_used': self.tokens_used,
            'model_used': self.model_used,
            'safety_flagged': self.safety_flagged,
            'quality_score': self.quality_score
        }
    
    @classmethod
    def get_session_history(cls, session_id, limit=50):
        """Get conversation history for a session"""
        return cls.query.filter_by(session_id=session_id)\
                      .order_by(cls.timestamp.asc())\
                      .limit(limit)\
                      .all()
    
    @classmethod
    def get_recent_conversations(cls, hours=24, limit=100):
        """Get recent conversations within specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(cls.timestamp >= cutoff_time)\
                      .order_by(cls.timestamp.desc())\
                      .limit(limit)\
                      .all()
    
    @classmethod
    def get_flagged_conversations(cls, limit=50):
        """Get conversations flagged for safety review"""
        return cls.query.filter_by(safety_flagged=True)\
                      .order_by(cls.timestamp.desc())\
                      .limit(limit)\
                      .all()
