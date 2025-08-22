"""
Admin dashboard endpoints for Tax Intelligence
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from marshmallow import Schema, fields, ValidationError
import structlog
from datetime import datetime, timedelta
from sqlalchemy import func

from models.conversation import Conversation
from models.user import User
from models.feedback import Feedback
from models import db

logger = structlog.get_logger()

admin_bp = Blueprint('admin', __name__)


class LoginSchema(Schema):
    """Schema for admin login validation"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """
    Admin authentication endpoint
    """
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
        
        email = data['email']
        password = data['password']
        
        # Check against configured admin credentials
        admin_email = current_app.config.get('ADMIN_EMAIL')
        admin_password = current_app.config.get('ADMIN_PASSWORD')
        
        if email == admin_email and password == admin_password:
            # Create JWT token
            access_token = create_access_token(
                identity=email,
                expires_delta=timedelta(hours=8)
            )
            
            logger.info("Admin login successful", email=email)
            
            return jsonify({
                'access_token': access_token,
                'token_type': 'bearer',
                'expires_in': 28800  # 8 hours in seconds
            })
        else:
            logger.warning("Admin login failed", email=email)
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
            
    except ValidationError as e:
        return jsonify({
            'error': 'validation_error',
            'message': 'Invalid login data',
            'details': e.messages
        }), 400
    except Exception as e:
        logger.error("Error in admin login", error=str(e))
        return jsonify({
            'error': 'login_error',
            'message': 'Login failed'
        }), 500


@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """
    Get dashboard statistics
    """
    try:
        # Date range for statistics
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total conversations
        total_conversations = Conversation.query.count()
        
        # Recent conversations
        recent_conversations = Conversation.query.filter(
            Conversation.timestamp >= start_date
        ).count()
        
        # Unique sessions
        unique_sessions = db.session.query(
            func.count(func.distinct(Conversation.session_id))
        ).filter(Conversation.timestamp >= start_date).scalar()
        
        # Language distribution
        language_stats = db.session.query(
            Conversation.language,
            func.count(Conversation.id)
        ).filter(
            Conversation.timestamp >= start_date
        ).group_by(Conversation.language).all()
        
        # Average response time (if tracked)
        # This would require additional fields in the Conversation model
        
        # Feedback statistics
        feedback_stats = {}
        if Feedback.query.first():  # Check if feedback table exists and has data
            avg_rating = db.session.query(
                func.avg(Feedback.rating)
            ).filter(Feedback.timestamp >= start_date).scalar()
            
            feedback_count = Feedback.query.filter(
                Feedback.timestamp >= start_date
            ).count()
            
            feedback_stats = {
                'average_rating': float(avg_rating) if avg_rating else 0,
                'total_feedback': feedback_count
            }
        
        stats = {
            'period_days': days,
            'total_conversations': total_conversations,
            'recent_conversations': recent_conversations,
            'unique_sessions': unique_sessions,
            'language_distribution': {lang: count for lang, count in language_stats},
            'feedback': feedback_stats,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        logger.info("Dashboard stats retrieved", 
                   admin=get_jwt_identity(),
                   period_days=days)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error("Error retrieving dashboard stats", error=str(e))
        return jsonify({
            'error': 'stats_error',
            'message': 'Unable to retrieve statistics'
        }), 500


@admin_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """
    Get paginated list of conversations
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        session_id = request.args.get('session_id')
        language = request.args.get('language')
        
        query = Conversation.query
        
        # Apply filters
        if session_id:
            query = query.filter(Conversation.session_id == session_id)
        if language:
            query = query.filter(Conversation.language == language)
        
        # Order by timestamp descending
        query = query.order_by(Conversation.timestamp.desc())
        
        # Paginate
        conversations = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = {
            'conversations': [{
                'id': conv.id,
                'session_id': conv.session_id,
                'user_message': conv.user_message[:200] + '...' if len(conv.user_message) > 200 else conv.user_message,
                'assistant_response': conv.assistant_response[:200] + '...' if len(conv.assistant_response) > 200 else conv.assistant_response,
                'language': conv.language,
                'timestamp': conv.timestamp.isoformat()
            } for conv in conversations.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': conversations.total,
                'pages': conversations.pages,
                'has_next': conversations.has_next,
                'has_prev': conversations.has_prev
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error("Error retrieving conversations", error=str(e))
        return jsonify({
            'error': 'retrieval_error',
            'message': 'Unable to retrieve conversations'
        }), 500


@admin_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation_detail(conversation_id):
    """
    Get detailed view of a specific conversation
    """
    try:
        conversation = Conversation.query.get_or_404(conversation_id)
        
        result = {
            'id': conversation.id,
            'session_id': conversation.session_id,
            'user_message': conversation.user_message,
            'assistant_response': conversation.assistant_response,
            'language': conversation.language,
            'context': conversation.context,
            'timestamp': conversation.timestamp.isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error("Error retrieving conversation detail", 
                    conversation_id=conversation_id,
                    error=str(e))
        return jsonify({
            'error': 'retrieval_error',
            'message': 'Unable to retrieve conversation'
        }), 500


@admin_bp.route('/feedback', methods=['GET'])
@jwt_required()
def get_feedback():
    """
    Get paginated list of user feedback
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        rating_filter = request.args.get('rating', type=int)
        
        query = Feedback.query
        
        # Apply rating filter
        if rating_filter:
            query = query.filter(Feedback.rating == rating_filter)
        
        # Order by timestamp descending
        query = query.order_by(Feedback.timestamp.desc())
        
        # Paginate
        feedback_items = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = {
            'feedback': [{
                'id': fb.id,
                'session_id': fb.session_id,
                'rating': fb.rating,
                'feedback_text': fb.feedback_text,
                'timestamp': fb.timestamp.isoformat()
            } for fb in feedback_items.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': feedback_items.total,
                'pages': feedback_items.pages,
                'has_next': feedback_items.has_next,
                'has_prev': feedback_items.has_prev
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error("Error retrieving feedback", error=str(e))
        return jsonify({
            'error': 'retrieval_error',
            'message': 'Unable to retrieve feedback'
        }), 500


@admin_bp.route('/system/health', methods=['GET'])
@jwt_required()
def system_health():
    """
    Get detailed system health information for admin
    """
    try:
        # This would include more detailed metrics than the public health endpoint
        # Database connection pool status, LLM API status, etc.
        
        health_info = {
            'database': {
                'status': 'healthy',
                'connection_pool': 'active'
            },
            'llm_service': {
                'status': 'configured' if current_app.config.get('OPENAI_API_KEY') else 'not_configured'
            },
            'safety_filter': {
                'status': 'active' if current_app.config.get('ENABLE_SAFETY_FILTER') else 'disabled'
            },
            'last_checked': datetime.utcnow().isoformat()
        }
        
        return jsonify(health_info)
        
    except Exception as e:
        logger.error("Error retrieving system health", error=str(e))
        return jsonify({
            'error': 'health_error',
            'message': 'Unable to retrieve system health'
        }), 500
