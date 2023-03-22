from flask import Flask, jsonify
from flask_restx import Api


BASE_URL = "/parser"

def create_app():
    from app.routes import register_routes
    app = Flask(__name__, instance_relative_config=False)

    api = Api(
        app,
        title="Arborator-Grew Parser",
        version="0.1.0",
        doc=f"{BASE_URL}/doc",
        endpoint=f"{BASE_URL}/",
        base_url=f"{BASE_URL}/",
    )

    register_routes(api, BASE_URL)

    @app.route("/health")
    def health():
        return jsonify("healthy")


    return app
