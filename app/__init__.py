from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from app.database import init_db
from app.routes import api_bp, pages_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    init_db(app)

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/health")
    def health():
        return jsonify(
            {
                "basari": True,
                "durum": "aktif",
                "servis": "TANAXIS AI"
            }
        ), 200

    return app