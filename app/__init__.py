"""
Flask application factory.
"""

from flask import Flask
from flask_session import Session

from app.config import get_config


def create_app(env=None):
    """
    Create and configure Flask application.
    
    Args:
        env: str, environment name ('development' or 'production')
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    config = get_config(env)
    app.config.from_object(config)
    
    # Initialize session
    Session(app)
    
    # Register blueprints
    from app import routes
    app.register_blueprint(routes.bp)
    
    # Health check route
    @app.route('/health')
    def health():
        return {'status': 'healthy'}, 200
    
    return app
