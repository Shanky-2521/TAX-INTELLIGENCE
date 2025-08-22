"""
Database models for Tax Intelligence application
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from .conversation import Conversation
from .user import User
from .feedback import Feedback
from .session import Session

__all__ = ['db', 'Conversation', 'User', 'Feedback', 'Session']
