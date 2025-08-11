#!/usr/bin/env python3
"""
Development server startup script.
This provides a clean way to start the development server locally.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = current_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"💡 No .env file found. Copy .env.example to .env to customize settings.")
except ImportError:
    print("💡 python-dotenv not installed. Install with: pip install python-dotenv")

# Set development environment
os.environ.setdefault('FLASK_ENV', 'development')

# Import and create the app
try:
    from app import create_app
    
    app = create_app('development')
    
    print("🚀 Starting EbookVoice AI - Development Server")
    print("=" * 60)
    print(f"🌐 Backend URL: http://localhost:{app.config['PORT']}")
    print(f"🔗 Health check: http://localhost:{app.config['PORT']}/health")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start development server
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5001),
        debug=True,
        use_reloader=True
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you've installed all dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Startup error: {e}")
    sys.exit(1)