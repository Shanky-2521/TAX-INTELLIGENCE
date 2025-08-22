"""
Health check endpoints for Tax Intelligence API
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import structlog
import psutil
import os

logger = structlog.get_logger()

health_bp = Blueprint('health', __name__)


@health_bp.route('/')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'tax-intelligence-api',
        'version': '1.0.0'
    })


@health_bp.route('/detailed')
def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database connectivity check
        db_status = 'healthy'
        try:
            from models import db
            db.engine.execute('SELECT 1')
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
            logger.error("Database health check failed", error=str(e))
        
        # Redis connectivity check (if configured)
        redis_status = 'not_configured'
        if current_app.config.get('REDIS_URL'):
            try:
                import redis
                r = redis.from_url(current_app.config['REDIS_URL'])
                r.ping()
                redis_status = 'healthy'
            except Exception as e:
                redis_status = f'unhealthy: {str(e)}'
                logger.error("Redis health check failed", error=str(e))
        
        # LLM service check
        llm_status = 'not_configured'
        if current_app.config.get('OPENAI_API_KEY'):
            llm_status = 'configured'
            # Could add actual API test here
        
        health_data = {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'tax-intelligence-api',
            'version': '1.0.0',
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'services': {
                'database': db_status,
                'redis': redis_status,
                'llm': llm_status
            }
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500


@health_bp.route('/ready')
def readiness_check():
    """Kubernetes readiness probe endpoint"""
    try:
        # Check if all critical services are ready
        from models import db
        db.engine.execute('SELECT 1')
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503


@health_bp.route('/live')
def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    })
