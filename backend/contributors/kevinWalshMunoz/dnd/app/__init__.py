from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Registrar controladores
    from app.controllers import monster_controller
    app.register_blueprint(monster_controller.bp)
    
    return app
