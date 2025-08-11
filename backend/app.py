import os
from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name=None):
    """Application factory pattern for flexible deployment."""
    
    # Determine configuration from environment
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize CORS with dynamic origins
    if config_name == 'development':
        # Development: Allow any local origin
        CORS(app, 
             origins=['http://localhost:*', 'http://127.0.0.1:*', 'http://192.168.*.*:*'],
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    else:
        # Production: Use configured origins
        CORS(app,
             origins=app.config['CORS_ORIGINS'],
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Import and register routes
    from routes import register_routes
    register_routes(app)
    
    return app

if __name__ == '__main__':
    # This allows both local development and production deployment
    app = create_app()
    
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'development':
        print("🚀 Starting EbookVoice AI - Development Mode")
        print("=" * 60)
        print(f"🌐 Frontend should connect to: http://localhost:{app.config['PORT']}")
        print(f"🔗 Health check: http://localhost:{app.config['PORT']}/health")
        print("=" * 60)
        
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    else:
        # Production mode - let WSGI server handle this
        print("🚀 EbookVoice AI - Production Mode")
        print("Application ready for WSGI server")