from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # Load .env file

    app = Flask(__name__)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
