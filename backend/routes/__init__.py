"""
Route blueprints for Tax Intelligence API
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog

from .api import api_bp
from .admin import admin_bp
from .health import health_bp

logger = structlog.get_logger()

__all__ = ['api_bp', 'admin_bp', 'health_bp']
