import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import CONFIG_BY_NAME
from app.database import init_db
from app.routes import api_bp, pages_bp


def create_app():
    """TANAXIS AI Flask uygulamasini olusturur."""

    app = Flask(__name__)

    # Render ortaminda production, yerelde development ayarlari kullanilir.
    environment = os.getenv(
        "APP_ENV",
        "production" if os.getenv("RENDER") else "development"
    )

    config_class = CONFIG_BY_NAME.get(
        environment,
        CONFIG_BY_NAME["development"]
    )

    app.config.from_object(config_class)

    # Wix ve diger istemcilerden gelen API isteklerine izin verir.
    cors_origins = app.config["CORS_ORIGINS"]

    if cors_origins == "*":
        CORS(app)
    else:
        CORS(
            app,
            origins=[
                origin.strip()
                for origin in cors_origins.split(",")
                if origin.strip()
            ]
        )

    # SQLite veritabanini hazirlar.
    init_db(app)

    # Sayfa ve API Blueprint'lerini uygulamaya kaydeder.
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/health")
    @app.route("/healthz")
    def health():
        return jsonify(
            {
                "basari": True,
                "durum": "aktif",
                "servis": "TANAXIS AI",
                "ortam": environment
            }
        ), 200

    return app