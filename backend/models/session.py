"""
Session model for managing user chat sessions
"""

from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import JSON
from . import db


class Session(db.Model):
    """
    Model for managing user chat sessions
    """
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    # Session metadata
    language = db.Column(db.String(10), nullable=False, default='en')
    user_agent = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    
    # Session state
    is_active = db.Column(db.Boolean, default=True)
    conversation_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # Session context and preferences
    context = db.Column(JSON, nullable=True)  # User preferences, state, etc.
    
    # Relationships
    conversations = db.relationship('Conversation', backref='session_obj', lazy='dynamic',
                                  foreign_keys='Conversation.session_id',
                                  primaryjoin='Session.session_id == foreign(Conversation.session_id)')
    
    def __repr__(self):
        return f'<Session {self.session_id}>'
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'language': self.language,
            'is_active': self.is_active,
            'conversation_count': self.conversation_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'context': self.context
        }
    
    def is_expired(self):
        """Check if session has expired"""
        if self.expires_at and self.expires_at < datetime.utcnow():
            return True
        return False
    
    def extend_session(self, hours=2):
        """Extend session expiration time"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def increment_conversation_count(self):
        """Increment conversation counter"""
        self.conversation_count += 1
        self.update_activity()
        db.session.commit()
    
    def deactivate(self):
        """Deactivate session"""
        self.is_active = False
        db.session.commit()
    
    def get_conversation_history(self, limit=50):
        """Get conversation history for this session"""
        return self.conversations.order_by('timestamp').limit(limit).all()
    
    @classmethod
    def create_session(cls, session_id, language='en', user_agent=None, ip_address=None, expires_hours=2):
        """Create a new session"""
        session = cls(
            session_id=session_id,
            language=language,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours)
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @classmethod
    def get_by_session_id(cls, session_id):
        """Get session by session ID"""
        return cls.query.filter_by(session_id=session_id).first()
    
    @classmethod
    def get_active_sessions(cls):
        """Get all active sessions"""
        return cls.query.filter_by(is_active=True)\
                       .filter(cls.expires_at > datetime.utcnow())\
                       .all()
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Remove expired sessions"""
        expired_sessions = cls.query.filter(cls.expires_at < datetime.utcnow()).all()
        for session in expired_sessions:
            session.deactivate()
        db.session.commit()
        return len(expired_sessions)
    
    @classmethod
    def get_session_stats(cls, days=7):
        """Get session statistics for the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_sessions = cls.query.filter(cls.created_at >= cutoff_date).count()
        active_sessions = cls.query.filter_by(is_active=True)\
                                  .filter(cls.created_at >= cutoff_date)\
                                  .count()
        
        avg_conversations = db.session.query(db.func.avg(cls.conversation_count))\
                                     .filter(cls.created_at >= cutoff_date)\
                                     .scalar()
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'average_conversations_per_session': float(avg_conversations) if avg_conversations else 0.0
        }
