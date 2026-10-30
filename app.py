import os
from flask import Flask, render_template, jsonify
from config import Config
from database.connection import db
from database.seed_data import seed_database
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.scan import scan_bp
from routes.analysis import analysis_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize directories
    Config.init_app()

    # Initialize and seed database
    try:
        schema_path = os.path.join(app.root_path, "database", "schema.sql")
        db.init_db(schema_path)
        seed_database()
    except Exception as e:
        print(f"CRITICAL: Failed to initialize or seed the database on startup: {e}")

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(analysis_bp)

    # Route for serving the frontend SPA
    @app.route('/')
    def index():
        return render_template('index.html')

    # General error handling
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "An internal server error occurred. Please contact support."}), 500

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({"error": "File size exceeds the maximum limit of 8MB."}), 413

    return app

app = create_app()

if __name__ == '__main__':
    # Start dev server on local port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
