"""
Development server launcher
Run this file to start the development server
"""

import os
from app import create_app

if __name__ == "__main__":
    app = create_app('development')
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )