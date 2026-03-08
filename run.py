"""
Run the Flask application.
"""

import os
from app import create_app

# Create app
app = create_app()

if __name__ == '__main__':
    # Get config
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║  Movie Recommender System - Starting    ║
    ╚══════════════════════════════════════════╝
    
    🎬 Server running at: http://localhost:{port}
    🔧 Debug mode: {debug}
    🌍 Environment: {os.getenv('FLASK_ENV', 'development')}
    
    Press CTRL+C to stop the server
    """)
    
    app.run(host=host, port=port, debug=debug)
