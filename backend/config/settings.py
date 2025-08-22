"""
Configuration settings for Tax Intelligence application
"""

import os
from datetime import timedelta
from typing import List


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tax_intelligence.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Redis settings (for session management and caching)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://tax-intelligence.app'  # Production domain
    ]
    
    # LLM API settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4-turbo-preview')
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '2048'))
    OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', '0.3'))
    
    # Alternative LLM settings (for local models)
    LOCAL_LLM_ENABLED = os.environ.get('LOCAL_LLM_ENABLED', 'false').lower() == 'true'
    LOCAL_LLM_MODEL_PATH = os.environ.get('LOCAL_LLM_MODEL_PATH', './models/llama-2-7b-chat')
    
    # Vector database settings
    VECTOR_DB_TYPE = os.environ.get('VECTOR_DB_TYPE', 'faiss')  # faiss, chroma, or whoosh
    VECTOR_DB_PATH = os.environ.get('VECTOR_DB_PATH', './knowledge_base/embeddings')
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # Knowledge base settings
    KNOWLEDGE_BASE_PATH = os.environ.get('KNOWLEDGE_BASE_PATH', './knowledge_base/documents')
    IRS_DOCUMENTS_PATH = os.path.join(KNOWLEDGE_BASE_PATH, 'irs_publications')
    
    # Safety and compliance settings
    ENABLE_SAFETY_FILTER = os.environ.get('ENABLE_SAFETY_FILTER', 'true').lower() == 'true'
    PII_DETECTION_ENABLED = os.environ.get('PII_DETECTION_ENABLED', 'true').lower() == 'true'
    CONTENT_MODERATION_ENABLED = os.environ.get('CONTENT_MODERATION_ENABLED', 'true').lower() == 'true'
    
    # Rate limiting settings
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Session settings
    SESSION_TYPE = 'redis'
    SESSION_REDIS_URL = REDIS_URL
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'tax_intelligence:'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json')  # json or text
    
    # Monitoring settings
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    PROMETHEUS_METRICS_ENABLED = os.environ.get('PROMETHEUS_METRICS_ENABLED', 'true').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
    
    # Language settings
    SUPPORTED_LANGUAGES = ['en', 'es']  # English and Spanish
    DEFAULT_LANGUAGE = 'en'
    
    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@tax-intelligence.app')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-in-production')
    
    # Feature flags
    ENABLE_ADMIN_DASHBOARD = os.environ.get('ENABLE_ADMIN_DASHBOARD', 'true').lower() == 'true'
    ENABLE_FEEDBACK_COLLECTION = os.environ.get('ENABLE_FEEDBACK_COLLECTION', 'true').lower() == 'true'
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', 'false').lower() == 'true'
    
    # Tax calculation settings
    TAX_YEAR = int(os.environ.get('TAX_YEAR', '2023'))
    EITC_ENABLED = os.environ.get('EITC_ENABLED', 'true').lower() == 'true'
    CTC_ENABLED = os.environ.get('CTC_ENABLED', 'false').lower() == 'true'  # Future feature
    AOTC_ENABLED = os.environ.get('AOTC_ENABLED', 'false').lower() == 'true'  # Future feature


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Relaxed rate limiting for development
    RATELIMIT_DEFAULT = "1000 per day, 200 per hour"
    
    # Development database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev_tax_intelligence.db'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # Use mock LLM for tests
    OPENAI_API_KEY = 'test-key'
    LOCAL_LLM_ENABLED = False
    
    # Disable external services for tests
    ENABLE_SAFETY_FILTER = False
    SENTRY_DSN = None
    
    # Test-specific settings
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Strict security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production database (PostgreSQL recommended)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/tax_intelligence_prod'
    
    # Enhanced rate limiting for production
    RATELIMIT_DEFAULT = "100 per day, 20 per hour"
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Enable all monitoring in production
    PROMETHEUS_METRICS_ENABLED = True
    ENABLE_ANALYTICS = True


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
