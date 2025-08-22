"""
Session Manager Service for Tax Intelligence
Handles user session management and conversation history
"""

import structlog
import uuid
import redis
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app

from models.session import Session
from models.conversation import Conversation
from models import db

logger = structlog.get_logger()


class SessionManager:
    """
    Service for managing user sessions and conversation history
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection for session caching"""
        try:
            if not self.redis_client and current_app:
                redis_url = current_app.config.get('REDIS_URL')
                if redis_url:
                    self.redis_client = redis.from_url(redis_url)
                    # Test connection
                    self.redis_client.ping()
                    logger.info("Redis connection established for session management")
        except Exception as e:
            logger.warning("Redis not available, using database only", error=str(e))
            self.redis_client = None
    
    def get_or_create_session(self, session_id: str = None, language: str = 'en',
                             user_agent: str = None, ip_address: str = None) -> 'SessionData':
        """
        Get existing session or create new one
        
        Args:
            session_id: Existing session ID or None to create new
            language: User's preferred language
            user_agent: User's browser user agent
            ip_address: User's IP address (for analytics, not PII)
            
        Returns:
            SessionData object with session information
        """
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Try to get from cache first
            session_data = self._get_session_from_cache(session_id)
            if session_data:
                return session_data
            
            # Try to get from database
            session = Session.get_by_session_id(session_id)
            
            if not session:
                # Create new session
                session = Session.create_session(
                    session_id=session_id,
                    language=language,
                    user_agent=user_agent,
                    ip_address=ip_address
                )
                logger.info("New session created", session_id=session_id, language=language)
            else:
                # Update existing session activity
                session.update_activity()
                logger.info("Existing session retrieved", session_id=session_id)
            
            # Create session data object
            session_data = SessionData(session, self)
            
            # Cache the session
            self._cache_session(session_data)
            
            return session_data
            
        except Exception as e:
            logger.error("Error in get_or_create_session", error=str(e))
            # Return a minimal session data object
            return SessionData(None, self, session_id=session_id or str(uuid.uuid4()))
    
    def _get_session_from_cache(self, session_id: str) -> Optional['SessionData']:
        """Get session from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"session:{session_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.debug("Session retrieved from cache", session_id=session_id)
                return SessionData.from_dict(data, self)
            
        except Exception as e:
            logger.warning("Error retrieving session from cache", error=str(e))
        
        return None
    
    def _cache_session(self, session_data: 'SessionData'):
        """Cache session in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"session:{session_data.session_id}"
            cache_data = session_data.to_dict()
            
            # Cache for 2 hours
            self.redis_client.setex(
                cache_key,
                timedelta(hours=2),
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.warning("Error caching session", error=str(e))
    
    def add_to_history(self, session_id: str, user_message: str, assistant_response: str):
        """Add conversation to session history"""
        try:
            # Update cache
            if self.redis_client:
                history_key = f"history:{session_id}"
                conversation_data = {
                    'user_message': user_message,
                    'assistant_response': assistant_response,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Add to list and keep only last 50 conversations
                self.redis_client.lpush(history_key, json.dumps(conversation_data))
                self.redis_client.ltrim(history_key, 0, 49)
                self.redis_client.expire(history_key, timedelta(hours=24))
            
            # Update session conversation count
            session = Session.get_by_session_id(session_id)
            if session:
                session.increment_conversation_count()
            
        except Exception as e:
            logger.error("Error adding to session history", error=str(e))
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for session"""
        try:
            # Try cache first
            if self.redis_client:
                history_key = f"history:{session_id}"
                cached_history = self.redis_client.lrange(history_key, 0, limit - 1)
                
                if cached_history:
                    history = []
                    for item in cached_history:
                        try:
                            history.append(json.loads(item))
                        except json.JSONDecodeError:
                            continue
                    
                    if history:
                        return list(reversed(history))  # Return in chronological order
            
            # Fallback to database
            conversations = Conversation.get_session_history(session_id, limit)
            return [
                {
                    'user_message': conv.user_message,
                    'assistant_response': conv.assistant_response,
                    'timestamp': conv.timestamp.isoformat()
                }
                for conv in conversations
            ]
            
        except Exception as e:
            logger.error("Error retrieving session history", error=str(e))
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from database and cache"""
        try:
            # Clean up database sessions
            expired_count = Session.cleanup_expired_sessions()
            
            # Clean up cache (Redis handles TTL automatically)
            logger.info("Session cleanup completed", expired_sessions=expired_count)
            return expired_count
            
        except Exception as e:
            logger.error("Error during session cleanup", error=str(e))
            return 0
    
    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        try:
            active_sessions = Session.get_active_sessions()
            return len(active_sessions)
        except Exception as e:
            logger.error("Error getting active session count", error=str(e))
            return 0


class SessionData:
    """
    Data class for session information
    """
    
    def __init__(self, session: Session = None, manager: SessionManager = None, 
                 session_id: str = None):
        self.session = session
        self.manager = manager
        self.session_id = session_id or (session.session_id if session else str(uuid.uuid4()))
        self.language = session.language if session else 'en'
        self.created_at = session.created_at if session else datetime.utcnow()
        self.conversation_count = session.conversation_count if session else 0
        self.context = session.context if session else {}
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get conversation history for this session"""
        if self.manager:
            return self.manager.get_session_history(self.session_id, limit)
        return []
    
    def add_context(self, key: str, value: Any):
        """Add context information to session"""
        self.context[key] = value
        
        # Update database if session exists
        if self.session:
            self.session.context = self.context
            db.session.commit()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context information from session"""
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict:
        """Convert session data to dictionary"""
        return {
            'session_id': self.session_id,
            'language': self.language,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'conversation_count': self.conversation_count,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict, manager: SessionManager) -> 'SessionData':
        """Create session data from dictionary"""
        session_data = cls(manager=manager, session_id=data['session_id'])
        session_data.language = data.get('language', 'en')
        session_data.conversation_count = data.get('conversation_count', 0)
        session_data.context = data.get('context', {})
        
        # Parse created_at
        created_at_str = data.get('created_at')
        if created_at_str:
            try:
                session_data.created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                session_data.created_at = datetime.utcnow()
        
        return session_data
