from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Register controllers
    from app.controllers import monster_controller
    app.register_blueprint(monster_controller.bp)
    
    return app
