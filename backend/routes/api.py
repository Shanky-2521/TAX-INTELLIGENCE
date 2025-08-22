"""
Main API endpoints for Tax Intelligence EITC Assistant
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, ValidationError
import structlog
import uuid
from datetime import datetime

from services.llm_service import LLMService
from services.eitc_calculator import EITCCalculator
from services.safety_filter import SafetyFilter
from services.session_manager import SessionManager
from models.conversation import Conversation
from models import db

logger = structlog.get_logger()

api_bp = Blueprint('api', __name__)

# Rate limiting for API endpoints
limiter = Limiter(key_func=get_remote_address)


class ChatRequestSchema(Schema):
    """Schema for chat request validation"""
    message = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    session_id = fields.Str(required=False)
    language = fields.Str(missing='en', validate=lambda x: x in ['en', 'es'])
    context = fields.Dict(missing={})


class EITCCalculationSchema(Schema):
    """Schema for EITC calculation request validation"""
    filing_status = fields.Str(required=True, validate=lambda x: x in ['single', 'married_joint', 'married_separate', 'head_of_household'])
    adjusted_gross_income = fields.Float(required=True, validate=lambda x: x >= 0)
    earned_income = fields.Float(required=True, validate=lambda x: x >= 0)
    investment_income = fields.Float(missing=0, validate=lambda x: x >= 0)
    qualifying_children = fields.Int(missing=0, validate=lambda x: x >= 0)
    children_ages = fields.List(fields.Int(), missing=[])
    tax_year = fields.Int(missing=2023)


@api_bp.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    """
    Main chat endpoint for tax assistance
    """
    try:
        # Validate request data
        schema = ChatRequestSchema()
        data = schema.load(request.json)
        
        message = data['message']
        session_id = data.get('session_id') or str(uuid.uuid4())
        language = data['language']
        context = data['context']
        
        logger.info("Chat request received", 
                   session_id=session_id,
                   language=language,
                   message_length=len(message))
        
        # Safety filter check
        safety_filter = current_app.safety_filter
        if not safety_filter.is_safe_input(message):
            logger.warning("Unsafe input detected", 
                          session_id=session_id,
                          message=message[:100])
            return jsonify({
                'error': 'unsafe_input',
                'message': 'I cannot process this request. Please rephrase your question about tax topics.',
                'session_id': session_id
            }), 400
        
        # Get or create session
        session_manager = current_app.session_manager
        session = session_manager.get_or_create_session(session_id, language)
        
        # Initialize LLM service
        llm_service = LLMService(language=language)
        
        # Process the message
        response = llm_service.process_message(
            message=message,
            session_history=session.get_history(),
            context=context
        )
        
        # Safety filter for response
        if not safety_filter.is_safe_output(response):
            logger.warning("Unsafe output detected", 
                          session_id=session_id)
            response = "I apologize, but I cannot provide that information. Please consult a qualified tax professional for specific advice."
        
        # Save conversation
        conversation = Conversation(
            session_id=session_id,
            user_message=message,
            assistant_response=response,
            language=language,
            context=context,
            timestamp=datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.commit()
        
        # Update session
        session_manager.add_to_history(session_id, message, response)
        
        logger.info("Chat response generated", 
                   session_id=session_id,
                   response_length=len(response))
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'language': language,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except ValidationError as e:
        logger.warning("Validation error in chat", errors=e.messages)
        return jsonify({
            'error': 'validation_error',
            'message': 'Invalid request data',
            'details': e.messages
        }), 400
        
    except Exception as e:
        logger.error("Error in chat endpoint", error=str(e))
        return jsonify({
            'error': 'internal_error',
            'message': 'An unexpected error occurred. Please try again.'
        }), 500


@api_bp.route('/calculate-eitc', methods=['POST'])
@limiter.limit("20 per minute")
def calculate_eitc():
    """
    Calculate EITC eligibility and amount
    """
    try:
        # Validate request data
        schema = EITCCalculationSchema()
        data = schema.load(request.json)
        
        logger.info("EITC calculation request", 
                   filing_status=data['filing_status'],
                   agi=data['adjusted_gross_income'],
                   children=data['qualifying_children'])
        
        # Initialize EITC calculator
        calculator = EITCCalculator(tax_year=data['tax_year'])
        
        # Perform calculation
        result = calculator.calculate(
            filing_status=data['filing_status'],
            adjusted_gross_income=data['adjusted_gross_income'],
            earned_income=data['earned_income'],
            investment_income=data['investment_income'],
            qualifying_children=data['qualifying_children'],
            children_ages=data['children_ages']
        )
        
        logger.info("EITC calculation completed", 
                   eligible=result['eligible'],
                   credit_amount=result.get('credit_amount', 0))
        
        return jsonify(result)
        
    except ValidationError as e:
        logger.warning("Validation error in EITC calculation", errors=e.messages)
        return jsonify({
            'error': 'validation_error',
            'message': 'Invalid calculation data',
            'details': e.messages
        }), 400
        
    except Exception as e:
        logger.error("Error in EITC calculation", error=str(e))
        return jsonify({
            'error': 'calculation_error',
            'message': 'Unable to calculate EITC. Please check your inputs.'
        }), 500


@api_bp.route('/session/<session_id>/history', methods=['GET'])
@limiter.limit("10 per minute")
def get_session_history(session_id):
    """
    Get conversation history for a session
    """
    try:
        conversations = Conversation.query.filter_by(session_id=session_id).order_by(Conversation.timestamp).all()
        
        history = []
        for conv in conversations:
            history.append({
                'user_message': conv.user_message,
                'assistant_response': conv.assistant_response,
                'timestamp': conv.timestamp.isoformat(),
                'language': conv.language
            })
        
        return jsonify({
            'session_id': session_id,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        logger.error("Error retrieving session history", 
                    session_id=session_id, 
                    error=str(e))
        return jsonify({
            'error': 'retrieval_error',
            'message': 'Unable to retrieve session history'
        }), 500


@api_bp.route('/feedback', methods=['POST'])
@limiter.limit("5 per minute")
def submit_feedback():
    """
    Submit user feedback
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        rating = data.get('rating')  # 1-5 scale
        feedback_text = data.get('feedback', '')
        
        # Validate basic requirements
        if not session_id or not rating or rating not in range(1, 6):
            return jsonify({
                'error': 'validation_error',
                'message': 'Session ID and rating (1-5) are required'
            }), 400
        
        # Save feedback (implement Feedback model as needed)
        logger.info("Feedback received", 
                   session_id=session_id,
                   rating=rating,
                   has_text=bool(feedback_text))
        
        return jsonify({
            'message': 'Thank you for your feedback!',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error("Error submitting feedback", error=str(e))
        return jsonify({
            'error': 'submission_error',
            'message': 'Unable to submit feedback'
        }), 500


@api_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """
    Get list of supported languages
    """
    return jsonify({
        'languages': [
            {'code': 'en', 'name': 'English'},
            {'code': 'es', 'name': 'Español'}
        ],
        'default': 'en'
    })
