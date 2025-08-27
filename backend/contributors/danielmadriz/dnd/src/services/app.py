"""
Creates and configures the Flask application with proper setup.
Implements dependency injection and HTTP error handling.
"""
import logging
from flask import Flask, jsonify, request
from ..domain.interfaces import IMonsterService, IValidator
from ..persistence import PostgreSQLMonsterRepository, DnD5eApiClient
from ..application import MonsterService, MonsterValidator
from .controllers import MonsterController


def create_app(
    repository=None,
    api_client=None,
    validator=None,
    monster_service=None
) -> Flask:
    """
    This factory function allows for dependency injection and testing.
    """
    app = Flask(__name__)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.config['JSON_SORT_KEYS'] = False  # Preserve response order
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Pretty JSON responses
    
    # Create dependencies if not provided (for production)
    if repository is None:
        repository = MonsterRepository()
    
    if api_client is None:
        api_client = DnD5eApiClient()
    
    if validator is None:
        validator = MonsterValidator()
    
    if monster_service is None:
        monster_service = MonsterService(repository, api_client)
    
    monster_controller = MonsterController(monster_service, validator)
    
    #Flask services configuration
    _register_routes(app, monster_controller)
    
    _register_error_handlers(app)
    
    _register_request_handlers(app)
    
    app.logger.info("Flask application created successfully")
    return app


def _register_routes(app: Flask, monster_controller: MonsterController):
    
    @app.route('/', methods=['GET'])
    def health_check():
        return monster_controller.health_check()
    
    @app.route('/list', methods=['POST'])
    def list_monsters():
        return monster_controller.list_monsters()
    
    @app.route('/get', methods=['POST'])
    def get_monster():
        return monster_controller.get_monster()


def _register_error_handlers(app: Flask):
    """
    Handles HTTP-level errors that Flask encounterss
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            'error': 'BadRequest',
            'message': 'Invalid request data',
            'status_code': 400
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': 'NotFound',
            'message': 'Endpoint not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        return jsonify({
            'error': 'MethodNotAllowed',
            'message': 'HTTP method not allowed for this endpoint',
            'status_code': 405
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error."""
        return jsonify({
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unhandled exceptions."""
        app.logger.error(f"Unhandled exception: {str(error)}")
        return jsonify({
            'error': 'InternalServerError',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500


def _register_request_handlers(app: Flask):
    """
    In charge of loggin of the requests for observability.
    """
    @app.before_request
    def before_request():
        app.logger.info(f"Request: {request.method} {request.path}")
        
        # Log request payload for POST requests
        if request.method == 'POST' and request.is_json:
            app.logger.debug(f"Request payload: {request.get_json()}")
    
    @app.after_request
    def after_request(response):
        app.logger.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response 