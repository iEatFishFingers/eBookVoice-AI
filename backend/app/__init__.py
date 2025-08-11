"""
eBookVoice-AI Application Factory
Flask application factory pattern for hybrid cloud architecture
"""

from flask import Flask
from flask_cors import CORS
import os

def create_app(config_name=None):
    """
    Application factory pattern
    Creates and configures Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        from .config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize CORS
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
         supports_credentials=True)
    
    # Register blueprints
    from .api.auth import auth_bp
    from .api.audiobooks import audiobooks_bp
    from .api.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(audiobooks_bp)
    app.register_blueprint(users_bp)
    
    # Root route
    @app.route('/')
    def root():
        return {
            'service': 'eBookVoice-AI API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'auth': '/api/auth',
                'users': '/api/users',
                'audiobooks': '/api/audiobooks'
            }
        }
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'ebookvoice-api'}
    
    return app